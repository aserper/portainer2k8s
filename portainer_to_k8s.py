#!/usr/bin/env python3
"""Generate a Kubernetes manifest from a Docker container defined in Portainer."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Any, Dict, Iterable, List, Optional

import requests

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None


class PortainerClient:
    """Small helper around the Portainer API."""

    def __init__(
        self,
        base_url: str,
        endpoint_id: int,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("Portainer URL must include http:// or https://")

        self.base_url = base_url.rstrip("/")
        self.endpoint_id = endpoint_id
        self.session = requests.Session()

        if api_key:
            self.session.headers["X-API-Key"] = api_key
        elif username and password:
            token = self._login(username, password)
            self.session.headers["Authorization"] = f"Bearer {token}"
        else:
            raise ValueError("Provide either an API key or username/password for Portainer")

    def _login(self, username: str, password: str) -> str:
        response = self.session.post(
            f"{self.base_url}/api/auth",
            json={"Username": username, "Password": password},
            timeout=15,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Failed to authenticate: HTTP {response.status_code} {response.text}")

        payload = response.json()
        return payload["jwt"]

    def resolve_container_id(self, container_ref: str) -> str:
        """Allow users to reference a container by prefix or name."""
        response = self.session.get(
            f"{self.base_url}/api/endpoints/{self.endpoint_id}/docker/containers/json",
            params={"all": True},
            timeout=15,
        )
        response.raise_for_status()

        matches: List[str] = []
        for container in response.json():
            container_id = container["Id"]
            names = [name.lstrip("/") for name in container.get("Names", [])]
            if container_id.startswith(container_ref) or container_ref in names:
                matches.append(container_id)

        if not matches:
            raise RuntimeError(f"No container matching '{container_ref}' on endpoint {self.endpoint_id}")
        if len(matches) > 1:
            raise RuntimeError(f"Multiple containers match '{container_ref}': {', '.join(matches)}")

        return matches[0]

    def get_container_details(self, container_id: str) -> Dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api/endpoints/{self.endpoint_id}/docker/containers/{container_id}/json",
            timeout=15,
        )
        response.raise_for_status()
        return response.json()


def sanitize_name(name: str) -> str:
    """Convert Docker names to valid Kubernetes resource names."""
    name = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    return name or "container"


def transform_env(env_list: Iterable[str]) -> List[Dict[str, str]]:
    env_entries: List[Dict[str, str]] = []
    for item in env_list:
        if "=" in item:
            key, value = item.split("=", 1)
        else:
            key, value = item, ""
        env_entries.append({"name": key, "value": value})
    return env_entries


def build_volumes(mounts: Iterable[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    volume_defs: List[Dict[str, Any]] = []
    mount_defs: List[Dict[str, Any]] = []

    for index, mount in enumerate(mounts):
        mount_name = sanitize_name(mount.get("Name") or mount.get("Source") or f"vol-{index}")
        volume_mount = {"name": mount_name, "mountPath": mount.get("Destination", "/data")}
        if mount.get("RW") is False or mount.get("ReadOnly"):
            volume_mount["readOnly"] = True
        mount_defs.append(volume_mount)

        if mount.get("Type") == "bind":
            source_path = mount.get("Source")
            if not source_path:
                continue
            volume_defs.append(
                {
                    "name": mount_name,
                    "hostPath": {
                        "path": source_path,
                        "type": "DirectoryOrCreate" if mount.get("Propagation") else "Directory",
                    },
                }
            )
        else:
            volume_defs.append(
                {
                    "name": mount_name,
                    "persistentVolumeClaim": {
                        "claimName": mount_name,
                    },
                }
            )

    return {"volumes": volume_defs, "volume_mounts": mount_defs}


def collect_ports(port_map: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not port_map:
        return []

    ports: List[Dict[str, Any]] = []
    for exposed, bindings in port_map.items():
        try:
            container_port, protocol = exposed.split("/")
        except ValueError:
            continue
        entry: Dict[str, Any] = {
            "name": f"port-{container_port}-{protocol}",
            "port": int(container_port),
            "targetPort": int(container_port),
            "protocol": protocol.upper(),
        }
        if bindings:
            binding = bindings[0]
            if binding.get("HostPort"):
                entry["port"] = int(binding["HostPort"])
        ports.append(entry)
    return ports


def build_k8s_documents(
    container_details: Dict[str, Any],
    namespace: str,
) -> List[Dict[str, Any]]:
    config = container_details.get("Config", {})
    container_name = sanitize_name(config.get("Hostname") or container_details.get("Name", "app"))
    image = config.get("Image", "image:latest")
    env_vars = transform_env(config.get("Env", []))
    mounts = build_volumes(container_details.get("Mounts", []))
    ports = collect_ports(container_details.get("NetworkSettings", {}).get("Ports"))

    container_spec: Dict[str, Any] = {
        "name": container_name,
        "image": image,
    }
    if config.get("Cmd"):
        container_spec["args"] = config["Cmd"]
    if config.get("Entrypoint"):
        container_spec["command"] = config["Entrypoint"]
    if env_vars:
        container_spec["env"] = env_vars
    if mounts["volume_mounts"]:
        container_spec["volumeMounts"] = mounts["volume_mounts"]
    if ports:
        container_spec["ports"] = [
            {"containerPort": port["targetPort"], "protocol": port["protocol"]} for port in ports
        ]

    deployment: Dict[str, Any] = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": container_name, "namespace": namespace},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app": container_name}},
            "template": {
                "metadata": {"labels": {"app": container_name}},
                "spec": {"containers": [container_spec]},
            },
        },
    }
    if mounts["volumes"]:
        deployment["spec"]["template"]["spec"]["volumes"] = mounts["volumes"]

    documents: List[Dict[str, Any]] = [deployment]

    if ports:
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": f"{container_name}-svc", "namespace": namespace},
            "spec": {
                "selector": {"app": container_name},
                "ports": ports,
                "type": "ClusterIP",
            },
        }
        documents.append(service)

    return documents


def dump_yaml(documents: Iterable[Dict[str, Any]]) -> str:
    if yaml:
        return "\n---\n".join(yaml.safe_dump(doc, sort_keys=False).rstrip() for doc in documents)

    return "\n---\n".join(_fallback_yaml_dump(doc).rstrip() for doc in documents)


def _fallback_yaml_dump(node: Any, indent: int = 0) -> str:
    spacing = " " * indent
    if isinstance(node, dict):
        lines: List[str] = []
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{spacing}{key}:")
                lines.append(_fallback_yaml_dump(value, indent + 2))
            else:
                lines.append(f"{spacing}{key}: {value}")
        return "\n".join(lines)
    if isinstance(node, list):
        lines = []
        for item in node:
            if isinstance(item, (dict, list)):
                lines.append(f"{spacing}-")
                lines.append(_fallback_yaml_dump(item, indent + 2))
            else:
                lines.append(f"{spacing}- {item}")
        return "\n".join(lines)
    return f"{spacing}{node}"


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a Portainer-managed container to a Kubernetes manifest.")
    
    # Try to load config for defaults
    try:
        from config import load_config
        config = load_config()
        if config and "portainer" in config:
            portainer_config = config["portainer"]
            default_url = portainer_config.get("url")
            default_endpoint = portainer_config.get("endpoint_id")
            auth_config = portainer_config.get("auth", {})
            default_api_key = auth_config.get("api_key")
            default_username = auth_config.get("username")
        else:
            default_url = default_endpoint = default_api_key = default_username = None
    except Exception:
        default_url = default_endpoint = default_api_key = default_username = None
    
    # Mode selection
    subparsers = parser.add_subparsers(dest="mode", help="Mode of operation")
    
    # CLI mode
    cli_parser = subparsers.add_parser("cli", help="Command-line interface mode")
    cli_parser.add_argument(
        "--url", 
        required=(default_url is None), 
        default=default_url,
        help="Base URL of the Portainer instance, e.g. https://portainer.local (default from config.yaml)"
    )
    cli_parser.add_argument(
        "--endpoint", 
        required=(default_endpoint is None),
        type=int,
        default=default_endpoint,
        help="Portainer endpoint ID (default from config.yaml)"
    )
    cli_parser.add_argument("--container", required=True, help="Container ID prefix or name to export")
    cli_parser.add_argument("--namespace", default="default", help="Kubernetes namespace for generated resources")

    auth = cli_parser.add_mutually_exclusive_group(required=(default_api_key is None and default_username is None))
    auth.add_argument("--api-key", default=default_api_key, help="Portainer API key (default from config.yaml)")
    auth.add_argument("--username", default=default_username, help="Portainer username (requires --password, default from config.yaml)")
    cli_parser.add_argument("--password", help="Portainer password (requires --username)")

    # TUI mode
    tui_parser = subparsers.add_parser("tui", help="Terminal user interface mode (interactive)")
    
    # Default to CLI if no subcommand
    args = parser.parse_args(argv)
    if args.mode is None:
        args.mode = "cli"
        # Re-parse with CLI mode expectations for backward compatibility
        args = cli_parser.parse_args(argv)
    
    return args


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    
    # Launch TUI mode if requested
    if args.mode == "tui":
        try:
            from portainer_tui import run_tui
            run_tui()
            return 0
        except ImportError:
            raise SystemExit(
                "TUI mode requires textual. Install with: pip install textual"
            )
    
    # CLI mode (default)
    if args.username and not args.password:
        raise SystemExit("--username also requires --password")

    client = PortainerClient(
        base_url=args.url,
        endpoint_id=args.endpoint,
        api_key=args.api_key,
        username=args.username,
        password=args.password,
    )

    container_id = client.resolve_container_id(args.container)
    container_details = client.get_container_details(container_id)
    documents = build_k8s_documents(container_details, args.namespace)
    manifest = dump_yaml(documents)
    print(manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())


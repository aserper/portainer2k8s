#!/usr/bin/env python3
"""Configuration file management for portainer-to-k8s."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None

CONFIG_FILE = "config.yaml"


def config_exists() -> bool:
    """Check if configuration file exists."""
    return os.path.exists(CONFIG_FILE)


def load_config() -> Optional[Dict[str, Any]]:
    """Load configuration from config.yaml.
    
    Returns:
        Configuration dictionary or None if file doesn't exist or is invalid.
    """
    if not config_exists():
        return None
    
    if yaml is None:
        return None
        
    try:
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
            return config if config else None
    except Exception:
        return None


def save_config(
    url: str,
    endpoint_id: int,
    api_key: Optional[str] = None,
    username: Optional[str] = None,
) -> None:
    """Save configuration to config.yaml.
    
    Note: Passwords are NOT saved for security reasons.
    
    Args:
        url: Portainer base URL
        endpoint_id: Portainer endpoint ID
        api_key: Optional API key (saved if provided)
        username: Optional username (saved if provided, but not password)
    """
    if yaml is None:
        raise RuntimeError("PyYAML is required to save configuration")
    
    config_data = {
        "portainer": {
            "url": url,
            "endpoint_id": endpoint_id,
            "auth": {},
        }
    }
    
    if api_key:
        config_data["portainer"]["auth"]["api_key"] = api_key
        config_data["portainer"]["auth"]["method"] = "api_key"
    elif username:
        config_data["portainer"]["auth"]["username"] = username
        config_data["portainer"]["auth"]["method"] = "username_password"
    
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(config_data, f, sort_keys=False, default_flow_style=False)


def delete_config() -> None:
    """Delete the configuration file."""
    if config_exists():
        os.remove(CONFIG_FILE)

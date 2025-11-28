# Portainer to Kubernetes Converter

![Portainer to K8s Logo](logo.png)

This tool converts Docker containers managed by Portainer into Kubernetes manifests (Deployment + Service). It supports both an interactive terminal UI (TUI) and a command-line interface (CLI) for automation.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/aserper/portainer2k8s.git
    cd portainer2k8s
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Interactive Mode (TUI)

Run the interactive tool to connect to Portainer, browse endpoints, and select containers to export.

```bash
python3 portainer_tui.py
```

The first run will prompt you for your Portainer URL and credentials.

### CLI Mode

Use the CLI for direct conversion or scripting.

```bash
python3 portainer_to_k8s.py cli --url <URL> --container <NAME_OR_ID> --api-key <KEY>
```

**Example:**

```bash
python3 portainer_to_k8s.py cli \
  --url https://portainer.local \
  --container my-app \
  --namespace production \
  --api-key "your-api-key"
```

## Configuration

Connection settings are stored in `config.yaml`. This file is created automatically by the TUI or can be created manually.

```yaml
portainer:
  url: "https://portainer.local"
  endpoint_id: 1
  auth:
    method: "api_key"
    api_key: "your-api-key"
```

## License

MIT License
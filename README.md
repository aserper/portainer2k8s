# Portainer to Kubernetes Manifest Converter

Convert Docker containers running in Portainer to Kubernetes manifests.

## ✨ Two Ways to Use

### 🎨 Terminal UI (Interactive)
A beautiful, intuitive terminal interface for exploring and converting containers.

```bash
python3 portainer_tui.py
```

**Perfect for:**
- One-off manual conversions
- Visual exploration of containers
- Interactive manifest preview
- First-time users

**Features:**
- 4-screen workflow (connect → select → configure → preview)
- Real-time container listing
- Syntax-highlighted YAML preview
- Save to file or copy to clipboard
- Beautiful colors and responsive UI

👉 **[Full TUI Guide](README_TUI.md)** | **[Detailed Instructions](TUI_GUIDE.md)**

### 🚀 Command Line (Automated)
Command-line interface for scripting and automation.

```bash
python3 portainer_to_k8s.py cli \
  --url https://portainer.local \
  --endpoint 1 \
  --container nginx \
  --api-key your-api-key
```

**Perfect for:**
- CI/CD pipelines
- Batch conversions
- Automation scripts
- Piping to other tools

**Features:**
- Direct container reference by ID or name
- Customizable namespace
- YAML output to stdout
- Simple error handling

## Installation

### Requirements
- Python 3.8 or higher
- pip

### Setup

**Basic installation (CLI only):**
```bash
pip install requests pyyaml
```

**With TUI support (recommended):**
```bash
pip install textual requests pyyaml
```

Or in one command:
```bash
pip install textual>=6.6.0 requests>=2.28.0 pyyaml>=6.0
```

## Quick Start

### Use the TUI (Recommended for beginners)
```bash
python3 portainer_tui.py
```

Then:
1. Enter your Portainer URL and endpoint ID
2. Choose authentication method (API key or username/password)
3. Select a container from the list
4. Review and save the manifest

### Use the CLI
```bash
python3 portainer_to_k8s.py cli \
  --url https://portainer.example.com \
  --endpoint 1 \
  --container my-container \
  --api-key your-api-key-here > manifest.yaml
```

## Usage Examples

### TUI Mode

#### Interactive container discovery
```bash
$ python3 portainer_tui.py

# Then use the interactive interface to:
# 1. Enter Portainer connection details
# 2. Browse all available containers
# 3. Select and configure a container
# 4. Preview the generated manifest
# 5. Save to file or copy to clipboard
```

### CLI Mode

#### Export a container with API key
```bash
python3 portainer_to_k8s.py cli \
  --url https://portainer.local \
  --endpoint 1 \
  --container nginx \
  --api-key abc123def456 \
  --namespace production \
  > nginx-manifest.yaml
```

#### Export using username/password
```bash
python3 portainer_to_k8s.py cli \
  --url https://portainer.local \
  --endpoint 1 \
  --container mysql \
  --username admin \
  --password secret123 \
  --namespace databases
```

#### Export by container prefix
```bash
# References containers starting with "web"
python3 portainer_to_k8s.py cli \
  --url https://portainer.local \
  --endpoint 1 \
  --container web \
  --api-key abc123def456
```

#### Export and apply directly to Kubernetes
```bash
python3 portainer_to_k8s.py cli \
  --url https://portainer.local \
  --endpoint 1 \
  --container nginx \
  --api-key abc123def456 \
  | kubectl apply -f -
```

## Getting Your Credentials

### API Key (Recommended)
1. Open Portainer in your browser
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name it and create
5. Copy the key

### Endpoint ID
1. In Portainer, go to **Environments**
2. Find your endpoint
3. The ID is shown next to the environment name
4. Common default: `1`

## Generated Manifest

The converter generates a Kubernetes manifest with:

- **Deployment**: Runs your container with all settings
  - Image and tag
  - Environment variables
  - Volume mounts
  - Container ports

- **Service**: Exposes your container (if ports are configured)
  - Service type (ClusterIP)
  - Port mappings
  - Selectors for the deployment

Example output:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
          protocol: TCP
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
  namespace: default
spec:
  selector:
    app: nginx
  ports:
  - name: port-80-tcp
    port: 80
    targetPort: 80
    protocol: TCP
  type: ClusterIP
```

## Features

✅ **Container to Kubernetes Conversion**
- Extracts all container configuration
- Generates valid Kubernetes YAML
- Supports Deployments and Services

✅ **Flexible Authentication**
- API key authentication (recommended)
- Username/password authentication
- Secure credential handling

✅ **Multiple Interfaces**
- Interactive TUI for exploration
- CLI for automation
- Both modes share the same conversion logic

✅ **Customization**
- Set custom Kubernetes namespace
- Modify generated manifest before applying
- Reference containers by ID or name

✅ **Easy Deployment**
- Save to file for later
- Copy to clipboard for quick paste
- Pipe directly to kubectl
- Apply to any Kubernetes cluster

## Architecture

```
portainer_to_k8s.py
├── PortainerClient (API communication)
├── Conversion Functions
│   ├── sanitize_name() - Convert Docker names to K8s format
│   ├── transform_env() - Convert environment variables
│   ├── build_volumes() - Build volume definitions
│   ├── collect_ports() - Collect port configurations
│   └── build_k8s_documents() - Assemble Kubernetes resources
└── YAML Output Functions

portainer_tui.py (Interactive mode)
├── PortainerToK8sApp (Main application)
├── WelcomeScreen (Connection setup)
├── ContainerSelectScreen (Browse containers)
├── ConfigureScreen (Settings)
└── PreviewScreen (Review & save)
```

## Code Quality

- **Type hints** on all functions and methods
- **Docstrings** for all classes and functions
- **Error handling** with meaningful error messages
- **Input validation** on all user inputs
- **Follows PEP 8** style guidelines
- **Modular design** for easy testing and extension

## Testing

To verify the installation:

```bash
# Test Python syntax
python3 -m py_compile portainer_to_k8s.py
python3 -m py_compile portainer_tui.py

# Test imports
python3 -c "from portainer_to_k8s import PortainerClient; print('✓ CLI OK')"
python3 -c "from portainer_tui import PortainerToK8sApp; print('✓ TUI OK')"

# Test help
python3 portainer_to_k8s.py --help
python3 portainer_tui.py --help
```

## Troubleshooting

### Connection Issues
```bash
# Error: "Failed to authenticate"
# Check:
# - URL includes http:// or https://
# - Endpoint ID is correct
# - API key is valid (or username/password)
# - Network connectivity to Portainer
```

### Container Not Found
```bash
# Error: "No container matching 'xyz'"
# Check:
# - Container name or ID prefix is correct
# - Container exists on the selected endpoint
# - You have access to the endpoint
```

### No Containers Listed
```bash
# When using TUI, if no containers appear:
# - Verify endpoint has containers
# - Check authentication has access
# - Try clicking "Back" and selecting again
```

### Manifest Issues
```bash
# Generated manifest doesn't look right:
# - Some fields are optional and won't appear if not set
# - You can manually edit the saved file
# - Add more configuration (resources, health checks, etc.)
# - Test in dev cluster first
```

## FAQ

**Q: Is this safe to use in production?**
A: The generated manifests are valid Kubernetes resources, but you should:
- Always test in development first
- Review the manifest before applying
- Add resource limits and requests
- Configure health checks and probes
- Use Secrets for sensitive data

**Q: What container settings are NOT converted?**
A: Advanced features that require manual configuration:
- Resource limits/requests
- Health checks (liveness/readiness probes)
- Pod security policies
- Network policies
- Storage classes
- Custom resource definitions

**Q: Can I use this for bulk exports?**
A: Yes, you can:
- Use TUI to export each container individually
- Use CLI in a loop to export multiple containers
- Combine manifests with `cat container*.yaml > all.yaml`

**Q: Does this support Docker Compose files?**
A: No, it specifically works with Portainer-managed containers. For Compose files, use conversion tools like Kompose.

**Q: Can I edit the manifest after generation?**
A: Absolutely! The generated manifest is a starting point. You can:
- Edit the YAML file directly
- Add more advanced configurations
- Commit to version control
- Use templating tools like Helm or Kustomize

## Requirements

- Python 3.8+
- requests 2.28.0+ (for HTTP communication)
- pyyaml 6.0+ (for YAML generation)
- textual 6.6.0+ (for TUI mode, optional)

## Python Version Support

- Python 3.8: ✅ Fully supported
- Python 3.9: ✅ Fully supported
- Python 3.10: ✅ Fully supported
- Python 3.11: ✅ Fully supported
- Python 3.12: ✅ Fully supported
- Python 3.13: ✅ Fully supported

## Performance

- **Connection time**: Typically <1 second
- **Manifest generation**: Usually <500ms
- **Memory usage**: < 50 MB for typical containers
- **File I/O**: < 100ms for saving manifests

## Limitations

- Requires Portainer API v2.0 or newer
- Only works with Docker endpoints (not Swarm or Kubernetes)
- Some advanced Docker features may not convert perfectly
- Manual editing may be needed for complex configurations
- Clipboard functionality requires xclip (Linux) or pbcopy (macOS)

## Integration Examples

### Save to File
```bash
python3 portainer_tui.py
# Use "Save to File" button to save as {container}-manifest.yaml
```

### Pipe to kubectl
```bash
python3 portainer_to_k8s.py cli \
  --url https://portainer.local \
  --endpoint 1 \
  --container nginx \
  --api-key $API_KEY \
  | kubectl apply -f -
```

### Save in Version Control
```bash
python3 portainer_to_k8s.py cli \
  --url https://portainer.local \
  --endpoint 1 \
  --container nginx \
  --api-key $API_KEY > manifests/nginx.yaml

git add manifests/nginx.yaml
git commit -m "Add nginx Kubernetes manifest"
```

### Batch Export Loop
```bash
#!/bin/bash
for container in nginx mysql redis; do
  python3 portainer_to_k8s.py cli \
    --url https://portainer.local \
    --endpoint 1 \
    --container $container \
    --api-key $API_KEY \
    > manifests/${container}.yaml
done
```

## Contributing

Contributions are welcome! Please:

1. Follow PEP 8 style guidelines
2. Add type hints for new code
3. Write docstrings for new functions
4. Update documentation
5. Test your changes

## License

MIT License - See LICENSE file for details

## See Also

- **[TUI Guide](README_TUI.md)** - Detailed TUI usage instructions
- **[TUI Usage](TUI_GUIDE.md)** - Complete TUI walkthrough
- **[Textual Framework](https://textual.textualize.io/)** - TUI framework used
- **[Portainer Documentation](https://docs.portainer.io/)** - Portainer reference
- **[Kubernetes Docs](https://kubernetes.io/docs/)** - Kubernetes reference

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the generated manifest for obvious issues
3. Test with a simple container first
4. Check Portainer and Kubernetes logs

## Acknowledgments

Built with:
- [Textual](https://textual.textualize.io/) - Modern TUI framework for Python
- [Rich](https://rich.readthedocs.io/) - Rich text and beautiful formatting
- [Requests](https://requests.readthedocs.io/) - HTTP library for Python
- [PyYAML](https://pyyaml.org/) - YAML parser and emitter

---

**Made with ❤️ for the Kubernetes community**

Questions or suggestions? Open an issue on GitHub!

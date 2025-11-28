# Portainer to Kubernetes - TUI Guide

A beautiful, intuitive terminal user interface for converting Docker containers from Portainer to Kubernetes manifests.

## Overview

The TUI provides an interactive, step-by-step workflow to:
1. Connect to your Portainer instance
2. Select a Docker container to export
3. Configure Kubernetes export settings
4. Preview and save the generated manifest

## Installation

### Requirements
- Python 3.8+
- `pip`

### Setup
```bash
pip install textual requests pyyaml
```

Or install with the TUI feature:
```bash
pip install -e .
```

## Quick Start

### Launch the TUI
```bash
python3 portainer_tui.py
```

Or use the main script with TUI mode:
```bash
python3 portainer_to_k8s.py tui
```

## Usage Guide

### Screen 1: Welcome / Connection Setup

This is the first screen you'll see when launching the application.

**Fields:**
- **Portainer URL**: The base URL of your Portainer instance
  - Example: `https://portainer.example.com`
  - Must include `http://` or `https://`

- **Endpoint ID**: The numeric ID of the Portainer endpoint
  - Example: `1`
  - You can find this in Portainer's UI

- **Authentication Method**: Choose how to authenticate
  - **API Key**: Use a pre-generated API key (recommended for security)
  - **Username/Password**: Use your Portainer credentials

- **API Key** (if using API Key auth):
  - Your Portainer API key
  - Generate one in Portainer: Settings → API Keys

- **Username** (if using Username/Password):
  - Your Portainer login username

- **Password** (if using Username/Password):
  - Your Portainer login password
  - Will be masked in the input field

**Actions:**
- **Connect**: Validate connection and proceed to container selection
- **Quit**: Exit the application

**Tips:**
- Use API Key authentication when possible for better security
- Ensure your Portainer instance is accessible from your network

### Screen 2: Container Selection

After connecting, you'll see a list of all containers available on the selected endpoint.

**Display Format:**
Each container shows:
```
container-name (short-id) - container-state
```

Example:
```
mysql (a1b2c3d4e5f6) - running
nginx (f6e5d4c3b2a1) - exited
```

**Actions:**
- **Export**: Select a container and export it (first select it with arrow keys)
- **Back**: Return to connection setup
- **Quit**: Exit the application

**Navigation:**
- **Arrow Up/Down**: Navigate through container list
- **Enter**: Select/confirm
- **Tab**: Move between buttons

### Screen 3: Configure Export Settings

Configure the Kubernetes namespace and other export parameters.

**Fields:**
- **Kubernetes Namespace**: The Kubernetes namespace where this manifest will be deployed
  - Default: `default`
  - Examples: `production`, `staging`, `my-app`
  - Must follow Kubernetes naming rules (lowercase, alphanumeric, hyphens)

**Actions:**
- **Generate & Preview**: Generate the K8s manifest and proceed to preview
- **Back**: Return to container selection
- **Quit**: Exit the application

**Tips:**
- Use descriptive namespace names to organize your workloads
- Ensure the namespace exists in your Kubernetes cluster

### Screen 4: Manifest Preview

Review the generated Kubernetes manifest before saving.

**Display:**
- Syntax-highlighted YAML manifest
- Includes Deployment and Service resources
- Fully scrollable to review all content

**Actions:**
- **Save to File**: Save the manifest to a file in the current directory
  - Filename format: `{container-name}-manifest.yaml`
  - Example: `nginx-manifest.yaml`

- **Copy to Clipboard**: Copy the entire manifest to your clipboard
  - Requires `xclip` (Linux) or `pbcopy` (macOS)
  - Useful for pasting into editors or directly applying to cluster

- **Back**: Return to configuration (you can regenerate with different settings)
- **Quit**: Exit the application

**Tips:**
- Review the manifest to ensure all configurations are correct
- Check volume mounts, environment variables, and port mappings
- You can edit the manifest after saving if needed

## Keyboard Shortcuts

### Global Shortcuts
| Key | Action |
|-----|--------|
| `Tab` | Move to next field/button |
| `Shift+Tab` | Move to previous field/button |
| `Enter` | Confirm selection or activate button |
| `Esc` | Cancel (context-dependent) |
| `q` | Quit application |
| `Ctrl+C` | Force quit |

### Navigation
| Key | Action |
|-----|--------|
| `Arrow Up` | Move up in lists |
| `Arrow Down` | Move down in lists |
| `Home` | Jump to start |
| `End` | Jump to end |
| `Page Up` | Scroll up |
| `Page Down` | Scroll down |

### Text Input
| Key | Action |
|-----|--------|
| `Ctrl+A` | Select all text |
| `Ctrl+U` | Clear field |
| `Backspace` | Delete character |
| `Ctrl+W` | Delete word |

## Common Workflows

### Export a Running Container
1. Launch TUI: `python3 portainer_tui.py`
2. Enter connection details (URL, Endpoint ID, API Key)
3. Click **Connect**
4. Select your running container from the list
5. Click **Export**
6. Review the default namespace (or customize it)
7. Click **Generate & Preview**
8. Review the manifest
9. Click **Save to File** or **Copy to Clipboard**

### Save for Later Review
1. After generating manifest, click **Save to File**
2. Open the saved file in your text editor
3. Make any necessary adjustments
4. Apply to cluster: `kubectl apply -f filename.yaml`

### Apply Directly to Cluster
1. After generating manifest, click **Copy to Clipboard**
2. Run: `kubectl apply -f -` and paste when prompted
3. Or pipe directly: `echo "manifest" | kubectl apply -f -`

## Troubleshooting

### "Connection failed: [error message]"
- Check that the Portainer URL is correct and includes `http://` or `https://`
- Verify you can reach the Portainer instance from your network
- Ensure the endpoint ID matches an existing endpoint in Portainer
- If using API key, verify it's valid and hasn't expired
- If using credentials, check username and password are correct

### "No containers found"
- The selected endpoint may have no containers
- Check that you selected the correct endpoint
- Some containers may be hidden if they're stopped (this shouldn't happen)

### "Failed to load containers"
- Verify network connectivity to Portainer
- Check that your authentication is still valid
- Try refreshing by going back and selecting the endpoint again

### "xclip not found" (when copying to clipboard)
- On Linux: Install xclip: `sudo apt install xclip`
- On macOS: Should use `pbcopy` automatically
- As fallback: Use **Save to File** instead

### Manifest looks incomplete
- This is normal - only configured settings are included
- Volumes may show as `persistentVolumeClaim` if not bind mounts
- You can manually edit the saved file to add missing fields

## Best Practices

### Security
- Use API Keys instead of username/password when possible
- Don't share your API key or credentials
- Use HTTPS URLs for Portainer connections
- Store generated manifests securely if they contain sensitive data

### Manifest Quality
- Always review the generated manifest before applying
- Test in a development cluster first
- Adjust resource requests/limits as needed
- Add health checks and probes for production use
- Consider using ConfigMaps for configuration data
- Use Secrets for sensitive data (API keys, passwords)

### Organization
- Use descriptive namespace names
- Group related containers in the same namespace
- Keep manifests in version control
- Document any manual modifications

## Advanced Usage

### Customizing Generated Manifests
After saving a manifest, you can:
1. Edit the YAML file manually
2. Add resource limits:
   ```yaml
   resources:
     requests:
       memory: "64Mi"
       cpu: "250m"
     limits:
       memory: "128Mi"
       cpu: "500m"
   ```
3. Add health checks:
   ```yaml
   livenessProbe:
     httpGet:
       path: /health
       port: 8080
     initialDelaySeconds: 30
     periodSeconds: 10
   ```

### Bulk Export
To export multiple containers:
1. Repeat the workflow for each container
2. Each will save to a separate file
3. Combine into a single manifest (optional):
   ```bash
   cat container1-manifest.yaml container2-manifest.yaml > combined.yaml
   ```

### Integration with Version Control
```bash
# Add manifests to Git
git add *-manifest.yaml
git commit -m "Add Kubernetes manifests from Portainer"
git push
```

## See Also

- **CLI Mode**: `python3 portainer_to_k8s.py cli --help`
- **Project README**: See `README.md`
- **Textual Framework**: https://textual.textualize.io
- **Kubernetes YAML Spec**: https://kubernetes.io/docs/concepts/configuration/overview/

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the generated manifest for obvious issues
3. Test with a simple container first
4. Check Portainer and Kubernetes logs for clues

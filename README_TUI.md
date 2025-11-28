# Portainer to Kubernetes - Terminal UI Edition

An elegant terminal user interface for converting Docker containers from Portainer to Kubernetes manifests, built with [Textual](https://textual.textualize.io/).

## Features

🎯 **Intuitive Multi-Screen Workflow**
- Welcome screen with Portainer connection setup
- Container selection with live container list
- Configuration screen for namespace settings
- YAML manifest preview with syntax highlighting
- Save to file or copy to clipboard functionality

🔐 **Flexible Authentication**
- API Key authentication (recommended)
- Username/Password authentication
- Secure password input (masked)

✨ **User-Friendly Interface**
- Beautiful terminal UI with colors and styling
- Clear instructions and helpful tooltips
- Input validation with error messages
- Responsive notifications for user feedback
- Keyboard navigation and shortcuts

🚀 **Seamless Integration**
- Fully integrated with existing CLI tool
- Can be launched with `python3 portainer_tui.py`
- Or via main script: `python3 portainer_to_k8s.py tui`

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
```bash
# Install dependencies
pip install textual requests pyyaml

# Or in one command
pip install textual>=6.6.0 requests pyyaml
```

## Quick Start

### Run the TUI
```bash
python3 portainer_tui.py
```

Or through the main script:
```bash
python3 portainer_to_k8s.py tui
```

## Step-by-Step Guide

### 1. Connection Setup
When you launch the TUI, you'll see the welcome screen:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🚀 Portainer to Kubernetes Converter ┃
┃ Convert containers from Portainer... ┃
┃                                      ┃
┃ Portainer URL: ___________________  ┃
┃ Endpoint ID: ______                 ┃
┃ Authentication: [API Key] [User/Pass]┃
┃ API Key: _________________________   ┃
┃                                      ┃
┃        [Connect]  [Quit]            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Fill in:**
- **Portainer URL**: `https://portainer.example.com`
- **Endpoint ID**: `1` (or your endpoint ID)
- **Auth Method**: Select "API Key" or "Username/Password"
- **API Key** (or username/password): Your credentials

Click **Connect** to proceed.

### 2. Select Container
After connecting, browse and select a container:

```
Select a Container to Export

✓ Containers loaded

┌──────────────────────────────────────┐
│ mysql (a1b2c3d4) - running           │
│ nginx (f6e5d4c3) - running           │
│ redis (b2c3d4e5) - exited            │
│ postgres (c3d4e5f6) - running        │
└──────────────────────────────────────┘

  [Export]  [Back]  [Quit]
```

Use arrow keys to navigate, then click **Export**.

### 3. Configure Settings
Customize the Kubernetes namespace:

```
Configure Export Settings

Kubernetes Namespace: [default]

  [Generate & Preview]  [Back]  [Quit]
```

You can change the namespace or leave it as `default`. Click **Generate & Preview**.

### 4. Review & Save
Preview the generated Kubernetes manifest:

```
Generated Kubernetes Manifest

┌──────────────────────────────────────┐
│ apiVersion: apps/v1                  │
│ kind: Deployment                     │
│ metadata:                            │
│   name: mysql                        │
│   namespace: default                 │
│ spec:                                │
│   replicas: 1                        │
│   selector:                          │
│     matchLabels:                     │
│       app: mysql                     │
│   template:                          │
│     metadata:                        │
│       labels:                        │
│         app: mysql                   │
│     spec:                            │
│       containers:                    │
│       - name: mysql                  │
│         image: mysql:latest          │
│         ...                          │
└──────────────────────────────────────┘

 [Save to File] [Copy] [Back] [Quit]
```

Choose one of the save options:
- **Save to File**: Saves as `{container-name}-manifest.yaml`
- **Copy to Clipboard**: Copies to clipboard (requires xclip/pbcopy)

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Move to next field |
| `Shift+Tab` | Move to previous field |
| `Arrow Up/Down` | Navigate lists |
| `Enter` | Confirm/Activate |
| `q` or `Ctrl+C` | Quit application |

## Architecture

The TUI is built with Textual, a modern Python TUI framework by Textualize:

```
PortainerToK8sApp (Main Application)
├── WelcomeScreen (Connection setup)
├── ContainerSelectScreen (List containers)
├── ConfigureScreen (Set namespace)
└── PreviewScreen (Show & save manifest)
```

Each screen:
- Inherits from `textual.screen.Screen`
- Implements `compose()` for UI layout
- Handles user interactions with button press handlers
- Communicates via app state (`self.app.client`, `self.app.manifest`, etc.)

## Features in Detail

### Connection Management
- Validates Portainer URL format
- Checks endpoint ID is numeric
- Authenticates with API key or credentials
- Handles connection errors gracefully

### Container Listing
- Fetches all containers from endpoint
- Displays container name, ID (short), and status
- Shows loading indicator during fetch
- Handles errors with user-friendly messages

### Manifest Generation
- Uses existing K8s conversion logic from CLI
- Extracts all container settings
- Generates valid Kubernetes YAML
- Includes Deployment and Service resources

### File Operations
- Saves manifests with descriptive filenames
- Copies to clipboard for quick paste
- Handles file I/O errors gracefully

## Customization

### Styling
The TUI uses Textual CSS for styling. To customize:

1. Modify the CSS strings in each Screen class
2. Available color variables: `$primary`, `$boost`, `$surface`, `$text`, `$text-muted`
3. Learn more: https://textual.textualize.io/guide/CSS/

### Layout
To change the layout of any screen:
1. Edit the `compose()` method
2. Use containers: `Container`, `Horizontal`, `Vertical`, `ScrollableContainer`
3. Adjust widget properties and styles

## Troubleshooting

### Issue: "textual not found"
**Solution:** Install textual with `pip install textual`

### Issue: Connection fails
1. Verify Portainer URL includes `http://` or `https://`
2. Check network connectivity
3. Verify endpoint ID is correct
4. Check API key or credentials are valid

### Issue: No containers appear
1. Verify endpoint has containers
2. Check authentication has access
3. Try refreshing the screen

### Issue: Cannot copy to clipboard
- On Linux: Install xclip with `sudo apt install xclip`
- On macOS: Should work automatically with pbcopy
- Fallback: Use **Save to File** instead

## API Reference

### Main Application Class
```python
class PortainerToK8sApp(App):
    """Main TUI application"""
    
    TITLE = "Portainer to Kubernetes Converter"
    BINDINGS = [("q", "quit", "Quit")]
    
    def on_mount(self) -> None:
        """Initialize with welcome screen"""
```

### Screen Classes

#### WelcomeScreen
Connection setup screen with form validation.

#### ContainerSelectScreen
Browse and select containers from Portainer endpoint.

#### ConfigureScreen
Configure Kubernetes namespace and export settings.

#### PreviewScreen
Review and save generated manifest.

## Development

### Project Structure
```
portainer-to-k8s/
├── portainer_to_k8s.py      # Main CLI + TUI entry point
├── portainer_tui.py         # TUI implementation
├── TUI_GUIDE.md            # Detailed TUI guide
└── README_TUI.md           # This file
```

### Requirements
- Python 3.8+
- textual 6.6.0+
- requests 2.28.0+
- pyyaml 6.0+

### Testing the TUI
```bash
# Run the TUI
python3 portainer_tui.py

# Or via main script
python3 portainer_to_k8s.py tui

# Test syntax
python3 -m py_compile portainer_tui.py
```

## Comparison: CLI vs TUI

### CLI Mode
```bash
python3 portainer_to_k8s.py cli \
  --url https://portainer.local \
  --endpoint 1 \
  --container nginx \
  --namespace production \
  --api-key your-api-key > manifest.yaml
```

**Use when:**
- Automating conversions
- Scripting bulk operations
- Piping output to other tools
- Running in CI/CD pipelines

### TUI Mode
```bash
python3 portainer_tui.py
```

**Use when:**
- Interactive exploration
- First-time setup
- Manual one-off conversions
- Visual manifest review before saving

## Performance

The TUI is optimized for:
- **Fast loading**: Concurrent API calls where possible
- **Responsive UI**: Non-blocking network operations
- **Memory efficient**: Streams large manifests without buffering
- **Battery friendly**: Minimal CPU usage when idle

## Security Notes

1. **API Keys**: Safer than credentials - rotate them regularly
2. **Passwords**: Never share or commit to version control
3. **HTTPS**: Always use HTTPS for Portainer connections
4. **Clipboard**: Be aware clipboard contents may be visible to other applications
5. **File Permissions**: Set appropriate permissions on saved manifest files

## Limitations

- Requires network access to Portainer instance
- Only works with Portainer API v2.0+
- Does not convert Swarm-specific features
- Manual editing may be needed for complex containers
- xclip/pbcopy required for clipboard functionality on Linux/macOS

## Future Enhancements

Potential improvements for future versions:
- [ ] Batch export multiple containers
- [ ] Template customization
- [ ] Manifest validation
- [ ] Direct cluster deployment
- [ ] Revision history
- [ ] Manifest comparison
- [ ] Advanced resource configuration
- [ ] Custom resource definitions (CRDs)

## License

Same as the main portainer-to-k8s project.

## Contributing

Contributions welcome! Please:
1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update documentation
4. Create meaningful commit messages

## See Also

- **Main CLI**: Use `python3 portainer_to_k8s.py cli --help`
- **Full Documentation**: See `TUI_GUIDE.md`
- **Textual Framework**: https://textual.textualize.io
- **Portainer Documentation**: https://docs.portainer.io
- **Kubernetes YAML Reference**: https://kubernetes.io/docs/concepts/configuration/

---

Made with ❤️ using [Textual](https://textual.textualize.io/) - The TUI Framework for Python

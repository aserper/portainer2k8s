# Installation Guide

## Quick Start

### Using Virtual Environment (Recommended)

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the TUI
python3 portainer_tui.py

# 5. Or run CLI
python3 portainer_to_k8s.py cli --help
```

### System-wide Installation

```bash
# Install dependencies globally
pip install -r requirements.txt

# Run the tool
python3 portainer_tui.py
```

## Requirements

### Python Version
- Python 3.8 or higher
- Tested with Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

### Dependencies

**Core Dependencies:**
- `requests>=2.28.0` - HTTP client for Portainer API
- `pyyaml>=6.0` - YAML parsing and generation

**TUI Dependencies:**
- `textual>=6.6.0` - Modern TUI framework

### Optional Dependencies

**For clipboard support (Linux):**
```bash
sudo apt install xclip
```

**For clipboard support (macOS):**
- `pbcopy` (pre-installed on macOS)

## Installation Methods

### Method 1: requirements.txt (Recommended)

```bash
pip install -r requirements.txt
```

### Method 2: Manual Installation

```bash
pip install requests>=2.28.0 pyyaml>=6.0 textual>=6.6.0
```

### Method 3: Minimal Installation (CLI only)

If you only need CLI mode and don't want TUI:

```bash
pip install requests>=2.28.0 pyyaml>=6.0
```

Then use only CLI mode:
```bash
python3 portainer_to_k8s.py cli --help
```

## Development Setup

For development with linting and testing tools:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 .
black --check .

# Run type checking
mypy *.py

# Run tests (if available)
pytest
```

## Verification

### Verify Installation

```bash
# Check Python version
python3 --version

# Check installed packages
pip list | grep -E "requests|pyyaml|textual"

# Test imports
python3 -c "import requests, yaml, textual; print('✓ All dependencies installed')"
```

### Test the Tools

```bash
# Test TUI
python3 -c "from portainer_tui import PortainerToK8sApp; print('✓ TUI ready')"

# Test CLI
python3 portainer_to_k8s.py --help

# Test config module
python3 -c "from config import load_config; print('✓ Config module ready')"
```

## Troubleshooting

### "No module named 'textual'"

**Solution:**
```bash
pip install textual>=6.6.0
```

### "No module named 'yaml'"

**Solution:**
```bash
pip install pyyaml>=6.0
```

### "No module named 'requests'"

**Solution:**
```bash
pip install requests>=2.28.0
```

### Virtual environment not activated

**Symptoms:** Installation seems to work but imports fail

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Reinstall
pip install -r requirements.txt
```

### Permission errors (system-wide install)

**Solution:** Use virtual environment or install with `--user`:
```bash
pip install --user -r requirements.txt
```

### Clipboard not working

**On Linux:**
```bash
sudo apt install xclip
# or
sudo yum install xclip
```

**On macOS:**
- Should work out of the box with `pbcopy`

**On Windows:**
- Clipboard copy may not work
- Use "Save to File" instead

## Upgrade

### Upgrade all dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Upgrade specific package

```bash
pip install --upgrade textual
```

## Uninstall

### Remove dependencies

```bash
pip uninstall requests pyyaml textual
```

### Remove virtual environment

```bash
deactivate  # First deactivate if active
rm -rf venv
```

## Platform-Specific Notes

### Linux

```bash
# Ubuntu/Debian
sudo apt install python3-pip python3-venv xclip

# Fedora/RHEL
sudo yum install python3-pip xclip
```

### macOS

```bash
# Install Python 3 (if not already installed)
brew install python3

# xclip equivalent (pbcopy) is pre-installed
```

### Windows

```bash
# Install Python 3 from python.org
# Then in PowerShell or Command Prompt:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Docker (Alternative)

If you prefer Docker:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "portainer_tui.py"]
```

Build and run:
```bash
docker build -t portainer-to-k8s .
docker run -it portainer-to-k8s
```

## Next Steps

After installation:

1. **First-time users:** Read [CONFIG_GUIDE.md](CONFIG_GUIDE.md)
2. **TUI users:** Check [TUI_GUIDE.md](TUI_GUIDE.md)
3. **CLI users:** See [README.md](README.md)

## Quick Reference

```bash
# Install
pip install -r requirements.txt

# Run TUI
python3 portainer_tui.py

# Run CLI
python3 portainer_to_k8s.py cli --container nginx --api-key KEY

# Get help
python3 portainer_to_k8s.py --help
```

That's it! You're ready to convert Portainer containers to Kubernetes manifests.

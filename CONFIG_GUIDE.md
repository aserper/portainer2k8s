# Configuration Guide

## Overview

The portainer-to-k8s project uses a `config.yaml` file to store your Portainer connection settings, making it faster and easier to use the tool without repeatedly entering the same information.

## Configuration Wizard

### First Run

When you launch the TUI for the first time (or if `config.yaml` doesn't exist), you'll be greeted with the **Configuration Wizard**:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    ⚙️ Configuration Wizard          ┃
┃  No configuration file found.       ┃
┃  Let's set up your Portainer!       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

The wizard will guide you through:
1. **Portainer URL** - Your Portainer server address
2. **Endpoint ID** - The endpoint number to use
3. **Authentication** - Choose API Key or Username/Password
4. **Save & Connect** - Test connection and save configuration

### What Gets Saved

The wizard saves to `config.yaml`:
- ✅ Portainer URL
- ✅ Endpoint ID  
- ✅ API Key (if using API key auth)
- ✅ Username (if using username/password auth)
- ❌ **Password** (NEVER saved for security)

## Configuration File Format

### Example with API Key

```yaml
portainer:
  url: https://portainer.example.com
  endpoint_id: 1
  auth:
    api_key: your-api-key-here
    method: api_key
```

### Example with Username

```yaml
portainer:
  url: https://portainer.example.com
  endpoint_id: 1
  auth:
    username: admin
    method: username_password
```

**Note:** Passwords are intentionally NOT saved. You'll be prompted for your password each time you connect.

## Using the Configuration

### TUI Mode

**First Run (No config.yaml):**
```bash
$ python3 portainer_tui.py
# Configuration Wizard appears
# Fill in your details
# Click "Save & Connect"
# config.yaml is created
```

**Subsequent Runs (config.yaml exists):**
```bash
$ python3 portainer_tui.py
# Welcome Screen appears with loaded settings
# If using username auth, enter password
# Click "Connect"
# You're immediately connected!
```

### CLI Mode

**Without config.yaml:**
```bash
$ python3 portainer_to_k8s.py cli \
    --url https://portainer.local \
    --endpoint 1 \
    --container nginx \
    --api-key abc123
```

**With config.yaml (URL, endpoint, API key saved):**
```bash
$ python3 portainer_to_k8s.py cli --container nginx
# URL, endpoint, and API key are loaded from config!
```

**Override config.yaml values:**
```bash
$ python3 portainer_to_k8s.py cli \
    --container nginx \
    --endpoint 2  # Override the saved endpoint
```

## Configuration Management

### View Current Configuration

```bash
$ cat config.yaml
```

### Edit Configuration

You can manually edit `config.yaml`:
```bash
$ nano config.yaml
# or
$ vim config.yaml
```

### Reconfigure via TUI

1. Launch TUI: `python3 portainer_tui.py`
2. Click **"Reconfigure"** button
3. Configuration Wizard appears
4. Enter new settings
5. Click **"Save & Connect"**
6. config.yaml is updated

### Delete Configuration

**Manual deletion:**
```bash
$ rm config.yaml
```

**Next TUI launch will show Configuration Wizard again.**

## Security Best Practices

### API Key vs Username/Password

**API Key (Recommended):**
- ✅ More secure
- ✅ Can be rotated easily
- ✅ Saved in config.yaml
- ✅ No password prompts

**Username/Password:**
- ⚠️ Password required each time
- ⚠️ Password NOT saved (security)
- ✅ Good for temporary use
- ✅ No API key needed

### Protecting config.yaml

**Set restrictive permissions:**
```bash
$ chmod 600 config.yaml
# Only you can read/write
```

**Avoid committing to version control:**
```bash
# Add to .gitignore
echo "config.yaml" >> .gitignore
```

**Use environment-specific configs:**
```bash
# Development
cp config.yaml config.dev.yaml

# Production
cp config.yaml config.prod.yaml

# Use specific config
export CONFIG_FILE=config.prod.yaml
```

## Common Workflows

### Setup New Environment

```bash
# 1. Run TUI
python3 portainer_tui.py

# 2. Configuration Wizard appears
# 3. Enter Portainer details
# 4. Test connection with "Save & Connect"
# 5. config.yaml created

# 6. Future runs are faster
python3 portainer_tui.py
# Just enter password (if using username auth) and connect!
```

### Switch Between Portainer Instances

**Option 1: Multiple config files**
```bash
# Save current config
mv config.yaml config-prod.yaml

# Run wizard for new instance
python3 portainer_tui.py
# Creates new config.yaml

# Switch back
mv config.yaml config-dev.yaml
mv config-prod.yaml config.yaml
```

**Option 2: Manual editing**
```bash
# Edit config.yaml
nano config.yaml

# Change URL and endpoint_id
# Save and exit

# Next run uses new settings
python3 portainer_tui.py
```

### Automation Scripts

**CLI with config.yaml:**
```bash
#!/bin/bash
# export-containers.sh

# config.yaml has URL, endpoint, API key
for container in nginx mysql redis; do
  python3 portainer_to_k8s.py cli \
    --container $container \
    --namespace production
done
```

**No manual credentials needed!**

## Troubleshooting

### "Configuration error" or "Invalid configuration"

**Cause:** config.yaml is malformed or missing required fields

**Fix:**
```bash
# Delete and recreate
rm config.yaml
python3 portainer_tui.py
# Configuration Wizard will run
```

### "Connection failed" with saved config

**Cause:** Credentials may have changed or expired

**Fix:**
```bash
# TUI: Click "Reconfigure" button
# Or delete config and start fresh:
rm config.yaml
python3 portainer_tui.py
```

### Config not being loaded

**Cause:** config.yaml in wrong directory

**Fix:**
```bash
# Check current directory
pwd

# Config must be in same directory as script
ls -la config.yaml

# Or run from correct directory
cd /path/to/portainer-to-k8s
python3 portainer_tui.py
```

### API key doesn't work after saving

**Cause:** API key may have been revoked

**Fix:**
1. Generate new API key in Portainer
2. Run TUI and click "Reconfigure"
3. Enter new API key
4. Click "Save & Connect"

## Configuration File Location

The configuration file (`config.yaml`) is always created in the **current working directory** where you run the script.

**To use a specific location:**
```bash
# Option 1: Change to that directory
cd /path/to/your/configs
python3 /path/to/portainer-to-k8s/portainer_tui.py

# Option 2: Set CONFIG_FILE environment variable (future feature)
# Currently not implemented
```

## Advanced Usage

### Template Configuration

Create a template for teams:

**config.template.yaml:**
```yaml
portainer:
  url: https://portainer.company.com
  endpoint_id: 1
  auth:
    # Team members add their own credentials
    api_key: YOUR_API_KEY_HERE
    method: api_key
```

**Team members:**
```bash
# Copy template
cp config.template.yaml config.yaml

# Edit with your API key
nano config.yaml

# Run
python3 portainer_tui.py
```

### CI/CD Integration

**GitHub Actions example:**
```yaml
# .github/workflows/export.yml
- name: Create config
  run: |
    cat > config.yaml << EOF
    portainer:
      url: ${{ secrets.PORTAINER_URL }}
      endpoint_id: 1
      auth:
        api_key: ${{ secrets.PORTAINER_API_KEY }}
        method: api_key
    EOF

- name: Export container
  run: |
    python3 portainer_to_k8s.py cli --container nginx
```

**Environment variables (example wrapper):**
```bash
#!/bin/bash
# export-with-env.sh

if [ ! -f config.yaml ]; then
  cat > config.yaml << EOF
portainer:
  url: ${PORTAINER_URL}
  endpoint_id: ${PORTAINER_ENDPOINT_ID}
  auth:
    api_key: ${PORTAINER_API_KEY}
    method: api_key
EOF
fi

python3 portainer_to_k8s.py cli "$@"
```

## FAQ

**Q: Where is config.yaml stored?**  
A: In the current working directory where you run the script.

**Q: Is my password saved?**  
A: No, passwords are NEVER saved. You'll be prompted each time.

**Q: Can I use multiple configurations?**  
A: Yes, save different config files and rename them as needed.

**Q: What if I forget my saved API key?**  
A: Check `config.yaml` - it's stored in plain text (hence why you should protect the file).

**Q: Can I skip the wizard?**  
A: Yes, manually create `config.yaml` following the format above.

**Q: Does the CLI use config.yaml?**  
A: Yes! If config.yaml exists, CLI will use it for defaults.

**Q: How do I update my configuration?**  
A: Use TUI's "Reconfigure" button, or manually edit config.yaml.

**Q: Is config.yaml required?**  
A: No. For CLI, you can always provide all arguments. For TUI, wizard runs if missing.

## Summary

- 🎯 **First run**: Configuration Wizard guides you
- 💾 **Saves**: URL, Endpoint ID, API Key or Username
- 🔒 **Security**: Passwords never saved
- ⚡ **Speed**: No re-entering credentials
- 🔄 **Flexible**: Can reconfigure anytime
- 🛠️ **CLI friendly**: Load defaults from config

The configuration wizard makes portainer-to-k8s easier to use while maintaining security best practices!

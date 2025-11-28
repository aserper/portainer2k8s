#!/usr/bin/env python3
"""Terminal User Interface for converting Portainer containers to Kubernetes manifests."""

from __future__ import annotations

import subprocess
from typing import Any, Dict, Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    OptionList,
    Static,
    TextArea,
)
from textual.widgets.option_list import Option

from config import config_exists, load_config, save_config
from portainer_to_k8s import (
    PortainerClient,
    build_k8s_documents,
    dump_yaml,
    sanitize_name,
)



class EndpointSelectScreen(Screen):
    """Screen to select an endpoint (environment)."""

    CSS = """
    EndpointSelectScreen {
        align: center middle;
    }

    #endpoint-select-box {
        width: 80;
        height: auto;
        border: solid $primary;
        background: $surface;
    }

    #endpoint-list {
        height: 15;
        margin: 2;
    }

    #title {
        text-style: bold;
        text-align: center;
        margin: 1 2;
        width: 100%;
    }

    Button {
        margin: 0 2;
    }
    #button-container {
        height: auto;
        align: center middle;
        margin-top: 2;
    }
    """

    def __init__(self, endpoints: List[Dict[str, Any]]) -> None:
        super().__init__()
        self.endpoints = endpoints

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="endpoint-select-box"):
            yield Label("Select Portainer Endpoint", id="title")
            with ScrollableContainer(id="endpoint-list"):
                yield OptionList(id="endpoints")

            with Horizontal(id="button-container"):
                yield Button("Select", id="btn-select", variant="primary")
                yield Button("Back", id="btn-back")
                yield Button("Quit", id="btn-quit", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        option_list = self.query_one("#endpoints", OptionList)
        for endpoint in self.endpoints:
            name = endpoint.get("Name", "Unnamed")
            e_id = str(endpoint.get("Id", "?"))
            option_list.add_option(Option(f"{name} (ID: {e_id})", id=e_id))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-quit":
            self.app.exit()
        elif event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-select":
            self._select_endpoint()

    def _select_endpoint(self) -> None:
        option_list = self.query_one("#endpoints", OptionList)
        if option_list.highlighted is None:
            self.app.notify("Please select an endpoint", severity="warning")
            return

        selected = option_list.get_option_at_index(option_list.highlighted)
        if selected and selected.id:
            endpoint_id = int(selected.id)
            self.app.client.endpoint_id = endpoint_id

            # Save config now
            config_data = self.app.pending_config
            try:
                save_config(
                    url=config_data["url"],
                    endpoint_id=endpoint_id,
                    api_key=config_data["api_key"],
                    username=config_data["username"],
                )
                self.app.notify("Configuration saved!", severity="information")
                self.app.push_screen(ContainerSelectScreen())
            except Exception as e:
                self.app.notify(f"Could not save config: {e}", severity="warning")


class ConfigWizardScreen(Screen):
    """Configuration wizard that runs when config.yaml doesn't exist."""

    CSS = """
    ConfigWizardScreen {
        align: center middle;
    }

    #wizard-container {
        width: 80;
        height: auto;
        border: solid $accent;
        background: $surface;
    }

    .form-group {
        margin: 1 0;
        height: auto;
    }

    .form-label {
        text-style: bold;
        margin-bottom: 1;
    }

    Input {
        margin: 0 2;
    }

    #button-container {
        height: auto;
        margin-top: 2;
        align: center middle;
    }

    Button {
        margin: 0 2;
    }

    #wizard-title {
        text-style: bold;
        text-align: center;
        margin: 1 0;
        width: 100%;
        color: $accent;
    }

    #wizard-subtitle {
        text-align: center;
        margin: 0 0 2 0;
        width: 100%;
        color: $text-muted;
    }

    #wizard-notice {
        text-align: center;
        margin: 1 2;
        padding: 1;
        background: $boost;
        color: $warning;
    }

    #username-group {
        display: none;
    }

    #password-group {
        display: none;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the configuration wizard screen."""
        yield Header(show_clock=False)
        with Container(id="wizard-container"):
            yield Label("⚙️ Configuration Wizard", id="wizard-title")
            yield Static(
                "No configuration file found. Let's set up your Portainer connection!",
                id="wizard-subtitle",
            )
            yield Static(
                "This wizard will create config.yaml with your connection settings.",
                id="wizard-notice",
            )

            # Portainer URL
            with Vertical(classes="form-group"):
                yield Label("Portainer URL", classes="form-label")
                yield Input(
                    placeholder="https://portainer.example.com",
                    id="portainer-url",
                )

            # Authentication method
            with Vertical(classes="form-group"):
                yield Label("Authentication Method", classes="form-label")
                yield OptionList(
                    "API Key (Recommended)",
                    "Username/Password",
                    id="auth-method",
                )

            # API Key field
            with Vertical(classes="form-group"):
                yield Label("API Key", classes="form-label")
                yield Input(
                    placeholder="Your Portainer API key",
                    id="api-key",
                )

            # Username field
            with Vertical(classes="form-group", id="username-group"):
                yield Label("Username", classes="form-label")
                yield Input(
                    placeholder="Your Portainer username",
                    id="username",
                )

            # Password field
            with Vertical(classes="form-group", id="password-group"):
                yield Label("Password (NOT saved)", classes="form-label")
                yield Input(
                    placeholder="Your Portainer password",
                    password=True,
                    id="password",
                )

            # Buttons
            with Horizontal(id="button-container"):
                yield Button("Save & Connect", id="btn-connect", variant="primary")
                yield Button("Quit", id="btn-quit", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the wizard."""
        # Default to API Key method
        self._update_auth_fields()

    def _update_auth_fields(self) -> None:
        """Show/hide auth fields based on selection."""
        auth_method_list = self.query_one("#auth-method", OptionList)
        selected_index = auth_method_list.highlighted

        username_group = self.query_one("#username-group")
        password_group = self.query_one("#password-group")

        if selected_index == 0:  # API Key
            username_group.display = False
            password_group.display = False
        else:  # Username/Password
            username_group.display = True
            password_group.display = True

    @on(OptionList.OptionHighlighted)
    def on_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Handle authentication method change."""
        if event.option_list.id == "auth-method":
            self._update_auth_fields()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-quit":
            self.app.exit()
        elif event.button.id == "btn-connect":
            self._save_and_connect()

    def _save_and_connect(self) -> None:
        """Save configuration and attempt connection."""
        url = self.query_one("#portainer-url", Input).value.strip()
        auth_method_list = self.query_one("#auth-method", OptionList)
        auth_method = auth_method_list.highlighted

        # Validation
        if not url:
            self.app.notify("Please enter a Portainer URL", severity="error")
            return

        if auth_method == 0:  # API Key
            api_key = self.query_one("#api-key", Input).value.strip()
            if not api_key:
                self.app.notify("Please enter an API key", severity="error")
                return
            username = None
            password = None
        else:  # Username/Password
            username = self.query_one("#username", Input).value.strip()
            password = self.query_one("#password", Input).value.strip()
            if not username or not password:
                self.app.notify("Please enter username and password", severity="error")
                return
            api_key = None

        # Attempt connection
        try:
            client = PortainerClient(
                base_url=url,
                endpoint_id=None,
                api_key=api_key,
                username=username,
                password=password,
            )

            # Fetch endpoints
            endpoints = client.get_endpoints()
            if not endpoints:
                self.app.notify("No endpoints found on this Portainer instance", severity="warning")
                return
            
            # Store client and pending config
            self.app.client = client
            self.app.pending_config = {
                "url": url,
                "api_key": api_key,
                "username": username,
            }
            
            # Move to endpoint selection
            self.app.push_screen(EndpointSelectScreen(endpoints))
            
        except Exception as e:
            self.app.notify(f"Connection failed: {str(e)}", severity="error")


class WelcomeScreen(Screen):
    """Welcome screen for users with existing config."""

    CSS = """
    WelcomeScreen {
        align: center middle;
    }

    #welcome-container {
        width: 80;
        height: auto;
        border: solid $primary;
        background: $surface;
    }

    .form-group {
        margin: 1 0;
        height: auto;
    }

    .form-label {
        text-style: bold;
        margin-bottom: 1;
    }

    Input {
        margin: 0 2;
    }

    #button-container {
        height: auto;
        margin-top: 2;
        align: center middle;
    }

    Button {
        margin: 0 2;
    }

    #title {
        text-style: bold;
        text-align: center;
        margin: 1 0;
        width: 100%;
    }

    #subtitle {
        text-align: center;
        margin: 0 0 2 0;
        width: 100%;
        color: $text-muted;
    }
    
    #config-info {
        text-align: center;
        margin: 1 2;
        padding: 1;
        background: $boost;
        color: $success;
    }

    #password-field-group {
        display: none;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the welcome screen."""
        yield Header(show_clock=False)
        with Container(id="welcome-container"):
            yield Label("🚀 Portainer to Kubernetes Converter", id="title")
            yield Static(
                "Convert Docker containers from Portainer to Kubernetes manifests",
                id="subtitle",
            )
            yield Static(
                "✓ Loaded configuration from config.yaml",
                id="config-info",
            )

            # Password field (only shown if using username auth)
            with Vertical(classes="form-group", id="password-field-group"):
                yield Label("Password (required for username auth)", classes="form-label")
                yield Input(
                    placeholder="Your Portainer password",
                    password=True,
                    id="password",
                )

            # Save updated config checkbox
            with Horizontal(classes="form-group"):
                yield Checkbox(
                    "Update config.yaml with any changes",
                    id="save-config",
                    value=False,
                )

            # Buttons
            with Horizontal(id="button-container"):
                yield Button("Connect", id="btn-connect", variant="primary")
                yield Button("Reconfigure", id="btn-reconfig")
                yield Button("Quit", id="btn-quit", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Load configuration and pre-fill form."""
        config = load_config()
        if config and "portainer" in config:
            portainer_config = config["portainer"]
            auth_config = portainer_config.get("auth", {})
            
            # Store config for connection
            self.app.config = config
            
            # Show/hide password field based on auth method
            password_group = self.query_one("#password-field-group")
            if auth_config.get("method") == "username_password":
                password_group.display = True
            else:
                password_group.display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-quit":
            self.app.exit()
        elif event.button.id == "btn-reconfig":
            self._reconfigure()
        elif event.button.id == "btn-connect":
            self._attempt_connection()

    def _reconfigure(self) -> None:
        """Go back to configuration wizard."""
        self.app.pop_screen()
        self.app.push_screen(ConfigWizardScreen())

    def _attempt_connection(self) -> None:
        """Attempt to connect using saved configuration."""
        config = self.app.config
        if not config or "portainer" not in config:
            self.app.notify("Configuration error", severity="error")
            return

        portainer_config = config["portainer"]
        auth_config = portainer_config.get("auth", {})

        url = portainer_config.get("url")
        endpoint_id = portainer_config.get("endpoint_id")

        if not url or not endpoint_id:
            self.app.notify("Invalid configuration", severity="error")
            return

        # Prepare authentication
        api_key = auth_config.get("api_key")
        username = auth_config.get("username")
        password = None

        if username:
            password = self.query_one("#password", Input).value.strip()
            if not password:
                self.app.notify("Please enter your password", severity="error")
                return

        # Attempt connection
        try:
            client = PortainerClient(
                base_url=url,
                endpoint_id=endpoint_id,
                api_key=api_key,
                username=username,
                password=password,
            )
            
            # Connection successful
            self.app.client = client
            self.app.push_screen(ContainerSelectScreen())
            
        except Exception as e:
            self.app.notify(f"Connection failed: {str(e)}", severity="error")


class ContainerSelectScreen(Screen):
    """Screen to select a container from Portainer."""

    CSS = """
    ContainerSelectScreen {
        align: center middle;
    }

    #container-select-box {
        width: 100;
        height: auto;
        border: solid $primary;
        background: $surface;
    }

    #container-list {
        height: 20;
        margin: 2;
    }

    #status-message {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $boost;
    }

    #button-container {
        height: auto;
        align: center middle;
        margin-top: 2;
    }

    #title {
        text-style: bold;
        text-align: center;
        margin: 1 2;
        width: 100%;
    }

    #subtitle {
        text-align: center;
        margin: 0 2 2 2;
        width: 100%;
        color: $text-muted;
    }

    Button {
        margin: 0 2;
    }
    """

    containers_loaded = var(False)

    def compose(self) -> ComposeResult:
        """Compose the container select screen."""
        yield Header(show_clock=False)
        with Container(id="container-select-box"):
            yield Static("Loading containers...", id="status-message")
            yield Label("Select a Container to Export", id="title")
            yield Label(
                "Choose which container you want to convert to a Kubernetes manifest",
                id="subtitle",
            )

            with ScrollableContainer(id="container-list"):
                yield OptionList(id="containers")

            with Horizontal(id="button-container"):
                yield Button("Export", id="btn-export", variant="primary")
                yield Button("Back", id="btn-back")
                yield Button("Quit", id="btn-quit", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Load containers when screen is mounted."""
        self.load_containers()

    def load_containers(self) -> None:
        """Load containers from Portainer."""
        try:
            client: PortainerClient = self.app.client
            response = client.session.get(
                f"{client.base_url}/api/endpoints/{client.endpoint_id}/docker/containers/json",
                params={"all": True},
                timeout=15,
            )
            response.raise_for_status()

            containers = response.json()
            if not containers:
                self.app.notify("No containers found", severity="warning")
                return

            option_list = self.query_one("#containers", OptionList)
            for container in containers:
                container_id = container["Id"][:12]  # Short ID
                names = container.get("Names", [])
                name = names[0].lstrip("/") if names else "unnamed"
                status = container.get("State", "unknown")
                display = f"{name} ({container_id}) - {status}"
                option_list.add_option(Option(display, id=container["Id"]))

            self.query_one("#status-message", Static).update("✓ Containers loaded")
            self.containers_loaded = True

        except Exception as e:
            self.app.notify(f"Failed to load containers: {str(e)}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-quit":
            self.app.exit()
        elif event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-export":
            self._export_container()

    def _export_container(self) -> None:
        """Export the selected container."""
        option_list = self.query_one("#containers", OptionList)
        if option_list.highlighted is None:
            self.app.notify("Please select a container", severity="warning")
            return

        # Get the selected option
        selected_option = option_list.get_option_at_index(option_list.highlighted)
        if selected_option and selected_option.id:
            container_id = selected_option.id
            self.app.selected_container_id = container_id
            self.app.push_screen(ConfigureScreen())


class ConfigureScreen(Screen):
    """Screen to configure export settings."""

    CSS = """
    ConfigureScreen {
        align: center middle;
    }

    #configure-box {
        width: 80;
        height: auto;
        border: solid $primary;
        background: $surface;
    }

    .form-group {
        margin: 1 0;
        height: auto;
    }

    .form-label {
        text-style: bold;
        margin-bottom: 1;
    }

    Input {
        margin: 0 2;
    }

    #button-container {
        height: auto;
        margin-top: 2;
        align: center middle;
    }

    #title {
        text-style: bold;
        text-align: center;
        margin: 1 2;
        width: 100%;
    }

    Button {
        margin: 0 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the configure screen."""
        yield Header(show_clock=False)
        with Container(id="configure-box"):
            yield Label("Configure Export Settings", id="title")

            # Kubernetes Namespace
            with Vertical(classes="form-group"):
                yield Label("Kubernetes Namespace", classes="form-label")
                yield Input(
                    value="default",
                    id="namespace",
                )

            with Horizontal(id="button-container"):
                yield Button("Generate & Preview", id="btn-preview", variant="primary")
                yield Button("Back", id="btn-back")
                yield Button("Quit", id="btn-quit", variant="error")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-quit":
            self.app.exit()
        elif event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-preview":
            self._generate_manifest()

    def _generate_manifest(self) -> None:
        """Generate the Kubernetes manifest."""
        try:
            namespace = self.query_one("#namespace", Input).value.strip()
            if not namespace:
                namespace = "default"

            client: PortainerClient = self.app.client
            container_id = self.app.selected_container_id

            # Fetch container details
            container_details = client.get_container_details(container_id)

            # Generate K8s documents
            documents = build_k8s_documents(container_details, namespace)
            manifest = dump_yaml(documents)

            # Move to preview screen
            self.app.manifest = manifest
            self.app.container_details = container_details
            self.app.push_screen(PreviewScreen())

        except Exception as e:
            self.app.notify(f"Failed to generate manifest: {str(e)}", severity="error")


class PreviewScreen(Screen):
    """Screen to preview and save the generated manifest."""

    CSS = """
    PreviewScreen {
        layout: vertical;
    }

    #preview-header {
        dock: top;
        height: 3;
        background: $boost;
    }

    #manifest-text {
        height: 1fr;
        border: solid $primary;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
    }

    #preview-title {
        text-style: bold;
        text-align: center;
        width: 100%;
    }

    Button {
        margin: 0 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the preview screen."""
        yield Header(show_clock=False)
        with Vertical(id="preview-header"):
            yield Label("Generated Kubernetes Manifest", id="preview-title")

        yield TextArea.code_editor(
            self.app.manifest,
            id="manifest-text",
            read_only=True,
            language="yaml",
        )

        with Horizontal(id="button-container"):
            yield Button("Save to File", id="btn-save", variant="primary")
            yield Button("Copy to Clipboard", id="btn-copy")
            yield Button("Back", id="btn-back")
            yield Button("Quit", id="btn-quit", variant="error")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-quit":
            self.app.exit()
        elif event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-save":
            self._save_manifest()
        elif event.button.id == "btn-copy":
            self._copy_to_clipboard()

    def _save_manifest(self) -> None:
        """Save the manifest to a file."""
        try:
            # Generate filename from container name
            container_details = self.app.container_details
            config = container_details.get("Config", {})
            container_name = sanitize_name(
                config.get("Hostname") or container_details.get("Name", "app")
            )
            filename = f"{container_name}-manifest.yaml"

            with open(filename, "w") as f:
                f.write(self.app.manifest)

            self.app.notify(f"Manifest saved to {filename}", severity="information")
        except Exception as e:
            self.app.notify(f"Failed to save manifest: {str(e)}", severity="error")

    def _copy_to_clipboard(self) -> None:
        """Copy manifest to clipboard."""
        try:
            process = subprocess.Popen(
                ["xclip", "-selection", "clipboard"],
                stdin=subprocess.PIPE,
            )
            process.communicate(self.app.manifest.encode())
            if process.returncode == 0:
                self.app.notify("Manifest copied to clipboard", severity="information")
            else:
                self.app.notify("xclip not found - clipboard copy failed", severity="warning")
        except Exception as e:
            self.app.notify(f"Failed to copy to clipboard: {str(e)}", severity="warning")


class PortainerToK8sApp(App):
    """Main TUI application."""

    TITLE = "Portainer to Kubernetes Converter"
    SUB_TITLE = "Convert Docker containers to Kubernetes manifests"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }

    Header {
        dock: top;
        height: 3;
        background: $boost;
    }

    Footer {
        dock: bottom;
    }

    Button {
        min-width: 20;
    }
    """

    def on_mount(self) -> None:
        """Start with appropriate screen based on config file existence."""
        if not hasattr(self, "client"):
            self.client: Optional[PortainerClient] = None
        if not hasattr(self, "selected_container_id"):
            self.selected_container_id: Optional[str] = None
        if not hasattr(self, "manifest"):
            self.manifest: str = ""
        if not hasattr(self, "container_details"):
            self.container_details: Dict[str, Any] = {}
        if not hasattr(self, "config"):
            self.config: Optional[Dict[str, Any]] = None
        
        # Check if configuration exists
        if config_exists():
            # Load existing config and show welcome screen
            self.push_screen(WelcomeScreen())
        else:
            # No config - run configuration wizard
            self.push_screen(ConfigWizardScreen())


def run_tui() -> None:
    """Run the TUI application."""
    app = PortainerToK8sApp()
    app.run()


if __name__ == "__main__":
    run_tui()

#!/usr/bin/env python3
"""
Sparrow SPOT Scale™ - Text User Interface (TUI)
Interactive terminal interface for document analysis
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Button, Input, Select, Switch, Static, Header, Footer,
    TabbedContent, TabPane, Label, TextArea, DirectoryTree
)
from textual.binding import Binding
from pathlib import Path
import subprocess
import json
import sys


class SparrowTUI(App):
    """Sparrow SPOT Scale TUI Application"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #title {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    TabbedContent {
        height: 100%;
    }
    
    .input-group {
        height: auto;
        padding: 1;
        border: solid $primary;
        margin: 1;
    }
    
    .input-label {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    
    Input {
        margin-bottom: 1;
    }
    
    Select {
        margin-bottom: 1;
    }
    
    Switch {
        margin: 1;
    }
    
    #command_preview {
        dock: bottom;
        height: 8;
        background: $panel;
        border: solid $accent;
        padding: 1;
        margin: 1;
    }
    
    #button_bar {
        dock: bottom;
        height: 3;
        background: $surface;
        padding: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    .success {
        background: $success;
    }
    
    .warning {
        background: $warning;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+r", "run", "Run Analysis", show=True),
        Binding("ctrl+s", "save_config", "Save Config", show=True),
        Binding("ctrl+l", "load_config", "Load Config", show=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.config = self.load_default_config()
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        
        yield Static("🦅 Sparrow SPOT Scale™ - TUI", id="title")
        
        with TabbedContent():
            # Document Tab
            with TabPane("📄 Document", id="tab_document"):
                with ScrollableContainer():
                    with Container(classes="input-group"):
                        yield Label("Document Path", classes="input-label")
                        yield Input(
                            placeholder="/path/to/document.txt or .pdf",
                            id="doc_path",
                            value=self.config.get("doc_path", "")
                        )
                        yield Button("Browse...", id="browse_doc", variant="default")
                    
                    with Container(classes="input-group"):
                        yield Label("Output Directory", classes="input-label")
                        yield Input(
                            placeholder="/path/to/output",
                            id="output_dir",
                            value=self.config.get("output_dir", "")
                        )
                        yield Button("Browse...", id="browse_output", variant="default")
                    
                    with Container(classes="input-group"):
                        yield Label("Document Title", classes="input-label")
                        yield Input(
                            placeholder="My Document",
                            id="doc_title",
                            value=self.config.get("doc_title", "")
                        )
            
            # Analysis Tab
            with TabPane("🧠 Analysis", id="tab_analysis"):
                with ScrollableContainer():
                    with Container(classes="input-group"):
                        yield Label("Chunking Settings", classes="input-label")
                        yield Switch(
                            value=self.config.get("enable_chunking", True),
                            id="enable_chunking"
                        )
                        yield Label("Enable Chunking")
                        
                        yield Label("Chunk Strategy", classes="input-label")
                        yield Select(
                            [
                                ("section", "Section (Preserves boundaries)"),
                                ("sliding", "Sliding Window"),
                                ("semantic", "Semantic")
                            ],
                            value=self.config.get("chunk_strategy", "section"),
                            id="chunk_strategy"
                        )
                        
                        yield Label("Max Chunk Tokens", classes="input-label")
                        yield Input(
                            placeholder="4000",
                            id="max_chunk_tokens",
                            value=str(self.config.get("max_chunk_tokens", "4000"))
                        )
                    
                    with Container(classes="input-group"):
                        yield Label("Analysis Options", classes="input-label")
                        yield Switch(
                            value=self.config.get("deep_analysis", False),
                            id="deep_analysis"
                        )
                        yield Label("Enable Deep Analysis")
                        
                        yield Switch(
                            value=self.config.get("skip_narrative", False),
                            id="skip_narrative"
                        )
                        yield Label("Skip Narrative Generation")
            
            # Q&A Tab
            with TabPane("❓ Q&A", id="tab_qa"):
                with ScrollableContainer():
                    with Container(classes="input-group"):
                        yield Label("Document Q&A", classes="input-label")
                        yield Input(
                            placeholder="Your question about the document...",
                            id="qa_question",
                            value=self.config.get("qa_question", "")
                        )
                        
                        yield Label("Q&A Routing Strategy", classes="input-label")
                        yield Select(
                            [
                                ("comprehensive", "Comprehensive (All chunks)"),
                                ("keyword", "Keyword Matching"),
                                ("semantic", "Semantic Similarity"),
                                ("quick", "Quick (First match)")
                            ],
                            value=self.config.get("qa_routing", "comprehensive"),
                            id="qa_routing"
                        )
                        
                        yield Switch(
                            value=self.config.get("multiple_questions", False),
                            id="multiple_questions"
                        )
                        yield Label("Enable Multiple Questions")
            
            # Ollama Tab
            with TabPane("🤖 Ollama", id="tab_ollama"):
                with ScrollableContainer():
                    with Container(classes="input-group"):
                        yield Label("Ollama Configuration", classes="input-label")
                        yield Label("Model Name", classes="input-label")
                        yield Input(
                            placeholder="llama3.2:3b",
                            id="ollama_model",
                            value=self.config.get("ollama_model", "llama3.2:3b")
                        )
                        
                        yield Label("Ollama URL", classes="input-label")
                        yield Input(
                            placeholder="http://localhost:11434",
                            id="ollama_url",
                            value=self.config.get("ollama_url", "http://localhost:11434")
                        )
                        
                        yield Label("Temperature (0.0-1.0)", classes="input-label")
                        yield Input(
                            placeholder="0.7",
                            id="ollama_temperature",
                            value=str(self.config.get("ollama_temperature", "0.7"))
                        )
                        
                        yield Switch(
                            value=self.config.get("ollama_streaming", True),
                            id="ollama_streaming"
                        )
                        yield Label("Enable Streaming")
            
            # Advanced Tab
            with TabPane("⚙️ Advanced", id="tab_advanced"):
                with ScrollableContainer():
                    with Container(classes="input-group"):
                        yield Label("Output Formats", classes="input-label")
                        yield Switch(
                            value=self.config.get("html_certificate", True),
                            id="html_certificate"
                        )
                        yield Label("Generate HTML Certificate")
                        
                        yield Switch(
                            value=self.config.get("json_output", True),
                            id="json_output"
                        )
                        yield Label("Generate JSON Output")
                        
                        yield Switch(
                            value=self.config.get("markdown_output", True),
                            id="markdown_output"
                        )
                        yield Label("Generate Markdown Output")
                    
                    with Container(classes="input-group"):
                        yield Label("Performance", classes="input-label")
                        yield Label("Max Workers", classes="input-label")
                        yield Input(
                            placeholder="4",
                            id="max_workers",
                            value=str(self.config.get("max_workers", "4"))
                        )
                        
                        yield Switch(
                            value=self.config.get("verbose", False),
                            id="verbose"
                        )
                        yield Label("Verbose Output")
            
            # Profiles Tab
            with TabPane("💾 Profiles", id="tab_profiles"):
                with ScrollableContainer():
                    with Container(classes="input-group"):
                        yield Label("Configuration Profiles", classes="input-label")
                        yield Label("Profile Name", classes="input-label")
                        yield Input(
                            placeholder="my-analysis-profile",
                            id="profile_name",
                            value=""
                        )
                        yield Button("Save Profile", id="save_profile", variant="success")
                        yield Button("Load Profile", id="load_profile", variant="primary")
                        yield Button("Delete Profile", id="delete_profile", variant="error")
                        
                        yield Label("Available Profiles:", classes="input-label")
                        yield Static("", id="profile_list")
        
        # Command Preview
        yield Static("Command Preview:\n\n(Configure options above)", id="command_preview")
        
        # Button Bar
        with Horizontal(id="button_bar"):
            yield Button("▶ Run Analysis", id="run_button", variant="success")
            yield Button("💾 Save Config", id="save_config_button", variant="primary")
            yield Button("📂 Load Config", id="load_config_button", variant="default")
            yield Button("🔄 Reset", id="reset_button", variant="warning")
            yield Button("❌ Quit", id="quit_button", variant="error")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.update_command_preview()
        self.update_profile_list()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Update command preview when any input changes."""
        self.update_command_preview()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Update command preview when any select changes."""
        self.update_command_preview()
    
    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Update command preview when any switch changes."""
        self.update_command_preview()
    
    def update_command_preview(self) -> None:
        """Update the command preview display."""
        try:
            command = self.build_command()
            preview = self.query_one("#command_preview", Static)
            preview.update(f"Command Preview:\n\n{command}")
        except Exception as e:
            pass
    
    def build_command(self) -> str:
        """Build the sparrow_grader_v8.py command from current settings."""
        parts = ["python sparrow_grader_v8.py"]
        
        # Document path (required)
        doc_path = self.query_one("#doc_path", Input).value
        if doc_path:
            parts.append(f'"{doc_path}"')
        else:
            parts.append('"<document_path>"')
        
        # Output directory
        output_dir = self.query_one("#output_dir", Input).value
        if output_dir:
            parts.append(f'-o "{output_dir}"')
        
        # Document title
        doc_title = self.query_one("#doc_title", Input).value
        if doc_title:
            parts.append(f'--document-title "{doc_title}"')
        
        # Chunking
        if self.query_one("#enable_chunking", Switch).value:
            parts.append("--enable-chunking")
            
            chunk_strategy = self.query_one("#chunk_strategy", Select).value
            if chunk_strategy and chunk_strategy != "section":
                parts.append(f"--chunk-strategy {chunk_strategy}")
            
            max_tokens = self.query_one("#max_chunk_tokens", Input).value
            if max_tokens and max_tokens != "4000":
                parts.append(f"--max-chunk-tokens {max_tokens}")
        
        # Q&A
        qa_question = self.query_one("#qa_question", Input).value
        if qa_question:
            parts.append(f'--document-qa "{qa_question}"')
            
            qa_routing = self.query_one("#qa_routing", Select).value
            if qa_routing != "comprehensive":
                parts.append(f"--qa-routing {qa_routing}")
        
        # Ollama
        ollama_model = self.query_one("#ollama_model", Input).value
        if ollama_model and ollama_model != "llama3.2:3b":
            parts.append(f"--ollama-model {ollama_model}")
        
        ollama_url = self.query_one("#ollama_url", Input).value
        if ollama_url and ollama_url != "http://localhost:11434":
            parts.append(f"--ollama-url {ollama_url}")
        
        # Advanced options
        if self.query_one("#deep_analysis", Switch).value:
            parts.append("--enable-deep-analysis")
        
        if self.query_one("#skip_narrative", Switch).value:
            parts.append("--skip-narrative")
        
        if self.query_one("#verbose", Switch).value:
            parts.append("--verbose")
        
        return " \\\n    ".join(parts)
    
    def get_current_config(self) -> dict:
        """Get current configuration from UI."""
        return {
            "doc_path": self.query_one("#doc_path", Input).value,
            "output_dir": self.query_one("#output_dir", Input).value,
            "doc_title": self.query_one("#doc_title", Input).value,
            "enable_chunking": self.query_one("#enable_chunking", Switch).value,
            "chunk_strategy": self.query_one("#chunk_strategy", Select).value,
            "max_chunk_tokens": self.query_one("#max_chunk_tokens", Input).value,
            "qa_question": self.query_one("#qa_question", Input).value,
            "qa_routing": self.query_one("#qa_routing", Select).value,
            "multiple_questions": self.query_one("#multiple_questions", Switch).value,
            "ollama_model": self.query_one("#ollama_model", Input).value,
            "ollama_url": self.query_one("#ollama_url", Input).value,
            "ollama_temperature": self.query_one("#ollama_temperature", Input).value,
            "ollama_streaming": self.query_one("#ollama_streaming", Switch).value,
            "deep_analysis": self.query_one("#deep_analysis", Switch).value,
            "skip_narrative": self.query_one("#skip_narrative", Switch).value,
            "html_certificate": self.query_one("#html_certificate", Switch).value,
            "json_output": self.query_one("#json_output", Switch).value,
            "markdown_output": self.query_one("#markdown_output", Switch).value,
            "max_workers": self.query_one("#max_workers", Input).value,
            "verbose": self.query_one("#verbose", Switch).value,
        }
    
    def load_default_config(self) -> dict:
        """Load default configuration."""
        return {
            "doc_path": "",
            "output_dir": "",
            "doc_title": "",
            "enable_chunking": True,
            "chunk_strategy": "section",
            "max_chunk_tokens": "4000",
            "qa_question": "",
            "qa_routing": "comprehensive",
            "multiple_questions": False,
            "ollama_model": "llama3.2:3b",
            "ollama_url": "http://localhost:11434",
            "ollama_temperature": "0.7",
            "ollama_streaming": True,
            "deep_analysis": False,
            "skip_narrative": False,
            "html_certificate": True,
            "json_output": True,
            "markdown_output": True,
            "max_workers": "4",
            "verbose": False,
        }
    
    def update_profile_list(self) -> None:
        """Update the list of available profiles."""
        profile_dir = Path.home() / ".sparrow" / "profiles"
        profile_list = self.query_one("#profile_list", Static)
        
        if not profile_dir.exists():
            profile_list.update("No profiles saved yet.")
            return
        
        profiles = list(profile_dir.glob("*.json"))
        if not profiles:
            profile_list.update("No profiles saved yet.")
            return
        
        profile_names = "\n".join([f"  • {p.stem}" for p in profiles])
        profile_list.update(profile_names)
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "run_button":
            await self.action_run()
        elif button_id == "save_config_button":
            await self.action_save_config()
        elif button_id == "load_config_button":
            await self.action_load_config()
        elif button_id == "reset_button":
            self.config = self.load_default_config()
            self.refresh()
        elif button_id == "quit_button":
            self.exit()
        elif button_id == "save_profile":
            await self.save_profile()
        elif button_id == "load_profile":
            await self.load_profile()
    
    async def action_run(self) -> None:
        """Run the Sparrow analysis."""
        command = self.build_command()
        
        # Validate required fields
        doc_path = self.query_one("#doc_path", Input).value
        if not doc_path or doc_path == "<document_path>":
            self.notify("❌ Please specify a document path", severity="error")
            return
        
        if not Path(doc_path).exists():
            self.notify(f"❌ Document not found: {doc_path}", severity="error")
            return
        
        # Run analysis
        self.notify("▶ Starting analysis...", severity="information")
        
        try:
            # Build actual command list
            cmd_parts = command.replace(" \\\n    ", " ").split()
            
            # Run subprocess
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            if result.returncode == 0:
                self.notify("✅ Analysis completed successfully!", severity="success")
            else:
                self.notify(f"❌ Analysis failed: {result.stderr[:100]}", severity="error")
        
        except Exception as e:
            self.notify(f"❌ Error: {str(e)[:100]}", severity="error")
    
    async def action_save_config(self) -> None:
        """Save current configuration."""
        config_dir = Path.home() / ".sparrow"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "tui_config.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.get_current_config(), f, indent=2)
            
            self.notify(f"💾 Configuration saved to {config_file}", severity="success")
        except Exception as e:
            self.notify(f"❌ Failed to save config: {e}", severity="error")
    
    async def action_load_config(self) -> None:
        """Load saved configuration."""
        config_file = Path.home() / ".sparrow" / "tui_config.json"
        
        if not config_file.exists():
            self.notify("❌ No saved configuration found", severity="warning")
            return
        
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            
            self.refresh()
            self.notify("📂 Configuration loaded", severity="success")
        except Exception as e:
            self.notify(f"❌ Failed to load config: {e}", severity="error")
    
    async def save_profile(self) -> None:
        """Save current configuration as a named profile."""
        profile_name = self.query_one("#profile_name", Input).value
        
        if not profile_name:
            self.notify("❌ Please enter a profile name", severity="error")
            return
        
        profile_dir = Path.home() / ".sparrow" / "profiles"
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        profile_file = profile_dir / f"{profile_name}.json"
        
        try:
            with open(profile_file, 'w') as f:
                json.dump(self.get_current_config(), f, indent=2)
            
            self.notify(f"💾 Profile '{profile_name}' saved", severity="success")
            self.update_profile_list()
        except Exception as e:
            self.notify(f"❌ Failed to save profile: {e}", severity="error")
    
    async def load_profile(self) -> None:
        """Load a named configuration profile."""
        profile_name = self.query_one("#profile_name", Input).value
        
        if not profile_name:
            self.notify("❌ Please enter a profile name", severity="error")
            return
        
        profile_file = Path.home() / ".sparrow" / "profiles" / f"{profile_name}.json"
        
        if not profile_file.exists():
            self.notify(f"❌ Profile '{profile_name}' not found", severity="error")
            return
        
        try:
            with open(profile_file, 'r') as f:
                self.config = json.load(f)
            
            self.refresh()
            self.notify(f"📂 Profile '{profile_name}' loaded", severity="success")
        except Exception as e:
            self.notify(f"❌ Failed to load profile: {e}", severity="error")


def main():
    """Run the Sparrow TUI application."""
    app = SparrowTUI()
    app.run()


if __name__ == "__main__":
    main()

# Sparrow SPOT Scale™ - TUI

Text User Interface for Sparrow SPOT Scale document analysis.

## Installation

```bash
pip install textual
```

## Usage

Run the TUI:

```bash
python -m tui.sparrow_tui
```

Or from the tui directory:

```bash
cd tui
python sparrow_tui.py
```

## Features

### 📄 Document Tab
- Document path selection
- Output directory configuration
- Document title

### 🧠 Analysis Tab
- Chunking settings (enable/disable, strategy, max tokens)
- Deep analysis toggle
- Skip narrative option

### ❓ Q&A Tab
- Document question input
- Routing strategy selection (comprehensive, keyword, semantic, quick)
- Multiple questions support

### 🤖 Ollama Tab
- Model selection (default: llama3.2:3b)
- Ollama URL configuration
- Temperature settings
- Streaming toggle

### ⚙️ Advanced Tab
- Output format selection (HTML, JSON, Markdown)
- Performance settings (max workers)
- Verbose output toggle

### 💾 Profiles Tab
- Save current configuration as named profile
- Load saved profiles
- Delete profiles
- View all available profiles

## Keyboard Shortcuts

- **Ctrl+Q**: Quit application
- **Ctrl+R**: Run analysis
- **Ctrl+S**: Save current configuration
- **Ctrl+L**: Load saved configuration

## Configuration Storage

Configurations are saved in:
- Default config: `~/.sparrow/tui_config.json`
- Named profiles: `~/.sparrow/profiles/<profile_name>.json`

## Command Preview

The TUI displays a real-time preview of the command that will be executed, making it easy to:
- Verify all settings before running
- Copy the command for manual execution
- Learn the CLI flags and options
- Debug configuration issues

## Example Workflow

1. Launch TUI: `python -m tui.sparrow_tui`
2. Navigate to **Document** tab, enter document path
3. Configure analysis options in **Analysis** tab
4. Add questions in **Q&A** tab if needed
5. Review command preview at bottom
6. Press **Ctrl+R** or click **Run Analysis**
7. Save configuration for reuse: **Ctrl+S** or save as profile

## Profile Management

Save frequently used configurations as profiles:

1. Configure all settings
2. Go to **Profiles** tab
3. Enter profile name (e.g., "quick-analysis" or "deep-dive")
4. Click **Save Profile**
5. Load later by entering name and clicking **Load Profile**

## Notes

- All options from `sparrow_grader_v8.py` are available
- Changes update command preview in real-time
- Invalid settings show error notifications
- Successfully completed analyses show success notifications

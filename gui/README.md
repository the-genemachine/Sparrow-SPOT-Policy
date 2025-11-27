# Sparrow SPOT Scale™ GUI

Interactive web interface for Sparrow policy document analysis.

## Quick Start

### 1. Install Gradio

```bash
pip install gradio
```

### 2. Launch the GUI

```bash
cd /home/gene/Wave-2-2025-Methodology/SPOT_News
python gui/sparrow_gui.py
```

### 3. Open in Browser

The interface will automatically open at **http://localhost:7860**

## Features

### 📄 Document Input Tab
- Upload PDF files or provide URLs
- Choose analysis variant (Policy/Journalism)
- Set custom output filenames

### 📝 Narrative Settings Tab
- Select editorial style (Journalistic, Academic, Civic, Critical, Explanatory)
- Control narrative length (Concise → Comprehensive)
- Choose Ollama model for generation

### 🔍 Analysis Options Tab
- **Deep AI Analysis**: 6-level transparency with statistical proof
- **Citation Check**: Extract and score sources
- **URL Verification**: Test cited links for accessibility

### 🔒 Transparency & Compliance Tab
- **Enhanced Provenance**: Document metadata extraction
- **AI Disclosure**: Auto-generate transparency statements (4 formats)
- **Data Source Tracing**: Validate claims against Statistics Canada/IMF/OECD
- **NIST Compliance**: AI RMF compliance mapping
- **Lineage Charts**: Visualize analysis pipeline

### ▶️ Run Analysis Tab
- One-click document analysis
- Real-time progress updates
- Copy-paste command output for terminal use

## Interface Tabs Explained

### Tab 1: Document Input
Choose your input source (file or URL) and basic settings.

**Example:**
- Upload: `2025-Budget.pdf`
- Variant: `policy`
- Output: `budget_analysis`

### Tab 2: Narrative Settings (Policy Only)
Generate publish-ready narratives in different styles.

**Example for journalistic style:**
- Style: `journalistic` (Globe & Mail tone)
- Length: `comprehensive` (~3500 words)
- Model: `phi4:14b` (higher quality)

### Tab 3: Analysis Options
Control depth of analysis.

**Recommended for budgets:**
- ✅ Deep AI Analysis (catch hidden AI content)
- ✅ Citation Check (find missing sources)
- ❌ Check URLs (slow, only if needed)

### Tab 4: Transparency Features
New in v8.3 - comprehensive transparency toolkit.

**Recommended combination:**
- ✅ AI Disclosure (government transparency)
- ✅ Trace Data Sources (validate economic claims)
- ✅ NIST Compliance (regulatory mapping)
- Lineage Chart: `html` (visual pipeline)

### Tab 5: Run Analysis
Execute and monitor.

**Output shows:**
- Generated files list
- Command for terminal reproduction
- Status updates

## Example Use Cases

### Use Case 1: Quick Policy Analysis
**Settings:**
- Input: Upload `policy.pdf`
- Variant: `policy`
- Narrative: `None`
- Flags: Default (all unchecked)

**Result:** Basic scores + certificate (~2 min)

### Use Case 2: Full Transparency Audit
**Settings:**
- Input: Upload `2025-Budget.pdf`
- Variant: `policy`
- Narrative: `explanatory`, `comprehensive`
- Deep Analysis: ✅
- Citation Check: ✅
- AI Disclosure: ✅
- Trace Data Sources: ✅
- NIST Compliance: ✅
- Lineage Chart: `html`

**Result:** Complete transparency package (~8 min)
- 82.9/100 composite score
- 53.2% AI detection (Cohere)
- 5 contradictions flagged
- 0.9/100 citation score
- 15/100 NIST compliance
- Data lineage validation
- 4 AI disclosure formats
- HTML certificate + flowchart

### Use Case 3: Opposition Research
**Settings:**
- Input: Government policy URL
- Variant: `policy`
- Narrative: `critical`, `detailed`
- Deep Analysis: ✅
- Citation Check: ✅
- Trace Data Sources: ✅

**Result:** Critical analysis for Parliamentary questions
- Economic claim validation
- Missing citations highlighted
- AI usage exposed
- Contradiction detection

## Advanced: Sharing Your Interface

### Public URL (Temporary)
Set `share=True` in `interface.launch()`:

```python
interface.launch(share=True)
```

Gradio generates a public URL like: `https://abc123.gradio.live`
- Valid for 72 hours
- Anyone with link can access
- Perfect for demos/collaboration

### Permanent Deployment
Deploy to Hugging Face Spaces (free):

```bash
# Create Hugging Face account
# Create new Space with Gradio SDK
# Push code to Space
```

## Tips & Tricks

### Faster Analysis
- Skip `--check-urls` unless you need it
- Use `llama3.2` instead of larger models
- Don't enable `--deep-analysis` for quick checks

### Best Quality
- Use `phi4:14b` for narratives (better reasoning)
- Enable all transparency features
- Use `comprehensive` length for thorough reports

### Batch Processing
GUI is for single documents. For batch:
- Use command-line with shell scripts
- Or extend GUI with batch upload feature

## Keyboard Shortcuts
- **Ctrl+Enter**: Submit form (while in text field)
- **Ctrl+C**: Stop server (in terminal)
- **F5**: Refresh interface

## Troubleshooting

### "Sparrow not available - demo mode"
- GUI launches but can't run analysis
- **Fix**: Ensure `sparrow_grader_v8.py` is in parent directory
- Check imports at top of `sparrow_gui.py`

### "Port already in use"
- Another app using port 7860
- **Fix**: Change port in `interface.launch(server_port=7861)`

### "Model not found" (Ollama)
- Selected model not pulled locally
- **Fix**: Run `ollama pull phi4:14b` before starting GUI

### Slow performance
- Deep analysis + citation check + URL verification = ~10 min
- **Fix**: Disable unnecessary features for faster results

## Customization

### Change Theme
Edit `gr.themes.Soft()` to:
- `gr.themes.Default()`
- `gr.themes.Glass()`
- `gr.themes.Monochrome()`

### Add Custom Presets
Add preset buttons for common configurations:

```python
gr.Button("Quick Analysis").click(lambda: set_quick_preset())
gr.Button("Full Audit").click(lambda: set_full_preset())
```

### Modify Colors
Change `primary_hue` in theme:
```python
theme=gr.themes.Soft(primary_hue="green")  # or "red", "orange", etc.
```

## Future Enhancements

Potential additions:
- [ ] Batch document upload
- [ ] Live preview of outputs
- [ ] Comparison mode (2+ documents side-by-side)
- [ ] Historical trend charts
- [ ] Download all outputs as ZIP
- [ ] API key management for remote models
- [ ] Custom weighting sliders
- [ ] Real-time progress bar with ETA

## Support

**Issues**: Report bugs or request features on GitHub
**Documentation**: See main README.md
**Examples**: Check `docs/` for case studies

---

**Built with Gradio** - https://gradio.app  
**Sparrow SPOT Scale™** v8.3 - Open-source transparency toolkit

#!/usr/bin/env python3
"""
Sparrow SPOT Scale™ GUI
Interactive web interface for policy document analysis

Built with Gradio - https://gradio.app
Install: pip install gradio

Usage:
    python gui/sparrow_gui.py
    # Opens in browser at http://localhost:7860
"""

import gradio as gr
import sys
import os
from pathlib import Path
import json
import tempfile
import shutil
import io
from contextlib import redirect_stdout
from datetime import datetime

# Add SPOT_News directory to path (gui/ is subdirectory of SPOT_News/)
# This file is at: SPOT_News/gui/sparrow_gui.py
# We need to add: SPOT_News/ to sys.path
CURRENT_FILE = Path(__file__).resolve()  # Absolute path to this file
GUI_DIR = CURRENT_FILE.parent  # gui/
SPOT_NEWS_DIR = GUI_DIR.parent  # SPOT_News/
WAVE_DIR = SPOT_NEWS_DIR.parent  # Wave-2-2025-Methodology/

# CRITICAL: Insert SPOT_News FIRST before any other imports
# This ensures we get the correct versions of modules that exist in both places
sys.path.insert(0, str(SPOT_NEWS_DIR))

# Import support modules FIRST (before sparrow_grader_v8 which will add parent to sys.path)
# Import only modules that are in SPOT_News/ directory
try:
    from certificate_generator import CertificateGenerator
    from ai_disclosure_generator import AIDisclosureGenerator
    from data_lineage_source_mapper import DataLineageSourceMapper
    from citation_quality_scorer import CitationQualityScorer
    from deep_analyzer import DeepAnalyzer
    
    # Now import sparrow_grader_v8 (it will add parent for article_analyzer)
    from sparrow_grader_v8 import SPARROWGrader, SPOTPolicy
    from article_analyzer import ArticleAnalyzer
    
    SPARROW_AVAILABLE = True
except ImportError as e:
    SPARROW_AVAILABLE = False
    print(f"⚠️  Sparrow grader not available - running in demo mode: {e}")


def analyze_document(
    # File input
    pdf_file,
    url_input,
    
    # Basic settings
    variant,
    output_name,
    
    # Narrative settings
    narrative_style,
    narrative_length,
    ollama_model,
    
    # Analysis flags
    deep_analysis,
    citation_check,
    check_urls,
    
    # Transparency flags
    enhanced_provenance,
    generate_ai_disclosure,
    trace_data_sources,
    nist_compliance,
    lineage_chart_format,
    
    # Progress callback
    progress=gr.Progress()
):
    """
    Main analysis function called when user clicks 'Analyze Document'.
    
    Returns: Status message and path to results
    """
    
    # Capture stdout to show detailed progress
    output_buffer = io.StringIO()
    
    # Validate inputs
    if not pdf_file and not url_input:
        return "❌ Error: Please provide either a PDF file or URL", None
    
    if pdf_file and url_input:
        return "❌ Error: Please provide either a file OR URL, not both", None
    
    progress(0.1, desc="Initializing analysis...")
    
    # Track temporary files
    temp_files = []
    
    try:
        # Prepare input file path
        if pdf_file:
            input_path = pdf_file.name
            input_source = Path(pdf_file.name).stem
        else:
            # For URL input, we'll pass it to the CLI command
            input_path = None
            input_source = url_input.split('/')[-1].split('?')[0] or 'remote_document'
        
        # Set output name
        if not output_name:
            output_name = f"{input_source}_analysis"
        
        progress(0.2, desc="Reading document...")
        
        # Extract text from input
        if input_path:
            is_pdf = input_path.lower().endswith('.pdf')
            if is_pdf:
                grader = SPARROWGrader()
                text = grader.extract_text_from_pdf(input_path)
            else:
                with open(input_path, 'r', encoding='utf-8') as f:
                    text = f.read()
        else:
            # Handle URL - use subprocess for now
            return run_via_subprocess(
                url_input, variant, output_name, narrative_style, narrative_length,
                ollama_model, deep_analysis, citation_check, check_urls,
                enhanced_provenance, generate_ai_disclosure, trace_data_sources,
                nist_compliance, lineage_chart_format, progress
            )
        
        progress(0.3, desc=f"Analyzing with {variant} variant...")
        
        # Run analysis based on variant
        if variant == 'journalism':
            grader = SPARROWGrader()
            results = grader.grade_article(text, input_source)
            
            progress(0.8, desc="Generating outputs...")
            
            # Generate outputs
            output_files = []
            
            # JSON report
            json_path = f"{output_name}.json"
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            output_files.append(json_path)
            
            # Text summary
            txt_path = f"{output_name}.txt"
            with open(txt_path, 'w') as f:
                f.write(format_journalism_summary(results))
            output_files.append(txt_path)
            
            # Certificate
            cert_path = generate_certificate(results, output_name, variant)
            output_files.append(cert_path)
            
        else:  # policy variant
            # Capture stdout from all analysis modules
            with redirect_stdout(output_buffer):
                policy = SPOTPolicy()
                results = policy.grade(text, pdf_path=input_path if is_pdf else None)
                
                progress(0.5, desc="Running policy evaluation...")
                
                # Initialize output files list
                output_files = []
                
                # Apply optional enhancements
                if deep_analysis:
                    progress(0.6, desc="Running deep AI analysis (6 levels)...")
                    results = add_deep_analysis(results, text, input_path)
                
                if citation_check:
                    progress(0.65, desc="Checking citation quality...")
                    results, citation_file = add_citation_analysis(results, text, check_urls, output_name)
                    output_files.append(citation_file)
                
                if generate_ai_disclosure:
                    progress(0.7, desc="Generating AI disclosure statements...")
                    disclosure_files = add_ai_disclosure(results, output_name)
                    if disclosure_files:
                        output_files.extend(disclosure_files)
                
                if trace_data_sources:
                    progress(0.75, desc="Tracing data sources...")
                    results, lineage_files = add_data_lineage(results, text, output_name)
                    output_files.extend(lineage_files)
                
                if nist_compliance:
                    progress(0.8, desc="Checking NIST compliance...")
                    results = add_nist_compliance(results, text)
                
                progress(0.85, desc="Generating outputs...")
                
                # JSON report
                json_path = f"{output_name}.json"
                with open(json_path, 'w') as f:
                    json.dump(results, f, indent=2)
                output_files.append(json_path)
                
                # Text summary
                txt_path = f"{output_name}.txt"
                with open(txt_path, 'w') as f:
                    f.write(format_policy_summary(results))
                output_files.append(txt_path)
                
                # Certificate
                cert_path = generate_certificate(results, output_name, variant)
                output_files.append(cert_path)
                
                # Narrative (if requested)
                if narrative_style != "None":
                    progress(0.9, desc=f"Generating {narrative_style} narrative...")
                    narrative_files = generate_narrative(
                        results, text, output_name, narrative_style, 
                        narrative_length, ollama_model
                    )
                    output_files.extend(narrative_files)
                
                # Lineage chart (if requested)
                if lineage_chart_format != "None":
                    progress(0.92, desc="Creating lineage flowchart...")
                    chart_path = generate_lineage_chart(results, output_name, lineage_chart_format)
                    if chart_path:
                        output_files.append(chart_path)
        
        progress(1.0, desc="Analysis complete!")
        
        # Get captured output
        detailed_output = output_buffer.getvalue()
        
        # Format success message
        score = results.get('composite_score', 0)
        grade = results.get('composite_letter_grade', 'N/A')
        
        result_msg = f"""✅ Analysis Complete!

**Score:** {score:.1f}/100 ({grade})

**Generated Files:**
"""
        for file_path in output_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path) / 1024
                result_msg += f"• {file_path} ({size:.1f} KB)\n"
        
        # Add detailed analysis output
        if detailed_output.strip():
            result_msg += f"\n\n{'='*60}\nDETAILED ANALYSIS OUTPUT:\n{'='*60}\n{detailed_output}"
        
        # Build equivalent CLI command
        cmd_parts = [sys.executable, "sparrow_grader_v8.py"]
        if input_path:
            cmd_parts.append(input_path)
        else:
            cmd_parts.extend(["--url", url_input])
        cmd_parts.extend(["--variant", variant, "--output", output_name])
        
        if narrative_style != "None":
            cmd_parts.extend(["--narrative-style", narrative_style])
        if narrative_length != "standard":
            cmd_parts.extend(["--narrative-length", narrative_length])
        if deep_analysis:
            cmd_parts.append("--deep-analysis")
        if citation_check:
            cmd_parts.append("--citation-check")
        if check_urls:
            cmd_parts.append("--check-urls")
        if enhanced_provenance:
            cmd_parts.append("--enhanced-provenance")
        if generate_ai_disclosure:
            cmd_parts.append("--generate-ai-disclosure")
        if trace_data_sources:
            cmd_parts.append("--trace-data-sources")
        if nist_compliance:
            cmd_parts.append("--nist-compliance")
        if lineage_chart_format != "None":
            cmd_parts.extend(["--lineage-chart", lineage_chart_format])
        
        command_str = " ".join(cmd_parts)
        result_msg += f"\n**Equivalent CLI Command:**\n```\n{command_str}\n```"
        
        return result_msg, json_path
        
    except Exception as e:
        import traceback
        error_msg = f"""❌ Analysis Failed

**Error:** {str(e)}

**Traceback:**
```
{traceback.format_exc()}
```
"""
        return error_msg, None
    
    finally:
        # Cleanup temp files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass


def run_via_subprocess(url, variant, output_name, narrative_style, narrative_length,
                       ollama_model, deep_analysis, citation_check, check_urls,
                       enhanced_provenance, generate_ai_disclosure, trace_data_sources,
                       nist_compliance, lineage_chart_format, progress):
    """Run analysis via subprocess for URL inputs."""
    import subprocess
    
    # Use sys.executable to get the current Python interpreter
    cmd = [sys.executable, "sparrow_grader_v8.py", "--url", url, "--variant", variant, "--output", output_name]
    
    if narrative_style != "None":
        cmd.extend(["--narrative-style", narrative_style])
    if narrative_length != "standard":
        cmd.extend(["--narrative-length", narrative_length])
    if ollama_model != "llama3.2":
        cmd.extend(["--ollama-model", ollama_model])
    if deep_analysis:
        cmd.append("--deep-analysis")
    if citation_check:
        cmd.append("--citation-check")
    if check_urls:
        cmd.append("--check-urls")
    if enhanced_provenance:
        cmd.append("--enhanced-provenance")
    if generate_ai_disclosure:
        cmd.append("--generate-ai-disclosure")
    if trace_data_sources:
        cmd.append("--trace-data-sources")
    if nist_compliance:
        cmd.append("--nist-compliance")
    if lineage_chart_format != "None":
        cmd.extend(["--lineage-chart", lineage_chart_format])
    
    progress(0.3, desc="Running Sparrow via subprocess...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            progress(1.0, desc="Complete!")
            return f"""✅ Analysis Complete (via subprocess)

**Output:**
{result.stdout}

**Command:**
```
{' '.join(cmd)}
```
""", f"{output_name}.json"
        else:
            return f"""❌ Analysis Failed

**Error:**
{result.stderr}

**Command:**
```
{' '.join(cmd)}
```
""", None
    except subprocess.TimeoutExpired:
        return "❌ Analysis timed out (>10 minutes)", None
    except Exception as e:
        return f"❌ Subprocess error: {str(e)}", None


def format_journalism_summary(results):
    """Format journalism results as text summary."""
    lines = []
    lines.append("=" * 60)
    lines.append("SPARROW SCALE™ - JOURNALISM ANALYSIS")
    lines.append("=" * 60)
    lines.append(f"\nDocument: {results.get('document_name', 'Unknown')}")
    lines.append(f"Analysis Date: {results.get('analysis_date', 'Unknown')}")
    lines.append(f"\nComposite Score: {results.get('composite_score', 0):.1f}/100")
    lines.append(f"Letter Grade: {results.get('composite_letter_grade', 'N/A')}")
    lines.append("\n" + "-" * 60)
    lines.append("CATEGORY SCORES:")
    lines.append("-" * 60)
    
    for cat, details in results.get('categories', {}).items():
        score = details.get('score', 0)
        label = details.get('qualitative_label', 'N/A')
        lines.append(f"\n{cat}: {score:.1f}/100 - {label}")
    
    return "\n".join(lines)


def format_policy_summary(results):
    """Format policy results as text summary."""
    lines = []
    lines.append("=" * 60)
    lines.append("SPOT POLICY™ - POLICY DOCUMENT ANALYSIS")
    lines.append("=" * 60)
    lines.append(f"\nDocument: {results.get('document_name', 'Unknown')}")
    lines.append(f"Analysis Date: {results.get('analysis_date', 'Unknown')}")
    lines.append(f"\nComposite Score: {results.get('composite_score', 0):.1f}/100")
    lines.append(f"Letter Grade: {results.get('composite_letter_grade', 'N/A')}")
    lines.append("\n" + "-" * 60)
    lines.append("CATEGORY SCORES:")
    lines.append("-" * 60)
    
    for cat, details in results.get('categories', {}).items():
        score = details.get('score', 0)
        label = details.get('qualitative_label', 'N/A')
        lines.append(f"\n{cat}: {score:.1f}/100 - {label}")
    
    if 'ai_transparency' in results:
        lines.append("\n" + "-" * 60)
        lines.append("AI TRANSPARENCY:")
        lines.append("-" * 60)
        at_score = results['ai_transparency'].get('score', 0)
        lines.append(f"Score: {at_score:.1f}/100")
    
    return "\n".join(lines)


def generate_certificate(results, output_name, variant):
    """Generate HTML certificate."""
    cert_gen = CertificateGenerator()
    cert_path = f"{output_name}_certificate.html"
    
    if variant == 'journalism':
        cert_gen.generate_journalism_certificate(
            report=results,
            output_file=cert_path
        )
    else:  # policy
        cert_gen.generate_policy_certificate(
            report=results,
            output_file=cert_path
        )
    
    return cert_path


def add_deep_analysis(results, text, input_path):
    """Add 6-level deep AI analysis."""
    analyzer = DeepAnalyzer()
    deep_results = analyzer.analyze_document(input_path)
    
    results['deep_analysis'] = deep_results
    return results


def add_citation_analysis(results, text, check_urls, output_name):
    """Add citation quality scoring."""
    scorer = CitationQualityScorer()
    citation_results = scorer.analyze_citations(text, check_urls=check_urls)
    
    # Save citation report
    citation_file = f"{output_name}_citation_report.txt"
    with open(citation_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("CITATION QUALITY ANALYSIS REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Overall Score: {citation_results.get('overall_score', 0):.1f}/100\n\n")
        f.write("Details:\n")
        for key, value in citation_results.items():
            if key != 'overall_score':
                f.write(f"  {key}: {value}\n")
    
    results['citation_quality'] = citation_results
    return results, citation_file


def add_ai_disclosure(results, output_name):
    """Generate AI disclosure statements."""
    # Initialize generator with full results (positional argument, not keyword)
    generator = AIDisclosureGenerator(results)
    
    # Generate all formats
    files = generator.generate_all_formats(output_prefix=output_name)
    
    return files


def add_data_lineage(results, text, output_name):
    """Add data lineage source tracing."""
    mapper = DataLineageSourceMapper()
    lineage_data = mapper.trace_sources(text)
    
    # Save text report
    output_lineage_txt = f"{output_name}_data_lineage.txt"
    with open(output_lineage_txt, 'w', encoding='utf-8') as f:
        f.write(mapper.generate_report(lineage_data, 'text'))
    
    # Save JSON report
    output_lineage_json = f"{output_name}_data_lineage.json"
    with open(output_lineage_json, 'w', encoding='utf-8') as f:
        json.dump(lineage_data, f, indent=2)
    
    # Add summary to results
    results['data_lineage'] = lineage_data.get('summary', {})
    
    return results, [output_lineage_txt, output_lineage_json]


def add_nist_compliance(results, text):
    """Add NIST AI RMF compliance check."""
    from nist_compliance_checker import NISTComplianceChecker
    
    checker = NISTComplianceChecker()
    nist_results = checker.check_compliance(results)
    
    results['nist_compliance'] = nist_results
    return results


def generate_narrative(results, text, output_name, style, length, model):
    """Generate narrative outputs."""
    from narrative_integration import create_pipeline
    
    pipeline = create_pipeline()
    
    output_files = []
    
    # Generate complete narrative
    narrative_result = pipeline.generate_complete_narrative(
        analysis=results,
        tone=style,
        length=length,
        ollama_model=model,
        formats=['x_thread', 'linkedin', 'social_badge', 'html_certificate']
    )
    
    # Save narrative text
    narrative_path = f"{output_name}_narrative.txt"
    with open(narrative_path, 'w') as f:
        f.write(narrative_result.get('narrative_text', ''))
    output_files.append(narrative_path)
    
    return output_files


def generate_lineage_chart(results, output_name, format):
    """Generate data lineage flowchart."""
    from data_lineage_visualizer import DataLineageVisualizer
    
    viz = DataLineageVisualizer()
    
    if format == "html":
        content = viz.generate_html_flowchart()
        chart_path = f"{output_name}_lineage_flowchart.html"
    else:  # ascii
        content = viz.generate_ascii_flowchart()
        chart_path = f"{output_name}_lineage_flowchart.txt"
    
    with open(chart_path, 'w') as f:
        f.write(content)
    
    return chart_path


def update_settings_summary(pdf_file, url_input, variant, output_name, narrative_style, 
                           narrative_length, ollama_model, deep_analysis, citation_check, 
                           check_urls, enhanced_provenance, generate_ai_disclosure, 
                           trace_data_sources, nist_compliance, lineage_chart_format):
    """Generate a summary of current settings."""
    
    # Input source
    if pdf_file:
        input_src = f"📄 **File:** {Path(pdf_file.name).name}"
    elif url_input:
        input_src = f"🌐 **URL:** {url_input}"
    else:
        input_src = "⚠️ **No input selected**"
    
    # Build summary
    summary = f"""### Current Configuration

{input_src}

**Analysis Variant:** {variant.upper()}  
**Output Prefix:** {output_name if output_name else '(auto-generated)'}

---

**Narrative Generation:**
- Style: {narrative_style.title() if narrative_style != 'None' else 'Disabled'}
- Length: {narrative_length.title()}
- Model: {ollama_model}

---

**Analysis Options:**
- Deep AI Analysis (6 levels): {'✅ Enabled' if deep_analysis else '❌ Disabled'}
- Citation Quality Check: {'✅ Enabled' if citation_check else '❌ Disabled'}
- URL Verification: {'✅ Enabled' if check_urls else '❌ Disabled'}

---

**Transparency Features:**
- Enhanced Provenance: {'✅ Enabled' if enhanced_provenance else '❌ Disabled'}
- AI Disclosure Statements: {'✅ Enabled' if generate_ai_disclosure else '❌ Disabled'}
- Data Source Tracing: {'✅ Enabled' if trace_data_sources else '❌ Disabled'}
- NIST Compliance Check: {'✅ Enabled' if nist_compliance else '❌ Disabled'}
- Lineage Flowchart: {lineage_chart_format if lineage_chart_format != 'None' else 'Disabled'}

---

**Ready to analyze!** Click the button below to start.
"""
    
    return summary


def get_available_ollama_models():
    """Get list of available Ollama models on the system."""
    try:
        import subprocess
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Parse the output
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Skip header
                models = []
                for line in lines[1:]:
                    # Extract model name (first column)
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        # Only remove :latest suffix, keep other tags like :14b
                        if model_name.endswith(':latest'):
                            model_name = model_name.replace(':latest', '')
                        models.append(model_name)
                
                if models:
                    return models
        
        # Fallback to common models if ollama list fails
        return ["llama3.2", "phi4:14b", "mistral", "qwen2.5", "gemma2"]
        
    except Exception as e:
        print(f"Could not check Ollama models: {e}")
        # Return default list
        return ["llama3.2", "phi4:14b", "mistral", "qwen2.5", "gemma2"]


# Build the Gradio interface
def create_interface():
    """Create the Gradio web interface."""
    
    # Get available Ollama models
    available_models = get_available_ollama_models()
    
    with gr.Blocks(title="Sparrow SPOT Scale™") as interface:
        
        # Add custom CSS using gr.HTML
        gr.HTML("""
        <style>
        /* Modern tab styling for Gradio 6.x */
        .gradio-container {
            max-width: 1200px;
            margin: 0 auto;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Tab improvements */
        .tab-nav {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px 12px 0 0;
            padding: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .tab-nav button {
            background: rgba(255,255,255,0.2) !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
            color: white !important;
            margin-right: 4px;
            padding: 14px 24px !important;
            font-weight: 600 !important;
            border-radius: 8px 8px 0 0 !important;
            transition: all 0.3s ease !important;
        }
        
        .tab-nav button:hover {
            background: rgba(255,255,255,0.3) !important;
            transform: translateY(-2px);
        }
        
        .tab-nav button.selected,
        .tab-nav button[aria-selected="true"] {
            background: white !important;
            color: #667eea !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        
        /* Header styling */
        h1 {
            color: #2c3e50 !important;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        h3 {
            color: #667eea !important;
            font-weight: 600 !important;
            margin-bottom: 15px;
            border-bottom: 2px solid #e1e8ed;
            padding-bottom: 8px;
        }
        
        /* Button improvements */
        button.primary, .primary button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 30px !important;
            font-weight: 600 !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease !important;
        }
        
        button.primary:hover, .primary button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
        }
        
        /* Accordion improvements */
        .gr-accordion .gr-accordion-header {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 16px !important;
        }
        </style>
        """)
        
        gr.Markdown("""
        # 🦅 Sparrow SPOT Scale™ v8.3
        ### Automated Policy & Journalism Analysis
        
        Comprehensive transparency analysis for policy documents with AI detection, 
        citation validation, and NIST compliance checking.
        """)
        
        with gr.Tabs():
            
            # ========== TAB 1: DOCUMENT INPUT ==========
            with gr.Tab("📄 Document Input"):
                gr.Markdown("### Input Source")
                gr.Markdown("Choose **either** file upload or URL (not both)")
                
                with gr.Row():
                    with gr.Column():
                        pdf_file = gr.File(
                            label="Upload PDF Document",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                    
                    with gr.Column():
                        url_input = gr.Textbox(
                            label="OR: Enter Document URL",
                            placeholder="https://example.com/document.pdf",
                            lines=1
                        )
                
                gr.Markdown("### Basic Settings")
                
                with gr.Row():
                    variant = gr.Radio(
                        choices=["policy", "journalism"],
                        value="policy",
                        label="Analysis Variant",
                        info="Policy = SPOT-Policy™ (government docs) | Journalism = SPARROW™ (news articles)"
                    )
                    
                    output_name = gr.Textbox(
                        label="Output Filename Prefix",
                        placeholder="my_analysis (leave empty to auto-generate)",
                        lines=1
                    )
            
            # ========== TAB 2: NARRATIVE SETTINGS ==========
            with gr.Tab("📝 Narrative Settings"):
                gr.Markdown("""
                ### Publish-Ready Narrative Generation
                Generate professional narratives in different editorial styles.
                *Only available for policy variant.*
                """)
                
                narrative_style = gr.Radio(
                    choices=["None", "journalistic", "academic", "civic", "critical", "explanatory"],
                    value="None",
                    label="Narrative Style",
                    info="Journalistic = Globe & Mail | Academic = Policy Options | Civic = Open government | Critical = Investigative | Explanatory = Educational"
                )
                
                narrative_length = gr.Radio(
                    choices=["concise", "standard", "detailed", "comprehensive"],
                    value="standard",
                    label="Narrative Length",
                    info="Concise (500 words) • Standard (1000) • Detailed (2000) • Comprehensive (3500+)"
                )
                
                ollama_model = gr.Dropdown(
                    choices=available_models,
                    value=available_models[0] if available_models else "llama3.2",
                    label="Ollama Model",
                    info=f"Available local models ({len(available_models)} found). Run 'ollama pull <model>' to add more.",
                    allow_custom_value=True
                )
            
            # ========== TAB 3: ANALYSIS OPTIONS ==========
            with gr.Tab("🔍 Analysis Options"):
                gr.Markdown("### Deep Analysis")
                
                deep_analysis = gr.Checkbox(
                    label="Enable Deep AI Analysis (6-level transparency)",
                    value=False,
                    info="Statistical proof, phrase fingerprints, sentence-level detection. Adds ~2 minutes."
                )
                
                gr.Markdown("### Citation Analysis")
                
                citation_check = gr.Checkbox(
                    label="Analyze Citation Quality",
                    value=False,
                    info="Extract and score citations/sources. Identifies missing references."
                )
                
                check_urls = gr.Checkbox(
                    label="Verify URL Accessibility (slower)",
                    value=False,
                    info="Check if cited URLs are accessible. Only works with --citation-check. Checks first 10 URLs."
                )
            
            # ========== TAB 4: TRANSPARENCY FEATURES ==========
            with gr.Tab("🔒 Transparency & Compliance"):
                gr.Markdown("### Enhanced Transparency Modules (v8.3)")
                
                enhanced_provenance = gr.Checkbox(
                    label="Enhanced Provenance Tracking",
                    value=False,
                    info="Extract comprehensive document metadata (author, creation tool, edit patterns)"
                )
                
                generate_ai_disclosure = gr.Checkbox(
                    label="Generate AI Disclosure Statements",
                    value=True,
                    info="Auto-create transparency disclosures (formal, plain-language, technical, social media)"
                )
                
                trace_data_sources = gr.Checkbox(
                    label="Trace Data Sources",
                    value=True,
                    info="Validate quantitative claims against Statistics Canada, IMF, OECD data"
                )
                
                nist_compliance = gr.Checkbox(
                    label="NIST AI RMF Compliance Check",
                    value=False,
                    info="Generate compliance report mapping to Gov/Map/Measure/Manage pillars"
                )
                
                lineage_chart_format = gr.Radio(
                    choices=["None", "html", "ascii", "json"],
                    value="None",
                    label="Data Lineage Flowchart",
                    info="Visualize analysis pipeline stages"
                )
            
            # ========== TAB 5: OUTPUT & EXECUTION ==========
            with gr.Tab("▶️ Run Analysis"):
                gr.Markdown("### Ready to Analyze")
                
                # Settings summary
                with gr.Accordion("📋 Current Settings Summary", open=False):
                    settings_summary = gr.Markdown(
                        "**Tip:** Review your settings in the tabs above before clicking Analyze Document.",
                        elem_id="settings-summary"
                    )
                
                analyze_btn = gr.Button(
                    "🎯 Analyze Document",
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("---")
                
                with gr.Row():
                    with gr.Column():
                        output_status = gr.Textbox(
                            label="Analysis Status",
                            lines=15,
                            max_lines=25,
                            interactive=False
                        )
                    
                    with gr.Column():
                        command_output = gr.Textbox(
                            label="Command Executed",
                            lines=5,
                            max_lines=10,
                            interactive=False
                        )
        
        # ========== BOTTOM INFO ==========
        gr.Markdown("""
        ---
        ### About Sparrow SPOT Scale™
        
        **Open-source transparency toolkit** for automated policy analysis.
        
        **Features:**
        - 🤖 AI detection (6 levels: None → Heavy, with model identification)
        - 📊 Economic rigor validation with contradiction detection
        - 📚 Citation quality scoring and source tracing
        - 🏛️ NIST AI RMF compliance mapping
        - 📋 Multi-format outputs (14 types: JSON, HTML, narrative, social media, etc.)
        
        **Market Value:** $340M-1B TAM | **Cost:** $0 (vs. $430-1,225/month commercial tools)
        
        [GitHub Repository](#) | [Documentation](#) | [Case Studies](#)
        """)
        
        # Wire up settings summary to update when any input changes
        all_inputs = [
            pdf_file, url_input, variant, output_name,
            narrative_style, narrative_length, ollama_model,
            deep_analysis, citation_check, check_urls,
            enhanced_provenance, generate_ai_disclosure,
            trace_data_sources, nist_compliance, lineage_chart_format
        ]
        
        for input_component in all_inputs:
            input_component.change(
                fn=update_settings_summary,
                inputs=all_inputs,
                outputs=settings_summary
            )
        
        # Connect the analyze button to the function
        analyze_btn.click(
            fn=analyze_document,
            inputs=[
                # Document input
                pdf_file,
                url_input,
                
                # Basic settings
                variant,
                output_name,
                
                # Narrative settings
                narrative_style,
                narrative_length,
                ollama_model,
                
                # Analysis flags
                deep_analysis,
                citation_check,
                check_urls,
                
                # Transparency flags
                enhanced_provenance,
                generate_ai_disclosure,
                trace_data_sources,
                nist_compliance,
                lineage_chart_format,
            ],
            outputs=[output_status, command_output]
        )
    
    return interface


if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         Sparrow SPOT Scale™ v8.3 - Web Interface        ║
    ╚══════════════════════════════════════════════════════════╝
    
    🚀 Starting Gradio server...
    📱 Interface will open in your browser automatically
    🌐 Access at: http://localhost:7860
    
    Press Ctrl+C to stop the server
    """)
    
    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True to get public URL for sharing
        show_error=True
    )

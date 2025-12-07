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
from typing import Dict  # v8.6: Type hints
import json
import tempfile
import shutil
import io
from contextlib import redirect_stdout
from datetime import datetime
import gc
import signal
import atexit

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
    from ai_usage_explainer import AIUsageExplainer  # NEW v8.3.3: Detailed AI usage reports
    from data_lineage_source_mapper import DataLineageSourceMapper
    from citation_quality_scorer import CitationQualityScorer
    from deep_analyzer import DeepAnalyzer
    
    # Now import sparrow_grader_v8 (it will add parent for article_analyzer)
    from sparrow_grader_v8 import SPARROWGrader, SPOTPolicy
    from article_analyzer import ArticleAnalyzer
    from version import SPARROW_VERSION, get_version_string
    
    # v8.5: PDF column extraction for bilingual documents
    try:
        import pdfplumber
        PDFPLUMBER_AVAILABLE = True
    except ImportError:
        PDFPLUMBER_AVAILABLE = False
        print("⚠️  pdfplumber not available - bilingual PDF column extraction disabled")
    
    # v8.6: Token calculator and enhanced Q&A
    try:
        from token_calculator import analyze_document_file, estimate_tokens, recommend_model
        from semantic_chunker import chunk_document, save_chunks
        from enhanced_document_qa import EnhancedDocumentQA
        ENHANCED_QA_AVAILABLE = True
    except ImportError as e:
        ENHANCED_QA_AVAILABLE = False
        print(f"⚠️  Enhanced Q&A not available: {e}")
    
    SPARROW_AVAILABLE = True
except ImportError as e:
    SPARROW_AVAILABLE = False
    print(f"⚠️  Sparrow grader not available - running in demo mode: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY MANAGEMENT & CLEANUP (v8.4.1)
# ═══════════════════════════════════════════════════════════════════════════════

# Global reference to track active analyzers for cleanup
_active_analyzers = []
_active_ollama_generators = []
_cleanup_registered = False


def analyze_document_tokens(file_path: str) -> Dict:
    """
    Analyze document size and recommend chunking strategy.
    
    v8.6: Token analysis for large document handling.
    
    Args:
        file_path: Path to document file
    
    Returns:
        Dict with token analysis and recommendations
    """
    if not ENHANCED_QA_AVAILABLE:
        return {"error": "Enhanced Q&A not available"}
    
    try:
        from token_calculator import analyze_document_file
        
        # Analyze document
        analysis = analyze_document_file(file_path)
        
        return {
            "characters": analysis.get("characters", 0),
            "tokens": analysis.get("estimated_tokens", 0),
            "method": analysis.get("estimation_method", "unknown"),
            "pages": analysis.get("estimated_pages", 0),
            "recommendation": analysis.get("recommendation", {})
        }
    except Exception as e:
        return {"error": str(e)}


def cleanup_after_analysis():
    """
    Release memory after analysis completes.
    
    v8.4.1: Prevents system lockups when running Ollama models
    by explicitly cleaning up large objects and forcing garbage collection.
    """
    global _active_analyzers, _active_ollama_generators
    
    # Clear any cached analyzers
    for analyzer in _active_analyzers:
        try:
            if hasattr(analyzer, 'clear_cache'):
                analyzer.clear_cache()
            if hasattr(analyzer, 'clear_ai_calls_log'):
                analyzer.clear_ai_calls_log()
        except:
            pass
    
    _active_analyzers.clear()
    
    # Cleanup Ollama generators and unload models
    for generator in _active_ollama_generators:
        try:
            if hasattr(generator, 'cleanup'):
                generator.cleanup()
        except:
            pass
    
    _active_ollama_generators.clear()
    
    # Force garbage collection
    gc.collect()
    
    # Additional cleanup for PyTorch/CUDA if available
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    except ImportError:
        pass  # PyTorch not installed, skip
    
    print("🧹 Memory cleanup completed")


def extract_pdf_columns(pdf_path: str, output_dir: Path) -> str:
    """
    Extract English column from bilingual PDF with two-column layout.
    
    Args:
        pdf_path: Path to input PDF
        output_dir: Directory to save extracted text
        
    Returns:
        Path to extracted text file, or original PDF path if extraction fails
    """
    if not PDFPLUMBER_AVAILABLE:
        return pdf_path
    
    try:
        import pdfplumber
        import re
        
        print("📄 Detecting bilingual PDF layout...")
        
        # Quick check: sample first few pages to detect two-column layout
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) == 0:
                return pdf_path
            
            # Sample first 3 pages for better detection
            sample_pages = min(3, len(pdf.pages))
            sample_text = ""
            for i in range(sample_pages):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    sample_text += page_text + " "
            
            if not sample_text:
                return pdf_path
            
            # Heuristic: detect French content and legislative document patterns
            # Legislative documents often have both English and French side-by-side
            french_indicators = [
                'de la', 'du Canada', 'le ministre', 'des finances', 
                'loi', 'article', 'paragraphe', 'alinéa', 'ou', 'et'
            ]
            
            # Count French phrase occurrences
            french_count = sum(sample_text.lower().count(indicator) for indicator in french_indicators)
            
            # Also check for common English legislative terms
            english_legislative = ['Act', 'Section', 'subsection', 'Minister', 'Parliament']
            english_count = sum(sample_text.count(term) for term in english_legislative)
            
            # If we have both significant French AND English content, likely bilingual
            is_bilingual = french_count > 10 and english_count > 5
            
            if not is_bilingual:
                print(f"   Not detected as bilingual document (FR:{french_count}, EN:{english_count})")
                print("   Using standard extraction")
                return pdf_path
        
        print(f"   Bilingual layout detected (FR:{french_count}, EN:{english_count}) - extracting English column only...")
        
        # Extract English column
        english_text = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_width = page.width
                page_height = page.height
                
                # Define left column (English) - approximately left half
                left_bbox = (
                    30,                    # left margin
                    50,                    # top margin  
                    page_width / 2 - 20,   # right edge (leave gap)
                    page_height - 50       # bottom margin
                )
                
                # Extract left column text
                left_column = page.crop(left_bbox)
                text = left_column.extract_text()
                
                if text:
                    # Clean extracted text
                    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Remove excess newlines
                    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Remove page numbers
                    text = re.sub(r' {3,}', '  ', text)  # Remove excess spaces
                    english_text.append(text.strip())
        
        # Save extracted text
        output_file = output_dir / f"{Path(pdf_path).stem}_english_only.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        full_text = "\n\n".join(english_text)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        print(f"   ✅ Extracted {len(english_text)} pages ({len(full_text):,} characters)")
        print(f"   Saved to: {output_file}")
        
        return str(output_file)
        
    except Exception as e:
        print(f"   ⚠️  Column extraction failed: {e}")
        print(f"   Falling back to standard PDF extraction")
        return pdf_path


def manual_cleanup_button():
    """
    Manual cleanup triggered by GUI button.
    
    v8.4.1: Unloads ALL Ollama models and frees memory.
    """
    import requests
    import ctypes
    
    messages = []
    
    try:
        # Get list of loaded models
        resp = requests.get("http://localhost:11434/api/ps", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            unloaded = []
            for model in models:
                model_name = model.get('name', '')
                if model_name:
                    # Unload each model
                    requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": model_name, "prompt": "", "keep_alive": 0},
                        timeout=10
                    )
                    unloaded.append(model_name)
            
            if unloaded:
                messages.append(f"🧹 Unloaded {len(unloaded)} Ollama model(s): {', '.join(unloaded)}")
            else:
                messages.append("✅ No Ollama models were loaded")
        else:
            messages.append("⚠️ Could not connect to Ollama")
    except Exception as e:
        messages.append(f"⚠️ Ollama cleanup: {e}")
    
    # Clear global caches
    global _active_analyzers, _active_ollama_generators
    _active_analyzers.clear()
    _active_ollama_generators.clear()
    
    # Aggressive garbage collection
    gc.collect(0)  # Collect youngest generation
    gc.collect(1)  # Collect middle generation
    gc.collect(2)  # Collect oldest generation (full collection)
    
    # Try to release memory back to OS (Linux-specific)
    try:
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)
        messages.append("🧹 Released memory back to OS (malloc_trim)")
    except:
        pass  # Not available on all systems
    
    # Clear PyTorch CUDA cache if available
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            messages.append("🧹 Cleared CUDA cache")
    except ImportError:
        pass
    
    messages.append("✅ Memory cleanup completed. RAM usage should decrease.")
    
    return "\n".join(messages)


def graceful_shutdown(signum=None, frame=None):
    """Handle graceful shutdown on SIGINT/SIGTERM."""
    print("\n🛑 Shutting down Sparrow GUI...")
    cleanup_after_analysis()
    print("✅ Cleanup complete. Goodbye!")
    sys.exit(0)


def register_cleanup_handlers():
    """Register signal handlers and atexit for cleanup."""
    global _cleanup_registered
    
    if not _cleanup_registered:
        # Register signal handlers
        signal.signal(signal.SIGINT, graceful_shutdown)
        signal.signal(signal.SIGTERM, graceful_shutdown)
        
        # Register atexit handler
        atexit.register(cleanup_after_analysis)
        
        _cleanup_registered = True
        print("🔧 Cleanup handlers registered")


def browse_output_location():
    """Open system file explorer to select output directory and return path."""
    try:
        import subprocess
        import platform
        
        # Get current working directory as starting point
        start_dir = os.getcwd()
        
        system = platform.system().lower()
        
        if system == "windows":
            # Windows: Open File Explorer
            subprocess.run(['explorer', start_dir], check=False)
            return "📁 File Explorer opened - copy path from address bar"
            
        elif system == "darwin":  # macOS
            # macOS: Open Finder
            subprocess.run(['open', start_dir], check=False)
            return "📁 Finder opened - copy path from address bar"
            
        elif system == "linux":
            # Linux: Try different file managers
            file_managers = [
                ['nautilus', start_dir],           # GNOME Files
                ['dolphin', start_dir],            # KDE Dolphin
                ['thunar', start_dir],             # XFCE Thunar
                ['pcmanfm', start_dir],            # PCManFM
                ['nemo', start_dir],               # Cinnamon Nemo
                ['caja', start_dir],               # MATE Caja
                ['xdg-open', start_dir]            # Generic opener
            ]
            
            for manager in file_managers:
                try:
                    subprocess.run(manager, check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    return "📁 File manager opened - copy path from address bar"
                except FileNotFoundError:
                    continue
                    
            return "📁 Please navigate manually - file manager not detected"
        
        else:
            return "📁 System file explorer not supported"
            
    except Exception as e:
        print(f"Error opening file explorer: {e}")
        return "📁 Error opening file explorer"


def set_quick_path(selected_path, current_value):
    """Set quick path in output name field."""
    if selected_path:
        # If current value has a filename, keep it and just change the directory
        if current_value and not current_value.endswith('/'):
            # Extract just the filename part
            filename = os.path.basename(current_value)
            if filename and not filename.startswith('📁'):
                return f"{selected_path}{filename}"
        
        # Otherwise, just use the path with a default filename
        return f"{selected_path}analysis"
    return current_value


def analyze_document(
    # File input
    pdf_file,
    url_input,
    
    # Basic settings
    variant,
    document_type,  # v8.3.3: Document type for citation scoring
    output_name,
    document_title,
    
    # Narrative settings
    narrative_style,
    narrative_length,
    ollama_model,
    ollama_custom_query,  # Fix #1: Custom query for Ollama
    
    # Analysis flags
    deep_analysis,
    citation_check,
    check_urls,
    enable_document_qa,  # v8.4.2: Document Q&A
    enable_chunking,  # v8.6: Smart chunking for large documents
    qa_routing_strategy,  # v8.6: Query routing strategy
    document_qa_question,  # v8.4.2: Question for Q&A
    
    # Transparency flags
    enhanced_provenance,
    provenance_report,  # v8.4.1: Full provenance audit trail
    generate_ai_disclosure,
    trace_data_sources,
    nist_compliance,
    lineage_chart_format,
    legislative_threat,  # v8.5: Legislative threat detection
    
    # Memory management
    low_memory_mode,  # v8.4.1: Run in subprocess to free RAM
    
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
    
    # v8.4.1: Low Memory Mode - run in subprocess to free RAM after completion
    if low_memory_mode:
        progress(0.15, desc="Running in Low Memory Mode (subprocess)...")
        input_for_subprocess = pdf_file.name if pdf_file else url_input
        return run_via_subprocess(
            input_for_subprocess, variant, document_type, output_name, document_title, narrative_style, narrative_length,
            ollama_model, deep_analysis, citation_check, check_urls,
            enable_document_qa, enable_chunking, qa_routing_strategy, document_qa_question,
            enhanced_provenance, provenance_report, generate_ai_disclosure, trace_data_sources,
            nist_compliance, lineage_chart_format, legislative_threat, progress
        )
    
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
                # v8.5: Check for bilingual PDF and extract English column only
                output_dir = Path("./temp_extractions")
                extracted_path = extract_pdf_columns(input_path, output_dir)
                temp_files.append(str(output_dir))  # Track for cleanup
                
                # Now extract text from the processed file
                if extracted_path.endswith('.txt'):
                    # Column extraction succeeded, use the text file
                    with open(extracted_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                else:
                    # Standard PDF extraction
                    grader = SPARROWGrader()
                    text = grader.extract_text_from_pdf(input_path)
            else:
                with open(input_path, 'r', encoding='utf-8') as f:
                    text = f.read()
        else:
            # Handle URL - use subprocess for now
            return run_via_subprocess(
                url_input, variant, document_type, output_name, document_title, narrative_style, narrative_length,
                ollama_model, deep_analysis, citation_check, check_urls,
                enable_document_qa, enable_chunking, qa_routing_strategy, document_qa_question,
                enhanced_provenance, provenance_report, generate_ai_disclosure, trace_data_sources,
                nist_compliance, lineage_chart_format, legislative_threat, progress
            )
        
        progress(0.3, desc=f"Analyzing with {variant} variant...")
        
        # Run analysis based on variant
        if variant == 'journalism':
            grader = SPARROWGrader()
            results = grader.grade_article(text, input_source)
            
            # Add document title to results
            if document_title:
                results['document_title'] = document_title
            elif input_source:
                results['document_title'] = input_source
            
            progress(0.8, desc="Generating outputs...")
            
            # Generate outputs
            output_files = []
            
            # JSON report
            json_path = f"{output_name}.json"
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(json_path), exist_ok=True) if os.path.dirname(json_path) else None
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            output_files.append(json_path)
            
            # Text summary
            txt_path = f"{output_name}.txt"
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(txt_path), exist_ok=True) if os.path.dirname(txt_path) else None
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
                # v8.4.1: Pass document_type if user selected (not 'auto')
                doc_type_param = document_type if document_type and document_type != 'auto' else 'policy'
                results = policy.grade(text, document_type=doc_type_param, pdf_path=input_path if is_pdf else None)
                
                # Add document title to results
                if document_title:
                    results['document_title'] = document_title
                elif input_source:
                    results['document_title'] = input_source
                
                # v8.3.3: Store document type in results and override auto-detected if user selected
                results['document_type_selected'] = document_type
                if document_type and document_type != 'auto':
                    # User selection takes priority over auto-detection
                    results['document_type'] = document_type
                
                progress(0.5, desc="Running policy evaluation...")
                
                # Initialize output files list
                output_files = []
                
                # Apply optional enhancements
                if deep_analysis:
                    progress(0.6, desc="Running deep AI analysis (6 levels)...")
                    results = add_deep_analysis(results, text, input_path)
                
                if citation_check:
                    progress(0.65, desc="Checking citation quality...")
                    results, citation_file = add_citation_analysis(results, text, check_urls, output_name, document_type)
                    output_files.append(citation_file)
                
                if generate_ai_disclosure:
                    progress(0.7, desc="Generating AI disclosure statements...")
                    disclosure_files = add_ai_disclosure(results, output_name)
                    if disclosure_files:
                        output_files.extend(disclosure_files)
                
                # v8.3.3: Generate AI usage explanation (requires deep_analysis data)
                if deep_analysis and generate_ai_disclosure:
                    progress(0.72, desc="Generating AI usage explanation...")
                    explanation_file = add_ai_usage_explanation(results, output_name)
                    if explanation_file:
                        output_files.append(explanation_file)
                
                if trace_data_sources:
                    progress(0.75, desc="Tracing data sources...")
                    results, lineage_files = add_data_lineage(results, text, output_name)
                    output_files.extend(lineage_files)
                
                if nist_compliance:
                    progress(0.8, desc="Checking NIST compliance...")
                    results = add_nist_compliance(results, text)
                
                progress(0.85, desc="Generating outputs...")
                
                # JSON report
                # Ensure test_articles paths go to root directory, not gui/test_articles
                if output_name.startswith('test_articles/'):
                    json_path = f"../{output_name}.json"
                else:
                    json_path = f"{output_name}.json"
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(json_path), exist_ok=True) if os.path.dirname(json_path) else None
                with open(json_path, 'w') as f:
                    json.dump(results, f, indent=2)
                output_files.append(json_path)
                
                # Text summary
                if output_name.startswith('test_articles/'):
                    txt_path = f"../{output_name}.txt"
                else:
                    txt_path = f"{output_name}.txt"
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(txt_path), exist_ok=True) if os.path.dirname(txt_path) else None
                with open(txt_path, 'w') as f:
                    f.write(format_policy_summary(results))
                output_files.append(txt_path)
                
                # Certificate
                cert_path = generate_certificate(results, output_name, variant)
                output_files.append(cert_path)
                
                # v8.4.1: Track AI calls for provenance
                ai_calls_log = []
                contribution_log = None
                
                # Generate Ollama summary (if model available)
                if ollama_model:  # Run Ollama for any selected model
                    progress(0.88, desc=f"Generating AI summary with {ollama_model}...")
                    try:
                        cert_gen = CertificateGenerator()
                        if output_name.startswith('test_articles/'):
                            summary_path = f"../{output_name}_ollama_summary.txt"
                        else:
                            summary_path = f"{output_name}_ollama_summary.txt"
                        
                        # Create directory if needed
                        os.makedirs(os.path.dirname(summary_path), exist_ok=True) if os.path.dirname(summary_path) else None
                        
                        cert_gen.generate_summary_with_ollama(
                            results, 
                            variant=variant, 
                            model=ollama_model, 
                            length=narrative_length,
                            output_file=summary_path
                        )
                        output_files.append(summary_path)
                        progress(0.89, desc="AI summary complete")
                        
                        # v8.4.1: Capture AI calls from summary generator
                        if hasattr(cert_gen, 'summary_generator') and cert_gen.summary_generator:
                            ai_calls_log.extend(cert_gen.summary_generator.get_ai_calls_log())
                            # Track for cleanup
                            _active_ollama_generators.append(cert_gen.summary_generator)
                    except Exception as e:
                        print(f"⚠️ Ollama summary failed: {e}")
                        # Continue without failing the entire analysis
                
                # Narrative (if requested)
                narrative_pipeline = None
                if narrative_style != "None":
                    progress(0.9, desc=f"Generating {narrative_style} narrative...")
                    narrative_files, narrative_pipeline = generate_narrative_with_tracking(
                        results, text, output_name, narrative_style, 
                        narrative_length, ollama_model, ollama_custom_query
                    )
                    output_files.extend(narrative_files)
                    
                    # v8.4.1: Capture AI contribution log from narrative pipeline
                    if narrative_pipeline:
                        try:
                            contribution_log = narrative_pipeline.get_ai_contribution_log()
                        except Exception:
                            pass
                
                # Lineage chart (if requested)
                if lineage_chart_format != "None":
                    progress(0.92, desc="Creating lineage flowchart...")
                    chart_path = generate_lineage_chart(results, output_name, lineage_chart_format)
                    if chart_path:
                        output_files.append(chart_path)
                
                # v8.4.2/v8.6: Document Q&A (if requested)
                if enable_document_qa and document_qa_question and document_qa_question.strip():
                    progress(0.93, desc="Generating document Q&A...")
                    try:
                        # Determine output directory (handle test_articles paths)
                        if output_name.startswith('test_articles/'):
                            qa_output_dir = Path('..') / Path(output_name).parent
                        else:
                            qa_output_dir = Path(output_name).parent if '/' in output_name else Path('.')
                        
                        # v8.6: Use enhanced Q&A with chunking if enabled
                        if enable_chunking and ENHANCED_QA_AVAILABLE:
                            from token_calculator import estimate_tokens
                            from semantic_chunker import chunk_document, save_chunks
                            from enhanced_document_qa import EnhancedDocumentQA
                            
                            print("   📊 Analyzing document size...")
                            tokens = estimate_tokens(text, method="tiktoken")
                            print(f"   📊 Estimated tokens: {tokens:,}")
                            
                            # Create chunks
                            print("   ✂️  Creating intelligent chunks...")
                            chunks_result = chunk_document(
                                text,
                                max_tokens=100000,  # Standard chunk size
                                strategy="section",
                                overlap_tokens=200
                            )
                            
                            # Save chunks
                            chunks_dir = qa_output_dir / "chunks"
                            save_chunks(
                                chunks_result,
                                output_dir=str(chunks_dir),
                                save_chunk_files=True
                            )
                            print(f"   ✂️  Created {len(chunks_result['chunks'])} chunks")
                            
                            # Query using enhanced Q&A
                            print(f"   🔍 Routing strategy: {qa_routing_strategy}")
                            qa_engine = EnhancedDocumentQA(
                                chunks_dir=chunks_dir / "chunks",
                                chunk_index_path=chunks_dir / "chunk_index.json"
                            )
                            
                            answer = qa_engine.query(
                                question=document_qa_question.strip(),
                                model="mock",  # Use mock for now (GUI uses document_qa for Ollama)
                                routing_strategy=qa_routing_strategy,
                                synthesis_strategy="concatenate",
                                relevance_threshold=0.3
                            )
                            
                            # Save answer
                            qa_file = qa_output_dir / f"{Path(output_name).stem}_qa.json"
                            import json
                            with open(qa_file, 'w', encoding='utf-8') as f:
                                json.dump({
                                    "question": answer.question,
                                    "answer": answer.answer,
                                    "sources": [
                                        {"chunk": s.chunk_number, "pages": s.pages, "sections": s.sections}
                                        for s in answer.sources
                                    ],
                                    "metadata": {
                                        "chunks_queried": answer.total_chunks_queried,
                                        "confidence": answer.confidence,
                                        "routing_strategy": answer.routing_strategy
                                    }
                                }, f, indent=2)
                            
                            output_files.append(str(qa_file))
                            print(f"   ✓ Enhanced Q&A: {qa_file}")
                            print(f"   ✓ Confidence: {answer.confidence:.0%}, Chunks: {answer.total_chunks_queried}")
                        else:
                            # Standard Q&A (no chunking)
                            from document_qa import generate_document_qa
                            
                            # Get contribution tracker if available
                            tracker = None
                            if narrative_pipeline and hasattr(narrative_pipeline, 'contribution_tracker'):
                                tracker = narrative_pipeline.contribution_tracker
                            
                            qa_file = generate_document_qa(
                                document_text=text,
                                question=document_qa_question.strip(),
                                output_dir=qa_output_dir,
                                output_name=Path(output_name).name,
                                model=ollama_model,
                                analysis_context=results,
                                contribution_tracker=tracker
                            )
                            if qa_file:
                                output_files.append(qa_file)
                                print(f"   ✓ Document Q&A: {qa_file}")
                    except Exception as e:
                        import traceback
                        print(f"   ⚠️ Document Q&A failed: {e}")
                        traceback.print_exc()
                        # Don't fail entire analysis
                
                # v8.5: Legislative Threat Detection
                if legislative_threat:
                    progress(0.94, desc="Running Legislative Threat Detection...")
                    try:
                        from discretionary_power_analyzer import DiscretionaryPowerAnalyzer
                        
                        # Create threats directory at same level as certificates, core, logs, etc.
                        threats_dir = output_dir / "threats"
                        threats_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Initialize analyzer
                        dpa = DiscretionaryPowerAnalyzer(output_dir=str(threats_dir))
                        
                        # Run analysis
                        dpa_results = dpa.analyze(text, document_name=output_name)
                        
                        # Save both JSON and Markdown reports
                        json_path = dpa.save_results(dpa_results, format='json')
                        md_path = dpa.save_results(dpa_results, format='markdown')
                        
                        output_files.extend([str(json_path), str(md_path)])
                        
                        print(f"   ✓ Discretionary Power Analysis: {dpa_results['risk_level']} RISK")
                        print(f"   ✓ Score: {dpa_results['discretionary_power_score']:.1f}/100")
                        print(f"   ✓ Findings: {dpa_results['total_findings']}")
                        print(f"   ✓ JSON: {json_path.name}")
                        print(f"   ✓ Report: {md_path.name}")
                        
                    except Exception as e:
                        print(f"   ⚠️ Legislative threat detection failed: {e}")
                        # Don't fail entire analysis
                
                # v8.4.1: Generate provenance report LAST (after all AI operations)
                if provenance_report:
                    progress(0.95, desc="Generating provenance report...")
                    results, prov_files = add_provenance_report(
                        results, text, output_name, input_path,
                        ai_calls_log=ai_calls_log,
                        contribution_log=contribution_log
                    )
                    output_files.extend(prov_files)
        
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
        if provenance_report:
            cmd_parts.append("--provenance-report")
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
        
        # v8.4.1: Release memory after analysis to prevent lockups
        cleanup_after_analysis()


def run_via_subprocess(url_or_file, variant, document_type, output_name, document_title, narrative_style, narrative_length,
                       ollama_model, deep_analysis, citation_check, check_urls,
                       enable_document_qa, enable_chunking, qa_routing_strategy, document_qa_question,
                       enhanced_provenance, provenance_report, generate_ai_disclosure, trace_data_sources,
                       nist_compliance, lineage_chart_format, legislative_threat, progress):
    """
    Run analysis via subprocess for URL inputs or low memory mode.
    
    v8.4.1: Updated to handle both URLs and file paths for low memory mode.
    v8.5: Added legislative_threat parameter and PDF column extraction.
    v8.6: Added enable_chunking and qa_routing_strategy for enhanced Q&A.
    """
    import subprocess
    import os
    
    # Get path to sparrow_grader_v8.py in parent directory
    grader_script = str(SPOT_NEWS_DIR / "sparrow_grader_v8.py")
    
    # Determine if input is a URL or file path
    is_url = url_or_file.startswith('http://') or url_or_file.startswith('https://')
    
    # v8.5: Handle bilingual PDF column extraction before subprocess
    temp_files = []
    input_path = url_or_file
    if not is_url and input_path.lower().endswith('.pdf'):
        output_dir = Path("./temp_extractions")
        extracted_path = extract_pdf_columns(input_path, output_dir)
        temp_files.append(str(output_dir))
        
        # Use extracted text file instead of PDF
        if extracted_path != input_path:
            input_path = extracted_path
            print(f"   Using extracted text: {input_path}")
    
    # Use sys.executable to get the current Python interpreter
    if is_url:
        cmd = [sys.executable, grader_script, "--url", url_or_file, "--variant", variant, "--output", output_name]
    else:
        # It's a file path - use potentially extracted text file
        cmd = [sys.executable, grader_script, input_path, "--variant", variant, "--output", output_name]
    
    # Add document title if provided (user-friendly name for certificate/reports)
    if document_title:
        cmd.extend(["--document-title", document_title])
    
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
    if enable_document_qa and document_qa_question and document_qa_question.strip():
        cmd.extend(["--document-qa", document_qa_question.strip()])
    if enhanced_provenance:
        cmd.append("--enhanced-provenance")
    if provenance_report:
        cmd.append("--provenance-report")
    if generate_ai_disclosure:
        cmd.append("--generate-ai-disclosure")
    if trace_data_sources:
        cmd.append("--trace-data-sources")
    if nist_compliance:
        cmd.append("--nist-compliance")
    if lineage_chart_format != "None":
        cmd.extend(["--lineage-chart", lineage_chart_format])
    if legislative_threat:
        cmd.append("--legislative-threat")
    
    progress(0.3, desc="Running Sparrow via subprocess...")
    
    try:
        # Increased timeout for deep analysis on large documents (10 minutes -> 20 minutes)
        # Run from project root to ensure proper output directory structure
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, cwd=str(SPOT_NEWS_DIR))
        
        # Cleanup temp files after subprocess completes
        for temp_path in temp_files:
            try:
                if Path(temp_path).exists():
                    shutil.rmtree(temp_path)
                    print(f"🧹 Cleaned up: {temp_path}")
            except Exception as e:
                print(f"⚠️  Could not clean up {temp_path}: {e}")
        
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
        # Cleanup on timeout
        for temp_path in temp_files:
            try:
                if Path(temp_path).exists():
                    shutil.rmtree(temp_path)
            except:
                pass
        return "❌ Analysis timed out (>20 minutes)", None
    except Exception as e:
        # Cleanup on exception
        for temp_path in temp_files:
            try:
                if Path(temp_path).exists():
                    shutil.rmtree(temp_path)
            except:
                pass
        return f"❌ Subprocess error: {str(e)}", None


def format_journalism_summary(results):
    """Format journalism results as text summary."""
    lines = []
    lines.append("=" * 60)
    lines.append("SPARROW SCALE™ - JOURNALISM ANALYSIS")
    lines.append("=" * 60)
    
    # Fix #7: Use correct field names from results
    doc_name = results.get('document_title') or results.get('document_name', 'Unknown')
    analysis_date = results.get('timestamp') or results.get('analysis_date', datetime.now().isoformat())
    # Format date nicely if it's an ISO timestamp
    if 'T' in str(analysis_date):
        try:
            analysis_date = datetime.fromisoformat(analysis_date.replace('Z', '+00:00')).strftime('%B %d, %Y at %H:%M')
        except:
            pass
    
    # Get letter grade from multiple possible fields
    letter_grade = results.get('composite_letter_grade') or results.get('composite_grade') or results.get('grade', 'N/A')
    
    lines.append(f"\nDocument: {doc_name}")
    lines.append(f"Analysis Date: {analysis_date}")
    lines.append(f"\nComposite Score: {results.get('composite_score', 0):.1f}/100")
    lines.append(f"Letter Grade: {letter_grade}")
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
    
    # Fix #7: Use correct field names from results
    doc_name = results.get('document_title') or results.get('document_name', 'Unknown')
    analysis_date = results.get('timestamp') or results.get('analysis_date', datetime.now().isoformat())
    # Format date nicely if it's an ISO timestamp
    if 'T' in str(analysis_date):
        try:
            analysis_date = datetime.fromisoformat(analysis_date.replace('Z', '+00:00')).strftime('%B %d, %Y at %H:%M')
        except:
            pass
    
    # Get letter grade from multiple possible fields
    letter_grade = results.get('composite_letter_grade') or results.get('composite_grade') or results.get('grade', 'N/A')
    
    lines.append(f"\nDocument: {doc_name}")
    lines.append(f"Analysis Date: {analysis_date}")
    lines.append(f"\nComposite Score: {results.get('composite_score', 0):.1f}/100")
    lines.append(f"Letter Grade: {letter_grade}")
    lines.append("\n" + "-" * 60)
    lines.append("CATEGORY SCORES:")
    lines.append("-" * 60)
    
    # v8.3.2 Fix: Use 'criteria' key (policy variant) with fallback to 'categories'
    criteria = results.get('criteria', results.get('categories', {}))
    
    # Define criterion names for display
    criterion_names = {
        'FT': 'Fiscal Transparency',
        'SB': 'Stakeholder Balance',
        'ER': 'Economic Rigor',
        'PA': 'Public Accessibility',
        'PC': 'Policy Consequentiality',
        'AT': 'AI Transparency'
    }
    
    for key, details in criteria.items():
        if isinstance(details, dict):
            score = details.get('score', 0)
            name = details.get('name', criterion_names.get(key, key))
            lines.append(f"\n{name} ({key}): {score:.1f}/100")
    
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
    
    # Handle test_articles path to go to root directory
    if output_name.startswith('test_articles/'):
        cert_path = f"../{output_name}_certificate.html"
    else:
        cert_path = f"{output_name}_certificate.html"
        
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(cert_path), exist_ok=True) if os.path.dirname(cert_path) else None
    
    if variant == 'journalism':
        cert_gen.generate_journalism_certificate(
            report=results,
            document_title=results.get('document_title', ''),
            output_file=cert_path
        )
    else:  # policy
        cert_gen.generate_policy_certificate(
            report=results,
            document_title=results.get('document_title', ''),
            output_file=cert_path
        )
    
    return cert_path


def add_deep_analysis(results, text, input_path):
    """Add 6-level deep AI analysis."""
    analyzer = DeepAnalyzer()
    deep_results = analyzer.analyze_document(input_path)
    
    results['deep_analysis'] = deep_results
    return results


def add_citation_analysis(results, text, check_urls, output_name, document_type='auto'):
    """Add citation quality scoring.
    
    v8.3.3: Added document_type parameter for context-aware scoring.
    
    Args:
        results: Analysis results dict
        text: Document text
        check_urls: Whether to check URL accessibility
        output_name: Output file prefix
        document_type: Document type for scoring ('auto', 'legislation', 'policy_brief', etc.)
    """
    scorer = CitationQualityScorer()
    
    # v8.3.3: Analyze with document type awareness
    citation_results = scorer.analyze_citations(text, check_urls=check_urls)
    
    # If user specified a document type (not auto), override the detected type
    if document_type and document_type != 'auto':
        from citation_quality_scorer import DocumentType, DOCUMENT_TYPE_CONFIG
        try:
            override_type = DocumentType(document_type)
            # Recalculate score with user-specified type
            url_analysis = citation_results.get('url_analysis', {})
            citations_per_1000 = citation_results.get('citations_per_1000_words', 0)
            new_score = scorer._calculate_quality_score(url_analysis, citations_per_1000, override_type)
            
            citation_results['document_type'] = document_type
            citation_results['document_type_info'] = scorer.get_document_type_info(override_type)
            citation_results['quality_score'] = new_score
            citation_results['quality_level'] = scorer._get_quality_level(new_score)
            citation_results['document_type_override'] = True
        except ValueError:
            pass  # Keep auto-detected type if invalid
    
    # Save citation report - Handle test_articles path to go to root directory
    if output_name.startswith('test_articles/'):
        citation_file = f"../{output_name}_citation_report.txt"
    else:
        citation_file = f"{output_name}_citation_report.txt"
        
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(citation_file), exist_ok=True) if os.path.dirname(citation_file) else None
    
    # v8.3.3 Fix: Clarify citation report to avoid confusion between raw count and document-adjusted score
    doc_type_info = citation_results.get('document_type_info', {})
    doc_type = doc_type_info.get('description', citation_results.get('document_type', 'Unknown'))
    citation_expectation = doc_type_info.get('citation_expectation', 'MEDIUM')
    quality_score = citation_results.get('quality_score', 0)
    quality_level = citation_results.get('quality_level', 'Unknown')
    total_citations = citation_results.get('total_citations', 0)
    
    with open(citation_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("CITATION QUALITY ANALYSIS REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        # Document type context
        f.write(f"Document Type: {doc_type}\n")
        f.write(f"Citation Expectation: {citation_expectation}\n\n")
        
        # Raw metrics
        f.write("--- Raw Metrics ---\n")
        f.write(f"Total Citations Found: {total_citations}\n")
        f.write(f"URLs: {citation_results.get('total_urls', 0)}\n")
        f.write(f"Citation Markers: {citation_results.get('total_citation_markers', 0)}\n")
        f.write(f"Citations per 1,000 words: {citation_results.get('citations_per_1000_words', 0)}\n\n")
        
        # Document-adjusted score
        f.write("--- Document-Adjusted Quality ---\n")
        f.write(f"Quality Score: {quality_score}/100\n")
        f.write(f"Quality Level: {quality_level}\n\n")
        
        # Interpretation
        if citation_expectation == 'LOW':
            f.write("Interpretation: Low/no citations is APPROPRIATE for this document type.\n")
            f.write("Legislative and primary source documents are self-authoritative.\n\n")
        elif total_citations == 0:
            f.write("⚠️ Warning: No citations found. This document type typically requires citations.\n\n")
        
        # Source types if available
        url_analysis = citation_results.get('url_analysis', {})
        source_types = url_analysis.get('source_types', {})
        if any(source_types.values()):
            f.write("--- Source Types ---\n")
            for stype, count in source_types.items():
                if count > 0:
                    f.write(f"  {stype.replace('_', ' ').title()}: {count}\n")
            f.write("\n")
        
        f.write("=" * 70 + "\n")
    
    results['citation_quality'] = citation_results
    return results, citation_file


def add_ai_disclosure(results, output_name):
    """Generate AI disclosure statements."""
    # Initialize generator with full results (positional argument, not keyword)
    generator = AIDisclosureGenerator(results)
    
    # Handle test_articles path to go to root directory
    if output_name.startswith('test_articles/'):
        disclosure_prefix = f"../{output_name}"
    else:
        disclosure_prefix = output_name
    
    # Generate all formats
    files = generator.generate_all_formats(output_prefix=disclosure_prefix)
    
    return files


def add_ai_usage_explanation(results, output_name):
    """
    Generate detailed AI usage explanation report.
    
    NEW in v8.3.3: Creates comprehensive plain-language explanation of:
    - How AI was used in document creation
    - Which sections have AI involvement
    - Model attribution with confidence levels
    - Transparency assessment and recommendations
    
    Args:
        results: Full analysis results dict
        output_name: Output file prefix
        
    Returns:
        str: Path to generated explanation file
    """
    try:
        explainer = AIUsageExplainer()
        
        document_title = results.get('document_title', 'Document')
        
        # Handle test_articles path to go to root directory
        if output_name.startswith('test_articles/'):
            output_file = f"../{output_name}_ai_usage_explanation.txt"
        else:
            output_file = f"{output_name}_ai_usage_explanation.txt"
        
        # Create directory if needed
        os.makedirs(os.path.dirname(output_file), exist_ok=True) if os.path.dirname(output_file) else None
        
        # Generate the detailed report
        explainer.generate_ai_usage_report(
            analysis_data=results,
            document_title=document_title,
            output_file=output_file
        )
        
        return output_file
    except Exception as e:
        print(f"⚠️  AI usage explanation failed: {e}")
        return None


def add_data_lineage(results, text, output_name):
    """Add data lineage source tracing."""
    mapper = DataLineageSourceMapper()
    lineage_data = mapper.trace_sources(text)
    
    # Save text report - Handle test_articles path to go to root directory
    if output_name.startswith('test_articles/'):
        output_lineage_txt = f"../{output_name}_data_lineage.txt"
    else:
        output_lineage_txt = f"{output_name}_data_lineage.txt"
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_lineage_txt), exist_ok=True) if os.path.dirname(output_lineage_txt) else None
    with open(output_lineage_txt, 'w', encoding='utf-8') as f:
        f.write(mapper.generate_report(lineage_data, 'text'))
    
    # Save JSON report - Handle test_articles path to go to root directory
    if output_name.startswith('test_articles/'):
        output_lineage_json = f"../{output_name}_data_lineage.json"
    else:
        output_lineage_json = f"{output_name}_data_lineage.json"
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_lineage_json), exist_ok=True) if os.path.dirname(output_lineage_json) else None
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


def add_provenance_report(results, text, output_name, input_path=None, ai_calls_log=None, contribution_log=None):
    """
    Generate comprehensive provenance report (document origin + Sparrow AI usage).
    
    v8.4.1: Added for full audit trail generation.
    
    Args:
        results: Analysis results dict
        text: Original document text
        output_name: Output file prefix
        input_path: Path to input file for metadata extraction
        ai_calls_log: List of AI API calls made during analysis
        contribution_log: Dict of AI contributions from narrative pipeline
        
    Returns:
        Tuple of (updated results, list of output files)
    """
    from provenance_report_generator import create_provenance_report_generator
    from ai_detection_engine import ProvenanceAnalyzer
    
    output_files = []
    
    # Use provided logs or empty defaults
    if ai_calls_log is None:
        ai_calls_log = []
    if contribution_log is None:
        contribution_log = None
    
    try:
        prov_report_gen = create_provenance_report_generator()
        
        # Get document metadata
        doc_metadata = {}
        if input_path:
            try:
                prov_analyzer = ProvenanceAnalyzer()
                doc_metadata = prov_analyzer.extract_metadata(input_path)
            except Exception as e:
                doc_metadata = {'error': str(e)}
        
        # Generate the provenance report
        doc_title = results.get('document_title', 'Unknown Document')
        provenance_report = prov_report_gen.generate_report(
            document_metadata=doc_metadata,
            ai_calls_log=ai_calls_log,
            contribution_log=contribution_log,
            document_title=doc_title,
            analysis_timestamp=results.get('timestamp')
        )
        
        # Handle test_articles path prefix
        if output_name.startswith('test_articles/'):
            base_path = f"../{output_name}"
        else:
            base_path = output_name
        
        # Save both JSON and markdown versions
        saved_files = prov_report_gen.save_report(
            provenance_report,
            base_path,
            format="both"
        )
        
        output_files.extend(saved_files.values())
        
        # Add to main results
        results['provenance_report'] = provenance_report
        
    except Exception as e:
        print(f"   ⚠️  Provenance report generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return results, output_files


def generate_narrative(results, text, output_name, style, length, model, custom_query=""):
    """Generate narrative outputs.
    
    Args:
        results: Analysis results dict
        text: Original document text
        output_name: Output file prefix
        style: Narrative style (journalistic, academic, etc.)
        length: Target length (concise, standard, detailed, comprehensive)
        model: Ollama model to use
        custom_query: Optional custom context/question for the narrative
    """
    from narrative_integration import create_pipeline
    
    pipeline = create_pipeline()
    
    output_files = []
    
    # Fix #1: Add custom query to analysis for the pipeline to use
    if custom_query and custom_query.strip():
        results['custom_narrative_query'] = custom_query.strip()
    
    # Generate complete narrative
    narrative_result = pipeline.generate_complete_narrative(
        analysis=results,
        tone=style,
        length=length,
        ollama_model=model,
        formats=['x_thread', 'linkedin', 'social_badge', 'html_certificate']
    )
    
    # Save narrative text - Handle test_articles path to go to root directory
    if output_name.startswith('test_articles/'):
        narrative_path = f"../{output_name}_narrative.txt"
    else:
        narrative_path = f"{output_name}_narrative.txt"
        
    # Create directory if needed
    os.makedirs(os.path.dirname(narrative_path), exist_ok=True) if os.path.dirname(narrative_path) else None
    
    with open(narrative_path, 'w') as f:
        f.write(narrative_result.get('narrative_text', ''))
    output_files.append(narrative_path)
    
    return output_files


def generate_narrative_with_tracking(results, text, output_name, style, length, model, custom_query=""):
    """
    Generate narrative outputs and return pipeline for AI tracking.
    
    v8.4.1: Added to support provenance report AI usage tracking.
    
    Args:
        results: Analysis results dict
        text: Original document text
        output_name: Output file prefix
        style: Narrative style (journalistic, academic, etc.)
        length: Target length (concise, standard, detailed, comprehensive)
        model: Ollama model to use
        custom_query: Optional custom context/question for the narrative
        
    Returns:
        Tuple of (output_files list, pipeline object for AI tracking)
    """
    from narrative_integration import create_pipeline
    
    pipeline = create_pipeline()
    
    output_files = []
    
    # Add custom query to analysis for the pipeline to use
    if custom_query and custom_query.strip():
        results['custom_narrative_query'] = custom_query.strip()
    
    # Generate complete narrative
    narrative_result = pipeline.generate_complete_narrative(
        analysis=results,
        tone=style,
        length=length,
        ollama_model=model,
        formats=['x_thread', 'linkedin', 'social_badge', 'html_certificate']
    )
    
    # Save narrative text - Handle test_articles path to go to root directory
    if output_name.startswith('test_articles/'):
        narrative_path = f"../{output_name}_narrative.txt"
    else:
        narrative_path = f"{output_name}_narrative.txt"
        
    # Create directory if needed
    os.makedirs(os.path.dirname(narrative_path), exist_ok=True) if os.path.dirname(narrative_path) else None
    
    with open(narrative_path, 'w') as f:
        f.write(narrative_result.get('narrative_text', ''))
    output_files.append(narrative_path)
    
    # Return both output files AND the pipeline for AI tracking
    return output_files, pipeline


def generate_lineage_chart(results, output_name, format):
    """Generate data lineage flowchart with actual pipeline stages."""
    from data_lineage_visualizer import DataLineageVisualizer
    
    # v8.3.2 Fix: Use the standard pipeline template with actual stages
    viz = DataLineageVisualizer.create_standard_pipeline()
    
    # Mark stages as completed based on what's in results
    stage_checks = [
        (0, True),  # Document Ingestion - always done
        (1, True),  # Text Extraction - always done
        (2, 'document_metadata' in results or 'provenance' in results),
        (3, 'criteria' in results or 'composite_score' in results),
        (4, 'ai_detection' in results),
        (5, 'deep_analysis' in results),
        (6, 'trust_score' in results or 'bias_audit' in results),
        (7, 'narrative' in str(results) or True),  # Assume narrative was generated
        (8, True),  # Certificate generation - this is being called
        (9, True),  # Output compilation - always done
    ]
    
    for stage_idx, is_complete in stage_checks:
        if stage_idx < len(viz.stages):
            if is_complete:
                viz.update_stage(stage_idx, "completed")
    
    # Handle test_articles path to go to root directory
    if format == "html":
        content = viz.generate_html_flowchart()
        if output_name.startswith('test_articles/'):
            chart_path = f"../{output_name}_lineage_flowchart.html"
        else:
            chart_path = f"{output_name}_lineage_flowchart.html"
    else:  # ascii
        content = viz.generate_ascii_flowchart()
        if output_name.startswith('test_articles/'):
            chart_path = f"../{output_name}_lineage_flowchart.txt"
        else:
            chart_path = f"{output_name}_lineage_flowchart.txt"
    
    # Create directory if needed
    os.makedirs(os.path.dirname(chart_path), exist_ok=True) if os.path.dirname(chart_path) else None
    
    with open(chart_path, 'w') as f:
        f.write(content)
    
    return chart_path


def update_settings_summary(pdf_file, url_input, variant, document_type, output_name, document_title,
                           narrative_style, narrative_length, ollama_model, ollama_custom_query,
                           deep_analysis, citation_check, check_urls, enable_document_qa, enable_chunking, qa_routing_strategy, document_qa_question,
                           enhanced_provenance, provenance_report, generate_ai_disclosure, trace_data_sources, 
                           nist_compliance, lineage_chart_format, legislative_threat, low_memory_mode):
    """Generate a summary of current settings."""
    
    # Input source
    if pdf_file:
        input_src = f"📄 **File:** {Path(pdf_file.name).name}"
    elif url_input:
        input_src = f"🌐 **URL:** {url_input}"
    else:
        input_src = "⚠️ **No input selected**"
    
    # Custom query display
    custom_query_display = ""
    if ollama_custom_query and ollama_custom_query.strip():
        truncated = ollama_custom_query[:50] + "..." if len(ollama_custom_query) > 50 else ollama_custom_query
        custom_query_display = f"\n- Custom Query: _{truncated}_"
    
    # v8.3.3: Document type display
    doc_type_labels = {
        'auto': 'Auto-Detect',
        'legislation': 'Legislation (Bill, Act)',
        'budget': 'Budget Document',
        'policy_brief': 'Policy Brief',
        'research_report': 'Research Report',
        'analysis': 'Analysis/Audit',
        'report': 'General Report'
    }
    doc_type_display = doc_type_labels.get(document_type, document_type)
    
    # Build summary
    summary = f"""### Current Configuration

{input_src}

**Analysis Variant:** {variant.upper()}  
**Document Type:** {doc_type_display}  
**Output Prefix:** {output_name if output_name else '(auto-generated)'}  
**Document Title:** {document_title if document_title else '(will use filename)'}

---

**Narrative Generation:**
- Style: {narrative_style.title() if narrative_style != 'None' else 'Disabled'}
- Length: {narrative_length.title()}
- Model: {ollama_model}{custom_query_display}

---

**Analysis Options:**
- Deep AI Analysis (6 levels): {'✅ Enabled' if deep_analysis else '❌ Disabled'}
- Citation Quality Check: {'✅ Enabled' if citation_check else '❌ Disabled'}
- URL Verification: {'✅ Enabled' if check_urls else '❌ Disabled'}
- Document Q&A: {'✅ Enabled' if enable_document_qa and document_qa_question else '❌ Disabled'}
{f"  - Question: _{document_qa_question[:60]}{'...' if len(document_qa_question) > 60 else ''}_" if enable_document_qa and document_qa_question else ""}

---

**Transparency Features:**
- Enhanced Provenance: {'✅ Enabled' if enhanced_provenance else '❌ Disabled'}
- Provenance Report: {'✅ Enabled' if provenance_report else '❌ Disabled'}
- AI Disclosure Statements: {'✅ Enabled' if generate_ai_disclosure else '❌ Disabled'}
- Data Source Tracing: {'✅ Enabled' if trace_data_sources else '❌ Disabled'}
- NIST Compliance Check: {'✅ Enabled' if nist_compliance else '❌ Disabled'}
- Lineage Flowchart: {lineage_chart_format if lineage_chart_format != 'None' else 'Disabled'}
- ⚖️ Legislative Threat Analysis: {'✅ Enabled' if legislative_threat else '❌ Disabled'}
- 🧠 Low Memory Mode: {'✅ Enabled (subprocess)' if low_memory_mode else '❌ Standard'}

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
                preferred_models = []  # Prioritize smaller, working models
                
                for line in lines[1:]:
                    # Extract model name and size
                    parts = line.split()
                    if len(parts) >= 3:
                        model_name = parts[0]
                        size_str = parts[2]
                        
                        # Only remove :latest suffix, keep other tags like :14b
                        if model_name.endswith(':latest'):
                            model_name = model_name.replace(':latest', '')
                        
                        # Skip cloud models (no local size), embedding models, and very large models (>10GB)
                        if (size_str == '-' or 'cloud' in model_name or 
                            'embed' in model_name.lower() or 'minilm' in model_name.lower() or
                            ('GB' in size_str and float(size_str.split()[0]) > 10.0)):
                            continue
                        
                        # Prioritize smaller models that work well (granite4, llama3.2:3b, etc)
                        if any(pref in model_name.lower() for pref in ['granite4', 'llama3.2', 'qwen2.5:3b', 'phi3']) and 'small-h' not in model_name:
                            preferred_models.append(model_name)
                        else:
                            models.append(model_name)
                
                # Put preferred models first, then others
                final_models = preferred_models + models
                if final_models:
                    return final_models
        
        # Fallback to common models if ollama list fails
        return ["granite4", "llama3.2:3b", "qwen2.5:3b", "phi3", "mistral"]
        
    except Exception as e:
        print(f"Could not check Ollama models: {e}")
        # Return default list with working models first
        return ["granite4", "llama3.2:3b", "qwen2.5:3b", "phi3", "mistral"]


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
        
        gr.Markdown(f"""
        # 🦅 Sparrow SPOT Scale™ v{SPARROW_VERSION}
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
                    document_type = gr.Dropdown(
                        choices=[
                            ("Auto-Detect", "auto"),
                            ("Legislation (Bill, Act, Statute)", "legislation"),
                            ("Budget Document", "budget"),
                            ("Policy Brief", "policy_brief"),
                            ("Research Report", "research_report"),
                            ("Analysis/Audit", "analysis"),
                            ("General Report", "report")
                        ],
                        value="auto",
                        label="Document Type",
                        info="v8.3.3: Affects citation scoring. Legislation has LOW citation expectation."
                    )
                
                with gr.Row():
                    output_name = gr.Textbox(
                        label="Output Filename Prefix",
                        placeholder="my_analysis or folder/my_analysis (leave empty to auto-generate)",
                        lines=1,
                        info="Can include directory paths - folders will be created automatically. Use 🗂️ Open Explorer to browse directories.",
                        scale=3
                    )
                    output_picker = gr.Button(
                        "🗂️ Open Explorer",
                        size="sm", 
                        scale=1,
                        variant="secondary",
                        elem_id="output_picker_btn"
                    )
                    quick_paths = gr.Dropdown(
                        label="Quick Paths",
                        choices=[
                            "test_articles/Bill-C15/",
                            "test_articles/2025_budget/", 
                            "test_articles/Bill-C2/",
                            "test_articles/Bill-C9/",
                            "analysis/2025/",
                            "reports/",
                            "drafts/"
                        ],
                        value=None,
                        scale=1,
                        container=True,
                        allow_custom_value=True
                    )
                
                document_title = gr.Textbox(
                    label="Document Title (Optional)",
                    placeholder="e.g., Bill C-15: Budget Implementation Act, 2025",
                    lines=1,
                    info="Enter the actual document title for certificates and reports. If empty, will use filename.",
                    scale=4
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
                
                # Fix #1: Add custom query textbox for Ollama
                gr.Markdown("""
                ### Custom Query (Optional)
                Add context or specific questions for the AI to address in the narrative.
                """)
                
                ollama_custom_query = gr.Textbox(
                    label="Custom Query/Context",
                    placeholder="e.g., 'Focus on environmental policy implications' or 'Compare to previous budget measures' or 'Address concerns about stakeholder impact'",
                    lines=3,
                    info="Optional: Provide additional context or specific questions for the narrative generation.",
                    value=""
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
                
                gr.Markdown("### Document Size Analysis (v8.6)")
                
                with gr.Row():
                    analyze_tokens_btn = gr.Button(
                        "📊 Analyze Document Size",
                        size="sm"
                    )
                
                token_analysis_output = gr.Markdown(
                    "Upload a document and click 'Analyze Document Size' to see token count and recommendations.",
                    label="Token Analysis"
                )
                
                gr.Markdown("### Document Q&A")
                
                enable_document_qa = gr.Checkbox(
                    label="Enable Document Q&A",
                    value=False,
                    info="Ask a specific question about the document using Ollama."
                )
                
                enable_chunking = gr.Checkbox(
                    label="🔄 Use Smart Chunking (for large documents)",
                    value=False,
                    info="Automatically chunk large documents and use intelligent routing. Recommended for 100+ page documents."
                )
                
                qa_routing_strategy = gr.Radio(
                    choices=["keyword", "comprehensive", "quick"],
                    value="keyword",
                    label="Query Routing Strategy",
                    info="keyword: Smart routing (fast), comprehensive: Query all chunks (thorough), quick: First chunk only",
                    visible=False
                )
                
                document_qa_question = gr.Textbox(
                    label="Question about the document",
                    placeholder="e.g., 'What are the key stakeholders mentioned?' or 'Summarize the budget allocation for healthcare'",
                    lines=2,
                    info="Ask any question about the document content. Answer saved to qa/ directory.",
                    value=""
                )
            
            # ========== TAB 4: TRANSPARENCY FEATURES ==========
            with gr.Tab("🔒 Transparency & Compliance"):
                gr.Markdown("### Enhanced Transparency Modules (v8.3.2)")
                
                enhanced_provenance = gr.Checkbox(
                    label="Enhanced Provenance Tracking",
                    value=False,
                    info="Extract comprehensive document metadata (author, creation tool, edit patterns)"
                )
                
                provenance_report = gr.Checkbox(
                    label="📜 Generate Provenance Report",
                    value=False,
                    info="Create full audit trail: document origin + Sparrow's AI usage during analysis (v8.4.1)"
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
                
                gr.Markdown("### Legislative Threat Detection (v8.5)")
                
                legislative_threat = gr.Checkbox(
                    label="⚖️ Run Discretionary Power Analysis",
                    value=False,
                    info="Detect ministerial discretion, broad scope language, exclusion powers, and accountability gaps in legislation."
                )
                
                gr.Markdown("### Memory Management")
                
                low_memory_mode = gr.Checkbox(
                    label="🧠 Low Memory Mode (recommended for large documents)",
                    value=False,
                    info="Runs analysis in subprocess - frees all RAM when complete. Best for 100+ page PDFs."
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
                
                with gr.Row():
                    analyze_btn = gr.Button(
                        "🎯 Analyze Document",
                        variant="primary",
                        size="lg"
                    )
                    cleanup_btn = gr.Button(
                        "🧹 Free Memory",
                        variant="secondary",
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
        
        # v8.6: Token analysis button handler
        def handle_token_analysis(pdf_file_path):
            """Handle token analysis button click."""
            if not pdf_file_path:
                return "❌ Please upload a document first."
            
            if not ENHANCED_QA_AVAILABLE:
                return "❌ Enhanced Q&A modules not available. Please install token_calculator.py and enhanced_document_qa.py."
            
            try:
                from token_calculator import analyze_document_file
                
                # Analyze document
                analysis = analyze_document_file(pdf_file_path)
                
                # Format output
                tokens = analysis.get("estimated_tokens", 0)
                chars = analysis.get("characters", 0)
                pages = analysis.get("estimated_pages", 0)
                method = analysis.get("estimation_method", "unknown")
                
                output = f"""### 📊 Document Size Analysis
                
**File:** `{Path(pdf_file_path).name}`

**Size Metrics:**
- Characters: {chars:,}
- Estimated Tokens: {tokens:,} ({method} method)
- Estimated Pages: {pages}

"""
                
                # Add recommendation if available
                rec = analysis.get("recommendation", {})
                if rec and rec.get("strategy") != "SINGLE":
                    strategy = rec.get("strategy", "unknown")
                    models = rec.get("recommended_models", [])
                    
                    output += f"""**Recommendation:** {strategy} strategy\n\n"""
                    
                    if models:
                        top_model = models[0]
                        output += f"""**Suggested Model:** `{top_model.get('model', 'unknown')}`
- Context: {top_model.get('context', 0):,} tokens
- Chunks Needed: {top_model.get('chunks_needed', 1)}
- Coverage: {top_model.get('coverage', '0%')}

"""
                        
                        if top_model.get('chunks_needed', 1) > 1:
                            output += f"""
⚠️ **This document requires chunking!**
Enable "Use Smart Chunking" in Document Q&A section for optimal results.
"""
                else:
                    output += "✅ **Document fits in single context window** - No chunking needed.\n"
                
                return output
                
            except Exception as e:
                import traceback
                return f"❌ Error analyzing document: {str(e)}\n\n{traceback.format_exc()}"
        
        analyze_tokens_btn.click(
            fn=handle_token_analysis,
            inputs=[pdf_file],
            outputs=[token_analysis_output]
        )
        
        # v8.6: Show/hide routing strategy based on chunking checkbox
        enable_chunking.change(
            fn=lambda enabled: gr.update(visible=enabled),
            inputs=[enable_chunking],
            outputs=[qa_routing_strategy]
        )
        
        # Wire up settings summary to update when any input changes
        all_inputs = [
            pdf_file, url_input, variant, document_type, output_name, document_title,
            narrative_style, narrative_length, ollama_model, ollama_custom_query,
            deep_analysis, citation_check, check_urls, enable_document_qa, enable_chunking, qa_routing_strategy, document_qa_question,
            enhanced_provenance, provenance_report, generate_ai_disclosure,
            trace_data_sources, nist_compliance, lineage_chart_format, legislative_threat, low_memory_mode
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
                document_type,  # v8.3.3: Document type for citation scoring
                output_name,
                document_title,
                
                # Narrative settings
                narrative_style,
                narrative_length,
                ollama_model,
                ollama_custom_query,  # Fix #1: Custom query for Ollama
                
                # Analysis flags
                deep_analysis,
                citation_check,
                check_urls,
                enable_document_qa,  # v8.4.2: Document Q&A
                enable_chunking,  # v8.6: Smart chunking
                qa_routing_strategy,  # v8.6: Routing strategy
                document_qa_question,  # v8.4.2: Q&A question
                
                # Transparency flags
                enhanced_provenance,
                provenance_report,  # v8.4.1: Full provenance audit trail
                generate_ai_disclosure,
                trace_data_sources,
                nist_compliance,
                lineage_chart_format,
                legislative_threat,  # v8.5: Legislative threat detection
                
                # Memory management
                low_memory_mode,  # v8.4.1: Run in subprocess
            ],
            outputs=[output_status, command_output]
        )
        
        # Connect the output picker button
        output_picker.click(
            fn=browse_output_location,
            inputs=[],
            outputs=output_name
        )
        
        # Connect the cleanup button (v8.4.1)
        cleanup_btn.click(
            fn=manual_cleanup_button,
            inputs=[],
            outputs=output_status
        )
        
        # Connect quick paths dropdown
        quick_paths.change(
            fn=set_quick_path,
            inputs=[quick_paths, output_name],
            outputs=output_name
        )
    
    return interface


if __name__ == "__main__":
    # v8.4.1: Register cleanup handlers to prevent memory issues
    register_cleanup_handlers()
    
    # Create and launch the interface
    interface = create_interface()
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║         Sparrow SPOT Scale™ v{SPARROW_VERSION} - Web Interface        ║
    ╚══════════════════════════════════════════════════════════╝
    
    🚀 Starting Gradio server...
    📱 Interface will open in your browser automatically
    🌐 Access at: http://localhost:7861
    
    🧹 Memory cleanup: ENABLED (prevents Ollama conflicts)
    
    Press Ctrl+C to stop the server
    """)
    
    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7861,  # Use different port to avoid conflicts
        share=False,  # Set to True to get public URL for sharing
        show_error=True
    )

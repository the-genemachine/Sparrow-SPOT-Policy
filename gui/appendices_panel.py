"""
Sparrow SPOT GUI Appendices Panel
Provides UI controls for viewing and downloading auto-generated appendices

v8.6.1+: Appendices auto-generation with GUI integration
"""

import gradio as gr
import os
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime


class AppendicesPanelManager:
    """Manages appendices UI panel and download functionality."""
    
    def __init__(self):
        self.last_appendices = None
        self.last_document_title = None
    
    def set_appendices(self, appendices: Dict, document_title: str):
        """Store generated appendices for display and download."""
        self.last_appendices = appendices
        self.last_document_title = document_title
    
    def get_appendix_markdown(self, appendix_key: str) -> str:
        """Get markdown content for a specific appendix."""
        if not self.last_appendices or appendix_key not in self.last_appendices:
            return f"❌ Appendix not generated yet. Complete an analysis first."
        
        content = self.last_appendices[appendix_key]
        if isinstance(content, str):
            return content
        return str(content)
    
    def export_appendices_zip(self, output_dir: str = None) -> Optional[str]:
        """Export all appendices as a ZIP file."""
        if not self.last_appendices:
            return None
        
        try:
            import zipfile
            import tempfile
            
            # Use provided directory or temp directory
            if not output_dir:
                output_dir = tempfile.gettempdir()
            
            # Create ZIP
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_name = f"Appendices_{self.last_document_title}_{timestamp}.zip"
            zip_path = Path(output_dir) / zip_name
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add each appendix as a file
                appendix_map = {
                    'appendix_a': 'A_EVIDENCE_CITATIONS.md',
                    'appendix_b': 'B_METHODOLOGY.md',
                    'appendix_c': 'C_COMPONENT_DISCLOSURE.md',
                    'appendix_d': 'D_BILL_FINDINGS.md',
                    'appendix_e': 'E_VERIFICATION_GUIDE.md',
                    'navigation_index': 'INDEX.md',
                }
                
                for key, filename in appendix_map.items():
                    if key in self.last_appendices:
                        content = self.last_appendices[key]
                        if isinstance(content, str):
                            zipf.writestr(filename, content)
                
                # Add metadata if available
                if 'metadata' in self.last_appendices:
                    import json
                    metadata_json = json.dumps(self.last_appendices['metadata'], indent=2)
                    zipf.writestr('METADATA.json', metadata_json)
                
                # Add README
                readme = f"""# Appendices for {self.last_document_title}

Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}

## Contents

- **A_EVIDENCE_CITATIONS.md**: Evidence mapping for all criteria scores
- **B_METHODOLOGY.md**: Complete scoring framework and methodology
- **C_COMPONENT_DISCLOSURE.md**: AI involvement and human review details
- **D_BILL_FINDINGS.md**: Policy-specific findings and recommendations
- **E_VERIFICATION_GUIDE.md**: How to independently verify this analysis
- **INDEX.md**: Navigation guide and reading paths
- **METADATA.json**: Generation metadata

## Quick Start

1. **Want to verify a score?** → Read A_EVIDENCE_CITATIONS.md
2. **Want to understand how scores were calculated?** → Read B_METHODOLOGY.md
3. **Concerned about AI involvement?** → Read C_COMPONENT_DISCLOSURE.md
4. **Need bill-specific findings?** → Read D_BILL_FINDINGS.md
5. **Want to verify independently?** → Read E_VERIFICATION_GUIDE.md
6. **Want navigation help?** → Read INDEX.md

## What This Is

These appendices provide complete transparency about the policy analysis:
- Every score is backed by specific evidence
- Methodology is fully documented and replicable
- AI involvement is disclosed completely
- Findings are specific to the analyzed document
- Independent verification is enabled

## What This Is Not

This is not:
- Opinion or recommendations without evidence
- Generic policy analysis template
- Marketing material or promotional content
- Substitute for reading the original document

Always verify claims against the source document yourself.

---

For more information, visit: https://github.com/the-genemachine/Sparrow-SPOT-Policy
"""
                zipf.writestr('README.md', readme)
            
            return str(zip_path)
        
        except Exception as e:
            print(f"Error exporting appendices ZIP: {e}")
            return None
    
    def create_appendices_panel(self) -> Tuple:
        """Create Gradio components for appendices panel."""
        
        with gr.Group() as panel:
            gr.Markdown("""
            ## 📚 Appendices (Auto-Generated Transparency)
            
            Complete transparency documentation automatically generated from your analysis:
            - **Appendix A:** Evidence Citations - tie every score to source
            - **Appendix B:** Methodology - complete scoring framework
            - **Appendix C:** Component Disclosure - AI/human involvement
            - **Appendix D:** Bill Findings - policy-specific analysis
            - **Appendix E:** Verification Guide - independent verification process
            """)
            
            with gr.Tabs():
                # Appendix A
                with gr.Tab("A: Evidence Citations"):
                    appendix_a_text = gr.Markdown(
                        "Run an analysis to see evidence citations",
                        label="Appendix A"
                    )
                    a_copy_btn = gr.Button("📋 Copy to Clipboard", size="sm")
                
                # Appendix B
                with gr.Tab("B: Methodology"):
                    appendix_b_text = gr.Markdown(
                        "Run an analysis to see methodology",
                        label="Appendix B"
                    )
                    b_copy_btn = gr.Button("📋 Copy to Clipboard", size="sm")
                
                # Appendix C
                with gr.Tab("C: Component Disclosure"):
                    appendix_c_text = gr.Markdown(
                        "Run an analysis to see component disclosure",
                        label="Appendix C"
                    )
                    c_copy_btn = gr.Button("📋 Copy to Clipboard", size="sm")
                
                # Appendix D
                with gr.Tab("D: Bill Findings"):
                    appendix_d_text = gr.Markdown(
                        "Run an analysis to see bill findings",
                        label="Appendix D"
                    )
                    d_copy_btn = gr.Button("📋 Copy to Clipboard", size="sm")
                
                # Appendix E
                with gr.Tab("E: Verification Guide"):
                    appendix_e_text = gr.Markdown(
                        "Run an analysis to see verification guide",
                        label="Appendix E"
                    )
                    e_copy_btn = gr.Button("📋 Copy to Clipboard", size="sm")
                
                # Index
                with gr.Tab("Index: Navigation"):
                    index_text = gr.Markdown(
                        "Run an analysis to see navigation index",
                        label="Navigation Index"
                    )
                    index_copy_btn = gr.Button("📋 Copy to Clipboard", size="sm")
            
            with gr.Row():
                export_zip_btn = gr.Button(
                    "⬇️ Download All as ZIP",
                    variant="primary",
                    size="lg"
                )
                view_metadata_btn = gr.Button(
                    "📊 View Metadata",
                    size="sm"
                )
            
            export_status = gr.Textbox(
                label="Export Status",
                interactive=False,
                visible=False
            )
            
            metadata_display = gr.Markdown(
                "No metadata available",
                label="Metadata"
            )
        
        return (
            panel,
            appendix_a_text, appendix_b_text, appendix_c_text, 
            appendix_d_text, appendix_e_text, index_text,
            a_copy_btn, b_copy_btn, c_copy_btn, d_copy_btn, e_copy_btn, index_copy_btn,
            export_zip_btn, view_metadata_btn, export_status, metadata_display
        )


def create_copy_handler(text_component):
    """Create a handler function for copy to clipboard button."""
    def copy_to_clipboard():
        # In a real implementation, this would use JavaScript to copy
        # For now, return a message
        return gr.update(visible=True, value="✅ Content ready to copy (use Ctrl+A then Ctrl+C)")
    return copy_to_clipboard


def create_metadata_display(metadata_dict: Dict) -> str:
    """Format metadata for display."""
    if not metadata_dict:
        return "No metadata available"
    
    lines = ["### Appendices Metadata\n"]
    lines.append(f"**Generated:** {metadata_dict.get('generated_at', 'Unknown')}")
    lines.append(f"**Document:** {metadata_dict.get('document_title', 'Unknown')}")
    lines.append(f"**Total Words:** {metadata_dict.get('total_words', 0):,}")
    lines.append(f"**Criteria Analyzed:** {metadata_dict.get('criteria_count', 0)}")
    lines.append(f"**Trust Score:** {metadata_dict.get('trust_score', 0):.1f}/100")
    lines.append(f"**AI Contribution:** {metadata_dict.get('ai_detection_percentage', 0):.1f}%")
    
    lines.append("\n### Appendices Summary\n")
    for key, info in metadata_dict.get('appendices', {}).items():
        lines.append(f"- **{info['name']}**: ~{info['words']:,} words")
    
    return '\n'.join(lines)


# Integration function to add appendices to analysis output
def integrate_appendices_into_result(analysis_result: Dict, appendices_panel_manager: AppendicesPanelManager) -> str:
    """
    After analysis completes, extract and display appendices.
    
    Args:
        analysis_result: Result dictionary from narrative pipeline
        appendices_panel_manager: Manager instance for storing appendices
    
    Returns:
        Status message
    """
    try:
        # Check if appendices are in the result
        if 'appendices' not in analysis_result:
            return "⚠️ Analysis complete but appendices not generated. Check if appendices_generator is enabled."
        
        appendices = analysis_result['appendices']
        doc_title = analysis_result.get('metadata', {}).get('document_title', 'Analysis')
        
        # Store for panel display
        appendices_panel_manager.set_appendices(appendices, doc_title)
        
        return f"✅ Analysis complete. {len([k for k in appendices.keys() if k.startswith('appendix')])} appendices generated."
    
    except Exception as e:
        return f"⚠️ Analysis complete but error processing appendices: {str(e)}"

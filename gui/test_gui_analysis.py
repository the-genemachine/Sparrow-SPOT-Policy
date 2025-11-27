#!/usr/bin/env python3
"""
Test script for GUI analysis function
Tests the wired-up analyze_document() function with 2025 Budget PDF
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Simple mock for Gradio Progress
class MockProgress:
    def __call__(self, value, desc=""):
        print(f"  Progress: {int(value*100)}% - {desc}")

# Mock file upload object
class MockFileUpload:
    def __init__(self, file_path):
        self.name = file_path

def main():
    print("=" * 70)
    print("GUI ANALYSIS TEST - 2025 Budget PDF")
    print("=" * 70)
    print()
    
    # Import the analyze_document function
    try:
        from sparrow_gui import analyze_document
        print("✓ Successfully imported analyze_document from GUI module")
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return 1
    
    # Prepare test inputs
    pdf_path = "../test_articles/2025-Budget.pdf"
    if not Path(pdf_path).exists():
        pdf_path = "test_articles/2025-Budget.pdf"
    
    print(f"\nTest file: {pdf_path}")
    print(f"File exists: {Path(pdf_path).exists()}")
    
    if not Path(pdf_path).exists():
        print("✗ Test file not found!")
        return 1
    
    # Create mock file upload
    mock_file = MockFileUpload(pdf_path)
    
    # Test parameters (simple policy analysis)
    print("\nTest Configuration:")
    print("  Variant: policy")
    print("  Output: GUI-Test-2025-Budget")
    print("  Deep Analysis: No")
    print("  Citation Check: Yes")
    print("  AI Disclosure: Yes")
    print("  Data Tracing: Yes")
    print()
    
    print("=" * 70)
    print("RUNNING ANALYSIS...")
    print("=" * 70)
    print()
    
    try:
        result_msg, result_path = analyze_document(
            pdf_file=mock_file,
            url_input=None,
            variant="policy",
            output_name="GUI-Test-2025-Budget",
            narrative_style="None",
            narrative_length="standard",
            ollama_model="llama3.2",
            deep_analysis=False,
            citation_check=True,
            check_urls=False,
            enhanced_provenance=False,
            generate_ai_disclosure=True,
            trace_data_sources=True,
            nist_compliance=False,
            lineage_chart_format="None",
            progress=MockProgress()
        )
        
        print()
        print("=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print()
        print(result_msg)
        print()
        
        if result_path:
            print(f"Result file: {result_path}")
            if Path(result_path).exists():
                print(f"File size: {Path(result_path).stat().st_size / 1024:.1f} KB")
                print("✓ Result file created successfully")
            else:
                print("✗ Result file not found")
                return 1
        
        print()
        print("=" * 70)
        print("TEST PASSED ✓")
        print("=" * 70)
        return 0
        
    except Exception as e:
        import traceback
        print()
        print("=" * 70)
        print("TEST FAILED ✗")
        print("=" * 70)
        print(f"\nError: {e}")
        print("\nTraceback:")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())

"""
Appendices Auto-Save Utility
Automatically saves generated appendices to disk when present in analysis result

v8.6.1+: Auto-save functionality for appendices
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


def save_appendices_from_result(
    result: Dict,
    output_dir: str,
    document_title: str = "Analysis"
) -> Optional[Dict[str, str]]:
    """
    Extract and save appendices from a narrative pipeline result.
    
    This function checks if appendices are present in the result dictionary
    (from NarrativeGenerationPipeline.generate_complete_narrative) and saves them
    to disk in a structured appendices directory.
    
    Args:
        result: Dictionary returned from NarrativeGenerationPipeline.generate_complete_narrative()
        output_dir: Base output directory where appendices/ folder will be created
        document_title: Document being analyzed (used for folder naming)
    
    Returns:
        Dictionary mapping appendix names to file paths, or None if no appendices in result
    
    Example:
        result = pipeline.generate_complete_narrative(analysis)
        saved_files = save_appendices_from_result(result, "./Investigations/Bill-C-15/Bill-C15-02/")
        
        if saved_files:
            print(f"Saved {len(saved_files)} appendix files")
            for name, path in saved_files.items():
                print(f"  {name}: {path}")
    """
    
    # Check if appendices are in result
    if 'appendices' not in result or not result['appendices']:
        return None
    
    appendices = result['appendices']
    
    # Create appendices directory
    appendices_dir = Path(output_dir) / 'appendices'
    appendices_dir.mkdir(parents=True, exist_ok=True)
    
    # File mapping for appendices
    file_map = {
        'appendix_a': 'A_EVIDENCE_CITATIONS.md',
        'appendix_b': 'B_METHODOLOGY.md',
        'appendix_c': 'C_COMPONENT_DISCLOSURE.md',
        'appendix_d': 'D_BILL_FINDINGS.md',
        'appendix_e': 'E_VERIFICATION_GUIDE.md',
        'navigation_index': 'INDEX.md',
    }
    
    saved_files = {}
    
    # Save each appendix
    for key, filename in file_map.items():
        if key in appendices:
            content = appendices[key]
            if isinstance(content, str):
                filepath = appendices_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved_files[key] = str(filepath)
                print(f"✅ Saved {key.title()}: {filepath}")
    
    # Save metadata if available
    if 'metadata' in appendices:
        metadata_file = appendices_dir / 'METADATA.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(appendices['metadata'], f, indent=2)
        saved_files['metadata'] = str(metadata_file)
        print(f"✅ Saved Metadata: {metadata_file}")
    
    # Create README
    readme_content = f"""# Appendices for {document_title}

Generated: {appendices.get('metadata', {}).get('generated_at', 'Unknown')}

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

---

For more information, visit: https://github.com/the-genemachine/Sparrow-SPOT-Policy
"""
    
    readme_file = appendices_dir / 'README.md'
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    saved_files['readme'] = str(readme_file)
    print(f"✅ Saved README: {readme_file}")
    
    return saved_files


def integrate_appendices_saver(
    result: Dict,
    base_output_dir: str,
    document_title: str = "Analysis"
) -> Dict:
    """
    Integrate appendices saving into existing result processing.
    
    This is a convenience wrapper that:
    1. Saves appendices to disk if present
    2. Adds appendices file paths to result metadata
    3. Returns updated result
    
    Args:
        result: Pipeline result dictionary
        base_output_dir: Base directory for analysis output
        document_title: Document title for appendices
    
    Returns:
        Updated result dictionary with appendices_saved metadata
    """
    
    # Save appendices
    saved = save_appendices_from_result(result, base_output_dir, document_title)
    
    # Update result metadata
    if 'metadata' not in result:
        result['metadata'] = {}
    
    if saved:
        result['metadata']['appendices_saved'] = True
        result['metadata']['appendices_location'] = str(Path(base_output_dir) / 'appendices')
        result['metadata']['appendices_files'] = saved
        print(f"\n✅ Appendices saved to: {Path(base_output_dir) / 'appendices'}")
    else:
        result['metadata']['appendices_saved'] = False
        print("\n⚠️ No appendices found in result to save")
    
    return result


if __name__ == '__main__':
    # Example usage
    example_result = {
        'appendices': {
            'appendix_a': '# Appendix A\n\nContent here...',
            'appendix_b': '# Appendix B\n\nContent here...',
            'metadata': {
                'generated_at': '2025-12-11T00:00:00Z',
                'document_title': 'Test'
            }
        }
    }
    
    saved = save_appendices_from_result(example_result, '/tmp/test_appendices/', 'Test Document')
    print(f"\nSaved files: {saved}")

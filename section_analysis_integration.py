"""
Integration module for AI Section Analyzer with Sparrow SPOT Scale v8
Adds optional section-by-section AI analysis to grading pipeline
"""

from typing import Dict, Optional
from ai_section_analyzer import AISectionAnalyzer


def add_section_analysis_to_report(report: Dict, full_text: str, enable: bool = False) -> Dict:
    """
    Add section-by-section AI analysis to existing grading report.
    
    Args:
        report: Existing grading report dictionary
        full_text: Complete document text
        enable: Whether to run section analysis (optional enhancement)
        
    Returns:
        Updated report with section_analysis field added
    """
    if not enable:
        report['section_analysis'] = {
            'enabled': False,
            'note': 'Section analysis disabled. Use --section-analysis flag to enable.'
        }
        return report
    
    print("🔍 Running section-by-section AI analysis...")
    
    try:
        analyzer = AISectionAnalyzer()
        
        # Analyze sections
        section_results = analyzer.analyze_document_sections(
            full_text,
            min_section_length=1000  # Analyze chunks of 1000+ chars
        )
        
        # Add to report
        report['section_analysis'] = {
            'enabled': True,
            'total_sections': section_results['total_sections'],
            'sections_analyzed': len(section_results['section_details']),
            'ai_detected_sections': len(section_results['ai_detected_sections']),
            'overall_ai_percentage': section_results['overall_ai_percentage'],
            'model_distribution': section_results['model_distribution'],
            'section_details': section_results['section_details'][:10],  # Top 10 sections
            'cohere_sections_count': len(section_results['cohere_sections']),
            'summary': _generate_section_summary(section_results)
        }
        
        # Add section-specific insights
        if section_results['cohere_sections']:
            cohere_patterns_total = {}
            for section in section_results['cohere_sections']:
                for pattern, count in section.get('cohere_patterns', {}).items():
                    cohere_patterns_total[pattern] = cohere_patterns_total.get(pattern, 0) + count
            
            report['section_analysis']['cohere_pattern_totals'] = cohere_patterns_total
        
        print(f"   ✓ Analyzed {section_results['total_sections']} sections")
        print(f"   ✓ AI detected in {len(section_results['ai_detected_sections'])} sections")
        if section_results.get('cohere_percentage', 0) > 0:
            print(f"   ✓ Cohere patterns in {len(section_results['cohere_sections'])} sections ({section_results['cohere_percentage']:.1f}%)")
        
    except Exception as e:
        print(f"   ⚠️  Section analysis failed: {e}")
        report['section_analysis'] = {
            'enabled': True,
            'error': str(e),
            'note': 'Section analysis encountered an error'
        }
    
    return report


def _generate_section_summary(results: Dict) -> str:
    """Generate human-readable summary of section analysis."""
    total = results['total_sections']
    ai_detected = len(results['ai_detected_sections'])
    
    if ai_detected == 0:
        return f"No AI-generated sections detected in {total} analyzed sections."
    
    percentage = results['overall_ai_percentage']
    summary = f"{ai_detected} of {total} sections ({percentage:.1f}%) show AI generation patterns. "
    
    # Add model distribution
    models = results.get('model_distribution', {})
    if models:
        primary_model = max(models.items(), key=lambda x: x[1] if x[0] else 0)
        if primary_model[0] and primary_model[0] != 'None':
            summary += f"Primary model detected: {primary_model[0]} ({primary_model[1]} sections). "
    
    # Add Cohere-specific info if relevant
    cohere_sections = len(results.get('cohere_sections', []))
    if cohere_sections > 0:
        summary += f"Cohere AI patterns found in {cohere_sections} sections."
    
    return summary


def generate_section_analysis_file(report: Dict, output_path: str) -> Optional[str]:
    """
    Generate standalone section analysis report file.
    
    Args:
        report: Full grading report with section_analysis
        output_path: Base output path (without extension)
        
    Returns:
        Path to generated file, or None if section analysis disabled
    """
    if not report.get('section_analysis', {}).get('enabled'):
        return None
    
    section_data = report['section_analysis']
    
    if section_data.get('error'):
        return None
    
    # Generate markdown report
    lines = []
    lines.append("# AI Section Analysis Report\n")
    lines.append(f"**Document:** {report.get('document_type', 'Unknown')}")
    lines.append(f"**Total Sections:** {section_data['total_sections']}")
    lines.append(f"**AI Detection:** {section_data['ai_detected_sections']} sections ({section_data['overall_ai_percentage']:.1f}%)\n")
    
    lines.append("## Summary\n")
    lines.append(section_data['summary'])
    lines.append("")
    
    # Model distribution
    if section_data.get('model_distribution'):
        lines.append("\n## Model Distribution\n")
        for model, count in sorted(section_data['model_distribution'].items(), 
                                   key=lambda x: x[1], reverse=True):
            if model and model != 'None':
                lines.append(f"- **{model}:** {count} sections")
    
    # Cohere patterns if detected
    if section_data.get('cohere_pattern_totals'):
        lines.append("\n## Cohere AI Patterns Detected\n")
        for pattern, count in sorted(section_data['cohere_pattern_totals'].items(), 
                                     key=lambda x: x[1], reverse=True):
            pattern_name = pattern.replace('_', ' ').title()
            lines.append(f"- **{pattern_name}:** {count} instances")
    
    # Section details
    if section_data.get('section_details'):
        lines.append("\n## Top Sections by AI Content\n")
        
        # Sort by AI score
        sorted_sections = sorted(section_data['section_details'], 
                                key=lambda x: x['ai_score'], reverse=True)
        
        for idx, section in enumerate(sorted_sections[:5], 1):
            lines.append(f"\n### {idx}. {section['title']}")
            lines.append(f"- **AI Score:** {section['ai_score']*100:.1f}%")
            if section['detected_model']:
                lines.append(f"- **Model:** {section['detected_model']} ({section['model_confidence']*100:.0f}% confidence)")
            lines.append(f"- **Length:** {section['length']:,} characters")
            
            # Show top patterns
            if section.get('cohere_patterns'):
                top_patterns = sorted(section['cohere_patterns'].items(), 
                                    key=lambda x: x[1], reverse=True)[:3]
                if top_patterns:
                    lines.append("- **Patterns:**")
                    for pattern, count in top_patterns:
                        lines.append(f"  - {pattern.replace('_', ' ').title()}: {count}")
            
            lines.append(f"- **Preview:** {section['preview'][:150]}...")
    
    # Write to file
    output_file = f"{output_path}_section_analysis.md"
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))
    
    return output_file


# Example integration with sparrow_grader_v8.py:
# 
# In the grade() method, after AI detection:
#
#     if args.section_analysis:  # New CLI flag
#         report = add_section_analysis_to_report(
#             report, 
#             full_text=text,
#             enable=True
#         )
#
# In the file output section:
#
#     if args.section_analysis and narrative_outputs:
#         section_file = generate_section_analysis_file(
#             report,
#             output_path=args.output
#         )
#         if section_file:
#             print(f"   ✓ Section Analysis: {section_file}")

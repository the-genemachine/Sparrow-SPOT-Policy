"""
AI Section Analyzer
Identifies specific sections of documents where AI was likely used
Based on model-specific heuristics and content patterns
"""

import json
import re
from typing import Dict, List, Tuple
from ai_detection_engine import AIDetectionEngine


class AISectionAnalyzer:
    """
    Analyzes documents to identify which specific sections
    were likely AI-generated and which AI model was used.
    """
    
    def __init__(self):
        self.detector = AIDetectionEngine()
        
        # Cohere-specific patterns (business/policy focused)
        self.cohere_patterns = {
            'rag_citations': r'according to|as reported|research shows|studies indicate',
            'structured_lists': r'(?:•|\*|\d+\.)\s+[A-Z].*?(?:\n|$)',
            'executive_summary': r'(?:Executive Summary|Overview|Key Points)',
            'policy_language': r'will\s+(?:enable|support|enhance|strengthen|establish)',
            'impact_statements': r'impact(?:s|ing)?\s+(?:of|on|to)',
            'stakeholder_focus': r'(?:stakeholder|constituent|citizen|business|community)',
            'data_driven': r'(?:data shows|evidence suggests|analysis indicates)',
            'action_oriented': r'(?:implement|deploy|establish|create|develop)\s+\w+',
        }
        
        # General AI patterns
        self.ai_patterns = {
            'uniform_structure': r'^(?:\d+\.|\•|\*)\s+[A-Z]',
            'hedging_language': r'(?:may|might|could|potentially|likely)',
            'passive_voice': r'(?:is|are|was|were|been)\s+\w+ed\s+by',
            'transition_phrases': r'(?:Furthermore|Moreover|Additionally|In addition|However)',
            'comprehensive_coverage': r'(?:comprehensive|holistic|integrated|multi-faceted)',
        }
    
    def analyze_document_sections(self, full_text: str, min_section_length: int = 500) -> Dict:
        """
        Analyze document by sections to identify AI usage patterns.
        
        Args:
            full_text: Complete document text
            min_section_length: Minimum section size to analyze
            
        Returns:
            Dictionary with section-by-section AI analysis
        """
        # Split into logical sections
        sections = self._split_into_sections(full_text)
        
        results = {
            'total_sections': len(sections),
            'ai_detected_sections': [],
            'cohere_sections': [],
            'section_details': [],
            'overall_ai_percentage': 0.0,
            'model_distribution': {}
        }
        
        ai_section_count = 0
        cohere_section_count = 0
        
        for idx, section in enumerate(sections):
            if len(section['text']) < min_section_length:
                continue
                
            # Run AI detection on this section
            detection = self.detector.analyze_document(section['text'])
            
            section_analysis = {
                'section_number': idx + 1,
                'title': section.get('title', f'Section {idx + 1}'),
                'length': len(section['text']),
                'ai_score': detection['ai_detection_score'],
                'detected_model': detection.get('likely_ai_model', {}).get('model'),
                'model_confidence': detection.get('likely_ai_model', {}).get('confidence', 0),
                'preview': section['text'][:200] + '...',
                'cohere_patterns': self._detect_cohere_patterns(section['text']),
                'ai_indicators': self._count_ai_patterns(section['text'])
            }
            
            # Classify section
            if detection['ai_detection_score'] > 0.5:
                ai_section_count += 1
                results['ai_detected_sections'].append(section_analysis)
                
                if section_analysis['detected_model'] == 'Cohere':
                    cohere_section_count += 1
                    results['cohere_sections'].append(section_analysis)
            
            results['section_details'].append(section_analysis)
        
        # Calculate statistics
        total_analyzed = len([s for s in sections if len(s['text']) >= min_section_length])
        if total_analyzed > 0:
            results['overall_ai_percentage'] = (ai_section_count / total_analyzed) * 100
            results['cohere_percentage'] = (cohere_section_count / total_analyzed) * 100
        
        # Model distribution
        model_counts = {}
        for section in results['section_details']:
            model = section.get('detected_model', 'Unknown')
            model_counts[model] = model_counts.get(model, 0) + 1
        results['model_distribution'] = model_counts
        
        return results
    
    def _split_into_sections(self, text: str) -> List[Dict]:
        """Split document into logical sections."""
        sections = []
        
        # Try to split by headers/titles (common patterns)
        # Pattern 1: All caps headers
        header_pattern = r'\n([A-Z][A-Z\s]{10,})\n'
        parts = re.split(header_pattern, text)
        
        if len(parts) > 3:  # Found meaningful sections
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    sections.append({
                        'title': parts[i].strip(),
                        'text': parts[i + 1].strip()
                    })
        else:
            # Fallback: split by page breaks or paragraph chunks
            page_pattern = r'--- Page \d+ ---'
            pages = re.split(page_pattern, text)
            
            # Chunk pages into larger sections
            chunk_size = 3  # 3 pages per section
            for i in range(0, len(pages), chunk_size):
                chunk_pages = pages[i:i + chunk_size]
                sections.append({
                    'title': f'Pages {i + 1}-{i + len(chunk_pages)}',
                    'text': '\n'.join(chunk_pages)
                })
        
        return sections
    
    def _detect_cohere_patterns(self, text: str) -> Dict[str, int]:
        """Detect Cohere-specific patterns in text."""
        pattern_counts = {}
        
        for pattern_name, pattern_regex in self.cohere_patterns.items():
            matches = re.findall(pattern_regex, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                pattern_counts[pattern_name] = len(matches)
        
        return pattern_counts
    
    def _count_ai_patterns(self, text: str) -> Dict[str, int]:
        """Count general AI patterns in text."""
        pattern_counts = {}
        
        for pattern_name, pattern_regex in self.ai_patterns.items():
            matches = re.findall(pattern_regex, text, re.MULTILINE)
            if matches:
                pattern_counts[pattern_name] = len(matches)
        
        return pattern_counts
    
    def generate_section_report(self, analysis_results: Dict) -> str:
        """Generate human-readable report of section analysis."""
        report = []
        report.append("=" * 70)
        report.append("AI SECTION ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"\nTotal Sections Analyzed: {analysis_results['total_sections']}")
        report.append(f"Sections with AI Detection: {len(analysis_results['ai_detected_sections'])}")
        report.append(f"Overall AI Percentage: {analysis_results['overall_ai_percentage']:.1f}%")
        
        if 'cohere_percentage' in analysis_results:
            report.append(f"Cohere-Detected Sections: {len(analysis_results['cohere_sections'])} ({analysis_results['cohere_percentage']:.1f}%)")
        
        report.append("\nModel Distribution:")
        for model, count in sorted(analysis_results['model_distribution'].items(), key=lambda x: x[1], reverse=True):
            if model and model != 'None':
                report.append(f"  • {model}: {count} sections")
        
        # Highlight Cohere sections
        if analysis_results['cohere_sections']:
            report.append("\n" + "=" * 70)
            report.append("COHERE-DETECTED SECTIONS:")
            report.append("=" * 70)
            
            for section in analysis_results['cohere_sections'][:10]:  # Top 10
                report.append(f"\n[{section['section_number']}] {section['title']}")
                report.append(f"  AI Score: {section['ai_score']*100:.1f}%")
                report.append(f"  Confidence: {section['model_confidence']*100:.0f}%")
                report.append(f"  Length: {section['length']} chars")
                
                if section['cohere_patterns']:
                    report.append(f"  Cohere Patterns Detected:")
                    for pattern, count in sorted(section['cohere_patterns'].items(), key=lambda x: x[1], reverse=True)[:3]:
                        report.append(f"    - {pattern.replace('_', ' ').title()}: {count}")
                
                report.append(f"  Preview: {section['preview'][:150]}...")
                report.append("")
        
        return '\n'.join(report)


def main():
    """Command-line interface for section analysis."""
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python ai_section_analyzer.py <file.pdf|analysis.json>")
        print("  Analyzes sections of a document to identify AI usage")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Handle PDF or JSON input
    if input_file.endswith('.pdf'):
        print(f"Extracting text from PDF: {input_file}...")
        try:
            import pdfplumber
            text_content = []
            with pdfplumber.open(input_file) as pdf:
                total_pages = min(len(pdf.pages), 100)  # Analyze first 100 pages
                for page_num, page in enumerate(pdf.pages[:total_pages], 1):
                    if page_num % 25 == 0:
                        print(f"  Processed {page_num}/{total_pages} pages...")
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- Page {page_num} ---\n{text}")
            full_text = '\n\n'.join(text_content)
            print(f"✓ Extracted {len(full_text):,} characters from {len(text_content)} pages")
        except ImportError:
            print("ERROR: pdfplumber not installed. Install with: pip install pdfplumber")
            sys.exit(1)
    else:
        print(f"Loading analysis from {input_file}...")
        with open(input_file) as f:
            data = json.load(f)
        
        full_text = data.get('full_text', '')
        if not full_text:
            print("ERROR: No full_text field found in JSON")
            print("Try using the PDF file directly instead")
            sys.exit(1)
    
    print(f"Analyzing {len(full_text):,} characters...")
    
    analyzer = AISectionAnalyzer()
    results = analyzer.analyze_document_sections(full_text)
    
    # Generate report
    report = analyzer.generate_section_report(results)
    print("\n" + report)
    
    # Save detailed results
    base_name = input_file.replace('.pdf', '').replace('.json', '')
    output_file = f'{base_name}_section_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Detailed results saved to: {output_file}")


if __name__ == '__main__':
    main()

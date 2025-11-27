"""
Sentence-Level AI Detection (Level 4 Analysis)
Identifies which specific sentences in a document are AI-generated
"""

import re
from typing import List, Dict
from ai_detection_engine import AIDetectionEngine


class SentenceLevelDetector:
    """
    Analyzes documents at sentence granularity to identify
    exact AI-generated vs human-written boundaries.
    """
    
    def __init__(self, threshold: float = 0.6):
        self.detector = AIDetectionEngine()
        self.threshold = threshold  # AI probability threshold
        
    def analyze_paragraph(self, paragraph: str) -> Dict:
        """
        Analyze a paragraph sentence-by-sentence.
        
        Returns:
            Dictionary with sentence-level analysis
        """
        sentences = self._split_sentences(paragraph)
        
        if not sentences:
            return {'sentences': [], 'summary': 'No sentences found'}
        
        results = []
        ai_count = 0
        total_ai_score = 0
        
        for idx, sentence in enumerate(sentences, 1):
            # Skip very short sentences (likely fragments)
            if len(sentence.split()) < 5:
                results.append({
                    'number': idx,
                    'text': sentence,
                    'classification': 'SKIPPED',
                    'ai_score': 0,
                    'reason': 'Too short to analyze'
                })
                continue
            
            # Detect AI in this sentence
            detection = self.detector.analyze_document(sentence)
            ai_score = detection['ai_detection_score']
            total_ai_score += ai_score
            
            # Classify
            if ai_score >= self.threshold:
                classification = 'AI'
                ai_count += 1
            elif ai_score >= 0.4:
                classification = 'MIXED'
            else:
                classification = 'HUMAN'
            
            results.append({
                'number': idx,
                'text': sentence,
                'classification': classification,
                'ai_score': ai_score,
                'confidence': detection.get('confidence', 0),
                'likely_model': detection.get('likely_ai_model', {}).get('model', 'Unknown')
            })
        
        # Calculate paragraph stats
        analyzed_count = len([r for r in results if r['classification'] != 'SKIPPED'])
        avg_ai_score = total_ai_score / len(sentences) if sentences else 0
        
        return {
            'sentences': results,
            'summary': {
                'total_sentences': len(sentences),
                'analyzed': analyzed_count,
                'ai_sentences': ai_count,
                'human_sentences': analyzed_count - ai_count,
                'ai_percentage': (ai_count / analyzed_count * 100) if analyzed_count > 0 else 0,
                'avg_ai_score': avg_ai_score
            }
        }
    
    def analyze_document(self, text: str) -> Dict:
        """
        Analyze entire document paragraph-by-paragraph at sentence level.
        
        Returns:
            Document-level sentence analysis
        """
        paragraphs = self._split_paragraphs(text)
        
        all_results = []
        total_sentences = 0
        total_ai_sentences = 0
        paragraph_summaries = []
        
        for para_idx, paragraph in enumerate(paragraphs[:20], 1):  # First 20 paragraphs
            if len(paragraph.strip()) < 50:  # Skip very short paragraphs
                continue
                
            para_analysis = self.analyze_paragraph(paragraph)
            
            all_results.extend(para_analysis['sentences'])
            summary = para_analysis['summary']
            
            total_sentences += summary['analyzed']
            total_ai_sentences += summary['ai_sentences']
            
            paragraph_summaries.append({
                'paragraph_number': para_idx,
                'preview': paragraph[:100] + '...',
                **summary
            })
        
        return {
            'paragraphs_analyzed': len(paragraph_summaries),
            'total_sentences': total_sentences,
            'ai_sentences': total_ai_sentences,
            'human_sentences': total_sentences - total_ai_sentences,
            'overall_ai_percentage': (total_ai_sentences / total_sentences * 100) if total_sentences > 0 else 0,
            'paragraph_summaries': paragraph_summaries,
            'all_sentences': all_results[:100]  # First 100 sentences for detail
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter (can be improved with nltk)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        # Split on double newlines or page breaks
        paragraphs = re.split(r'\n\s*\n|--- Page \d+ ---', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def generate_report(self, results: Dict, output_format: str = 'text') -> str:
        """Generate human-readable report of sentence-level analysis."""
        if output_format == 'text':
            return self._generate_text_report(results)
        elif output_format == 'html':
            return self._generate_html_report(results)
        else:
            return str(results)
    
    def _generate_text_report(self, results: Dict) -> str:
        """Generate text format report."""
        lines = []
        lines.append("=" * 70)
        lines.append("SENTENCE-LEVEL AI DETECTION REPORT")
        lines.append("=" * 70)
        lines.append(f"\nTotal Sentences Analyzed: {results['total_sentences']}")
        lines.append(f"AI-Generated Sentences: {results['ai_sentences']} ({results['overall_ai_percentage']:.1f}%)")
        lines.append(f"Human-Written Sentences: {results['human_sentences']} ({100-results['overall_ai_percentage']:.1f}%)")
        
        lines.append("\n" + "=" * 70)
        lines.append("PARAGRAPH-BY-PARAGRAPH BREAKDOWN")
        lines.append("=" * 70)
        
        for para in results['paragraph_summaries'][:10]:  # First 10 paragraphs
            lines.append(f"\nParagraph {para['paragraph_number']}:")
            lines.append(f"  Sentences: {para['analyzed']} total, {para['ai_sentences']} AI ({para['ai_percentage']:.1f}%)")
            lines.append(f"  Preview: {para['preview']}")
            
            # Add classification
            if para['ai_percentage'] > 75:
                lines.append(f"  ⚠️ Likely AI-GENERATED paragraph")
            elif para['ai_percentage'] > 50:
                lines.append(f"  ~ MIXED human/AI paragraph")
            else:
                lines.append(f"  ✓ Likely HUMAN-WRITTEN paragraph")
        
        # Show some example sentences
        if results.get('all_sentences'):
            lines.append("\n" + "=" * 70)
            lines.append("EXAMPLE SENTENCE CLASSIFICATIONS")
            lines.append("=" * 70)
            
            ai_examples = [s for s in results['all_sentences'] if s['classification'] == 'AI'][:5]
            human_examples = [s for s in results['all_sentences'] if s['classification'] == 'HUMAN'][:5]
            
            if ai_examples:
                lines.append("\nAI-Generated Sentences:")
                for sent in ai_examples:
                    lines.append(f"\n  [{sent['ai_score']*100:.0f}% AI] {sent['text'][:100]}...")
                    if sent['likely_model'] != 'Unknown':
                        lines.append(f"  Model: {sent['likely_model']}")
            
            if human_examples:
                lines.append("\nHuman-Written Sentences:")
                for sent in human_examples:
                    lines.append(f"\n  [{sent['ai_score']*100:.0f}% AI] {sent['text'][:100]}...")
        
        return '\n'.join(lines)
    
    def _generate_html_report(self, results: Dict) -> str:
        """Generate HTML format report with color-coding."""
        html = ['<!DOCTYPE html><html><head><style>']
        html.append('.ai { background-color: #ffcccc; padding: 5px; }')
        html.append('.human { background-color: #ccffcc; padding: 5px; }')
        html.append('.mixed { background-color: #ffffcc; padding: 5px; }')
        html.append('</style></head><body>')
        html.append('<h1>Sentence-Level AI Detection</h1>')
        html.append(f'<p>Total: {results["total_sentences"]} sentences</p>')
        html.append(f'<p>AI: {results["ai_sentences"]} ({results["overall_ai_percentage"]:.1f}%)</p>')
        
        for para in results['paragraph_summaries'][:10]:
            html.append(f'<h3>Paragraph {para["paragraph_number"]}</h3>')
            html.append(f'<p>{para["preview"]}</p>')
            html.append(f'<p>AI: {para["ai_percentage"]:.1f}%</p>')
        
        html.append('</body></html>')
        return ''.join(html)


def main():
    """Demo sentence-level detection."""
    import sys
    
    if len(sys.argv) < 2:
        # Demo with sample text
        sample = """
        The 2025 Canadian Budget allocates significant resources to infrastructure development. 
        This comprehensive approach will enable transformative investments across multiple sectors. 
        Key stakeholders include citizens, businesses, and local governments. 
        Total spending is projected at $500 billion over five years. 
        According to economic analysis, this will create approximately 200,000 new jobs. 
        The framework establishes clear governance structures to support implementation.
        """
        
        print("Running demo on sample text...\n")
        detector = SentenceLevelDetector(threshold=0.5)
        results = detector.analyze_paragraph(sample)
        
        print("SENTENCE-BY-SENTENCE ANALYSIS:")
        print("=" * 70)
        for sent in results['sentences']:
            classification = sent['classification']
            marker = '🤖' if classification == 'AI' else '✍️' if classification == 'HUMAN' else '~'
            print(f"\n{marker} [{classification}] ({sent['ai_score']*100:.0f}% AI)")
            print(f"   {sent['text'][:100]}...")
        
        print("\n" + "=" * 70)
        print("SUMMARY:")
        print(f"  AI Sentences: {results['summary']['ai_sentences']}/{results['summary']['total_sentences']}")
        print(f"  Percentage: {results['summary']['ai_percentage']:.1f}%")
        
    else:
        # Analyze file
        print(f"Analyzing {sys.argv[1]}...")
        # Implementation for file input


if __name__ == '__main__':
    main()

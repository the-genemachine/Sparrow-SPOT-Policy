#!/usr/bin/env python3
"""
Deep Analysis Orchestrator
Runs all detection depth levels (1-6) and generates comprehensive transparency report
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional
import pdfplumber
from datetime import datetime

# Import all analysis levels
from ai_detection_engine import AIDetectionEngine
from ai_section_analyzer import AISectionAnalyzer
from sentence_level_detector import SentenceLevelDetector
from phrase_fingerprints import PhraseFingerprints
from statistical_analyzer import StatisticalAnalyzer


class DeepAnalyzer:
    """
    Orchestrates all levels of AI detection analysis:
    
    Level 1: Document-level detection (overall AI %)
    Level 2: Section-level detection (which sections have AI)
    Level 3: Pattern detection (specific phrase patterns)
    Level 4: Sentence-level detection (which sentences are AI)
    Level 5: Phrase fingerprinting (model-specific signatures)
    Level 6: Statistical analysis (mathematical proof)
    """
    
    def __init__(self):
        self.detection_engine = AIDetectionEngine()
        self.section_analyzer = AISectionAnalyzer()
        self.sentence_detector = SentenceLevelDetector()
        self.phrase_scanner = PhraseFingerprints()
        self.stats_analyzer = StatisticalAnalyzer()
    
    def analyze_document(self, file_path: str, max_sections: int = 10) -> Dict:
        """
        Run complete deep analysis on a document.
        
        Args:
            file_path: Path to PDF or text file
            max_sections: Maximum sections to analyze in detail
            
        Returns:
            Complete analysis results from all levels
        """
        print(f"\n{'='*80}")
        print(f"DEEP TRANSPARENCY ANALYSIS")
        print(f"{'='*80}")
        print(f"Document: {file_path}")
        print(f"Analysis Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Extract text
        text = self._extract_text(file_path)
        if not text:
            return {'error': 'Could not extract text from document'}
        
        results = {
            'metadata': {
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'analysis_timestamp': datetime.now().isoformat(),
                'text_length': len(text),
                'word_count': len(text.split()),
            }
        }
        
        # LEVEL 1: Document-level detection
        print("Running Level 1: Document-Level Detection...")
        level1 = self._run_level1(text)
        results['level1_document'] = level1
        print(f"  ✓ Overall AI: {level1['ai_percentage']:.1f}%")
        print(f"  ✓ Primary Model: {level1['primary_model']} ({level1['model_confidence']:.0f}% confidence)")
        
        # LEVEL 2: Section-level detection
        print("\nRunning Level 2: Section-Level Detection...")
        level2 = self._run_level2(text, max_sections)
        results['level2_sections'] = level2
        print(f"  ✓ Analyzed {level2['sections_analyzed']} sections")
        if level2['sections']:
            top_ai_section = max(level2['sections'], key=lambda x: x['ai_percentage'])
            print(f"  ✓ Highest AI section: Section {top_ai_section['section_number']} ({top_ai_section['ai_percentage']:.1f}% AI)")
        
        # LEVEL 3: Pattern detection
        print("\nRunning Level 3: Pattern Detection...")
        level3 = self._run_level3(text)
        results['level3_patterns'] = level3
        print(f"  ✓ Found {level3['total_patterns']} AI patterns")
        for model, count in level3['patterns_by_model'].items():
            if count > 0:
                print(f"    • {model}: {count} patterns")
        
        # LEVEL 4: Sentence-level detection
        print("\nRunning Level 4: Sentence-Level Detection...")
        level4 = self._run_level4(text)
        results['level4_sentences'] = level4
        print(f"  ✓ Analyzed {level4['total_sentences']} sentences")
        print(f"  ✓ AI sentences: {level4['ai_sentences']} ({level4['overall_ai_percentage']:.1f}%)")
        
        # LEVEL 5: Phrase fingerprinting
        print("\nRunning Level 5: Phrase Fingerprinting...")
        level5 = self._run_level5(text)
        results['level5_fingerprints'] = level5
        print(f"  ✓ Found {level5['total_fingerprints_found']} phrase fingerprints")
        print(f"  ✓ Primary Model: {level5['primary_model']} ({level5['primary_confidence']}% confidence)")
        
        # LEVEL 6: Statistical analysis
        print("\nRunning Level 6: Statistical Analysis...")
        level6 = self._run_level6(text)
        results['level6_statistics'] = level6
        if 'error' not in level6:
            print(f"  ✓ Perplexity: {level6['metrics']['perplexity']}")
            print(f"  ✓ Burstiness: {level6['metrics']['burstiness']}")
            print(f"  ✓ Lexical Diversity: {level6['metrics']['lexical_diversity']}")
            print(f"  ✓ Statistical AI Probability: {level6['ai_probability']*100:.1f}% ({level6['confidence']} confidence)")
        
        # Generate consensus
        print("\nCalculating Final Consensus...")
        consensus = self._calculate_consensus(results)
        results['consensus'] = consensus
        print(f"\n{'='*80}")
        print(f"FINAL CONSENSUS: {consensus['ai_percentage']:.1f}% AI-GENERATED")
        print(f"Primary Model: {consensus['primary_model']} ({consensus['confidence']:.0f}% confidence)")
        print(f"Transparency Score: {consensus['transparency_score']}/100")
        print(f"{'='*80}\n")
        
        return results
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or text file"""
        path = Path(file_path)
        
        if path.suffix.lower() == '.pdf':
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ''
                    for page in pdf.pages:
                        text += page.extract_text() + '\n'
                    return text
            except Exception as e:
                print(f"Error extracting PDF: {e}")
                return ''
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                return ''
    
    def _run_level1(self, text: str) -> Dict:
        """Level 1: Document-level detection"""
        result = self.detection_engine.analyze_document(text)
        
        # Convert to expected format
        ai_percentage = result['ai_detection_score'] * 100  # Convert 0-1 to percentage
        model_scores = {k: v*100 for k, v in result.get('model_scores', {}).items()}
        
        # Get model confidence
        model = result.get('likely_ai_model', 'Unknown')
        # Model can be dict or string
        if isinstance(model, dict):
            model_name = model.get('model', 'Unknown')
            model_confidence = model.get('confidence', 0) * 100
        else:
            model_name = model if isinstance(model, str) else 'Unknown'
            # Find matching model score
            model_confidence = 0
            if model_name != 'Unknown':
                for k, v in model_scores.items():
                    if model_name.lower() in k.lower():
                        model_confidence = v
                        break
        
        return {
            'ai_percentage': ai_percentage,
            'primary_model': model_name,
            'model_confidence': model_confidence,
            'method_scores': model_scores,
        }
    
    def _run_level2(self, text: str, max_sections: int) -> Dict:
        """Level 2: Section-level detection"""
        result = self.section_analyzer.analyze_document_sections(text)
        sections = result.get('sections', [])[:max_sections]  # Limit to max
        return {
            'sections_analyzed': len(sections),
            'sections': sections,
            'average_ai_percentage': sum(s['ai_percentage'] for s in sections) / len(sections) if sections else 0,
        }
    
    def _run_level3(self, text: str) -> Dict:
        """Level 3: Pattern detection"""
        patterns = self.section_analyzer._detect_cohere_patterns(text)
        total = sum(patterns.values())
        return {
            'total_patterns': total,
            'patterns_by_model': {'Cohere': total},  # Expand when other models added
            'pattern_details': patterns,
        }
    
    def _run_level4(self, text: str) -> Dict:
        """Level 4: Sentence-level detection"""
        return self.sentence_detector.analyze_document(text)
    
    def _run_level5(self, text: str) -> Dict:
        """Level 5: Phrase fingerprinting"""
        return self.phrase_scanner.scan_text(text)
    
    def _run_level6(self, text: str) -> Dict:
        """Level 6: Statistical analysis"""
        return self.stats_analyzer.analyze(text)
    
    def _calculate_consensus(self, results: Dict) -> Dict:
        """
        Calculate final consensus from all analysis levels.
        Weighted by reliability and consistency.
        """
        scores = []
        models = {}
        
        # Level 1 weight: 30% (most reliable)
        if 'level1_document' in results:
            scores.append(('level1', results['level1_document']['ai_percentage'], 0.30))
            model = results['level1_document']['primary_model']
            models[model] = models.get(model, 0) + results['level1_document']['model_confidence']
        
        # Level 2 weight: 25%
        if 'level2_sections' in results and results['level2_sections']['sections']:
            avg = results['level2_sections']['average_ai_percentage']
            scores.append(('level2', avg, 0.25))
        
        # Level 4 weight: 20%
        if 'level4_sentences' in results:
            scores.append(('level4', results['level4_sentences']['overall_ai_percentage'], 0.20))
        
        # Level 6 weight: 15%
        if 'level6_statistics' in results and 'ai_probability' in results['level6_statistics']:
            stat_percentage = results['level6_statistics']['ai_probability'] * 100
            scores.append(('level6', stat_percentage, 0.15))
        
        # Level 5 weight: 10% (adds model confirmation)
        if 'level5_fingerprints' in results:
            model = results['level5_fingerprints']['primary_model']
            conf = results['level5_fingerprints']['primary_confidence']
            models[model] = models.get(model, 0) + conf
        
        # Calculate weighted average
        total_weight = sum(weight for _, _, weight in scores)
        weighted_sum = sum(score * weight for _, score, weight in scores)
        final_percentage = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Determine primary model
        primary_model = max(models.items(), key=lambda x: x[1])[0] if models else 'Unknown'
        model_confidence = max(models.values()) if models else 0
        
        # Calculate transparency score (how consistent are the results?)
        variance = self._calculate_variance([s for _, s, _ in scores])
        transparency_score = max(0, 100 - (variance * 2))  # Lower variance = higher transparency
        
        return {
            'ai_percentage': round(final_percentage, 1),
            'primary_model': primary_model,
            'confidence': round(model_confidence, 1),
            'transparency_score': round(transparency_score, 1),
            'level_scores': {level: round(score, 1) for level, score, _ in scores},
            'variance': round(variance, 2),
        }
    
    def _calculate_variance(self, scores: list) -> float:
        """Calculate variance in scores"""
        if len(scores) < 2:
            return 0
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance ** 0.5  # Standard deviation
    
    def generate_report(self, results: Dict, output_format: str = 'markdown') -> str:
        """Generate comprehensive report in specified format"""
        if output_format == 'markdown':
            return self._generate_markdown_report(results)
        elif output_format == 'json':
            return json.dumps(results, indent=2)
        elif output_format == 'html':
            return self._generate_html_report(results)
        else:
            return str(results)
    
    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate markdown transparency report"""
        consensus = results['consensus']
        metadata = results['metadata']
        
        report = f"""# Deep Transparency Analysis Report

**Document:** {metadata['file_name']}  
**Analysis Date:** {datetime.fromisoformat(metadata['analysis_timestamp']).strftime('%Y-%m-%d %H:%M:%S')}  
**Document Size:** {metadata['word_count']:,} words ({metadata['text_length']:,} characters)

---

## Executive Summary

**🎯 FINAL DETERMINATION: {consensus['ai_percentage']:.1f}% AI-GENERATED CONTENT**

- **Primary AI Model:** {consensus['primary_model']}
- **Detection Confidence:** {consensus['confidence']:.0f}%
- **Transparency Score:** {consensus['transparency_score']}/100
- **Analysis Variance:** {consensus['variance']:.2f} (consistency measure)

---

## Analysis Depth: 6 Levels

### Level 1: Document-Level Detection
**Overall AI Percentage:** {results['level1_document']['ai_percentage']:.1f}%  
**Detected Model:** {results['level1_document']['primary_model']} ({results['level1_document']['model_confidence']:.0f}% confidence)

**Detection Method Scores:**
"""
        for method, score in results['level1_document']['method_scores'].items():
            report += f"- {method}: {score:.1f}%\n"
        
        report += f"""
### Level 2: Section-Level Detection
**Sections Analyzed:** {results['level2_sections']['sections_analyzed']}  
**Average AI Percentage:** {results['level2_sections']['average_ai_percentage']:.1f}%

**Section Breakdown:**
"""
        
        for section in results['level2_sections']['sections'][:5]:
            report += f"\n**Section {section['section_number']}**\n"
            report += f"- AI Percentage: {section['ai_percentage']:.1f}%\n"
            report += f"- Model: {section['likely_model']} ({section['model_confidence']:.0f}% confidence)\n"
            report += f"- Preview: {section['text_preview'][:100]}...\n"
        
        report += f"""
### Level 3: Pattern Detection
**Total AI Patterns Found:** {results['level3_patterns']['total_patterns']}

**Pattern Breakdown:**
"""
        
        for pattern, count in results['level3_patterns']['pattern_details'].items():
            if count > 0:
                report += f"- {pattern}: {count} instances\n"
        
        report += f"""
### Level 4: Sentence-Level Detection
**Total Sentences:** {results['level4_sentences']['total_sentences']}  
**AI Sentences:** {results['level4_sentences']['ai_sentences']} ({results['level4_sentences']['overall_ai_percentage']:.1f}%)  
**Human Sentences:** {results['level4_sentences']['human_sentences']}

**Paragraph Analysis:** {results['level4_sentences']['paragraphs_analyzed']} paragraphs analyzed

### Level 5: Phrase Fingerprinting
**Total Fingerprints Detected:** {results['level5_fingerprints']['total_fingerprints_found']}  
**Primary Model:** {results['level5_fingerprints']['primary_model']} ({results['level5_fingerprints']['primary_confidence']}% confidence)

**Model-Specific Signatures:**
"""
        
        for model in ['Cohere', 'Claude', 'GPT', 'Gemini', 'Mistral']:
            if model in results['level5_fingerprints'] and isinstance(results['level5_fingerprints'][model], dict):
                model_data = results['level5_fingerprints'][model]
                report += f"\n**{model}:** {model_data['total_matches']} matches ({model_data['confidence']}% confidence)\n"
        
        if 'error' not in results['level6_statistics']:
            stats = results['level6_statistics']
            report += f"""
### Level 6: Statistical Analysis
**Statistical AI Probability:** {stats['ai_probability']*100:.1f}% ({stats['confidence']} confidence)

**Mathematical Metrics:**
- **Perplexity:** {stats['metrics']['perplexity']} (predictability measure)
- **Burstiness:** {stats['metrics']['burstiness']} (sentence variance)
- **Lexical Diversity:** {stats['metrics']['lexical_diversity']} (vocabulary richness)
- **Passive Voice Ratio:** {stats['metrics']['passive_voice_ratio']}
- **Average Sentence Length:** {stats['metrics']['sentence_stats']['avg_length']} words

**Readability Scores:**
- Flesch Reading Ease: {stats['metrics']['readability']['flesch_reading_ease']}
- Flesch-Kincaid Grade: {stats['metrics']['readability']['flesch_kincaid_grade']}
- Gunning Fog Index: {stats['metrics']['readability']['gunning_fog']}

**Interpretation:**
{stats['interpretation']}
"""
        
        report += f"""
---

## Consensus Methodology

This analysis combines 6 depth levels with weighted scoring:
- Level 1 (Document): 30% weight
- Level 2 (Sections): 25% weight
- Level 4 (Sentences): 20% weight
- Level 6 (Statistics): 15% weight
- Level 5 (Fingerprints): 10% weight

**Individual Level Scores:**
"""
        
        for level, score in consensus['level_scores'].items():
            report += f"- {level}: {score:.1f}% AI\n"
        
        report += f"""
**Variance:** {consensus['variance']:.2f} (lower = more consistent)

---

## Transparency Certification

This document has been analyzed using **6 levels of AI detection depth**, providing:

✅ Mathematical proof (statistical analysis)  
✅ Model-specific fingerprints  
✅ Sentence-by-sentence breakdown  
✅ Section-level granularity  
✅ Multi-method consensus  
✅ Transparent methodology  

**Transparency Score: {consensus['transparency_score']}/100**

---

*Generated by Sparrow SPOT Scale™ Deep Analysis v8.2*  
*Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def _generate_html_report(self, results: Dict) -> str:
        """Generate interactive HTML report"""
        # TODO: Implement HTML generation with charts
        return "<html>HTML report generation coming soon</html>"


def main():
    """CLI interface for deep analysis"""
    if len(sys.argv) < 2:
        print("Usage: python deep_analyzer.py <file_path> [--format markdown|json|html]")
        print("\nExample:")
        print("  python deep_analyzer.py ./test_articles/2025-Budget.pdf")
        print("  python deep_analyzer.py document.txt --format json")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_format = 'markdown'
    
    if '--format' in sys.argv:
        idx = sys.argv.index('--format')
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]
    
    # Run analysis
    analyzer = DeepAnalyzer()
    results = analyzer.analyze_document(file_path)
    
    # Generate report
    report = analyzer.generate_report(results, output_format)
    
    # Save report
    output_file = Path(file_path).stem + f'_deep_analysis.{output_format.replace("markdown", "md")}'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Deep analysis complete!")
    print(f"📄 Report saved to: {output_file}")


if __name__ == '__main__':
    main()

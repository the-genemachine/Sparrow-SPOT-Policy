#!/usr/bin/env python3
"""
Discretionary Power Analyzer (DPA)
Part of Sparrow SPOT Scale™ v8.5 - Legislative Threat Detection Suite

Detects and analyzes discretionary powers in legislative documents:
- Permissive language ("may", "may by order")
- Self-judgment clauses ("in the minister's opinion")
- Undefined timelines ("as soon as feasible")
- Broad scope language ("any entity", "any provision")
- Exclusion powers ("may exclude", "may exempt")

Author: Sparrow Development Team
Created: 2025-12-07
Version: 8.5.0
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict


class DiscretionaryPowerAnalyzer:
    """
    Analyzes legislative documents for discretionary power grants and
    potential accountability gaps.
    """
    
    def __init__(self, output_dir: str = "legislative_analysis/discretionary_power"):
        """
        Initialize the Discretionary Power Analyzer.
        
        Args:
            output_dir: Directory to save analysis outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Pattern definitions with risk levels
        self.patterns = {
            'permissive_language': {
                'patterns': [
                    r'\bmay\b(?!\s+not)',  # "may" but not "may not"
                    r'\bmay\s+by\s+order\b',
                    r'\bat\s+the\s+minister\'?s?\s+discretion\b',
                    r'\bat\s+(?:his|her|their)\s+discretion\b',
                    r'\bmay\s+(?:authorize|direct|require|order)\b',
                ],
                'risk_level': 'MEDIUM',
                'description': 'Permissive language granting optional authority'
            },
            'self_judgment': {
                'patterns': [
                    r'\bin\s+the\s+minister\'?s?\s+opinion\b',
                    r'\bif\s+the\s+minister\s+(?:is\s+)?satisfied\b',
                    r'\bconsiders?\s+(?:it\s+)?appropriate\b',
                    r'\bdeems?\s+(?:it\s+)?(?:necessary|appropriate|advisable)\b',
                    r'\bin\s+(?:his|her|their)\s+opinion\b',
                    r'\bif\s+(?:he|she|they)\s+(?:is\s+)?satisfied\b',
                    r'\bthe\s+minister\s+may\s+determine\b',
                    r'\bas\s+the\s+minister\s+(?:sees\s+fit|thinks\s+fit)\b',
                ],
                'risk_level': 'HIGH',
                'description': 'Self-judgment clauses where decision-maker is sole arbiter'
            },
            'undefined_timelines': {
                'patterns': [
                    r'\bas\s+soon\s+as\s+(?:feasible|practicable|possible)\b',
                    r'\bwithin\s+a\s+reasonable\s+(?:time|period)\b',
                    r'\bpromptly\b(?!\s+(?:within|before|by))',
                    r'\bwithout\s+delay\b(?!\s+(?:within|before|by))',
                    r'\bin\s+a\s+timely\s+manner\b',
                    r'\bas\s+(?:expeditiously|quickly)\s+as\s+(?:possible|practicable)\b',
                ],
                'risk_level': 'MEDIUM',
                'description': 'Undefined or vague timelines with no enforcement mechanism'
            },
            'broad_scope': {
                'patterns': [
                    r'\bany\s+entity\b',
                    r'\bany\s+provision\b',
                    r'\bany\s+federal\s+law\b',
                    r'\bfor\s+any\s+purpose\b',
                    r'\bany\s+(?:person|organization|company|corporation)\b',
                    r'\bany\s+requirement\s+of\s+this\s+Act\b',
                    r'\ball\s+or\s+any\s+part\s+of\b',
                    r'\bany\s+other\s+Act\s+of\s+Parliament\b',
                ],
                'risk_level': 'CRITICAL',
                'description': 'Broad scope language applying to wide categories'
            },
            'exclusion_powers': {
                'patterns': [
                    r'\bmay\s+exclude\b',
                    r'\bmay\s+exempt\b',
                    r'\bmay\s+waive\b',
                    r'\bexempt\s+from\s+the\s+application\s+of\b',
                    r'\brelieve\s+from\s+(?:the\s+)?obligation\b',
                    r'\bmay\s+dispense\s+with\b',
                    r'\bmay\s+grant\s+(?:an\s+)?exemption\b',
                ],
                'risk_level': 'HIGH',
                'description': 'Powers to exclude, exempt, or waive requirements'
            }
        }
        
        # Keywords that indicate power concentration
        self.power_keywords = [
            'minister', 'governor', 'cabinet', 'council',
            'authority', 'power', 'discretion', 'determine'
        ]
        
    def analyze(self, text: str, document_name: str = "document") -> Dict[str, Any]:
        """
        Analyze a legislative document for discretionary powers.
        
        Args:
            text: The legislative document text
            document_name: Name of the document for reporting
            
        Returns:
            Dictionary containing analysis results
        """
        findings = []
        pattern_counts = defaultdict(int)
        
        # Split into sections for better location tracking
        sections = self._split_into_sections(text)
        
        # Analyze each pattern type
        for pattern_type, config in self.patterns.items():
            for pattern_str in config['patterns']:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                
                for section_info in sections:
                    matches = pattern.finditer(section_info['text'])
                    
                    for match in matches:
                        context = self._extract_context(
                            section_info['text'], 
                            match.start(), 
                            match.end()
                        )
                        
                        finding = {
                            'pattern_type': pattern_type,
                            'pattern': pattern_str,
                            'matched_text': match.group(),
                            'location': {
                                'section': section_info['section'],
                                'position': section_info['position']
                            },
                            'context': context,
                            'risk_level': config['risk_level'],
                            'risk_assessment': self._assess_risk(
                                pattern_type, 
                                context, 
                                config['risk_level']
                            )
                        }
                        
                        findings.append(finding)
                        pattern_counts[pattern_type] += 1
        
        # Calculate scores
        discretionary_score = self._calculate_discretionary_score(pattern_counts)
        power_concentration = self._calculate_power_concentration(text, findings)
        
        # Determine overall risk level
        overall_risk = self._determine_overall_risk(discretionary_score, findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings, pattern_counts)
        
        # Compile results
        results = {
            'document_name': document_name,
            'analysis_timestamp': datetime.now().isoformat(),
            'discretionary_power_score': round(discretionary_score, 2),
            'power_concentration_index': round(power_concentration, 2),
            'risk_level': overall_risk,
            'total_findings': len(findings),
            'pattern_breakdown': dict(pattern_counts),
            'findings': findings,
            'recommendations': recommendations,
            'summary': self._generate_summary(
                discretionary_score, 
                power_concentration, 
                overall_risk, 
                pattern_counts
            )
        }
        
        return results
    
    def _split_into_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Split document into sections for location tracking.
        
        Args:
            text: Document text
            
        Returns:
            List of section dictionaries with text and metadata
        """
        sections = []
        
        # Try to detect section markers (Division, Part, Section, etc.)
        section_pattern = re.compile(
            r'(?:^|\n)\s*(?:Division|Part|Section|Article|Chapter)\s+[\d\w]+',
            re.IGNORECASE | re.MULTILINE
        )
        
        matches = list(section_pattern.finditer(text))
        
        if matches:
            # Document has clear sections
            for i, match in enumerate(matches):
                start = match.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                section_text = text[start:end]
                
                sections.append({
                    'section': match.group().strip(),
                    'text': section_text,
                    'position': round((start / len(text)) * 100, 2)
                })
        else:
            # No clear sections, divide into pages (assuming ~3000 chars/page)
            page_size = 3000
            num_pages = (len(text) + page_size - 1) // page_size
            
            for i in range(num_pages):
                start = i * page_size
                end = min((i + 1) * page_size, len(text))
                
                sections.append({
                    'section': f'Page {i + 1} (est.)',
                    'text': text[start:end],
                    'position': round((start / len(text)) * 100, 2)
                })
        
        return sections
    
    def _extract_context(self, text: str, match_start: int, match_end: int, 
                        context_chars: int = 200) -> str:
        """
        Extract context around a matched pattern.
        
        Args:
            text: Full text
            match_start: Start position of match
            match_end: End position of match
            context_chars: Characters to include on each side
            
        Returns:
            Context string with match highlighted
        """
        start = max(0, match_start - context_chars)
        end = min(len(text), match_end + context_chars)
        
        before = text[start:match_start]
        matched = text[match_start:match_end]
        after = text[match_end:end]
        
        # Clean up whitespace
        context = f"{before}**{matched}**{after}"
        context = re.sub(r'\s+', ' ', context).strip()
        
        # Clean up bilingual text artifacts
        context = self._clean_bilingual_text(context)
        
        return context
    
    def _clean_bilingual_text(self, text: str) -> str:
        """
        Clean up bilingual (English/French) text artifacts and duplicates.
        
        Args:
            text: Raw text possibly containing bilingual artifacts
            
        Returns:
            Cleaned text with better formatting
        """
        # Remove obvious duplicate patterns (garbled repetitions)
        # Pattern: text followed by similar-looking corrupted version
        text = re.sub(r'(\b\w+\b)\s+\(\1\)', r'\1', text)  # Remove (duplicate) patterns
        
        # Clean up common bilingual markers
        # Keep content before French section markers if they appear
        french_markers = [
            r'\s+a\)\s+[a-z]{3,}(?:\s+[a-z]{3,}){3,}',  # Detect French: "a) word word word word"
            r'\s+b\)\s+[a-z]{3,}(?:\s+[a-z]{3,}){3,}',  # Detect French: "b) word word word word"
        ]
        
        for marker in french_markers:
            # If we detect what looks like French translation starting, truncate there
            match = re.search(marker, text)
            if match:
                # Keep English portion only (before the French translation)
                text = text[:match.start()].strip()
        
        # Remove garbled character sequences (likely encoding issues)
        # Pattern: sequences of accented characters mixed with random chars
        text = re.sub(r'[éèêëàâäôöûüîïç]{3,}', '', text)  # Remove clusters of accented chars
        text = re.sub(r'\b[a-z]{1,2}[a-z]{1,2}[a-z]{1,2}\b', lambda m: '' if len(set(m.group())) < 2 else m.group(), text)
        
        # Clean up duplicate whitespace again after cleaning
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit length to avoid extremely long contexts
        if len(text) > 500:
            # Find a good break point near the match (the ** markers)
            match_pos = text.find('**')
            if match_pos > 250:
                # Keep text centered around the match
                start = max(0, match_pos - 200)
                end = min(len(text), match_pos + 300)
                text = '...' + text[start:end] + '...'
            else:
                text = text[:500] + '...'
        
        return text
    
    def _assess_risk(self, pattern_type: str, context: str, base_risk: str) -> str:
        """
        Assess risk based on pattern type and context.
        
        Args:
            pattern_type: Type of pattern matched
            context: Surrounding text
            base_risk: Base risk level from pattern
            
        Returns:
            Risk assessment string
        """
        assessments = {
            'permissive_language': "Grants optional authority; enforcement depends on political will",
            'self_judgment': "Decision-maker is sole arbiter with no explicit appeal mechanism",
            'undefined_timelines': "No enforceable deadline; may enable indefinite delay",
            'broad_scope': "Applies to wide category; potential for over-broad application",
            'exclusion_powers': "Power to exempt or exclude; creates accountability gaps"
        }
        
        base_assessment = assessments.get(pattern_type, "Requires scrutiny")
        
        # Enhanced assessment if combined with other risk factors
        if pattern_type == 'self_judgment' and 'may exclude' in context.lower():
            return f"{base_assessment}. ELEVATED: Combined with exclusion power"
        elif pattern_type == 'broad_scope' and 'any federal law' in context.lower():
            return f"{base_assessment}. ELEVATED: Applies across all federal legislation"
        
        return base_assessment
    
    def _calculate_discretionary_score(self, pattern_counts: Dict[str, int]) -> float:
        """
        Calculate discretionary power score (0-100).
        
        Args:
            pattern_counts: Count of each pattern type
            
        Returns:
            Score from 0-100
        """
        # Weight different pattern types
        weights = {
            'permissive_language': 1.0,
            'self_judgment': 2.5,
            'undefined_timelines': 1.5,
            'broad_scope': 3.0,
            'exclusion_powers': 2.5
        }
        
        weighted_sum = sum(
            pattern_counts[ptype] * weights.get(ptype, 1.0)
            for ptype in pattern_counts
        )
        
        # Normalize to 0-100 scale (cap at 50 occurrences for max score)
        score = min(100, (weighted_sum / 50) * 100)
        
        return score
    
    def _calculate_power_concentration(self, text: str, findings: List[Dict]) -> float:
        """
        Calculate power concentration index (0-100).
        
        Args:
            text: Full document text
            findings: List of findings
            
        Returns:
            Power concentration index
        """
        # Count power keywords
        keyword_count = sum(
            len(re.findall(rf'\b{keyword}\b', text, re.IGNORECASE))
            for keyword in self.power_keywords
        )
        
        # Normalize by document length
        words = len(text.split())
        keyword_density = (keyword_count / words) * 100 if words > 0 else 0
        
        # Check for power concentration in findings
        minister_decisions = sum(
            1 for f in findings
            if 'minister' in f['context'].lower() and f['pattern_type'] == 'self_judgment'
        )
        
        # Combine metrics
        concentration_score = min(100, (keyword_density * 10) + (minister_decisions * 2))
        
        return concentration_score
    
    def _determine_overall_risk(self, score: float, findings: List[Dict]) -> str:
        """
        Determine overall risk level.
        
        Args:
            score: Discretionary power score
            findings: List of findings
            
        Returns:
            Risk level string
        """
        critical_findings = sum(1 for f in findings if f['risk_level'] == 'CRITICAL')
        high_findings = sum(1 for f in findings if f['risk_level'] == 'HIGH')
        
        if score >= 70 or critical_findings >= 5:
            return 'CRITICAL'
        elif score >= 50 or critical_findings >= 2 or high_findings >= 10:
            return 'HIGH'
        elif score >= 30 or high_findings >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendations(self, findings: List[Dict], 
                                 pattern_counts: Dict[str, int]) -> List[str]:
        """
        Generate recommendations based on findings.
        
        Args:
            findings: List of findings
            pattern_counts: Pattern type counts
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if pattern_counts.get('self_judgment', 0) > 5:
            recommendations.append(
                "PRIORITY: Add independent review mechanism for ministerial decisions"
            )
        
        if pattern_counts.get('broad_scope', 0) > 3:
            recommendations.append(
                "PRIORITY: Narrow scope of exemption/exclusion powers with explicit limitations"
            )
        
        if pattern_counts.get('undefined_timelines', 0) > 5:
            recommendations.append(
                "Add specific deadlines with enforcement mechanisms"
            )
        
        if pattern_counts.get('exclusion_powers', 0) > 3:
            recommendations.append(
                "Require public disclosure and justification for all exemptions granted"
            )
        
        # Check for dangerous combinations
        if (pattern_counts.get('self_judgment', 0) > 3 and 
            pattern_counts.get('exclusion_powers', 0) > 3):
            recommendations.append(
                "CRITICAL: Combination of self-judgment + exclusion powers creates " +
                "accountability gap. Add parliamentary oversight requirement."
            )
        
        if not recommendations:
            recommendations.append(
                "Document shows reasonable balance of discretionary authority"
            )
        
        return recommendations
    
    def _generate_summary(self, score: float, concentration: float, 
                         risk_level: str, pattern_counts: Dict[str, int]) -> str:
        """
        Generate executive summary.
        
        Args:
            score: Discretionary power score
            concentration: Power concentration index
            risk_level: Overall risk level
            pattern_counts: Pattern counts
            
        Returns:
            Summary string
        """
        total_patterns = sum(pattern_counts.values())
        
        summary = f"Discretionary Power Analysis: {risk_level} RISK\n\n"
        summary += f"Detected {total_patterns} instances of discretionary power language "
        summary += f"(Score: {score:.1f}/100, Concentration: {concentration:.1f}/100).\n\n"
        
        if pattern_counts:
            summary += "Breakdown:\n"
            for ptype, count in sorted(pattern_counts.items(), 
                                      key=lambda x: x[1], reverse=True):
                summary += f"  - {ptype.replace('_', ' ').title()}: {count}\n"
        
        if risk_level in ['CRITICAL', 'HIGH']:
            summary += "\nThis document grants significant discretionary authority with "
            summary += "limited oversight mechanisms. Independent review recommended."
        
        return summary
    
    def save_results(self, results: Dict[str, Any], 
                    format: str = 'json') -> Path:
        """
        Save analysis results to file.
        
        Args:
            results: Analysis results dictionary
            format: Output format ('json' or 'markdown')
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        doc_name = results['document_name'].replace(' ', '_').replace('.', '_')
        
        if format == 'json':
            filename = f"{doc_name}_dpa_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        elif format == 'markdown':
            filename = f"{doc_name}_dpa_{timestamp}.md"
            filepath = self.output_dir / filename
            
            md_content = self._format_markdown_report(results)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
        
        return filepath
    
    def _format_markdown_report(self, results: Dict[str, Any]) -> str:
        """
        Format results as markdown report.
        
        Args:
            results: Analysis results
            
        Returns:
            Markdown formatted string
        """
        md = f"# Discretionary Power Analysis Report\n\n"
        md += f"**Document:** {results['document_name']}  \n"
        md += f"**Analysis Date:** {results['analysis_timestamp']}  \n"
        md += f"**Risk Level:** {results['risk_level']}  \n\n"
        
        md += f"## Executive Summary\n\n"
        md += results['summary'] + "\n\n"
        
        md += f"## Metrics\n\n"
        md += f"- **Discretionary Power Score:** {results['discretionary_power_score']}/100\n"
        md += f"- **Power Concentration Index:** {results['power_concentration_index']}/100\n"
        md += f"- **Total Findings:** {results['total_findings']}\n\n"
        
        md += f"## Pattern Breakdown\n\n"
        for pattern_type, count in results['pattern_breakdown'].items():
            md += f"- **{pattern_type.replace('_', ' ').title()}:** {count}\n"
        md += "\n"
        
        md += f"## Recommendations\n\n"
        for i, rec in enumerate(results['recommendations'], 1):
            md += f"{i}. {rec}\n"
        md += "\n"
        
        md += f"## Detailed Findings\n\n"
        
        # Group findings by risk level
        for risk_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            level_findings = [f for f in results['findings'] 
                            if f['risk_level'] == risk_level]
            
            if level_findings:
                md += f"### {risk_level} Risk Findings ({len(level_findings)})\n\n"
                
                for i, finding in enumerate(level_findings[:10], 1):  # Limit to first 10
                    md += f"**{i}. {finding['pattern_type'].replace('_', ' ').title()}**\n\n"
                    md += f"- **Location:** {finding['location']['section']} "
                    md += f"({finding['location']['position']}% through document)\n"
                    md += f"- **Matched Text:** `{finding['matched_text']}`\n"
                    md += f"- **Context:** {finding['context']}\n"
                    md += f"- **Assessment:** {finding['risk_assessment']}\n\n"
                
                if len(level_findings) > 10:
                    md += f"*... and {len(level_findings) - 10} more findings at this risk level*\n\n"
        
        md += f"\n---\n\n"
        md += f"*Report generated by Sparrow SPOT Scale™ v8.5 - Legislative Threat Detection Suite*\n"
        
        return md


def main():
    """
    Command-line interface for Discretionary Power Analyzer.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze legislative documents for discretionary powers'
    )
    parser.add_argument('input_file', help='Path to legislative document')
    parser.add_argument('--output-dir', default='legislative_analysis/discretionary_power',
                       help='Output directory for results')
    parser.add_argument('--format', choices=['json', 'markdown', 'both'], 
                       default='both', help='Output format')
    
    args = parser.parse_args()
    
    # Read input file
    with open(args.input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Initialize analyzer
    analyzer = DiscretionaryPowerAnalyzer(output_dir=args.output_dir)
    
    # Run analysis
    document_name = Path(args.input_file).stem
    results = analyzer.analyze(text, document_name)
    
    # Save results
    if args.format in ['json', 'both']:
        json_path = analyzer.save_results(results, format='json')
        print(f"JSON report saved to: {json_path}")
    
    if args.format in ['markdown', 'both']:
        md_path = analyzer.save_results(results, format='markdown')
        print(f"Markdown report saved to: {md_path}")
    
    # Print summary to console
    print("\n" + "="*60)
    print(results['summary'])
    print("="*60)
    print(f"\nRisk Level: {results['risk_level']}")
    print(f"Discretionary Power Score: {results['discretionary_power_score']:.1f}/100")
    print(f"Total Findings: {results['total_findings']}")


if __name__ == '__main__':
    main()

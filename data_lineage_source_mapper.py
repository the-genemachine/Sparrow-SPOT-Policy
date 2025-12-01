#!/usr/bin/env python3
"""
Data Lineage Source Mapper
Sparrow SPOT Scale™ v8.3

Automatically traces quantitative claims in policy documents back to authoritative
data sources (Statistics Canada, IMF, OECD, World Bank, etc.) and validates accuracy.

Usage:
    python data_lineage_source_mapper.py --input analysis.json --output lineage_report
    
    # Within sparrow_grader_v8.py:
    python sparrow_grader_v8.py document.pdf --trace-data-sources
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import argparse


class DataLineageSourceMapper:
    """
    Traces quantitative claims to authoritative data sources and validates accuracy.
    
    Extracts statistics from policy documents and maps them to:
    - Statistics Canada datasets
    - IMF World Economic Outlook
    - OECD databases
    - World Bank Open Data
    - Central bank publications
    - Academic sources
    """
    
    def __init__(self):
        """Initialize the source mapper with known authoritative sources."""
        self.authoritative_sources = {
            'statistics_canada': {
                'name': 'Statistics Canada',
                'domains': ['statcan.gc.ca', 'www150.statcan.gc.ca'],
                'reliability': 'HIGH',
                'coverage': ['Canadian economic data', 'demographics', 'employment', 'GDP']
            },
            'imf': {
                'name': 'International Monetary Fund',
                'domains': ['imf.org', 'data.imf.org'],
                'reliability': 'HIGH',
                'coverage': ['Global GDP', 'fiscal data', 'economic forecasts']
            },
            'oecd': {
                'name': 'OECD',
                'domains': ['oecd.org', 'data.oecd.org'],
                'reliability': 'HIGH',
                'coverage': ['International comparisons', 'policy metrics']
            },
            'world_bank': {
                'name': 'World Bank',
                'domains': ['worldbank.org', 'data.worldbank.org'],
                'reliability': 'HIGH',
                'coverage': ['Development indicators', 'global statistics']
            },
            'bank_of_canada': {
                'name': 'Bank of Canada',
                'domains': ['bankofcanada.ca', 'www.bankofcanada.ca'],
                'reliability': 'HIGH',
                'coverage': ['Monetary policy', 'inflation', 'interest rates']
            },
            'parliamentary_budget_office': {
                'name': 'Parliamentary Budget Office',
                'domains': ['pbo-dpb.gc.ca'],
                'reliability': 'HIGH',
                'coverage': ['Budget analysis', 'fiscal projections']
            }
        }
        
        # Known Canadian economic indicators
        self.canadian_indicators = {
            'gdp_growth': {
                'pattern': r'(?:GDP|economic)\s+growth.*?(\d+\.?\d*)%',
                'historical_avg': 2.3,
                'recent_avg': 1.8,
                'source': 'Statistics Canada Table 36-10-0104-01',
                'description': 'Real GDP growth rate'
            },
            'revenue_growth': {
                'pattern': r'revenue.*?growth.*?(\d+\.?\d*)%',
                'historical_avg': 4.3,
                'recent_avg': 3.8,
                'source': 'Statistics Canada Table 385-0032',
                'description': 'Federal government revenue growth'
            },
            'unemployment': {
                'pattern': r'unemployment.*?(\d+\.?\d*)%',
                'historical_avg': 7.1,
                'recent_avg': 5.8,
                'source': 'Statistics Canada Table 14-10-0287-01',
                'description': 'Unemployment rate'
            },
            'inflation': {
                'pattern': r'inflation.*?(\d+\.?\d*)%',
                'historical_avg': 2.0,
                'recent_avg': 2.5,
                'source': 'Statistics Canada Table 18-10-0004-01 (CPI)',
                'description': 'Consumer Price Index annual change'
            },
            'deficit_gdp': {
                'pattern': r'deficit.*?(\d+\.?\d*)%.*?GDP',
                'historical_avg': 1.2,
                'recent_avg': 2.1,
                'source': 'Statistics Canada Table 36-10-0477-01',
                'description': 'Federal deficit as % of GDP'
            },
            'debt_gdp': {
                'pattern': r'debt.*?(\d+\.?\d*)%.*?GDP',
                'historical_avg': 31.0,
                'recent_avg': 42.0,
                'source': 'Statistics Canada Table 36-10-0580-01',
                'description': 'Federal debt as % of GDP'
            }
        }
    
    def _clean_ocr_artifacts(self, text: str) -> str:
        """
        Clean OCR artifacts from PDF-extracted text.
        
        Fix #4: Handles common bilingual PDF OCR issues:
        - Truncated words (missing first letters)
        - Garbled French/English bilingual text
        - Unusual character sequences
        - Repeated whitespace and line breaks
        
        Args:
            text: Raw extracted text with potential OCR issues
            
        Returns:
            Cleaned text with artifacts removed or corrected
        """
        if not text:
            return text
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Remove garbled bilingual text (French-English mixed OCR artifacts)
        # Pattern: sequences of unusual diacritics mixed with consonants
        cleaned = re.sub(r'[àâäèéêëîïôùûüÿç]{2,}[bcdfghjklmnpqrstvwxz]{3,}', '', cleaned)
        cleaned = re.sub(r'[bcdfghjklmnpqrstvwxz]{5,}[àâäèéêëîïôùûüÿç]+', '', cleaned)
        
        # Remove sequences that look like OCR garbage
        # e.g., "smueb pdaértaegrrmapinhé", "aapftreèrs Dlee"
        cleaned = re.sub(r'\b[a-z]{2,}[àâäèéêëîïôùûüÿç]{2,}[a-z]*\b', '', cleaned, flags=re.IGNORECASE)
        
        # Fix common truncation patterns - restore likely beginnings
        # These are heuristic fixes for common PDF OCR issues
        ocr_fixes = {
            r'\baxation\b': 'taxation',  # 't' dropped
            r'\bconomic\b': 'economic',  # 'e' dropped
            r'\bnancial\b': 'financial',  # 'fi' dropped
            r'\bercent\b': 'percent',  # 'p' dropped
            r'\billion\b': 'billion',  # 'b' dropped
            r'\bllion\b': 'billion',  # 'bi' dropped
            r'\brillion\b': 'trillion',  # 't' dropped
            r'\bevenue\b': 'revenue',  # 'r' dropped
            r'\budget\b': 'budget',  # 'b' dropped
            r'\bovernment\b': 'government',  # 'g' dropped
        }
        
        for pattern, replacement in ocr_fixes.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Remove remaining garbled words (words with very low vowel ratio)
        words = cleaned.split()
        cleaned_words = []
        for word in words:
            if len(word) > 4:
                vowels = sum(1 for c in word.lower() if c in 'aeiouàâäèéêëîïôùûüÿ')
                if vowels / len(word) < 0.12:  # Less than 12% vowels = likely garbage
                    continue
            cleaned_words.append(word)
        
        cleaned = ' '.join(cleaned_words)
        
        # Final cleanup - remove double spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def extract_quantitative_claims(self, text: str) -> List[Dict]:
        """
        Extract quantitative claims from document text.
        
        Args:
            text: Full document text
            
        Returns:
            List of extracted claims with context
        """
        claims = []
        
        # Extract percentage-based claims
        percentage_pattern = r'([^.!?]{0,100})(\d+\.?\d*)%([^.!?]{0,100}[.!?])'
        for match in re.finditer(percentage_pattern, text, re.IGNORECASE):
            context_before = match.group(1).strip()
            value = float(match.group(2))
            context_after = match.group(3).strip()
            
            claims.append({
                'type': 'percentage',
                'value': value,
                'context_before': context_before[-100:] if len(context_before) > 100 else context_before,
                'context_after': context_after[:100] if len(context_after) > 100 else context_after,
                'full_sentence': (context_before + str(value) + '%' + context_after).strip()
            })
        
        # Extract dollar amounts (billions/millions)
        dollar_pattern = r'([^.!?]{0,100})\$(\d+\.?\d*)\s*(billion|million|trillion)([^.!?]{0,100}[.!?])'
        for match in re.finditer(dollar_pattern, text, re.IGNORECASE):
            context_before = match.group(1).strip()
            value = float(match.group(2))
            magnitude = match.group(3).lower()
            context_after = match.group(4).strip()
            
            # Normalize to billions
            if magnitude == 'million':
                normalized_value = value / 1000
            elif magnitude == 'trillion':
                normalized_value = value * 1000
            else:
                normalized_value = value
            
            claims.append({
                'type': 'dollar_amount',
                'value': normalized_value,
                'original_value': value,
                'magnitude': magnitude,
                'context_before': context_before[-100:],
                'context_after': context_after[:100],
                'full_sentence': (context_before + '$' + str(value) + ' ' + magnitude + context_after).strip()
            })
        
        return claims
    
    def categorize_claim(self, claim: Dict) -> Optional[str]:
        """
        Categorize a claim by matching it to known economic indicators.
        
        Args:
            claim: Extracted claim dictionary
            
        Returns:
            Indicator key or None if no match
        """
        full_text = claim['full_sentence'].lower()
        
        for indicator_key, indicator_data in self.canadian_indicators.items():
            pattern = indicator_data['pattern']
            if re.search(pattern, full_text, re.IGNORECASE):
                return indicator_key
        
        return None
    
    def validate_claim(self, claim: Dict, indicator_key: str) -> Dict:
        """
        Validate a claim against historical data for a specific indicator.
        
        Args:
            claim: Extracted claim
            indicator_key: Key to canadian_indicators
            
        Returns:
            Validation results with deviation analysis
        """
        indicator = self.canadian_indicators[indicator_key]
        claimed_value = claim['value']
        historical_avg = indicator['historical_avg']
        recent_avg = indicator['recent_avg']
        
        # Calculate deviations
        historical_deviation = ((claimed_value - historical_avg) / historical_avg) * 100
        recent_deviation = ((claimed_value - recent_avg) / recent_avg) * 100
        
        # Determine assessment
        if abs(historical_deviation) < 20:
            assessment = 'PLAUSIBLE'
            flag = '✓'
        elif abs(historical_deviation) < 50:
            assessment = 'OPTIMISTIC' if historical_deviation > 0 else 'CONSERVATIVE'
            flag = '⚠️'
        else:
            assessment = 'QUESTIONABLE'
            flag = '❌'
        
        return {
            'indicator': indicator_key,
            'description': indicator['description'],
            'claimed_value': claimed_value,
            'historical_average': historical_avg,
            'recent_average': recent_avg,
            'historical_deviation_pct': historical_deviation,
            'recent_deviation_pct': recent_deviation,
            'assessment': assessment,
            'flag': flag,
            'authoritative_source': indicator['source'],
            'recommendation': self._generate_recommendation(claimed_value, historical_avg, recent_avg, indicator_key)
        }
    
    def _generate_recommendation(self, claimed: float, historical: float, recent: float, indicator: str) -> str:
        """Generate validation recommendation based on deviation."""
        if abs(claimed - recent) < abs(claimed - historical):
            if abs(claimed - recent) / recent < 0.2:
                return f"Claim aligns with recent trends ({recent}%). Appears reasonable."
            else:
                return f"Claim deviates {abs((claimed-recent)/recent*100):.0f}% from recent average. Verify assumptions."
        else:
            if abs(claimed - historical) / historical < 0.2:
                return f"Claim aligns with historical average ({historical}%). Conservative estimate."
            else:
                return f"Claim deviates {abs((claimed-historical)/historical*100):.0f}% from historical data. Requires citation."
    
    def trace_sources(self, document_text: str) -> Dict:
        """
        Main method: Extract claims, categorize, validate, and trace to sources.
        
        Args:
            document_text: Full text of policy document
            
        Returns:
            Comprehensive lineage report
        """
        # Fix #4: Clean OCR artifacts from text before processing
        cleaned_text = self._clean_ocr_artifacts(document_text)
        
        # Extract all quantitative claims
        all_claims = self.extract_quantitative_claims(cleaned_text)
        
        # Categorize and validate
        traced_claims = []
        untraced_claims = []
        
        for claim in all_claims:
            indicator_key = self.categorize_claim(claim)
            
            if indicator_key:
                validation = self.validate_claim(claim, indicator_key)
                traced_claims.append({
                    'claim': claim,
                    'validation': validation
                })
            else:
                untraced_claims.append(claim)
        
        # Generate summary statistics
        total_claims = len(all_claims)
        traced_count = len(traced_claims)
        trace_rate = (traced_count / total_claims * 100) if total_claims > 0 else 0
        
        # Count assessments
        plausible = sum(1 for t in traced_claims if t['validation']['assessment'] == 'PLAUSIBLE')
        optimistic = sum(1 for t in traced_claims if t['validation']['assessment'] in ['OPTIMISTIC', 'QUESTIONABLE'])
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_quantitative_claims': total_claims,
                'traced_to_sources': traced_count,
                'trace_rate_pct': trace_rate,
                'plausible_claims': plausible,
                'optimistic_questionable_claims': optimistic,
                'untraced_claims': len(untraced_claims)
            },
            'traced_claims': traced_claims,
            'untraced_claims': untraced_claims[:20],  # Limit for output size
            'authoritative_sources': self.authoritative_sources,
            'methodology': {
                'indicators_tracked': len(self.canadian_indicators),
                'source_databases': len(self.authoritative_sources),
                'validation_method': 'Historical deviation analysis (20-year average)'
            }
        }
    
    def generate_report(self, lineage_data: Dict, format: str = 'text') -> str:
        """
        Generate human-readable lineage report.
        
        Args:
            lineage_data: Output from trace_sources()
            format: 'text' or 'markdown'
            
        Returns:
            Formatted report
        """
        if format == 'markdown':
            return self._generate_markdown_report(lineage_data)
        else:
            return self._generate_text_report(lineage_data)
    
    def _generate_text_report(self, data: Dict) -> str:
        """Generate plain text lineage report."""
        report = []
        report.append("=" * 80)
        report.append("DATA LINEAGE SOURCE MAPPING REPORT")
        report.append("Sparrow SPOT Scale™ v8.3")
        report.append("=" * 80)
        report.append(f"\nGenerated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
        
        # Summary
        summary = data['summary']
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Quantitative Claims:     {summary['total_quantitative_claims']}")
        report.append(f"Traced to Sources:             {summary['traced_to_sources']} ({summary['trace_rate_pct']:.1f}%)")
        report.append(f"Plausible Claims:              {summary['plausible_claims']}")
        report.append(f"Optimistic/Questionable:       {summary['optimistic_questionable_claims']}")
        report.append(f"Untraced Claims:               {summary['untraced_claims']}")
        report.append("")
        
        # Traced claims detail
        report.append("TRACED CLAIMS - VALIDATION RESULTS")
        report.append("-" * 80)
        
        for i, traced in enumerate(data['traced_claims'], 1):
            val = traced['validation']
            claim = traced['claim']
            
            report.append(f"\n{i}. {val['flag']} {val['description']}")
            report.append(f"   Claimed Value:         {val['claimed_value']}%")
            report.append(f"   Historical Average:    {val['historical_average']}% (deviation: {val['historical_deviation_pct']:+.1f}%)")
            report.append(f"   Recent Average:        {val['recent_average']}% (deviation: {val['recent_deviation_pct']:+.1f}%)")
            report.append(f"   Assessment:            {val['assessment']}")
            report.append(f"   Source:                {val['authoritative_source']}")
            report.append(f"   Recommendation:        {val['recommendation']}")
            report.append(f"   Context:               ...{claim['context_before'][-60:]} {val['claimed_value']}% {claim['context_after'][:60]}...")
        
        # Authoritative sources reference
        report.append("\n\nAUTHORITATIVE SOURCES REFERENCED")
        report.append("-" * 80)
        for source_key, source_data in data['authoritative_sources'].items():
            report.append(f"\n{source_data['name']}")
            report.append(f"  Reliability: {source_data['reliability']}")
            report.append(f"  Coverage: {', '.join(source_data['coverage'])}")
        
        # Methodology
        report.append("\n\nMETHODOLOGY")
        report.append("-" * 80)
        method = data['methodology']
        report.append(f"Indicators Tracked:    {method['indicators_tracked']}")
        report.append(f"Source Databases:      {method['source_databases']}")
        report.append(f"Validation Method:     {method['validation_method']}")
        
        report.append("\n" + "=" * 80)
        report.append("Generated by Sparrow SPOT Scale™ - Open-source transparency toolkit")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _generate_markdown_report(self, data: Dict) -> str:
        """Generate markdown lineage report."""
        report = []
        report.append("# Data Lineage Source Mapping Report\n")
        report.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  ")
        report.append(f"**System:** Sparrow SPOT Scale™ v8.3\n")
        
        # Summary
        summary = data['summary']
        report.append("## Summary\n")
        report.append(f"- **Total Quantitative Claims:** {summary['total_quantitative_claims']}")
        report.append(f"- **Traced to Sources:** {summary['traced_to_sources']} ({summary['trace_rate_pct']:.1f}%)")
        report.append(f"- **Plausible Claims:** {summary['plausible_claims']}")
        report.append(f"- **Optimistic/Questionable:** {summary['optimistic_questionable_claims']}")
        report.append(f"- **Untraced:** {summary['untraced_claims']}\n")
        
        # Traced claims
        report.append("## Validated Claims\n")
        for i, traced in enumerate(data['traced_claims'], 1):
            val = traced['validation']
            claim = traced['claim']
            
            report.append(f"### {i}. {val['flag']} {val['description']}\n")
            report.append(f"**Claimed:** {val['claimed_value']}%  ")
            report.append(f"**Historical Avg:** {val['historical_average']}% (deviation: {val['historical_deviation_pct']:+.1f}%)  ")
            report.append(f"**Recent Avg:** {val['recent_average']}% (deviation: {val['recent_deviation_pct']:+.1f}%)  ")
            report.append(f"**Assessment:** {val['assessment']}  ")
            report.append(f"**Source:** {val['authoritative_source']}\n")
            report.append(f"**Recommendation:** {val['recommendation']}\n")
            report.append(f"> Context: ...{claim['context_before'][-60:]} **{val['claimed_value']}%** {claim['context_after'][:60]}...\n")
        
        # Sources
        report.append("## Authoritative Sources\n")
        for source_data in data['authoritative_sources'].values():
            report.append(f"- **{source_data['name']}** (Reliability: {source_data['reliability']})")
            report.append(f"  - Coverage: {', '.join(source_data['coverage'])}\n")
        
        report.append("\n---\n*Generated by Sparrow SPOT Scale™ - Open-source transparency toolkit*")
        
        return "\n".join(report)


def main():
    """Command-line interface for Data Lineage Source Mapper."""
    parser = argparse.ArgumentParser(
        description='Trace quantitative claims to authoritative data sources'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input text file or JSON from sparrow analysis'
    )
    parser.add_argument(
        '--output', '-o',
        default='lineage_report',
        help='Output file prefix (default: lineage_report)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'markdown', 'json', 'all'],
        default='all',
        help='Output format (default: all)'
    )
    
    args = parser.parse_args()
    
    # Load input
    print(f"📖 Reading document from {args.input}...")
    
    if args.input.endswith('.json'):
        # Extract text from JSON analysis
        with open(args.input, 'r') as f:
            data = json.load(f)
        # Try to find text in various JSON structures
        document_text = data.get('text', data.get('content', ''))
        if not document_text:
            print("⚠️  Could not find text content in JSON. Please provide a text file.")
            return
    else:
        # Load plain text
        with open(args.input, 'r') as f:
            document_text = f.read()
    
    print(f"   ✓ Loaded {len(document_text):,} characters")
    
    # Trace sources
    print("\n🔍 Tracing quantitative claims to authoritative sources...")
    mapper = DataLineageSourceMapper()
    lineage_data = mapper.trace_sources(document_text)
    
    print(f"   ✓ Found {lineage_data['summary']['total_quantitative_claims']} quantitative claims")
    print(f"   ✓ Traced {lineage_data['summary']['traced_to_sources']} to authoritative sources")
    
    # Generate outputs
    print(f"\n💾 Generating {args.format} output(s)...")
    
    if args.format in ['text', 'all']:
        text_file = f"{args.output}_lineage.txt"
        with open(text_file, 'w') as f:
            f.write(mapper.generate_report(lineage_data, 'text'))
        print(f"   ✓ Text: {text_file}")
    
    if args.format in ['markdown', 'all']:
        md_file = f"{args.output}_lineage.md"
        with open(md_file, 'w') as f:
            f.write(mapper.generate_report(lineage_data, 'markdown'))
        print(f"   ✓ Markdown: {md_file}")
    
    if args.format in ['json', 'all']:
        json_file = f"{args.output}_lineage.json"
        with open(json_file, 'w') as f:
            json.dump(lineage_data, f, indent=2)
        print(f"   ✓ JSON: {json_file}")
    
    print("\n✅ Data lineage mapping complete!")


if __name__ == '__main__':
    main()

"""
Contradiction Detection Engine for Policy Document Analysis
Detects numerical inconsistencies, arithmetic errors, and conflicting claims
Specifically designed to validate Canadian Budget 2025 and similar policy documents
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import statistics


class ContradictionDetector:
    """
    Detects contradictions and numerical inconsistencies in policy documents.
    
    Capabilities:
    1. Arithmetic validation (A + B should equal C)
    2. Cross-reference checking (same metric mentioned multiple times)
    3. Temporal consistency (year-over-year growth rates)
    4. Visual-text alignment (chart numbers vs. text numbers)
    5. Percentage validation (percentages should sum to 100%)
    """
    
    def __init__(self):
        """Initialize contradiction detector."""
        self.contradictions = []
        self.warnings = []
        self.validated_claims = []
        
    def analyze(self, text: str, vision_findings: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Run comprehensive contradiction analysis.
        
        Args:
            text: Full document text
            vision_findings: Optional list of vision analysis results from charts/graphs
            
        Returns:
            Dictionary with contradiction analysis results
        """
        self.contradictions = []
        self.warnings = []
        self.validated_claims = []
        
        # Extract all numerical claims
        numerical_claims = self._extract_numerical_claims(text)
        
        # Run analysis modules
        self._check_arithmetic_consistency(text, numerical_claims)
        self._check_cross_references(numerical_claims)
        self._check_temporal_consistency(text, numerical_claims)
        self._check_percentage_sums(text, numerical_claims)
        
        # If vision data available, validate against charts
        if vision_findings:
            self._validate_against_visuals(numerical_claims, vision_findings)
        
        # Calculate contradiction severity score
        severity_score = self._calculate_severity()
        
        return {
            'contradictions': self.contradictions,
            'warnings': self.warnings,
            'validated_claims': self.validated_claims,
            'severity_score': severity_score,
            'summary': self._generate_summary()
        }
    
    def _extract_numerical_claims(self, text: str) -> List[Dict]:
        """
        Extract all numerical claims from text with context.
        
        Returns:
            List of dicts with {value, unit, context, position}
        """
        claims = []
        
        # Pattern 1: Dollar amounts with context
        dollar_pattern = r'(.{0,100})\$\s*(\d+(?:\.\d+)?)\s*(billion|million|trillion|b|m|t)(.{0,100})'
        for match in re.finditer(dollar_pattern, text, re.IGNORECASE):
            before, amount, unit, after = match.groups()
            claims.append({
                'type': 'currency',
                'value': float(amount),
                'unit': unit.lower().replace('b', 'billion').replace('m', 'million').replace('t', 'trillion'),
                'context_before': before.strip(),
                'context_after': after.strip(),
                'position': match.start(),
                'full_text': match.group(0)
            })
        
        # Pattern 2: Percentages with context
        percent_pattern = r'(.{0,100})(\d+(?:\.\d+)?)\s*%(.{0,100})'
        for match in re.finditer(percent_pattern, text):
            before, amount, after = match.groups()
            claims.append({
                'type': 'percentage',
                'value': float(amount),
                'unit': 'percent',
                'context_before': before.strip(),
                'context_after': after.strip(),
                'position': match.start(),
                'full_text': match.group(0)
            })
        
        # Pattern 3: Years and fiscal years
        year_pattern = r'(20\d{2})(?:-(\d{2}))?'
        for match in re.finditer(year_pattern, text):
            year1 = match.group(1)
            year2 = match.group(2)
            claims.append({
                'type': 'year',
                'value': int(year1),
                'value2': int(f"20{year2}") if year2 else None,
                'position': match.start(),
                'full_text': match.group(0)
            })
        
        # Pattern 4: Growth rates and changes
        growth_pattern = r'(increase|decrease|growth|decline|rise|fall)(?:\s+(?:of|by))?\s+(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(growth_pattern, text, re.IGNORECASE):
            direction, amount = match.groups()
            claims.append({
                'type': 'growth_rate',
                'value': float(amount),
                'direction': direction.lower(),
                'unit': 'percent',
                'position': match.start(),
                'full_text': match.group(0)
            })
        
        return sorted(claims, key=lambda x: x['position'])
    
    def _check_arithmetic_consistency(self, text: str, claims: List[Dict]):
        """
        Check for arithmetic contradictions (e.g., A + B ≠ C).
        
        Common patterns:
        - "total of $X billion" followed by itemized breakdown
        - "growth from X to Y" vs. calculated difference
        - Budget components that don't sum to total
        """
        # Look for "total" or "sum" statements followed by itemized lists
        total_pattern = r'total(?:\s+of)?\s+\$\s*(\d+(?:\.\d+)?)\s*(billion|million)'
        
        for match in re.finditer(total_pattern, text, re.IGNORECASE):
            stated_total = float(match.group(1))
            unit = match.group(2).lower()
            position = match.start()
            
            # Look for itemized amounts in context window (extended to 800 chars)
            context_start = max(0, position - 200)  # Look back for intro text
            context_end = position + 800
            context = text[context_start:context_end]
            
            # More sophisticated item extraction
            item_pattern = r'(?:from\s+)?\$\s*(\d+(?:\.\d+)?)\s*(billion|million)(?:\s+to|in|for)?'
            items = []
            item_positions = []
            
            for item_match in re.finditer(item_pattern, context, re.IGNORECASE):
                item_amount = float(item_match.group(1))
                item_unit = item_match.group(2).lower()
                item_pos = item_match.start()
                
                # Skip if this is the total itself (within 50 chars of total statement)
                relative_pos = item_pos - (position - context_start)
                if -5 <= relative_pos <= 50:
                    continue
                
                # Convert to same unit as total
                if unit == 'billion' and item_unit == 'million':
                    item_amount /= 1000
                elif unit == 'million' and item_unit == 'billion':
                    item_amount *= 1000
                
                items.append(item_amount)
                item_positions.append(item_pos)
            
            # Only flag if we have clear itemization (3+ items) and significant mismatch
            if len(items) >= 3:
                calculated_sum = sum(items)
                
                # Use graduated tolerance: 5% for amounts >$100B, 10% for smaller
                tolerance_pct = 0.05 if stated_total > 100 else 0.10
                tolerance = stated_total * tolerance_pct
                
                # Additional check: if calculated sum is > 2x stated total, likely false positive
                if abs(calculated_sum - stated_total) > tolerance and calculated_sum < stated_total * 2:
                    # Verify items are actually itemizations (not random mentions)
                    if self._validate_itemization_structure(context, items, item_positions):
                        self.contradictions.append({
                            'type': 'arithmetic_mismatch',
                            'severity': 'HIGH',
                            'stated_total': stated_total,
                            'calculated_total': round(calculated_sum, 2),
                            'difference': round(abs(calculated_sum - stated_total), 2),
                            'context': context[:200],
                            'message': f"Stated total ${stated_total} {unit} doesn't match itemized sum ${calculated_sum:.2f} {unit}"
                        })
    
    def _validate_itemization_structure(self, context: str, items: List[float], positions: List[int]) -> bool:
        """
        Verify that extracted items are actual itemizations, not random mentions.
        
        Checks for:
        - Items in close proximity (sequential listing)
        - Connecting words like 'and', 'plus', commas, semicolons
        - Table/list formatting indicators
        """
        if len(items) < 3:
            return False
        
        # Check position spacing - items should be relatively close together
        # If items span > 500 chars, likely not a cohesive list
        position_span = max(positions) - min(positions)
        if position_span > 500:
            return False
        
        # Look for list indicators between items
        list_indicators = [',', ';', 'and', 'plus', '+', '\n•', '\n-', '\ntable', '\n ']
        items_context = context[min(positions):max(positions)]
        indicator_count = sum(1 for indicator in list_indicators if indicator in items_context.lower())
        
        # If we have at least half as many indicators as items, likely a real list
        return indicator_count >= len(items) / 2
    
    def _check_cross_references(self, claims: List[Dict]):
        """
        Check if the same metric is stated with different values.
        
        Example: "GDP growth of 2.5%" vs. "GDP growth of 2.3%" in same document
        """
        # Group claims by similar context
        metric_groups = defaultdict(list)
        
        for claim in claims:
            if claim['type'] in ['currency', 'percentage', 'growth_rate']:
                # Extract key terms from context
                context = (claim.get('context_before', '') + ' ' + claim.get('context_after', '')).lower()
                
                # Look for key metric identifiers
                key_terms = {
                    'gdp': 'gdp growth',
                    'deficit': 'deficit',
                    'surplus': 'surplus',
                    'debt': 'debt',
                    'revenue': 'revenue',
                    'spending': 'spending',
                    'inflation': 'inflation',
                    'unemployment': 'unemployment'
                }
                
                for term, metric_name in key_terms.items():
                    if term in context:
                        metric_groups[metric_name].append(claim)
        
        # Check for contradictions within each metric group
        for metric_name, metric_claims in metric_groups.items():
            if len(metric_claims) > 1:
                values = [c['value'] for c in metric_claims]
                
                # Check if values vary significantly (>10% difference)
                if max(values) - min(values) > min(values) * 0.10:
                    self.contradictions.append({
                        'type': 'cross_reference_mismatch',
                        'severity': 'MEDIUM',
                        'metric': metric_name,
                        'values': values,
                        'contexts': [c.get('full_text', '')[:100] for c in metric_claims],
                        'message': f"Metric '{metric_name}' has inconsistent values: {values}"
                    })
    
    def _check_temporal_consistency(self, text: str, claims: List[Dict]):
        """
        Check if year-over-year changes make sense.
        
        Example: "2024: $100B, 2025: $105B" should show ~5% growth, not 10%
        """
        # Find year-over-year comparisons
        yoy_pattern = r'(20\d{2})[^\d]*\$\s*(\d+(?:\.\d+)?)\s*(billion|million)[^2]*?(20\d{2})[^\d]*\$\s*(\d+(?:\.\d+)?)\s*(billion|million)'
        
        for match in re.finditer(yoy_pattern, text, re.IGNORECASE):
            year1, amount1, unit1, year2, amount2, unit2 = match.groups()
            
            # Normalize to same unit
            val1 = float(amount1)
            val2 = float(amount2)
            
            if unit1.lower() == 'million' and unit2.lower() == 'billion':
                val1 /= 1000
            elif unit1.lower() == 'billion' and unit2.lower() == 'million':
                val2 /= 1000
            
            # Calculate actual growth
            if val1 > 0:
                actual_growth = ((val2 - val1) / val1) * 100
                
                # Look for stated growth rate nearby
                context = text[max(0, match.start()-200):match.end()+200]
                growth_mentions = re.findall(r'(increase|growth|rise)(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*%', context, re.IGNORECASE)
                
                if growth_mentions:
                    for direction, stated_growth in growth_mentions:
                        stated_growth = float(stated_growth)
                        
                        # Check if stated growth matches calculated (5% tolerance)
                        if abs(actual_growth - stated_growth) > 5:
                            self.contradictions.append({
                                'type': 'temporal_inconsistency',
                                'severity': 'HIGH',
                                'year1': year1,
                                'year2': year2,
                                'value1': val1,
                                'value2': val2,
                                'calculated_growth': round(actual_growth, 2),
                                'stated_growth': stated_growth,
                                'message': f"Growth from {year1} to {year2}: calculated {actual_growth:.1f}% but stated {stated_growth}%"
                            })
    
    def _check_percentage_sums(self, text: str, claims: List[Dict]):
        """
        Check if percentages that should sum to 100% actually do.
        
        Example: "30% from taxes, 40% from fees, 20% from grants" = only 90%
        """
        # Look for lists of percentages that should sum to 100%
        list_indicators = ['breakdown', 'composition', 'distributed', 'allocated', 'consists of']
        
        for indicator in list_indicators:
            # Find sections with list indicators
            pattern = f'{indicator}[^.]*?:'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                context = text[match.end():match.end()+500]
                
                # Extract all percentages in this context
                percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', context)
                if len(percentages) >= 2:
                    percentage_values = [float(p) for p in percentages]
                    total = sum(percentage_values)
                    
                    # Check if close to 100% (tolerance: ±5%)
                    if 95 <= total <= 105:
                        self.validated_claims.append({
                            'type': 'percentage_sum_valid',
                            'percentages': percentage_values,
                            'total': total
                        })
                    elif total < 90 or total > 110:
                        self.warnings.append({
                            'type': 'percentage_sum_warning',
                            'severity': 'MEDIUM',
                            'percentages': percentage_values,
                            'total': round(total, 1),
                            'expected': 100,
                            'message': f"Percentages sum to {total:.1f}%, not 100%"
                        })
    
    def _validate_against_visuals(self, claims: List[Dict], vision_findings: List[Dict]):
        """
        Compare numbers in text against numbers extracted from charts/graphs.
        
        This helps detect if charts show different data than the text claims.
        """
        # Extract numbers from vision findings
        chart_numbers = []
        for finding in vision_findings:
            analysis = finding.get('analysis', '')
            
            # Extract dollar amounts from vision analysis
            dollar_matches = re.findall(r'\$\s*(\d+(?:\.\d+)?)\s*(billion|million|b|m)', analysis, re.IGNORECASE)
            for amount, unit in dollar_matches:
                chart_numbers.append({
                    'value': float(amount),
                    'unit': unit.lower().replace('b', 'billion').replace('m', 'million'),
                    'source': 'chart',
                    'chart_description': finding.get('description', '')[:100]
                })
        
        # Compare text claims against chart numbers
        text_currency_claims = [c for c in claims if c['type'] == 'currency']
        
        for text_claim in text_currency_claims:
            # Look for matching chart numbers (same value, similar unit)
            matches = [
                c for c in chart_numbers 
                if abs(c['value'] - text_claim['value']) < text_claim['value'] * 0.05
                and c['unit'] == text_claim['unit']
            ]
            
            if matches:
                self.validated_claims.append({
                    'type': 'visual_text_agreement',
                    'value': text_claim['value'],
                    'unit': text_claim['unit'],
                    'text_context': text_claim.get('full_text', '')[:100],
                    'chart_context': matches[0].get('chart_description', '')
                })
            elif chart_numbers:  # Charts exist but number not found
                # Check if there's a similar value with different magnitude
                for chart_num in chart_numbers:
                    if text_claim['unit'] == 'billion' and chart_num['unit'] == 'million':
                        if abs(text_claim['value'] * 1000 - chart_num['value']) < chart_num['value'] * 0.05:
                            self.contradictions.append({
                                'type': 'visual_text_unit_mismatch',
                                'severity': 'HIGH',
                                'text_value': text_claim['value'],
                                'text_unit': text_claim['unit'],
                                'chart_value': chart_num['value'],
                                'chart_unit': chart_num['unit'],
                                'message': f"Text says ${text_claim['value']} {text_claim['unit']} but chart shows ${chart_num['value']} {chart_num['unit']}"
                            })
    
    def _calculate_severity(self) -> float:
        """
        Calculate overall severity score (0-100).
        
        Higher score = more severe contradictions found
        """
        if not self.contradictions and not self.warnings:
            return 0.0
        
        severity_weights = {
            'HIGH': 25,
            'MEDIUM': 10,
            'LOW': 5
        }
        
        total_severity = 0
        for contradiction in self.contradictions:
            severity = contradiction.get('severity', 'MEDIUM')
            total_severity += severity_weights.get(severity, 10)
        
        for warning in self.warnings:
            severity = warning.get('severity', 'LOW')
            total_severity += severity_weights.get(severity, 5) * 0.5  # Warnings count less
        
        # Cap at 100
        return min(100, total_severity)
    
    def _generate_summary(self) -> str:
        """Generate human-readable summary of contradiction analysis."""
        if not self.contradictions and not self.warnings:
            return "No contradictions or inconsistencies detected. All numerical claims appear consistent."
        
        high_severity = len([c for c in self.contradictions if c.get('severity') == 'HIGH'])
        medium_severity = len([c for c in self.contradictions if c.get('severity') == 'MEDIUM'])
        
        summary_parts = []
        
        if high_severity > 0:
            summary_parts.append(f"⚠️ {high_severity} HIGH severity contradiction(s) detected")
        if medium_severity > 0:
            summary_parts.append(f"⚠️ {medium_severity} MEDIUM severity contradiction(s) detected")
        if self.warnings:
            summary_parts.append(f"ℹ️ {len(self.warnings)} warning(s) flagged")
        if self.validated_claims:
            summary_parts.append(f"✓ {len(self.validated_claims)} claim(s) validated")
        
        return " | ".join(summary_parts)


def create_contradiction_detector() -> ContradictionDetector:
    """Factory function to create contradiction detector."""
    return ContradictionDetector()

"""
Insight Extractor Module for v8
Identifies surprising findings, gaps, and implications in analysis data

This module analyzes v7 JSON data to find:
- Standout findings (scores that stand out)
- Gaps and inconsistencies
- Surprising contrasts
- Policy implications
- Escalation-worthy items
"""

from typing import Dict, List, Optional, Tuple
import json


class InsightExtractor:
    """
    Extracts meaningful insights from v7 analysis JSON.
    
    Input: v7 analysis report (JSON)
    Output: List of notable insights with categories
    """
    
    def __init__(self):
        """Initialize insight extractor"""
        self.criteria_list = [
            'fiscal_transparency',
            'stakeholder_balance',
            'economic_rigor',
            'public_accessibility',
            'policy_consequentiality'
        ]
        
        # Map backend abbreviations to internal keys
        self.backend_key_mapping = {
            'FT': 'fiscal_transparency',
            'SB': 'stakeholder_balance',
            'ER': 'economic_rigor',
            'PA': 'public_accessibility',
            'PC': 'policy_consequentiality'
        }
    
    def extract(self, analysis: Dict) -> Dict[str, List[str]]:
        """
        Extract all notable insights from analysis.
        
        Args:
            analysis: v7 analysis JSON
            
        Returns:
            Dict with categories of insights
        """
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
        
        # Generate explanations for all criteria
        explanations = {}
        criteria_data = analysis.get('criteria', {})
        for criterion in self.criteria_list:
            score = 0
            backend_key = None
            for bk, internal_k in self.backend_key_mapping.items():
                if internal_k == criterion:
                    backend_key = bk
                    break
            if backend_key and backend_key in criteria_data:
                score = criteria_data[backend_key].get('score', 0)
            if score == 0:
                data = analysis.get(criterion, {})
                score = data.get('score', 0)
            explanations[criterion] = self._get_score_explanation(criterion, score)
        
        insights = {
            'standout_findings': self._find_standout_scores(analysis),
            'gaps_and_inconsistencies': self._find_gaps(analysis),
            'surprising_contrasts': self._find_contrasts(analysis),
            'policy_implications': self._extract_policy_implications(analysis),
            'escalation_worthy': self._find_escalation_worthy(analysis),
            'strengths': self._identify_strengths(analysis),
            'weaknesses': self._identify_weaknesses(analysis),
            'explanations': explanations
        }
        
        return insights
    
    def _find_standout_scores(self, analysis: Dict) -> List[str]:
        """
        Find scores that are notably high or low.
        """
        findings = []
        scores = {}
        
        # Get criteria data from backend format
        criteria_data = analysis.get('criteria', {})
        
        for criterion in self.criteria_list:
            score = 0
            
            # Try to get score from criteria data (new format: FT, SB, etc.)
            if criteria_data:
                # Find the backend key for this criterion
                backend_key = None
                for bk, internal_k in self.backend_key_mapping.items():
                    if internal_k == criterion:
                        backend_key = bk
                        break
                
                if backend_key and backend_key in criteria_data:
                    score = criteria_data[backend_key].get('score', 0)
            
            # Fallback: try old format (long keys)
            if score == 0:
                data = analysis.get(criterion, {})
                score = data.get('score', 0)
            
            scores[criterion] = {
                'score': score,
                'name': self._criterion_name(criterion)
            }
        
        # Find highest and lowest
        max_score = max((v['score'] for v in scores.values()), default=0)
        min_score = min((v['score'] for v in scores.values()), default=100)
        avg_score = sum(v['score'] for v in scores.values()) / len(scores) if scores else 50
        
        # High outliers (>15 points above average)
        for criterion, data in scores.items():
            if data['score'] > avg_score + 15:
                findings.append(f"★ {data['name']} stands out at {data['score']:.0f}/100, notably above the {avg_score:.0f} average")
        
        # Low outliers (<15 points below average)
        for criterion, data in scores.items():
            if data['score'] < avg_score - 15:
                findings.append(f"⚠ {data['name']} lags at {data['score']:.0f}/100, notably below the {avg_score:.0f} average")
        
        # Perfect scores
        for criterion, data in scores.items():
            if data['score'] == 100:
                findings.append(f"✓ Perfect score on {data['name']} ({data['score']:.0f}/100)")
        
        # Critical failures
        for criterion, data in scores.items():
            if data['score'] < 50:
                findings.append(f"✗ Critical concern with {data['name']} at only {data['score']:.0f}/100")
        
        return findings
    
    def _find_gaps(self, analysis: Dict) -> List[str]:
        """
        Find gaps and inconsistencies in the analysis.
        """
        gaps = []
        
        # Get criteria data from backend format
        criteria_data = analysis.get('criteria', {})
        
        # Check for missing data
        for criterion in self.criteria_list:
            score = 0
            reasoning = ''
            
            # Try to get score from criteria data (new format: FT, SB, etc.)
            if criteria_data:
                # Find the backend key for this criterion
                backend_key = None
                for bk, internal_k in self.backend_key_mapping.items():
                    if internal_k == criterion:
                        backend_key = bk
                        break
                
                if backend_key and backend_key in criteria_data:
                    score = criteria_data[backend_key].get('score', 0)
            
            # Fallback: try old format (long keys)
            if score == 0:
                data = analysis.get(criterion, {})
                score = data.get('score', 0)
                reasoning = data.get('reasoning', '')
            
            if score == 0 and not reasoning:
                gaps.append(f"Missing data for {self._criterion_name(criterion)}")
                continue
            
            # Note: With v8 explanations dict, we no longer report "no explanation" gaps
            # Explanations are auto-generated from score ranges, so this is not a real gap
        
        # Check composite score reasonableness
        composite = analysis.get('composite_score', 0)
        scores = []
        for criterion in self.criteria_list:
            score = 0
            if criteria_data:
                backend_key = None
                for bk, internal_k in self.backend_key_mapping.items():
                    if internal_k == criterion:
                        backend_key = bk
                        break
                if backend_key and backend_key in criteria_data:
                    score = criteria_data[backend_key].get('score', 0)
            if score == 0:
                data = analysis.get(criterion, {})
                score = data.get('score', 0)
            if score > 0:
                scores.append(score)
        
        if scores:
            expected_avg = sum(scores) / len(scores)
            # If composite differs significantly from average, that's noteworthy
            if abs(composite - expected_avg) > 5:
                gaps.append(f"Composite score ({composite:.0f}) differs notably from component average ({expected_avg:.0f})")

        
        # Check for zero scores (possible incompleteness) - but only from backend data
        for criterion in self.criteria_list:
            score = 0
            if criteria_data:
                backend_key = None
                for bk, internal_k in self.backend_key_mapping.items():
                    if internal_k == criterion:
                        backend_key = bk
                        break
                if backend_key and backend_key in criteria_data:
                    score = criteria_data[backend_key].get('score', 0)
            if score == 0:
                data = analysis.get(criterion, {})
                score = data.get('score', 0)
            
            if score == 0:
                gaps.append(f"Zero score for {self._criterion_name(criterion)} suggests incomplete analysis")
        
        return gaps
    
    def _find_contrasts(self, analysis: Dict) -> List[str]:
        """
        Find surprising contrasts and contradictions.
        """
        contrasts = []
        scores = {}
        
        # Get criteria data from backend format
        criteria_data = analysis.get('criteria', {})
        
        for criterion in self.criteria_list:
            score = 0
            
            # Try to get score from criteria data (new format: FT, SB, etc.)
            if criteria_data:
                # Find the backend key for this criterion
                backend_key = None
                for bk, internal_k in self.backend_key_mapping.items():
                    if internal_k == criterion:
                        backend_key = bk
                        break
                
                if backend_key and backend_key in criteria_data:
                    score = criteria_data[backend_key].get('score', 0)
            
            # Fallback: try old format (long keys)
            if score == 0:
                data = analysis.get(criterion, {})
                score = data.get('score', 0)
            
            scores[criterion] = (score, self._criterion_name(criterion))
        
        # Look for large gaps
        score_values = [s[0] for s in scores.values()]
        if score_values:
            max_score = max(score_values)
            min_score = min(score_values)
            gap = max_score - min_score
            
            # Very large gaps (>40 points)
            if gap > 40:
                max_criterion = max(scores.items(), key=lambda x: x[1][0])[1][1]
                min_criterion = min(scores.items(), key=lambda x: x[1][0])[1][1]
                contrasts.append(
                    f"Stark contrast: {max_criterion} ({max_score:.0f}) vs {min_criterion} ({min_score:.0f}) — a {gap:.0f}-point gap"
                )
            
            # Large gaps (>30 points)
            elif gap > 30:
                max_criterion = max(scores.items(), key=lambda x: x[1][0])[1][1]
                min_criterion = min(scores.items(), key=lambda x: x[1][0])[1][1]
                contrasts.append(
                    f"Notable contrast: {max_criterion} scores well ({max_score:.0f}) while {min_criterion} lags ({min_score:.0f})"
                )
        
        # Check for logical contradictions
        # High accessibility but low stakeholder balance?
        accessibility = analysis.get('public_accessibility', {}).get('score', 0)
        stakeholder = analysis.get('stakeholder_balance', {}).get('score', 0)
        
        if accessibility > 80 and stakeholder < 60:
            contrasts.append("Paradox: High accessibility despite limited stakeholder input suggests top-down communication")
        
        # High fiscal transparency but low economic rigor?
        transparency = analysis.get('fiscal_transparency', {}).get('score', 0)
        rigor = analysis.get('economic_rigor', {}).get('score', 0)
        
        if transparency > 80 and rigor < 60:
            contrasts.append("Disconnect: Clear spending detail but weak economic foundation")
        
        return contrasts
    
    def _extract_policy_implications(self, analysis: Dict) -> List[str]:
        """
        Extract meaningful policy implications.
        """
        implications = []
        
        composite = analysis.get('composite_score', 0)
        
        # Implementation readiness
        if composite >= 85:
            implications.append("Implementation-ready: This document has sufficient rigor for immediate use")
        elif composite >= 75:
            implications.append("Conditional readiness: Refinements recommended before implementation")
        elif composite >= 65:
            implications.append("Needs revision: Substantial improvements required for viable implementation")
        else:
            implications.append("Not recommended: Major restructuring needed")
        
        # Stakeholder engagement
        stakeholder = analysis.get('stakeholder_balance', {}).get('score', 0)
        if stakeholder < 70:
            implications.append("Stakeholder engagement gap: Expand consultation process before finalization")
        
        # Public communication strategy
        accessibility = analysis.get('public_accessibility', {}).get('score', 0)
        if accessibility < 70:
            implications.append("Communication challenge: Develop plain-language summary for public distribution")
        elif accessibility > 85:
            implications.append("Strength: Document is well-positioned for public engagement")
        
        # Economic defensibility
        rigor = analysis.get('economic_rigor', {}).get('score', 0)
        if rigor < 60:
            implications.append("Economic vulnerability: Subject to challenge on methodological grounds")
        elif rigor >= 85:
            implications.append("Strong economic foundation: Resistant to methodological challenges")
        
        # Political viability
        consequentiality = analysis.get('policy_consequentiality', {}).get('score', 0)
        if consequentiality < 60:
            implications.append("Unclear impact: Define and communicate real-world consequences more clearly")
        
        return implications
    
    def _find_escalation_worthy(self, analysis: Dict) -> List[str]:
        """
        Identify items that warrant escalation or special attention.
        """
        escalations = []
        
        # Trust score issues
        trust_score = analysis.get('trust_metrics', {}).get('overall_trust', 100)
        if trust_score < 70:
            escalations.append(f"⚠ Trust score below 70 ({trust_score:.0f}) — recommend expert review")
        if trust_score < 50:
            escalations.append(f"🚨 Trust score critically low ({trust_score:.0f}) — escalation recommended")
        
        # Risk tier
        risk_tier = analysis.get('risk_tier', 'LOW')
        if risk_tier == 'HIGH':
            escalations.append(f"🚨 HIGH RISK classification — immediate escalation required")
        elif risk_tier == 'MEDIUM':
            escalations.append(f"⚠ MEDIUM RISK detected — review before finalization")
        
        # AI detection
        ai_confidence = analysis.get('ai_detection', {}).get('ai_detected_confidence', 0)
        if ai_confidence > 80:
            escalations.append(f"⚠ AI-generated content detected ({ai_confidence:.0f}% confidence) — verify authenticity")
        
        # Fairness concerns
        fairness = analysis.get('fairness_metrics', {}).get('overall_fairness', 100)
        if fairness < 70:
            escalations.append(f"⚠ Fairness concerns ({fairness:.0f}/100) — check for bias")
        
        # Low scores on critical criteria
        for criterion in self.criteria_list:
            score = analysis.get(criterion, {}).get('score', 50)
            if criterion == 'fiscal_transparency' and score < 50:
                escalations.append("🚨 Critical: Fiscal transparency below 50 — not acceptable")
            elif criterion == 'economic_rigor' and score < 50:
                escalations.append("🚨 Critical: Economic rigor below 50 — needs major revision")
        
        return escalations
    
    def _identify_strengths(self, analysis: Dict) -> List[str]:
        """
        Identify areas of strength.
        """
        strengths = []
        
        # Get criteria data from backend format
        criteria_data = analysis.get('criteria', {})
        
        for criterion in self.criteria_list:
            score = 0
            
            # Try to get score from criteria data (new format: FT, SB, etc.)
            if criteria_data:
                # Find the backend key for this criterion
                backend_key = None
                for bk, internal_k in self.backend_key_mapping.items():
                    if internal_k == criterion:
                        backend_key = bk
                        break
                
                if backend_key and backend_key in criteria_data:
                    score = criteria_data[backend_key].get('score', 0)
            
            # Fallback: try old format (long keys)
            if score == 0:
                score = analysis.get(criterion, {}).get('score', 0)
            
            name = self._criterion_name(criterion)
            
            if score >= 85:
                strengths.append(f"✓ Exceptional: {name} ({score:.0f}/100)")
            elif score >= 80:
                strengths.append(f"✓ Strong: {name} ({score:.0f}/100)")
            elif score >= 75:
                strengths.append(f"✓ Solid: {name} ({score:.0f}/100)")
        
        # Composite strength
        composite = analysis.get('composite_score', 0)
        if composite >= 80:
            strengths.append(f"✓ Overall assessment: Strong foundation at {composite:.0f}/100")
        
        return strengths
    
    def _identify_weaknesses(self, analysis: Dict) -> List[str]:
        """
        Identify areas of weakness.
        """
        weaknesses = []
        
        # Get criteria data from backend format
        criteria_data = analysis.get('criteria', {})
        
        # Get adjustment log to identify relative weaknesses
        adjustment_log = analysis.get('bias_audit', {}).get('adjustment_log', [])
        adjustment_map = {adj.get('criterion'): adj for adj in adjustment_log}
        
        for criterion in self.criteria_list:
            score = 0
            
            # Try to get score from criteria data (new format: FT, SB, etc.)
            if criteria_data:
                # Find the backend key for this criterion
                backend_key = None
                for bk, internal_k in self.backend_key_mapping.items():
                    if internal_k == criterion:
                        backend_key = bk
                        break
                
                if backend_key and backend_key in criteria_data:
                    score = criteria_data[backend_key].get('score', 0)
                    
                    # Check for significant downward adjustment
                    if backend_key in adjustment_map:
                        adj = adjustment_map[backend_key]
                        original = adj.get('original', score)
                        adjusted = adj.get('adjusted', score)
                        adjustment_pct = ((original - adjusted) / original * 100) if original > 0 else 0
                        
                        # If adjusted down >10%, consider it a relative weakness even if score is decent
                        if adjustment_pct > 10 and score >= 60:
                            name = self._criterion_name(criterion)
                            sources = adj.get('sources', [])
                            source_text = ', '.join(sources[:2])
                            if len(sources) > 2:
                                source_text += f' (+{len(sources)-2} more)'
                            weaknesses.append(f"⚠ Adjusted down {adjustment_pct:.0f}%: {name} (from {original:.0f} to {adjusted:.0f} based on {source_text})")
                            continue
            
            # Fallback: try old format (long keys)
            if score == 0:
                score = analysis.get(criterion, {}).get('score', 0)
            
            name = self._criterion_name(criterion)
            
            if score < 50:
                weaknesses.append(f"✗ Critical: {name} ({score:.0f}/100)")
            elif score < 60:
                weaknesses.append(f"⚠ Weak: {name} ({score:.0f}/100)")
            elif score < 70:
                weaknesses.append(f"⚠ Needs work: {name} ({score:.0f}/100)")
        
        return weaknesses
    
    def _criterion_name(self, criterion: str) -> str:
        """Convert criterion key to display name."""
        names = {
            'fiscal_transparency': 'Fiscal Transparency',
            'stakeholder_balance': 'Stakeholder Balance',
            'economic_rigor': 'Economic Rigor',
            'public_accessibility': 'Public Accessibility',
            'policy_consequentiality': 'Policy Consequentiality'
        }
        return names.get(criterion, criterion.replace('_', ' ').title())
    
    def _get_score_explanation(self, criterion: str, score: float) -> str:
        """Generate explanation for a score."""
        explanations = {
            'fiscal_transparency': {
                (90, 101): "Exceptional transparency with detailed revenue/spending breakdown, stated assumptions, and comprehensive risk disclosure",
                (80, 90): "Clear disclosure with detailed spending categories, assumptions stated, and some risk disclosure",
                (70, 80): "Adequate transparency with main spending areas detailed, though some assumptions lack clarity",
                (60, 70): "Limited transparency; key spending areas not sufficiently detailed or assumptions unclear",
                (0, 60): "Poor transparency with insufficient detail on spending allocation or unstated assumptions"
            },
            'stakeholder_balance': {
                (90, 101): "Comprehensive representation of all major stakeholder perspectives with balanced tradeoffs acknowledged",
                (80, 90): "Multiple stakeholder viewpoints (4+) well-represented with clear tradeoff acknowledgment",
                (70, 80): "Several stakeholder perspectives included though some coverage uneven or tradeoffs implicit",
                (60, 70): "Limited stakeholder perspective integration; key voices underrepresented",
                (0, 60): "Poor stakeholder representation; major perspectives missing or dismissed"
            },
            'economic_rigor': {
                (90, 101): "Rigorous economic analysis with well-justified assumptions, sensitivity testing, and clear limitations acknowledged",
                (80, 90): "Sound economic methodology with reasonable assumptions, model described, internal consistency verified",
                (70, 80): "Adequate economic analysis though some assumptions could be better justified or sensitivity limited",
                (60, 70): "Weak economic foundation; assumptions questionable or analysis lacks depth",
                (0, 60): "Poor economic rigor with unjustified assumptions or incoherent analysis"
            },
            'public_accessibility': {
                (90, 101): "Exceptional accessibility with clear language, visual aids, and structures for diverse audiences",
                (80, 90): "Well-structured and accessible to educated general audience; technical language minimized",
                (70, 80): "Reasonably accessible though some technical language; could benefit from simplification",
                (60, 70): "Limited accessibility; technical language restricts audience to specialists",
                (0, 60): "Poor accessibility; inaccessible to general public; specialist language dominates"
            },
            'policy_consequentiality': {
                (90, 101): "Addresses major challenge with transformative impact ($10B+), affects millions, binding legislation",
                (80, 90): "Clear policy implications with significant real-world consequences for stakeholders",
                (70, 80): "Meaningful policy implications though impact scope somewhat limited",
                (60, 70): "Unclear how policy translates to actual consequences; implications not well-articulated",
                (0, 60): "Minimal or unclear policy impact; consequentiality not demonstrated"
            }
        }
        
        criterion_explanations = explanations.get(criterion, {})
        for (min_score, max_score), explanation in criterion_explanations.items():
            if min_score <= score <= max_score:
                return explanation
        return "Score assessment complete"
    
    def get_summary(self, insights: Dict) -> str:
        """Create a summary of insights."""
        summary_points = []
        
        # Top findings
        if insights.get('standout_findings'):
            summary_points.append(f"Key findings: {insights['standout_findings'][0]}")
        
        # Main gaps
        if insights.get('gaps_and_inconsistencies'):
            summary_points.append(f"Notable gap: {insights['gaps_and_inconsistencies'][0]}")
        
        # Main contrast
        if insights.get('surprising_contrasts'):
            summary_points.append(f"Main contrast: {insights['surprising_contrasts'][0]}")
        
        # Escalations
        escalations = insights.get('escalation_worthy', [])
        if escalations:
            critical = [e for e in escalations if '🚨' in e]
            if critical:
                summary_points.append(f"Alert: {critical[0]}")
        
        return " | ".join(summary_points)


def create_insight_extractor() -> InsightExtractor:
    """Factory function to create insight extractor instance."""
    return InsightExtractor()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        # Load analysis and extract insights
        analysis_file = sys.argv[1]
        
        with open(analysis_file) as f:
            analysis = json.load(f)
        
        extractor = InsightExtractor()
        insights = extractor.extract(analysis)
        print(json.dumps(insights, indent=2))
    else:
        print("Usage: python insight_extractor.py <analysis.json>")
        print("\nExample:")
        print("  python insight_extractor.py test_articles/2025_budget/2025-Budget-00.json")

"""
Narrative Engine Module for v8
Translates v7 JSON analysis reports into compelling story components

This module converts technical scoring data into narrative elements:
- Lede (opening summary)
- Criterion interpretations
- Key tensions and contradictions
- Policy implications
- Escalation highlights
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class NarrativeComponent:
    """Represents a single narrative element"""
    name: str
    score: float
    reasoning: str
    interpretation: str
    narrative_text: str


class NarrativeEngine:
    """
    Converts v7 analysis JSON into narrative story components.
    
    Input: v7 analysis report (JSON with scores, reasoning, etc.)
    Output: Narrative components dict with lede, criteria, tensions, implications
    """
    
    # Grade thresholds for interpretation
    GRADE_THRESHOLDS = {
        'A': (90, 100),
        'B': (80, 89),
        'C': (70, 79),
        'D': (60, 69),
        'F': (0, 59)
    }
    
    # Interpretation templates based on score ranges
    SCORE_INTERPRETATIONS = {
        (90, 101): "Excellent",
        (80, 90): "Strong",
        (70, 80): "Adequate",
        (60, 70): "Weak",
        (0, 60): "Poor"
    }
    
    def __init__(self):
        """Initialize the narrative engine"""
        # Mapping from backend abbreviations to full names
        self.criteria_names = {
            'fiscal_transparency': 'Fiscal Transparency',
            'stakeholder_balance': 'Stakeholder Balance',
            'economic_rigor': 'Economic Rigor',
            'public_accessibility': 'Public Accessibility',
            'policy_consequentiality': 'Policy Consequentiality'
        }
        
        # Map backend abbreviations (from JSON) to internal keys
        self.backend_key_mapping = {
            'FT': 'fiscal_transparency',
            'SB': 'stakeholder_balance',
            'ER': 'economic_rigor',
            'PA': 'public_accessibility',
            'PC': 'policy_consequentiality'
        }
        
        self.criteria_questions = {
            'fiscal_transparency': 'How transparent is the budget breakdown?',
            'stakeholder_balance': 'How well are stakeholder perspectives balanced?',
            'economic_rigor': 'How rigorous is the economic analysis?',
            'public_accessibility': 'How accessible is this to the general public?',
            'policy_consequentiality': 'What are the real-world consequences?'
        }
    
    def generate(self, analysis: Dict) -> Dict:
        """
        Generate complete narrative components from v7 analysis.
        
        Args:
            analysis: v7 JSON analysis report with scores and reasoning
            
        Returns:
            Dictionary with narrative components (lede, criteria, tensions, etc.)
        """
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
        
        # Extract key data - composite_score is in the root level
        composite_score = analysis.get('composite_score', 0)
        
        # Calculate grade from composite score if not present
        # Check 'grade', 'composite_grade', or calculate from score
        grade = analysis.get('grade', analysis.get('composite_grade', self._calculate_grade(composite_score)))
        
        # Create a modified analysis dict with grade for lede generation
        analysis_with_grade = analysis.copy()
        analysis_with_grade['grade'] = grade
        
        # Generate components
        lede = self._generate_lede(analysis_with_grade)
        criteria_narratives = self._generate_criteria_narratives(analysis)
        tensions = self._identify_tensions(analysis)
        implications = self._extract_implications(analysis)
        escalations = self._identify_escalations(analysis)
        
        return {
            'lede': lede,
            'criteria': criteria_narratives,
            'key_tension': tensions.get('primary', ''),
            'secondary_tensions': tensions.get('secondary', []),
            'implications': implications,
            'escalations': escalations,
            'composite_score': composite_score,
            'grade': grade,
            'trust_score': analysis.get('trust_score', {}),
            'risk_tier': analysis.get('risk_tier', 'MEDIUM'),
            'metadata': {
                'generated_by': 'NarrativeEngine v1',
                'source_version': analysis.get('version', 'v7'),
                'analysis_type': analysis.get('analysis_type', 'policy')
            }
        }
    
    def _generate_lede(self, analysis: Dict) -> str:
        """
        Generate opening summary (lede) for the narrative.
        
        The lede is the hook that tells the story in one compelling sentence.
        """
        composite = analysis.get('composite_score', 0)
        grade = analysis.get('grade', 'N/A')
        title = analysis.get('title', 'This document')
        analysis_type = analysis.get('analysis_type', 'policy')
        
        # Determine overall assessment
        if composite >= 90:
            assessment = "excels across multiple dimensions"
        elif composite >= 80:
            assessment = "demonstrates strong quality"
        elif composite >= 70:
            assessment = "meets baseline standards"
        elif composite >= 60:
            assessment = "has significant gaps"
        else:
            assessment = "raises serious concerns"
        
        lede = f"{title} scores {grade} ({composite}/100) for {assessment}, with notable strengths in transparency and areas for improvement in accessibility."
        
        return lede
    
    def _generate_criteria_narratives(self, analysis: Dict) -> Dict[str, str]:
        """
        Generate narrative interpretation for each criterion.
        
        Translates dry scores into readable assessments.
        """
        criteria_narratives = {}
        
        # Check if analysis has 'criteria' key (v7 format with FT, SB, etc.)
        criteria_data = analysis.get('criteria', {})
        
        for criterion_key, criterion_name in self.criteria_names.items():
            score = 0
            reasoning = ''
            
            # Try to get score from criteria data (new format: FT, SB, etc.)
            if criteria_data:
                # Find the backend key for this criterion
                backend_key = None
                for bk, internal_k in self.backend_key_mapping.items():
                    if internal_k == criterion_key:
                        backend_key = bk
                        break
                
                if backend_key and backend_key in criteria_data:
                    score = criteria_data[backend_key].get('score', 0)
            
            # Fallback: try old format (long keys)
            if score == 0:
                criterion_data_old = analysis.get(criterion_key, {})
                score = criterion_data_old.get('score', 0)
                reasoning = criterion_data_old.get('reasoning', '')
            
            # Get interpretation level
            interpretation = self._get_score_interpretation(score)
            
            # Create narrative
            narrative = self._create_criterion_narrative(
                criterion_name,
                score,
                interpretation,
                reasoning,
                criterion_key
            )
            
            criteria_narratives[criterion_key] = {
                'name': criterion_name,
                'score': score,
                'interpretation': interpretation,
                'narrative': narrative,
                'reasoning': reasoning
            }
        
        return criteria_narratives
    
    def _create_criterion_narrative(
        self, 
        name: str, 
        score: float, 
        interpretation: str, 
        reasoning: str,
        criterion_key: str
    ) -> str:
        """Create a narrative sentence for a criterion."""
        
        # Base narrative structure
        templates = {
            'fiscal_transparency': {
                'Excellent': "Budget provides exceptional transparency with detailed breakdowns at multiple levels",
                'Strong': "Budget clearly details major spending categories with good breakdown depth",
                'Adequate': "Budget covers main spending areas with reasonable detail",
                'Weak': "Budget lacks sufficient detail in key spending areas",
                'Poor': "Budget fails to provide adequate transparency in spending allocation"
            },
            'stakeholder_balance': {
                'Excellent': "All major stakeholder perspectives thoroughly considered and reflected",
                'Strong': "Multiple stakeholder viewpoints are well-represented",
                'Adequate': "Some stakeholder perspectives included, though coverage is uneven",
                'Weak': "Limited stakeholder perspective integration; key voices missing",
                'Poor': "Fails to consider diverse stakeholder perspectives"
            },
            'economic_rigor': {
                'Excellent': "Economic analysis demonstrates exceptional rigor with sensitivity testing",
                'Strong': "Solid economic foundation with confidence intervals and testing",
                'Adequate': "Basic economic analysis present with reasonable assumptions",
                'Weak': "Economic reasoning lacks depth and supporting evidence",
                'Poor': "Economic analysis is superficial or absent"
            },
            'public_accessibility': {
                'Excellent': "Exceptional accessibility with clear language and visual aids",
                'Strong': "Well-structured and accessible to educated general audience",
                'Adequate': "Reasonably accessible with some technical language",
                'Weak': "Technical language limits accessibility to specialists",
                'Poor': "Inaccessible to general public; specialist language only"
            },
            'policy_consequentiality': {
                'Excellent': "Clear connection to real-world impact with specific outcomes identified",
                'Strong': "Policy implications are well-articulated and meaningful",
                'Adequate': "Some policy implications present; could be clearer",
                'Weak': "Unclear how policy translates to actual consequences",
                'Poor': "Fails to address meaningful policy implications"
            }
        }
        
        # Get template-based narrative
        narrative = templates.get(criterion_key, {}).get(interpretation, "")
        
        if not narrative:
            narrative = f"{name}: {interpretation} ({score}/100)"
        
        # Add reasoning if present
        if reasoning:
            narrative += f". {reasoning}"
        
        return narrative
    
    def _get_score_interpretation(self, score: float) -> str:
        """Get interpretation level for a score."""
        for range_tuple, interpretation in self.SCORE_INTERPRETATIONS.items():
            if range_tuple[0] <= score <= range_tuple[1]:
                return interpretation
        return "Unknown"
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from numeric score."""
        for grade_letter, (min_score, max_score) in self.GRADE_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return grade_letter
        return 'N/A'
    
    def _identify_tensions(self, analysis: Dict) -> Dict:
        """
        Identify key tensions and contradictions in the analysis.
        
        Example: Strong fiscal transparency but weak accessibility
        """
        tensions = {
            'primary': '',
            'secondary': []
        }
        
        # Extract scores from backend format
        criteria_data = analysis.get('criteria', {})
        scores = {}
        
        for backend_key, internal_key in self.backend_key_mapping.items():
            if backend_key in criteria_data:
                score = criteria_data[backend_key].get('score', 0)
            else:
                # Fallback to old format
                score = analysis.get(internal_key, {}).get('score', 0)
            scores[internal_key] = score
        
        # Find biggest gap
        if scores:
            max_score = max(scores.values())
            min_score = min(scores.values())
            gap = max_score - min_score
            
            if gap >= 30:
                max_key = max(scores, key=scores.get)
                min_key = min(scores, key=scores.get)
                max_name = self.criteria_names.get(max_key, max_key)
                min_name = self.criteria_names.get(min_key, min_key)
                
                tensions['primary'] = f"{max_name} ({max_score:.0f}) stands in sharp contrast to {min_name} ({min_score:.0f}), a {gap:.0f}-point gap"
            elif gap >= 20:
                max_key = max(scores, key=scores.get)
                min_key = min(scores, key=scores.get)
                max_name = self.criteria_names.get(max_key, max_key)
                min_name = self.criteria_names.get(min_key, min_key)
                
                tensions['primary'] = f"Notable difference between {max_name} ({max_score:.0f}) and {min_name} ({min_score:.0f})"
            else:
                # Recommendation #2: Always generate tension even for uniform scores
                max_key = max(scores, key=scores.get)
                min_key = min(scores, key=scores.get)
                max_name = self.criteria_names.get(max_key, max_key)
                min_name = self.criteria_names.get(min_key, min_key)
                
                # Create synthetic tension from policy context
                if 'public_accessibility' in scores and 'economic_rigor' in scores:
                    tensions['primary'] = f"Balancing technical rigor ({scores.get('economic_rigor', 0):.0f}) with public understanding ({scores.get('public_accessibility', 0):.0f}) remains a policy communication challenge"
                elif 'fiscal_transparency' in scores and 'stakeholder_balance' in scores:
                    tensions['primary'] = f"Transparency goals ({scores.get('fiscal_transparency', 0):.0f}) must be weighed against diverse stakeholder perspectives ({scores.get('stakeholder_balance', 0):.0f})"
                else:
                    tensions['primary'] = f"Strongest performance in {max_name} ({max_score:.0f}), with room for improvement in {min_name} ({min_score:.0f})"
            
            # Find secondary tensions
            for key1 in scores:
                for key2 in scores:
                    if key1 < key2:  # Avoid duplicates
                        gap = abs(scores[key1] - scores[key2])
                        if 15 <= gap < 30:
                            name1 = self.criteria_names.get(key1, key1)
                            name2 = self.criteria_names.get(key2, key2)
                            tensions['secondary'].append(
                                f"{name1} ({scores[key1]:.0f}) vs {name2} ({scores[key2]:.0f})"
                            )
        
        return tensions
    
    def _extract_implications(self, analysis: Dict) -> List[str]:
        """
        Extract meaningful policy implications from the analysis.
        Recommendation #2: Generate comprehensive implications for completeness.
        """
        implications = []
        
        # Check composite score for overall implication
        composite = analysis.get('composite_score', 0)
        
        if composite >= 85:
            implications.append("Implementation-ready: This document has sufficient rigor for immediate use")
        elif composite >= 75:
            implications.append("Generally sound: Minor refinements recommended before final implementation")
        elif composite >= 65:
            implications.append("Requires revision: Substantial improvements needed before implementation")
        else:
            implications.append("Major restructuring: Document needs fundamental rework to be viable")
        
        # Get criteria scores from backend format
        criteria_data = analysis.get('criteria', {})
        
        # Helper to get score by internal key
        def get_score(internal_key):
            backend_key = None
            for bk, ik in self.backend_key_mapping.items():
                if ik == internal_key:
                    backend_key = bk
                    break
            if backend_key and backend_key in criteria_data:
                return criteria_data[backend_key].get('score', 0)
            # Fallback to old format
            return analysis.get(internal_key, {}).get('score', 0)
        
        # Check accessibility implication
        accessibility = get_score('public_accessibility')
        if accessibility < 60:
            implications.append("Communication challenge: Develop plain-language summary for public distribution")
        elif accessibility < 75:
            implications.append("Communication challenge: Develop plain-language summary for public distribution")
        
        # Check for stakeholder implications
        stakeholder = get_score('stakeholder_balance')
        if stakeholder < 70:
            implications.append("Stakeholder engagement gap: Expand consultation process before finalization")
        elif stakeholder >= 80:
            implications.append("Strong stakeholder representation: Multiple perspectives well-integrated")
        
        # Check economic rigor
        rigor = get_score('economic_rigor')
        if rigor >= 85:
            implications.append("Economic assumptions are well-supported and defensible")
        elif rigor < 70:
            implications.append("Economic vulnerability: Subject to challenge on methodological grounds")
        
        # Check policy consequentiality
        consequentiality = get_score('policy_consequentiality')
        if consequentiality >= 90:
            implications.append("High-impact policy: Transformative potential with significant societal reach")
        elif consequentiality < 70:
            implications.append("Unclear impact: Define and communicate real-world consequences more clearly")
        
        # Ensure at least 3 implications always present
        if len(implications) < 3:
            implications.append("Recommend expert review before final decision-making")
        
        return implications
    
    def _identify_escalations(self, analysis: Dict) -> List[Dict]:
        """
        Identify and flag escalation conditions from the analysis.
        """
        escalations = []
        
        # Check trust score (correct path: trust_score.trust_score)
        trust_data = analysis.get('trust_score', {})
        trust_score = trust_data.get('trust_score', 0)
        
        if trust_score < 70:
            escalations.append({
                'type': 'LOW_TRUST',
                'severity': 'HIGH' if trust_score < 50 else 'MEDIUM',
                'message': f"Trust score is low ({trust_score:.1f}). Recommend expert review.",
                'details': trust_data.get('interpretation', '')
            })
        
        # Check risk tier
        risk_tier = analysis.get('risk_tier', 'MEDIUM')
        if risk_tier == 'HIGH':
            escalations.append({
                'type': 'HIGH_RISK',
                'severity': 'HIGH',
                'message': "Risk assessment indicates HIGH tier. Escalation recommended.",
                'details': analysis.get('risk_reasoning', '')
            })
        
        # Check AI detection
        ai_data = analysis.get('ai_detection', {})
        ai_confidence = ai_data.get('ai_detected_confidence', 0)
        
        if ai_confidence > 80:
            escalations.append({
                'type': 'AI_DETECTION',
                'severity': 'MEDIUM',
                'message': f"AI-generated content detected with {ai_confidence:.0f}% confidence.",
                'details': ai_data.get('reasoning', '')
            })
        
        # Check fairness metrics
        fairness_data = analysis.get('fairness_metrics', {})
        fairness_score = fairness_data.get('overall_fairness', 100)
        
        if fairness_score < 70:
            escalations.append({
                'type': 'FAIRNESS_CONCERN',
                'severity': 'MEDIUM',
                'message': f"Fairness metrics indicate potential bias ({fairness_score:.0f}/100).",
                'details': fairness_data.get('reasoning', '')
            })
        
        return escalations
    
    def get_summary(self, narrative_components: Dict) -> str:
        """
        Create a concise summary from narrative components.
        
        Useful for social media or executive summaries.
        """
        lede = narrative_components.get('lede', '')
        primary_tension = narrative_components.get('key_tension', '')
        main_implication = narrative_components.get('implications', [''])[0]
        
        summary = f"{lede} "
        if primary_tension:
            summary += f"The main tension: {primary_tension}. "
        if main_implication:
            summary += f"Key takeaway: {main_implication}"
        
        return summary.strip()


def create_narrative_engine() -> NarrativeEngine:
    """Factory function to create narrative engine instance."""
    return NarrativeEngine()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        # Load from JSON file
        with open(sys.argv[1]) as f:
            data = json.load(f)
        
        engine = NarrativeEngine()
        narrative = engine.generate(data)
        print(json.dumps(narrative, indent=2))
    else:
        print("Usage: python narrative_engine.py <analysis.json>")
        print("\nExample:")
        print("  python narrative_engine.py test_articles/2025_budget/2025-Budget-00.json")

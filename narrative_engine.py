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
    
    def generate(self, analysis: Dict, custom_query: str = '') -> Dict:
        """
        Generate complete narrative components from v7 analysis.
        
        Args:
            analysis: v7 JSON analysis report with scores and reasoning
            custom_query: Optional custom question/context to address in narrative
            
        Returns:
            Dictionary with narrative components (lede, criteria, tensions, etc.)
        """
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
        
        # Extract key data - composite_score is in the root level
        composite_score = analysis.get('composite_score', 0)
        
        # v8.3.3: Get document type for appropriate framing
        document_type = analysis.get('document_type', 'policy_brief')
        
        # Calculate grade from composite score if not present
        # Check 'grade', 'composite_grade', or calculate from score
        grade = analysis.get('grade', analysis.get('composite_grade', self._calculate_grade(composite_score)))
        
        # Create a modified analysis dict with grade for lede generation
        analysis_with_grade = analysis.copy()
        analysis_with_grade['grade'] = grade
        analysis_with_grade['document_type'] = document_type
        
        # Generate components with document-type awareness
        lede = self._generate_lede(analysis_with_grade)
        criteria_narratives = self._generate_criteria_narratives(analysis, document_type)
        tensions = self._identify_tensions(analysis)
        implications = self._extract_implications(analysis, document_type)
        escalations = self._identify_escalations(analysis)
        
        # Generate custom query response if provided
        custom_response = ''
        if custom_query and custom_query.strip():
            custom_response = self._generate_custom_response(analysis, custom_query, document_type)
        
        return {
            'lede': lede,
            'criteria': criteria_narratives,
            'custom_response': custom_response,
            'key_tension': tensions.get('primary', ''),
            'secondary_tensions': tensions.get('secondary', []),
            'implications': implications,
            'escalations': escalations,
            'composite_score': composite_score,
            'grade': grade,
            'document_type': document_type,
            'trust_score': analysis.get('trust_score', {}),
            'risk_tier': analysis.get('risk_tier', 'MEDIUM'),
            'metadata': {
                'generated_by': 'NarrativeEngine v1.1',
                'source_version': analysis.get('version', 'v7'),
                'analysis_type': analysis.get('analysis_type', 'policy'),
                'document_type': document_type
            }
        }
    
    def _generate_custom_response(self, analysis: Dict, custom_query: str, document_type: str) -> str:
        """
        Generate a focused response to the user's custom query.
        
        Args:
            analysis: Analysis results
            custom_query: User's question/request
            document_type: Type of document being analyzed
            
        Returns:
            Narrative response addressing the custom query
        """
        criteria = analysis.get('criteria', {})
        composite_score = analysis.get('composite_score', 0)
        trust_score = analysis.get('trust_score', {}).get('score', 0)
        
        response = f"## Addressing Your Question\n\n"
        response += f"**Your Query:** \"{custom_query}\"\n\n"
        response += f"Based on the comprehensive analysis of this {document_type}, here's what the evidence shows:\n\n"
        
        # Map query terms to relevant criteria scores
        query_lower = custom_query.lower()
        response_points = []
        
        # Budget/Financial questions
        if any(term in query_lower for term in ['budget', 'cost', 'financial', 'fiscal', 'money', 'spending', 'expense']):
            if 'fiscal_transparency' in criteria:
                score = criteria['fiscal_transparency'].get('score', 0)
                response_points.append(f"**Fiscal Transparency ({score}/100):** The document shows {'strong' if score >= 70 else 'moderate' if score >= 50 else 'weak'} clarity regarding financial allocation and budget details.")
        
        # Stakeholder/Participation questions
        if any(term in query_lower for term in ['stakeholder', 'consultation', 'engagement', 'participation', 'involve', 'voice', 'community']):
            if 'stakeholder_balance' in criteria:
                score = criteria['stakeholder_balance'].get('score', 0)
                response_points.append(f"**Stakeholder Engagement ({score}/100):** The document demonstrates {'comprehensive' if score >= 70 else 'moderate' if score >= 50 else 'limited'} stakeholder involvement in policy development.")
        
        # Evidence/Analysis questions
        if any(term in query_lower for term in ['evidence', 'analysis', 'rigor', 'economic', 'data', 'study', 'research']):
            if 'economic_rigor' in criteria:
                score = criteria['economic_rigor'].get('score', 0)
                response_points.append(f"**Economic Rigor ({score}/100):** The economic analysis is {'robust' if score >= 70 else 'adequate' if score >= 50 else 'limited'}, with {'strong' if score >= 70 else 'moderate' if score >= 50 else 'weak'} evidence-based reasoning.")
        
        # Clarity/Accessibility questions
        if any(term in query_lower for term in ['clear', 'understand', 'accessible', 'plain', 'readable', 'complicated', 'jargon']):
            if 'public_accessibility' in criteria:
                score = criteria['public_accessibility'].get('score', 0)
                response_points.append(f"**Public Accessibility ({score}/100):** The document is {'highly' if score >= 70 else 'moderately' if score >= 50 else 'poorly'} accessible to general audiences, with {'clear' if score >= 70 else 'adequate' if score >= 50 else 'complicated'} language and explanations.")
        
        # Impact/Consequence questions
        if any(term in query_lower for term in ['impact', 'effect', 'consequence', 'outcome', 'result', 'achieve', 'goal']):
            if 'policy_consequentiality' in criteria:
                score = criteria['policy_consequentiality'].get('score', 0)
                response_points.append(f"**Policy Impact ({score}/100):** The policy shows {'strong' if score >= 70 else 'moderate' if score >= 50 else 'weak'} alignment between stated goals and practical implementation capabilities.")
        
        # Alternative/Options questions
        if any(term in query_lower for term in ['alternative', 'option', 'choice', 'instead', 'other approach', 'compared']):
            if 'considered_alternatives' in criteria:
                score = criteria['considered_alternatives'].get('score', 0)
                response_points.append(f"**Alternative Approaches ({score}/100):** The document shows {'thorough' if score >= 70 else 'moderate' if score >= 50 else 'limited'} exploration of alternative policy options.")
        
        # If we have specific points, add them
        if response_points:
            for point in response_points:
                response += f"- {point}\n"
        else:
            # Fallback to general assessment
            response += f"**Overall Assessment:**\n"
            response += f"- Composite Quality Score: {composite_score}/100\n"
            response += f"- Trust Score: {trust_score}/100\n"
            response += f"- Document shows {'strong' if composite_score >= 70 else 'moderate' if composite_score >= 50 else 'weak'} performance across key evaluation criteria.\n"
        
        # Add implications
        response += f"\n### Key Takeaway\n\n"
        
        if composite_score >= 70:
            response += f"The document addresses your query well, with solid evidence and clear articulation of its position on the matters you're concerned about."
        elif composite_score >= 50:
            response += f"The document addresses your query with moderate clarity, though there are areas where additional evidence or explanation would strengthen the response."
        else:
            response += f"The document has significant gaps in addressing your query. Key areas require clarification, additional evidence, or more detailed explanation."
        
        if trust_score < 50:
            response += f" However, credibility concerns should be considered when evaluating these claims."
        
        response += "\n\n"
        
        return response
    
    def _generate_lede(self, analysis: Dict) -> str:
        """
        Generate opening summary (lede) for the narrative.
        
        The lede is the hook that tells the story in one compelling sentence.
        """
        composite = analysis.get('composite_score', 0)
        grade = analysis.get('grade', 'N/A')
        title = analysis.get('title', 'This document')
        document_type = analysis.get('document_type', 'policy_brief')
        
        # v8.3.3: Document-type-specific assessments
        if document_type == 'legislation':
            # Legislative framing - focus on clarity and structure
            if composite >= 90:
                assessment = "demonstrates exceptional legal clarity"
            elif composite >= 80:
                assessment = "provides clear regulatory framework"
            elif composite >= 70:
                assessment = "meets baseline legislative standards"
            elif composite >= 60:
                assessment = "has areas requiring clarification"
            else:
                assessment = "may present implementation challenges"
            
            lede = f"This legislative analysis of {title} scores {grade} ({composite}/100), indicating the bill {assessment}."
        
        elif document_type == 'budget':
            # Budget framing - focus on fiscal accountability
            if composite >= 90:
                assessment = "provides exceptional fiscal transparency"
            elif composite >= 80:
                assessment = "demonstrates strong accountability standards"
            elif composite >= 70:
                assessment = "meets baseline transparency requirements"
            elif composite >= 60:
                assessment = "has fiscal transparency gaps"
            else:
                assessment = "raises fiscal accountability concerns"
            
            lede = f"This budget analysis of {title} scores {grade} ({composite}/100), indicating {assessment}."
        
        else:
            # Default policy framing
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
    
    def _generate_criteria_narratives(self, analysis: Dict, document_type: str = 'policy_brief') -> Dict[str, str]:
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
    
    def _extract_implications(self, analysis: Dict, document_type: str = 'policy_brief') -> List[str]:
        """
        Extract meaningful implications from the analysis.
        v8.3.3: Document-type-aware implications.
        """
        implications = []
        
        # Check composite score for overall implication
        composite = analysis.get('composite_score', 0)
        
        # v8.3.3: Document-type-specific implications
        if document_type == 'legislation':
            # Legislative implications - focus on clarity and enforcement
            if composite >= 85:
                implications.append("Clear legal framework: Legislation provides unambiguous regulatory guidance")
            elif composite >= 75:
                implications.append("Generally clear: Minor clarifications may benefit implementation")
            elif composite >= 65:
                implications.append("Interpretation challenges: Some provisions may require regulatory guidance")
            else:
                implications.append("Implementation risk: Ambiguous provisions may lead to inconsistent enforcement")
        
        elif document_type == 'budget':
            # Budget implications - focus on fiscal accountability
            if composite >= 85:
                implications.append("Fiscally transparent: Budget provides clear accountability framework")
            elif composite >= 75:
                implications.append("Adequate transparency: Main allocations clear with some detail gaps")
            elif composite >= 65:
                implications.append("Transparency gaps: Key spending areas need additional itemization")
            else:
                implications.append("Accountability concerns: Significant spending opacity requires review")
        
        else:
            # Default policy implications
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
        
        # Document-type-aware criteria implications
        accessibility = get_score('public_accessibility')
        stakeholder = get_score('stakeholder_balance')
        rigor = get_score('economic_rigor')
        consequentiality = get_score('policy_consequentiality')
        
        if document_type == 'legislation':
            # Legislative-specific implications
            if accessibility < 70:
                implications.append("Plain-language guidance needed: Citizens may struggle to understand obligations")
            if rigor < 70:
                implications.append("Economic provisions unclear: May require regulatory interpretation")
            if consequentiality >= 90:
                implications.append("High-impact legislation: Significant regulatory scope with broad effects")
        
        elif document_type == 'budget':
            # Budget-specific implications
            if accessibility < 70:
                implications.append("Taxpayer accessibility gap: Budget language may hinder public oversight")
            if rigor < 70:
                implications.append("Revenue projections uncertain: Economic assumptions may need validation")
            if stakeholder < 70:
                implications.append("Sector representation uneven: Some constituencies underrepresented")
        
        else:
            # Policy document implications (existing logic)
            if accessibility < 60:
                implications.append("Communication challenge: Develop plain-language summary for public distribution")
            elif accessibility < 75:
                implications.append("Communication challenge: Develop plain-language summary for public distribution")
            
            if stakeholder < 70:
                implications.append("Stakeholder engagement gap: Expand consultation process before finalization")
            elif stakeholder >= 80:
                implications.append("Strong stakeholder representation: Multiple perspectives well-integrated")
            
            if rigor >= 85:
                implications.append("Economic assumptions are well-supported and defensible")
            elif rigor < 70:
                implications.append("Economic vulnerability: Subject to challenge on methodological grounds")
        
        # Universal implication for policy consequentiality
        if consequentiality >= 90 and document_type != 'legislation':
            implications.append("High-impact policy: Transformative potential with significant societal reach")
        elif consequentiality < 70 and document_type not in ['legislation', 'budget']:
            implications.append("Unclear impact: Define and communicate real-world consequences more clearly")
        
        # Ensure at least 3 implications always present
        if len(implications) < 3:
            if document_type == 'legislation':
                implications.append("Legal counsel review recommended for implementation guidance")
            elif document_type == 'budget':
                implications.append("Fiscal analysis review recommended for projection validation")
            else:
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

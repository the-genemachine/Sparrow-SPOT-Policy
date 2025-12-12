"""
Tone Adaptor Module for v8
Adjusts narrative voice for different audiences and platforms

This module takes narrative components and adapts them for:
- Journalistic tone (news-style, objective)
- Academic tone (formal, evidence-based)
- Civic tone (citizen-friendly, actionable)
- Critical tone (analytical, questioning)
- Explanatory tone (educational, detailed)
"""

from typing import Dict, List, Optional
import re


class ToneAdaptor:
    """
    Adapts narrative text for different audiences and tones.
    
    Input: Narrative components + tone preference
    Output: Voice-adjusted narrative text
    """
    
    AVAILABLE_TONES = ['journalistic', 'academic', 'civic', 'critical', 'explanatory']
    
    def __init__(self):
        """Initialize tone adaptor with templates"""
        self.tone_markers = {
            'journalistic': {
                'keywords': ['breaking', 'reveals', 'analysis shows', 'finds'],
                'sentence_pattern': 'imperative_objective',
                'complexity': 'moderate',
                'audience': 'general_educated'
            },
            'academic': {
                'keywords': ['demonstrates', 'indicates', 'suggests', 'analysis'],
                'sentence_pattern': 'passive_formal',
                'complexity': 'high',
                'audience': 'expert'
            },
            'civic': {
                'keywords': ['means', 'affects you', 'action', 'community'],
                'sentence_pattern': 'active_personal',
                'complexity': 'low',
                'audience': 'general_public'
            },
            'critical': {
                'keywords': ['questions', 'concerns', 'gaps', 'issues'],
                'sentence_pattern': 'interrogative',
                'complexity': 'high',
                'audience': 'expert'
            },
            'explanatory': {
                'keywords': ['explained', 'means', 'example', 'because'],
                'sentence_pattern': 'didactic',
                'complexity': 'moderate',
                'audience': 'general_educated'
            }
        }
    
    def adapt(self, narrative_components: Dict, tone: str = 'journalistic', length: str = 'standard') -> str:
        """
        Adapt narrative components to specified tone and length.
        
        Args:
            narrative_components: Dict with lede, criteria, tensions, implications, custom_response
            tone: One of 'journalistic', 'academic', 'civic', 'critical', 'explanatory'
            length: One of 'concise' (~500 words), 'standard' (~1000), 'detailed' (~2000), 'comprehensive' (~3500+)
            
        Returns:
            Tone-adapted narrative text
        """
        if tone not in self.AVAILABLE_TONES:
            tone = 'journalistic'
        
        # Define target word counts for each length level
        length_targets = {
            'concise': 500,
            'standard': 1000,
            'detailed': 2000,
            'comprehensive': 3500
        }
        target_words = length_targets.get(length, 1000)
        
        lede = narrative_components.get('lede', '')
        criteria = narrative_components.get('criteria', {})
        tensions = narrative_components.get('key_tension', '')
        implications = narrative_components.get('implications', [])
        escalations = narrative_components.get('escalations', [])
        custom_response = narrative_components.get('custom_response', '')  # NEW: Get custom response
        
        # Build narrative according to tone
        # Route to tone-specific formatter with length parameter
        if tone == 'journalistic':
            return self._adapt_journalistic(lede, criteria, tensions, implications, escalations, target_words, custom_response)
        elif tone == 'academic':
            return self._adapt_academic(lede, criteria, tensions, implications, escalations, target_words, custom_response)
        elif tone == 'civic':
            return self._adapt_civic(lede, criteria, tensions, implications, escalations, target_words, custom_response)
        elif tone == 'critical':
            return self._adapt_critical(lede, criteria, tensions, implications, escalations, target_words, custom_response)
        elif tone == 'explanatory':
            return self._adapt_explanatory(lede, criteria, tensions, implications, escalations, target_words, custom_response)
        
        return lede  # Fallback
    
    def _adapt_journalistic(self, lede: str, criteria: Dict, tensions: str, implications: List, escalations: List, target_words: int = 1000, custom_response: str = '') -> str:
        """
        Journalistic tone: News-style, objective, inverted pyramid.
        Lead with most important info, add context, then details.
        Length controlled by target_words parameter.
        """
        narrative = []
        
        # Lead: The headline/opening
        narrative.append(f"ANALYSIS: {lede}")
        narrative.append("")
        
        # Custom query response if provided (insert right after lede)
        if custom_response:
            narrative.append(custom_response)
            narrative.append("---\n")
        
        # Nut graph: Why this matters
        if implications:
            narrative.append(f"The significance: {implications[0]}")
            narrative.append("")
        
        # Key finding
        if tensions:
            narrative.append(f"Key finding: {tensions}")
            narrative.append("")
        
        # Supporting details
        if criteria:
            narrative.append("Assessment breakdown:")
            for key, data in criteria.items():
                if isinstance(data, dict):
                    score = data.get('score', 0)
                    interpretation = data.get('interpretation', '')
                    narrative.append(f"• {data.get('name', key)}: {interpretation} ({score:.0f}/100)")
            narrative.append("")
        
        # Length expansion: Add more details for longer formats
        if target_words >= 2000:  # detailed or comprehensive
            # Add full implications section
            if len(implications) > 2:
                narrative.append("Policy Implications:")
                for i, imp in enumerate(implications[1:4], 2):
                    narrative.append(f"{i}. {imp}")
                narrative.append("")
            
            # Add detailed criteria narratives
            if criteria:
                narrative.append("Detailed Assessment:")
                for key, data in criteria.items():
                    if isinstance(data, dict) and data.get('narrative'):
                        narrative.append(f"\n{data.get('name', key)}:")
                        narrative.append(data['narrative'])
                narrative.append("")
        
        if target_words >= 3500:  # comprehensive
            # Add all remaining implications
            if len(implications) > 4:
                narrative.append("Additional Considerations:")
                for i, imp in enumerate(implications[4:], 5):
                    narrative.append(f"{i}. {imp}")
                narrative.append("")
        
        # Escalations (if newsworthy)
        if escalations:
            high_severity = [e for e in escalations if e.get('severity') == 'HIGH']
            if high_severity:
                narrative.append("Notable flags:")
                for escalation in high_severity:
                    narrative.append(f"• {escalation.get('message', '')}")
                narrative.append("")
        
        # Closing context (skip for concise)
        if len(implications) > 1 and target_words >= 500:
            narrative.append(f"Context: {implications[1]}")
        
        return "\n".join(narrative)
    
    def _adapt_academic(self, lede: str, criteria: Dict, tensions: str, implications: List, escalations: List, target_words: int = 1000, custom_response: str = '') -> str:
        """
        Academic tone: Formal, passive voice, evidence-heavy, structured.
        """
        narrative = []
        
        # Abstract-style opening
        narrative.append("Abstract")
        narrative.append("-" * 60)
        narrative.append(f"This analysis demonstrates that {lede.lower()}")
        
        # Custom query response if provided
        if custom_response:
            narrative.append("")
            narrative.append("Research Question & Findings")
            narrative.append("-" * 60)
            narrative.append(custom_response)
        narrative.append("")
        
        # Methodology
        narrative.append("Findings")
        narrative.append("-" * 60)
        narrative.append("The assessment is based on five key dimensions:")
        narrative.append("")
        
        # Results
        if criteria:
            for key, data in criteria.items():
                if isinstance(data, dict):
                    score = data.get('score', 0)
                    reasoning = data.get('reasoning', '')
                    narrative.append(f"{data.get('name', key)}: {score:.0f}/100")
                    if reasoning:
                        narrative.append(f"  Rationale: {reasoning}")
            narrative.append("")
        
        # Interpretation
        narrative.append("Interpretation")
        narrative.append("-" * 60)
        if tensions:
            narrative.append(f"Analysis reveals a significant tension: {tensions}")
            narrative.append("")
        
        # Implications
        if implications:
            narrative.append("Implications")
            narrative.append("-" * 60)
            for i, imp in enumerate(implications, 1):
                narrative.append(f"{i}. {imp}")
            narrative.append("")
        
        # Length expansion: Add detailed sections for longer formats
        if target_words >= 2000:  # detailed or comprehensive
            # Add methodology discussion
            narrative.append("Methodological Considerations")
            narrative.append("-" * 60)
            narrative.append("The analytical framework employed herein utilizes a multi-dimensional")
            narrative.append("assessment model to evaluate the document's efficacy across five key domains.")
            narrative.append("Each dimension represents a critical aspect of policy analysis, weighted")
            narrative.append("according to established scholarly conventions.")
            narrative.append("")
            
            # Detailed criteria narratives
            if criteria:
                narrative.append("Detailed Criterion Analysis")
                narrative.append("-" * 60)
                for key, data in criteria.items():
                    if isinstance(data, dict) and data.get('narrative'):
                        narrative.append(f"\n{data.get('name', key)}:")
                        narrative.append(data['narrative'])
                narrative.append("")
        
        if target_words >= 3500:  # comprehensive
            # Add all escalations with context
            if escalations:
                narrative.append("Comprehensive Escalation Review")
                narrative.append("-" * 60)
                for escalation in escalations:
                    severity = escalation.get('severity', 'UNKNOWN')
                    message = escalation.get('message', '')
                    narrative.append(f"[{severity}] {message}")
                    narrative.append("")
            
            # Add theoretical framework
            narrative.append("Theoretical Framework")
            narrative.append("-" * 60)
            narrative.append("This assessment draws upon established policy analysis frameworks,")
            narrative.append("integrating principles from public administration theory, institutional")
            narrative.append("economics, and deliberative democracy scholarship. The multi-criterion")
            narrative.append("approach enables holistic evaluation while maintaining analytical rigor.")
            narrative.append("")
        
        # Limitations/Considerations (always show if escalations exist)
        if escalations and target_words < 3500:
            narrative.append("Limitations and Considerations")
            narrative.append("-" * 60)
            for escalation in escalations:
                narrative.append(f"• {escalation.get('message', '')}")
        
        return "\n".join(narrative)
    
    def _adapt_civic(self, lede: str, criteria: Dict, tensions: str, implications: List, escalations: List, target_words: int = 1000, custom_response: str = '') -> str:
        """
        Civic tone: Citizen-friendly, actionable, personal relevance.
        Focus on "what does this mean for you?"
        """
        narrative = []
        
        # Hook with relevance
        narrative.append("Here's what you need to know:")
        narrative.append(lede)
        narrative.append("")
        
        # Custom query response if provided
        if custom_response:
            narrative.append("Your Questions Answered:")
            narrative.append(custom_response)
            narrative.append("")
        narrative.append("")
        
        # What it means for citizens
        narrative.append("What This Means for You")
        narrative.append("-" * 40)
        
        if criteria:
            narrative.append("In plain language:")
            interpretations = {
                'fiscal_transparency': 'How clear is the money breakdown?',
                'stakeholder_balance': 'Are all voices heard?',
                'economic_rigor': 'Is the math sound?',
                'public_accessibility': 'Can you understand it?',
                'policy_consequentiality': 'What actually changes?'
            }
            
            for key, data in criteria.items():
                if isinstance(data, dict) and key in interpretations:
                    score = data.get('score', 0)
                    interpretation = data.get('interpretation', '')
                    question = interpretations[key]
                    narrative.append(f"• {question}")
                    narrative.append(f"  Answer: {interpretation.lower()} ({score:.0f}/100)")
            narrative.append("")
        
        # The important part
        if implications:
            narrative.append("Why It Matters")
            narrative.append("-" * 40)
            for imp in implications[:2]:
                narrative.append(f"✓ {imp}")
            narrative.append("")
        
        # Length expansion: Add more details for longer formats
        if target_words >= 2000:  # detailed or comprehensive
            # Add detailed implications
            if len(implications) > 2:
                narrative.append("")
                narrative.append("Additional Impacts")
                narrative.append("-" * 40)
                for imp in implications[2:]:
                    narrative.append(f"• {imp}")
                narrative.append("")
            
            # Add practical examples
            narrative.append("Real-World Examples")
            narrative.append("-" * 40)
            narrative.append("Consider these scenarios:")
            if criteria:
                example_count = 0
                for key, data in criteria.items():
                    if isinstance(data, dict) and example_count < 2:
                        score = data.get('score', 0)
                        name = data.get('name', key)
                        if score < 60:
                            narrative.append(f"• Low {name} means you might struggle to understand key details")
                            example_count += 1
                        elif score >= 80:
                            narrative.append(f"• Strong {name} means this information is clear and actionable")
                            example_count += 1
            narrative.append("")
        
        if target_words >= 3500:  # comprehensive
            # Add escalations in plain language
            if escalations:
                narrative.append("Red Flags to Watch")
                narrative.append("-" * 40)
                for escalation in escalations:
                    narrative.append(f"⚠ {escalation.get('message', '')}")
                narrative.append("")
            
            # Add resources section
            narrative.append("Where to Learn More")
            narrative.append("-" * 40)
            narrative.append("• Check official sources for updates")
            narrative.append("• Attend public consultations if available")
            narrative.append("• Connect with community organizations")
            narrative.append("• Review detailed analysis documents")
            narrative.append("")
        
        # Call to action or next steps
        narrative.append("What Next?")
        narrative.append("-" * 40)
        narrative.append("• Stay informed about implementation")
        narrative.append("• Share your feedback with stakeholders")
        narrative.append("• Ask questions if anything is unclear")
        
        return "\n".join(narrative)
    
    def _adapt_critical(self, lede: str, criteria: Dict, tensions: str, implications: List, escalations: List, target_words: int = 1000, custom_response: str = '') -> str:
        """
        Critical tone: Analytical, questioning, identifying gaps and concerns.
        """
        narrative = []
        
        # Critical opening
        narrative.append("Critical Analysis")
        narrative.append("=" * 60)
        narrative.append(f"{lede}")
        narrative.append("")
        
        # Custom query response if provided
        if custom_response:
            narrative.append("Critical Assessment of Your Query")
            narrative.append("-" * 60)
            narrative.append(custom_response)
            narrative.append("")
        
        # The problems
        narrative.append("Issues Identified")
        narrative.append("-" * 60)
        
        if criteria:
            weak_areas = []
            for key, data in criteria.items():
                if isinstance(data, dict):
                    score = data.get('score', 0)
                    if score < 70:
                        weak_areas.append((data.get('name', key), score))
            
            if weak_areas:
                narrative.append("Areas of concern:")
                for name, score in sorted(weak_areas, key=lambda x: x[1]):
                    narrative.append(f"⚠ {name}: Insufficient at {score:.0f}/100")
            else:
                narrative.append("While generally sound, the following warrant closer scrutiny:")
                for key, data in criteria.items():
                    if isinstance(data, dict):
                        name = data.get('name', key)
                        score = data.get('score', 0)
                        narrative.append(f"• {name}: {score:.0f}/100")
            narrative.append("")
        
        # Main tensions
        if tensions:
            narrative.append("Central Tensions")
            narrative.append("-" * 60)
            narrative.append(f"The most significant issue is: {tensions}")
            narrative.append("")
        
        # What's missing?
        narrative.append("Gaps and Limitations")
        narrative.append("-" * 60)
        narrative.append("This analysis would benefit from:")
        narrative.append("• Stronger stakeholder input")
        narrative.append("• More rigorous economic testing")
        narrative.append("• Greater public accessibility")
        narrative.append("• Clearer implementation pathways")
        narrative.append("")
        
        # Recommendations
        if implications:
            narrative.append("Recommendations")
            narrative.append("-" * 60)
            for i, imp in enumerate(implications, 1):
                narrative.append(f"{i}. {imp}")
            narrative.append("")
        
        # Length expansion: Add deeper critique for longer formats
        if target_words >= 2000:  # detailed or comprehensive
            # Add systemic analysis
            narrative.append("Systemic Concerns")
            narrative.append("-" * 60)
            narrative.append("Beyond individual criterion deficiencies, this analysis reveals")
            narrative.append("structural issues in how the document approaches its core objectives.")
            if tensions:
                narrative.append(f"The tension identified—{tensions.lower()}—suggests fundamental")
                narrative.append("misalignment between stated goals and practical execution.")
            narrative.append("")
            
            # Add detailed criterion critiques
            if criteria:
                narrative.append("Criterion-Specific Critique")
                narrative.append("-" * 60)
                for key, data in criteria.items():
                    if isinstance(data, dict):
                        name = data.get('name', key)
                        score = data.get('score', 0)
                        reasoning = data.get('reasoning', '')
                        if score < 80:  # Critique anything not excellent
                            narrative.append(f"\n{name} ({score:.0f}/100):")
                            narrative.append(f"Issue: {reasoning}")
                            narrative.append("Impact: This deficiency undermines credibility and effectiveness.")
                narrative.append("")
        
        if target_words >= 3500:  # comprehensive
            # Add escalations as critical concerns
            if escalations:
                narrative.append("Critical Escalations")
                narrative.append("-" * 60)
                for escalation in escalations:
                    severity = escalation.get('severity', 'UNKNOWN')
                    message = escalation.get('message', '')
                    narrative.append(f"[{severity}] {message}")
                    narrative.append("This requires immediate attention and remediation.")
                    narrative.append("")
            
            # Add alternative approaches
            narrative.append("Alternative Approaches")
            narrative.append("-" * 60)
            narrative.append("A more effective approach would:")
            narrative.append("• Prioritize transparency over procedural compliance")
            narrative.append("• Balance technical rigor with public accessibility")
            narrative.append("• Integrate diverse stakeholder perspectives from inception")
            narrative.append("• Establish clear metrics for measuring real-world impact")
            narrative.append("• Build in adaptive mechanisms for course correction")
        
        return "\n".join(narrative)
    
    def _adapt_explanatory(self, lede: str, criteria: Dict, tensions: str, implications: List, escalations: List, target_words: int = 1000, custom_response: str = '') -> str:
        """
        Explanatory tone: Educational, detailed, step-by-step understanding.
        """
        narrative = []
        
        # Introduction with context
        narrative.append("Understanding This Analysis")
        narrative.append("=" * 60)
        narrative.append(lede)
        narrative.append("")
        
        # Custom query response if provided
        if custom_response:
            narrative.append("Explaining Your Question")
            narrative.append("-" * 60)
            narrative.append(custom_response)
            narrative.append("")
        narrative.append("=" * 60)
        narrative.append("")
        narrative.append(lede)
        narrative.append("")
        
        # Build understanding progressively
        narrative.append("How We Measure This")
        narrative.append("-" * 60)
        narrative.append("This assessment uses five key dimensions:")
        narrative.append("")
        
        if criteria:
            for key, data in criteria.items():
                if isinstance(data, dict):
                    name = data.get('name', key)
                    score = data.get('score', 0)
                    reasoning = data.get('reasoning', '')
                    narrative.append(f"{name}:")
                    narrative.append(f" Score: {score:.0f}/100")
                    narrative.append(f" What it means: {reasoning.lower() if reasoning else 'Measure of how well this criterion is met'}")
                    narrative.append("")
        
        # The bigger picture
        narrative.append("Putting It Together")
        narrative.append("-" * 60)
        if tensions:
            narrative.append(f"The most interesting finding is: {tensions}")
            narrative.append("")
        
        # Implications explained
        if implications:
            narrative.append("What This Means in Practice")
            narrative.append("-" * 60)
            for i, imp in enumerate(implications, 1):
                narrative.append(f"Point {i}: {imp}")
                narrative.append("")
        
        # Length expansion: Add educational details for longer formats
        if target_words >= 2000:  # detailed or comprehensive
            # Add detailed explanation of tensions
            if tensions:
                narrative.append("Understanding the Key Tension")
                narrative.append("-" * 60)
                narrative.append(f"Let's break down what this means: {tensions}")
                narrative.append("")
                narrative.append("Why does this matter?")
                narrative.append("When a document shows this kind of tension, it suggests the authors")
                narrative.append("faced trade-offs between competing priorities. Understanding these")
                narrative.append("trade-offs helps us see both the strengths and limitations.")
                narrative.append("")
            
            # Add step-by-step criterion walkthrough
            if criteria:
                narrative.append("Step-by-Step: How Each Criterion Works")
                narrative.append("-" * 60)
                for key, data in criteria.items():
                    if isinstance(data, dict):
                        name = data.get('name', key)
                        score = data.get('score', 0)
                        reasoning = data.get('reasoning', 'Overall quality in this area')
                        narrative.append(f"\n{name}:")
                        narrative.append(f" Current Score: {score:.0f}/100")
                        narrative.append(f" What we're measuring: {reasoning}")
                        narrative.append(f" What the score means: {'Strong performance' if score >= 80 else 'Needs improvement' if score >= 60 else 'Significant gaps'}")
                narrative.append("")
        
        if target_words >= 3500:  # comprehensive
            # Add escalations with educational context
            if escalations:
                narrative.append("Understanding the Flags")
                narrative.append("-" * 60)
                narrative.append("Some issues were flagged during analysis. Here's what they mean:")
                narrative.append("")
                for escalation in escalations:
                    message = escalation.get('message', '')
                    narrative.append(f"Flag: {message}")
                    narrative.append("Context: Flags indicate areas requiring closer review or")
                    narrative.append("potential concerns that might affect the document's effectiveness.")
                    narrative.append("")
            
            # Add practical application guide
            narrative.append("Applying This Analysis")
            narrative.append("-" * 60)
            narrative.append("How to use these findings:")
            narrative.append("")
            narrative.append("1. Focus on the lowest-scoring criteria first—they represent")
            narrative.append(" the biggest opportunities for improvement.")
            narrative.append("")
            narrative.append("2. Consider the implications listed above as a roadmap for")
            narrative.append(" understanding real-world impacts.")
            narrative.append("")
            narrative.append("3. Use the tensions identified to understand trade-offs and")
            narrative.append(" competing priorities in the document.")
            narrative.append("")
            narrative.append("4. Remember: scores are indicators, not final judgments. They")
            narrative.append(" point to areas worth examining more closely.")
            narrative.append("")
        
        # Final thoughts
        narrative.append("Summary")
        narrative.append("-" * 60)
        narrative.append("In summary, this analysis shows both strengths and areas for improvement.")
        narrative.append("The key takeaway is understanding where improvements are needed for better implementation.")
        
        return "\n".join(narrative)
    
    def get_available_tones(self) -> List[str]:
        """Return list of available tone options"""
        return self.AVAILABLE_TONES
    
    def get_tone_description(self, tone: str) -> str:
        """Get description of a tone"""
        descriptions = {
            'journalistic': 'News-style: objective, lead with key facts, supporting details',
            'academic': 'Formal: structured, evidence-based, passive voice',
            'civic': 'Citizen-friendly: actionable, personal relevance, plain language',
            'critical': 'Analytical: questioning, identifying gaps and concerns',
            'explanatory': 'Educational: step-by-step, detailed, builds understanding'
        }
        return descriptions.get(tone, 'Unknown tone')


def create_tone_adaptor() -> ToneAdaptor:
    """Factory function to create tone adaptor instance."""
    return ToneAdaptor()


if __name__ == "__main__":
    # Example usage
    import json
    import sys
    
    if len(sys.argv) > 2:
        # Load narrative and apply tone
        narrative_file = sys.argv[1]
        tone = sys.argv[2]
        
        with open(narrative_file) as f:
            narrative = json.load(f)
        
        adaptor = ToneAdaptor()
        if tone not in adaptor.get_available_tones():
            print(f"Unknown tone: {tone}")
            print(f"Available tones: {', '.join(adaptor.get_available_tones())}")
            sys.exit(1)
        
        adapted = adaptor.adapt(narrative, tone)
        print(adapted)
    else:
        print("Usage: python tone_adaptor.py <narrative.json> <tone>")
        print("\nAvailable tones:")
        adaptor = ToneAdaptor()
        for tone in adaptor.get_available_tones():
            print(f"  • {tone}: {adaptor.get_tone_description(tone)}")
        print("\nExample:")
        print("  python tone_adaptor.py narrative.json journalistic")

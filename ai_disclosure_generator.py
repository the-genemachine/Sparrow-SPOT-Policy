"""
AI Disclosure Generator Module for v8.3.3

Generates standardized AI Use Statements for public outputs per Recommendation #4:
"Improve Public-Facing AI Disclosure in Policy Summaries"

This module creates transparent disclosure language for:
- Government formal statements
- Plain-language public notices
- Technical audit reports
- Social media (X/Twitter, LinkedIn, Bluesky)
- Executive summaries
- Email footers

v8.3 Enhancement: Added comprehensive multi-format generation for full transparency compliance
v8.3.2 Enhancement: Added confidence level indicators for transparency
v8.3.3 Enhancement: Fixed confidence indicator key mappings for accurate multi-level detection
"""

import os
from typing import Dict, Optional, List
from datetime import datetime
import json
import argparse

# v8.3.2: Import AnalysisResults for single source of truth
try:
    from analysis_results import AnalysisResults, create_analysis_results, ConfidenceLevel
    ANALYSIS_RESULTS_AVAILABLE = True
except ImportError:
    ANALYSIS_RESULTS_AVAILABLE = False


class AIDisclosureGenerator:
    """
    Generates standardized AI disclosure statements for policy outputs.
    
    Implements NIST AI RMF transparency pillar by providing clear, consistent
    disclosure of AI involvement in analysis.
    
    Supports two modes:
    1. Simple API: generate_disclosure_statement() for basic use
    2. Comprehensive API: Initialize with full analysis data for multi-format generation
    """
    
    def __init__(self, analysis_data: Optional[Dict] = None):
        """
        Initialize disclosure generator.
        
        Args:
            analysis_data: Optional full JSON output from sparrow_grader_v8.py for comprehensive disclosure
        """
        self.timestamp = datetime.now()
        self.data = analysis_data or {}
        self.ai_detection = self.data.get('ai_detection', {}) if analysis_data else {}
        self.metadata = {
            'document_type': self.data.get('document_type', 'Policy Document'),
            'timestamp': self.data.get('timestamp', datetime.now().isoformat()),
            'version': self.data.get('version', 'v8.3')
        } if analysis_data else {}
    
    def generate_disclosure_statement(
        self,
        ai_detection: float,
        trust_score: float,
        risk_tier: str,
        human_reviewed: bool = False,
        review_date: Optional[str] = None,
        format_type: str = 'standard'
    ) -> str:
        """
        Generate standardized AI disclosure statement.
        
        Args:
            ai_detection: AI detection percentage (0-100)
            trust_score: Trust score (0-100)
            risk_tier: Risk tier (LOW, MEDIUM, HIGH)
            human_reviewed: Whether expert review has been attested
            review_date: Date of expert review (YYYY-MM-DD format)
            format_type: 'standard', 'extended', 'twitter', 'linkedin', 'email'
            
        Returns:
            Formatted disclosure statement appropriate for context
        """
        if format_type == 'twitter':
            return self._generate_twitter_disclosure(ai_detection, trust_score, risk_tier, human_reviewed)
        elif format_type == 'linkedin':
            return self._generate_linkedin_disclosure(ai_detection, trust_score, risk_tier, human_reviewed, review_date)
        elif format_type == 'extended':
            return self._generate_extended_disclosure(ai_detection, trust_score, risk_tier, human_reviewed, review_date)
        elif format_type == 'email':
            return self._generate_email_disclosure(ai_detection, trust_score, risk_tier, human_reviewed, review_date)
        else:
            return self._generate_standard_disclosure(ai_detection, trust_score, risk_tier, human_reviewed, review_date)
    
    def _generate_standard_disclosure(
        self,
        ai_detection: float,
        trust_score: float,
        risk_tier: str,
        human_reviewed: bool,
        review_date: Optional[str]
    ) -> str:
        """Generate standard disclosure statement for summaries/reports"""
        review_status = f"completed on {review_date}" if review_date else "completed"
        review_note = f"Expert review {review_status}." if human_reviewed else "Expert review recommended."
        
        return (
            f"This policy assessment includes AI-assisted analysis ({ai_detection:.0f}% detected). "
            f"{review_note} "
            f"Trust Score: {trust_score:.0f}/100. "
            f"Risk Tier: {risk_tier}. "
            f"See full certificate for methodology details."
        )
    
    def _generate_twitter_disclosure(
        self,
        ai_detection: float,
        trust_score: float,
        risk_tier: str,
        human_reviewed: bool
    ) -> str:
        """Generate concise disclosure for X (Twitter) - character-limited"""
        review_mark = "✓" if human_reviewed else "⚠️"
        return (
            f"{review_mark} AI-assisted analysis ({ai_detection:.0f}% detected). "
            f"Trust: {trust_score:.0f}/100 | Risk: {risk_tier}. "
            f"🔗 Full certificate for details."
        )
    
    def _generate_linkedin_disclosure(
        self,
        ai_detection: float,
        trust_score: float,
        risk_tier: str,
        human_reviewed: bool,
        review_date: Optional[str]
    ) -> str:
        """Generate professional disclosure for LinkedIn"""
        review_status = f"completed on {review_date}" if review_date else "completed"
        review_note = f"Expert review {review_status}." if human_reviewed else "Expert review recommended."
        
        risk_context = {
            'LOW': 'minimal governance concerns',
            'MEDIUM': 'material governance concerns requiring attention',
            'HIGH': 'substantial governance concerns requiring escalation'
        }.get(risk_tier, 'governance review')
        
        return (
            f"**Transparency Disclosure**: This analysis includes AI-assisted components ({ai_detection:.0f}% detected). "
            f"{review_note} "
            f"Assessment confidence: {trust_score:.0f}/100. "
            f"Risk profile: {risk_tier} ({risk_context}). "
            f"For full methodology and certification details, see the complete assessment report."
        )
    
    def _generate_extended_disclosure(
        self,
        ai_detection: float,
        trust_score: float,
        risk_tier: str,
        human_reviewed: bool,
        review_date: Optional[str]
    ) -> str:
        """Generate comprehensive disclosure with context for formal reports"""
        review_status = f"on {review_date}" if review_date else "upon request"
        review_note = f"Expert review completed {review_status}." if human_reviewed else "Expert review required before publication."
        
        risk_details = {
            'LOW': (
                'This assessment carries minimal AI-related governance risk. '
                'AI-assisted components have been validated and pose no material concerns.'
            ),
            'MEDIUM': (
                'This assessment carries material AI-related governance risks. '
                'Key findings require expert validation and institutional oversight. '
                'Recommend escalation for senior policy review.'
            ),
            'HIGH': (
                'This assessment carries substantial AI-related governance risks. '
                'All core recommendations require expert review and stakeholder consultation. '
                'Immediate escalation to governance authority is recommended.'
            )
        }.get(risk_tier, 'Assessment requires governance review.')
        
        return (
            f"## AI Involvement & Governance Disclosure\n\n"
            f"**AI Detection Level**: {ai_detection:.0f}% of content identified as AI-assisted\n"
            f"**Trust Score**: {trust_score:.0f}/100 (confidence in assessment validity)\n"
            f"**Risk Tier**: {risk_tier}\n"
            f"**Expert Review Status**: {review_note}\n\n"
            f"**Risk Context**: {risk_details}\n\n"
            f"**Methodology**: Assessment conducted using Sparrow SPOT Scale™ v8.0, "
            f"integrating NIST AI RMF governance principles with multi-stakeholder critique integration. "
            f"See certification document for complete technical details."
        )
    
    def _generate_email_disclosure(
        self,
        ai_detection: float,
        trust_score: float,
        risk_tier: str,
        human_reviewed: bool,
        review_date: Optional[str]
    ) -> str:
        """Generate disclosure for email communications"""
        review_status = f"on {review_date}" if review_date else "pending"
        review_emoji = "✓" if human_reviewed else "⚠️"
        
        return (
            f"—\n"
            f"Governance Notice: This policy assessment includes AI-assisted analysis.\n"
            f"• AI Detection: {ai_detection:.0f}%\n"
            f"• Trust Score: {trust_score:.0f}/100\n"
            f"• Risk Tier: {risk_tier}\n"
            f"• Expert Review: {review_emoji} {review_status}\n"
            f"→ See attached certificate for complete assessment details.\n"
        )
    
    def generate_escalation_disclosure(
        self,
        trust_score: float,
        risk_tier: str,
        ai_detection: float,
        escalation_reasons: Optional[list] = None
    ) -> str:
        """
        Generate escalation-specific disclosure when assessment requires senior review.
        
        Implements Recommendation #5: "Establish Escalation Protocols Tied to Trust and Risk Thresholds"
        """
        escalation_triggers = []
        
        if trust_score < 70:
            escalation_triggers.append(f"Trust Score below threshold: {trust_score:.0f}/100 (trigger: <70)")
        if risk_tier in ['MEDIUM', 'HIGH']:
            escalation_triggers.append(f"Risk Tier: {risk_tier} (triggers: MEDIUM or HIGH)")
        if ai_detection > 50:
            escalation_triggers.append(f"AI Detection elevated: {ai_detection:.0f}% (trigger: >50%)")
        
        if escalation_reasons:
            escalation_triggers.extend(escalation_reasons)
        
        triggers_text = "\n".join([f"  • {trigger}" for trigger in escalation_triggers])
        
        return (
            f"⚠️ ESCALATION REQUIRED ⚠️\n\n"
            f"This policy assessment has been flagged for senior governance review based on:\n"
            f"{triggers_text}\n\n"
            f"**Required Action**: Route to designated policy analyst or senior review authority "
            f"before final publication or stakeholder release.\n"
            f"**Review Scope**: Validate AI-assisted components, confirm policy alignment, "
            f"assess fairness across stakeholder groups.\n"
            f"**Timeline**: Complete within [X business days per organizational policy]."
        )


def create_ai_disclosure_generator() -> AIDisclosureGenerator:
    """Factory function to create AI disclosure generator"""
    return AIDisclosureGenerator()


# v8.3: Comprehensive multi-format disclosure generation (when initialized with full analysis data)
# Extends AIDisclosureGenerator class with additional methods


def _add_comprehensive_methods():
    """Add comprehensive disclosure generation methods to AIDisclosureGenerator class"""
    
    def _get_ai_percentage(self) -> float:
        """Extract AI percentage from detection results.
        
        v8.3.1: Prioritize deep analysis consensus over basic detection for consistency
        with certificate generation.
        """
        # First, check for deep analysis consensus (most accurate, 6-level weighted analysis)
        deep_analysis = self.data.get('deep_analysis', {})
        if deep_analysis:
            consensus = deep_analysis.get('consensus', {})
            if consensus and 'ai_percentage' in consensus:
                return consensus['ai_percentage']
        
        # Fallback to basic ai_detection score
        if not self.ai_detection:
            return 0.0
        # Handle both formats: decimal (0.532) or percentage (53.2)
        score = self.ai_detection.get('ai_detection_score', 0)
        if score < 1.0:
            return score * 100
        return score
    
    def _get_model_info(self) -> Dict[str, any]:
        """Extract AI model identification and confidence."""
        if not self.ai_detection:
            return {'model': 'Unknown', 'confidence': 0}
        
        likely_model = self.ai_detection.get('likely_ai_model', {})
        if isinstance(likely_model, dict):
            # Check if we have model_scores to get the actual highest scoring model
            model_scores = likely_model.get('model_scores', {})
            if model_scores:
                # Find the highest scoring model
                highest_model = max(model_scores.items(), key=lambda x: x[1])
                model_name, confidence = highest_model
                
                # Clean up model names for better display
                if model_name.lower() == 'cohere':
                    display_name = 'Cohere'
                elif 'claude' in model_name.lower():
                    display_name = 'Claude (Anthropic)'
                elif 'gemini' in model_name.lower():
                    display_name = 'Google Gemini'
                elif 'mistral' in model_name.lower():
                    display_name = 'Mistral AI'
                elif 'llama' in model_name.lower() or 'ollama' in model_name.lower():
                    display_name = 'Ollama/Llama'
                else:
                    display_name = model_name
                
                return {
                    'model': display_name,
                    'confidence': confidence * 100
                }
            
            # Fallback to the likely_ai_model.model if no model_scores
            return {
                'model': likely_model.get('model', 'Unknown'),
                'confidence': likely_model.get('confidence', 0) * 100
            }
        return {'model': 'Unknown', 'confidence': 0}
    
    def _get_flagged_sections(self) -> List[Dict]:
        """Get sections flagged as AI-generated."""
        if not self.ai_detection:
            return []
        return self.ai_detection.get('flagged_sections', [])
    
    def _get_ai_level(self, percentage: float) -> str:
        """Categorize AI usage level."""
        if percentage < 10:
            return "Minimal AI Assistance"
        elif percentage < 25:
            return "Light AI Assistance"
        elif percentage < 50:
            return "Moderate AI Assistance"
        elif percentage < 75:
            return "Substantial AI Assistance"
        else:
            return "Heavy AI Assistance"
    
    def _get_confidence_indicator(self) -> str:
        """
        v8.3.2: Get confidence level indicator for AI detection.
        
        Returns a human-readable confidence assessment based on:
        - Number of analysis levels with data
        - Agreement between detection methods
        - Model identification confidence
        """
        deep = self.data.get('deep_analysis', {})
        if not deep:
            return "Low Confidence - limited analysis data"
        
        # Count levels with data
        # v8.3.3 Fix: Use correct key names from deep_analyzer.py
        levels = ['level1_document', 'level2_sections', 'level3_patterns',
                 'level4_sentences', 'level5_fingerprints', 'level6_statistics']
        level_count = sum(1 for l in levels if deep.get(l))
        
        consensus = deep.get('consensus', {})
        confidence = consensus.get('confidence', 0)
        
        # Normalize confidence
        if confidence <= 2:
            confidence = confidence * 100
        confidence = min(confidence, 100)
        
        if level_count >= 5 and confidence >= 80:
            return "High Confidence - multi-method consensus"
        elif level_count >= 3 and confidence >= 60:
            return "Medium Confidence - partial consensus"
        elif level_count >= 2:
            return "Low Confidence - limited consensus"
        else:
            return "Uncertain - insufficient data"
    
    def generate_government_formal(self, document_name: str = None) -> str:
        """Generate formal government disclosure statement (NEW in v8.3)"""
        if not self.data:
            return "Error: No analysis data provided. Initialize with full analysis JSON."
        
        ai_pct = self._get_ai_percentage()
        model_info = self._get_model_info()
        ai_level = self._get_ai_level(ai_pct)
        confidence_indicator = self._get_confidence_indicator()  # v8.3.2
        
        doc_line = f"Document: {document_name}\n" if document_name else ""
        
        return f"""ARTIFICIAL INTELLIGENCE TRANSPARENCY DISCLOSURE
{doc_line}Generated: {datetime.now().strftime('%B %d, %Y')}
Analysis Version: Sparrow SPOT Scale™ {self.metadata['version']}

AI USAGE SUMMARY
• Overall AI Content: {ai_pct:.1f}% ({confidence_indicator})
• Classification: {ai_level}
• Primary AI Model: {model_info['model']}
• Detection Confidence: {model_info['confidence']:.1f}%

This {self.metadata['document_type']} was prepared with artificial intelligence assistance.
Expert review of AI-generated content is recommended before use.

For complete disclosure and methodology, see full transparency certificate."""
    
    def generate_plain_language(self, document_name: str = None) -> str:
        """Generate plain-language disclosure for public (NEW in v8.3)"""
        if not self.data:
            return "Error: No analysis data provided."
        
        ai_pct = self._get_ai_percentage()
        model_info = self._get_model_info()
        
        meaning = ""
        if ai_pct < 25:
            meaning = "AI played a minor role - mostly helping with routine tasks."
        elif ai_pct < 50:
            meaning = "AI played a moderate role - helping draft content. Expert review is recommended."
        else:
            meaning = "AI played a major role - creating substantial content. Expert review is essential."
        
        doc_line = f"\nDocument: {document_name}" if document_name else ""
        
        return f"""About This Document: AI Transparency Notice{doc_line}

We detected that about {ai_pct:.0f}% of this document appears to be AI-generated.
The AI system used was likely: {model_info['model']}

{meaning}

Expert review of AI-generated content is recommended. The publisher takes responsibility for accuracy."""
    
    def generate_social_media(self, document_name: str = None) -> Dict[str, str]:
        """Generate short-form disclosures for social media (NEW in v8.3)"""
        if not self.data:
            return {'error': 'No analysis data'}
        
        ai_pct = self._get_ai_percentage()
        model_info = self._get_model_info()
        
        # v8.3.3: Updated to honest language - no unverifiable claims
        if document_name:
            twitter = f"🔍 AI Transparency ({document_name}): {ai_pct:.1f}% AI-generated ({model_info['model']}). Expert review recommended. #AITransparency"
        else:
            twitter = f"🔍 AI Transparency: This document is {ai_pct:.1f}% AI-generated ({model_info['model']}). Expert review recommended. #AITransparency"

        doc_line = f"\nDocument: {document_name}\n" if document_name else ""
        linkedin = f"""AI Transparency Disclosure{doc_line}
This {self.metadata['document_type']} was prepared with AI assistance:

📊 AI Content: {ai_pct:.1f}%
🤖 Model: {model_info['model']}
⚠️ Expert Review: Recommended

We believe in transparency about AI use in government.

#AITransparency #ResponsibleAI"""
        
        return {
            'twitter': twitter[:280],
            'linkedin': linkedin
        }
    
    def generate_all_formats(self, output_prefix: str = 'ai_disclosure', document_name: str = None) -> List[str]:
        """Generate all disclosure formats and save to files (NEW in v8.3)"""
        if not self.data:
            print("Error: No analysis data. Initialize AIDisclosureGenerator with full analysis JSON.")
            return []
        
        files_created = []
        
        # Extract document name from output_prefix if not provided
        if not document_name and output_prefix:
            # Remove common suffixes like _analysis
            document_name = output_prefix.replace('_analysis', '').replace('_', ' ').title()
        
        # Formal government statement
        try:
            formal_file = f"{output_prefix}_ai_disclosure_formal.txt"
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(formal_file), exist_ok=True) if os.path.dirname(formal_file) else None
            with open(formal_file, 'w') as f:
                f.write(self.generate_government_formal(document_name))
            files_created.append(formal_file)
        except Exception as e:
            print(f"Error generating formal disclosure: {e}")
        
        # Plain language
        try:
            plain_file = f"{output_prefix}_ai_disclosure_plain.txt"
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(plain_file), exist_ok=True) if os.path.dirname(plain_file) else None
            with open(plain_file, 'w') as f:
                f.write(self.generate_plain_language(document_name))
            files_created.append(plain_file)
        except Exception as e:
            print(f"Error generating plain disclosure: {e}")
        
        # Social media
        try:
            social_file = f"{output_prefix}_ai_disclosure_social.txt"
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(social_file), exist_ok=True) if os.path.dirname(social_file) else None
            social = self.generate_social_media(document_name)
            with open(social_file, 'w') as f:
                f.write("TWITTER/X:\n" + "="*60 + "\n")
                f.write(social.get('twitter', 'N/A'))
                f.write("\n\nLINKEDIN:\n" + "="*60 + "\n")
                f.write(social.get('linkedin', 'N/A'))
            files_created.append(social_file)
        except Exception as e:
            print(f"Error generating social disclosure: {e}")
        
        # Combined HTML
        try:
            html_file = f"{output_prefix}_ai_disclosure_all.html"
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(html_file), exist_ok=True) if os.path.dirname(html_file) else None
            with open(html_file, 'w') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head><title>AI Transparency Disclosure</title>
<style>body{{font-family:Arial;margin:20px;}}h1{{color:#0066cc;}}</style>
</head>
<body>
<h1>AI Transparency Disclosure</h1>
<p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y')}</p>

<h2>Government Formal</h2>
<pre>{self.generate_government_formal(document_name)}</pre>

<h2>Plain Language</h2>
<pre>{self.generate_plain_language(document_name)}</pre>

<h2>Social Media</h2>
<pre>TWITTER: {self.generate_social_media(document_name).get('twitter', 'N/A')}

LINKEDIN: {self.generate_social_media(document_name).get('linkedin', 'N/A')}</pre>
</body>
</html>""")
            files_created.append(html_file)
        except Exception as e:
            print(f"Error generating HTML disclosure: {e}")
        
        return files_created
    
    # Add methods to class
    AIDisclosureGenerator._get_ai_percentage = _get_ai_percentage
    AIDisclosureGenerator._get_model_info = _get_model_info
    AIDisclosureGenerator._get_flagged_sections = _get_flagged_sections
    AIDisclosureGenerator._get_ai_level = _get_ai_level
    AIDisclosureGenerator._get_confidence_indicator = _get_confidence_indicator  # v8.3.2
    AIDisclosureGenerator.generate_government_formal = generate_government_formal
    AIDisclosureGenerator.generate_plain_language = generate_plain_language
    AIDisclosureGenerator.generate_social_media = generate_social_media
    AIDisclosureGenerator.generate_all_formats = generate_all_formats


# Apply comprehensive methods
_add_comprehensive_methods()

"""
AI Usage Explanation Generator for Sparrow SPOT Scale™ v8.4.0

Generates detailed, plain-language explanations of how AI was used in analyzed documents.
This module synthesizes detection data into actionable insights about:
- Where AI content appears in the document
- What types of content appear to be AI-generated
- Which critical sections may have AI involvement
- Model attribution and confidence levels
- Transparency assessment and recommendations

NEW in v8.3.3: Addresses the need for detailed AI usage reports beyond raw detection data.
v8.3.4: Integrates comprehensive document type baselines to recognize domain conventions
        and provide accurate context in reports.
v8.4.0: INCONCLUSIVE detection handling - when detection spread >50%, AI attribution
        is suppressed and replaced with uncertainty messaging.
"""

import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import os


class AIUsageExplainer:
    """Generate detailed AI usage explanations from SPOT Scale analysis data."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize with Ollama endpoint."""
        self.ollama_url = ollama_url
        self.model = "granite4:tiny-h"  # Primary model for explanations
        self.fallback_model = "qwen2.5:7b"
        self.version = "8.4.0"
    
    def _call_ollama(self, prompt: str, model: Optional[str] = None, max_tokens: int = 2000) -> Optional[str]:
        """Call Ollama API for text generation."""
        model = model or self.model
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.6,  # Slightly lower for factual accuracy
                    "num_predict": max_tokens,
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Ollama error with {model}: {str(e)}")
            return None
    
    def generate_ai_usage_report(
        self,
        analysis_data: Dict[str, Any],
        document_title: str = "Document",
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive AI usage explanation from analysis data.
        
        Args:
            analysis_data: Full SPOT Scale analysis JSON
            document_title: Title of the analyzed document
            output_file: Optional path to save report
            
        Returns:
            Detailed AI usage explanation text
        """
        print(f"📊 Generating AI Usage Explanation for: {document_title}")
        
        # Extract key data
        ai_detection = analysis_data.get('ai_detection', {})
        deep_analysis = analysis_data.get('deep_analysis', {})
        document_type = analysis_data.get('document_type', 'policy_brief')
        
        # Build the report sections
        sections = []
        
        # 1. Executive Summary
        sections.append(self._generate_executive_summary(ai_detection, deep_analysis, document_title, document_type))
        
        # 2. AI Detection Overview
        sections.append(self._generate_detection_overview(ai_detection, deep_analysis))
        
        # 3. Model Attribution Analysis
        sections.append(self._generate_model_attribution(ai_detection, deep_analysis))
        
        # 4. Critical Sections Analysis
        sections.append(self._generate_critical_sections_analysis(ai_detection, deep_analysis, document_type))
        
        # 5. Pattern Analysis Explained
        sections.append(self._generate_pattern_explanation(deep_analysis))
        
        # 6. Phrase Fingerprints Explained
        sections.append(self._generate_fingerprint_explanation(deep_analysis))
        
        # 7. Transparency Assessment
        sections.append(self._generate_transparency_assessment(analysis_data, document_type))
        
        # 8. Recommendations
        sections.append(self._generate_recommendations(ai_detection, deep_analysis, document_type))
        
        # Compile full report
        report = self._compile_report(sections, document_title, analysis_data)
        
        # Use Ollama to enhance key sections with synthesis
        enhanced_report = self._enhance_with_ollama(report, analysis_data, document_type)
        
        # Save if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_report)
            print(f"   ✓ Saved: {output_file}")
        
        return enhanced_report
    
    def _generate_executive_summary(
        self, 
        ai_detection: Dict, 
        deep_analysis: Dict,
        document_title: str,
        document_type: str
    ) -> str:
        """Generate executive summary section."""
        
        ai_percentage = ai_detection.get('ai_detection_score', 0) * 100
        has_deep_consensus = False
        if deep_analysis:
            level1 = deep_analysis.get('level1_document', {})
            consensus = deep_analysis.get('consensus', {})
            if consensus and 'ai_percentage' in consensus:
                ai_percentage = consensus.get('ai_percentage', ai_percentage)
                has_deep_consensus = True
            elif level1:
                ai_percentage = level1.get('ai_percentage', ai_percentage)
        
        model_info = ai_detection.get('likely_ai_model', {})
        primary_model = model_info.get('model', 'Unknown')
        model_confidence = model_info.get('confidence', 0) * 100
        
        # v8.3.4: Get document baseline if available
        document_baseline = ai_detection.get('document_baseline', {})
        detected_type = ai_detection.get('detected_document_type', document_type)
        is_specialized = document_baseline.get('is_specialized', False)
        baseline_pattern_count = document_baseline.get('pattern_count', 0)
        score_adjustment = document_baseline.get('score_adjustment', 0) * 100
        conventions = document_baseline.get('conventions', [])
        
        # v8.3.3: Get detection spread if available
        detection_spread = ai_detection.get('detection_spread', 0) * 100
        domain_warnings = ai_detection.get('domain_warnings', [])
        
        # v8.4.0: Check for INCONCLUSIVE detection
        detection_inconclusive = ai_detection.get('detection_inconclusive', False)
        inconclusive_reason = ai_detection.get('inconclusive_reason', '')
        
        # v8.4.2: Override usage level only if deep consensus is NOT available
        if (detection_inconclusive or detection_spread > 50) and not has_deep_consensus:
            usage_level = "⚠️ INCONCLUSIVE"
            usage_description = (
                "CANNOT be reliably assessed. Detection methods produced conflicting results "
                f"(spread: {detection_spread:.0f}%). Professional manual review is required."
            )
        # Determine AI usage level - v8.3.3: Use cautious language
        elif ai_percentage < 15:
            usage_level = "Minimal"
            usage_description = "shows patterns consistent with primarily human authorship"
        elif ai_percentage < 35:
            usage_level = "Low"
            usage_description = "shows some patterns associated with AI-assisted content"
        elif ai_percentage < 55:
            usage_level = "Moderate"
            usage_description = "shows patterns that MAY indicate AI-generated content mixed with human writing"
        elif ai_percentage < 75:
            usage_level = "High"
            usage_description = "shows strong patterns associated with AI generation (requires verification)"
        else:
            usage_level = "Very High"
            usage_description = "shows patterns strongly consistent with AI generation (requires verification)"
        
        # v8.3.4: Generate document type context based on detected type and baseline
        if is_specialized:
            conventions_text = ", ".join(conventions[:2]) if conventions else "domain-specific patterns"
            doc_context = (
                f"⚠️ **SPECIALIZED DOCUMENT**: This {detected_type.replace('_', ' ')} uses "
                f"standard domain conventions ({conventions_text}) that may trigger false positives. "
                f"Detected {baseline_pattern_count:,} standard patterns. "
                f"Score adjusted by {score_adjustment:.0f}% to reduce false positives."
            )
        elif document_type == 'legislation':
            doc_context = (
                "⚠️ **IMPORTANT**: Legislative text uses formulaic drafting conventions "
                "(enumerated lists, legal terminology, standardized phrases) that may "
                "trigger false positives in AI detection. Results should be interpreted "
                "with caution and verified against official sources."
            )
        elif document_type == 'budget':
            doc_context = (
                "As a budget document, AI involvement in fiscal projections or explanatory "
                "text should be noted for accountability if confirmed."
            )
        else:
            doc_context = "AI involvement in policy documents should be disclosed for public trust if confirmed."
        
        flagged_count = len(ai_detection.get('flagged_sections', []))
        
        # v8.4.2: Add INCONCLUSIVE warning only when no deep consensus available
        disagreement_warning = ""
        if (detection_inconclusive or detection_spread > 50) and not has_deep_consensus:
            disagreement_warning = f"""
### 🚨 DETECTION INCONCLUSIVE

Detection methods disagree by **{detection_spread:.0f} percentage points**. This exceeds the 
50% threshold for reliable detection. **AI involvement CANNOT be reliably determined.**

{inconclusive_reason if inconclusive_reason else 'Results should be treated as inconclusive.'}

**Recommendation:** Manual expert review required. The {ai_percentage:.1f}% figure should NOT 
be cited as a reliable estimate.
"""
        elif detection_spread > 40:
            disagreement_warning = f"""
### ⚠️ Detection Method Disagreement

Detection methods disagree by **{detection_spread:.0f} percentage points**. This indicates 
significant uncertainty in the AI content estimate. The {ai_percentage:.1f}% figure is an 
average that obscures substantial disagreement between methods. **Interpret with caution.**
"""
        
        # v8.4.2: Suppress model attribution only when INCONCLUSIVE and no deep consensus
        if (detection_inconclusive or detection_spread > 50) and not has_deep_consensus:
            model_display = "N/A (Detection Inconclusive)"
            model_confidence_display = "N/A"
        else:
            model_display = primary_model
            model_confidence_display = f"{model_confidence:.0f}%"
        
        return f"""## EXECUTIVE SUMMARY

**Document:** {document_title}
**Document Type:** {document_type.replace('_', ' ').title()}
**Detected AI Patterns:** {usage_level} ({ai_percentage:.1f}%) — *estimate, not verified*
**Primary Model Signature:** {model_display} ({model_confidence_display} pattern match)
**Flagged Sections:** {flagged_count} sections for review
{disagreement_warning}
### Key Finding

This document {usage_description}.

{doc_context}

### At a Glance

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Overall AI Content | {ai_percentage:.1f}% | {usage_level} AI involvement |
| Model Attribution | {model_display} | {model_confidence_display} confidence |
| Sections Flagged | {flagged_count} | Require professional review |
| Detection Methods | {len(ai_detection.get('methods', []))} | Multi-method consensus |
"""
    
    def _generate_detection_overview(self, ai_detection: Dict, deep_analysis: Dict) -> str:
        """Generate detection methodology overview."""
        
        methods = ai_detection.get('methods', [])
        model_scores = ai_detection.get('model_scores', {})
        
        # Build method breakdown
        method_lines = []
        for method in methods:
            score = model_scores.get(method, 0) * 100
            method_lines.append(f"| {method.title()} | {score:.1f}% |")
        
        method_table = "\n".join(method_lines)
        
        # Consensus analysis
        scores = list(model_scores.values())
        if scores:
            avg_score = sum(scores) / len(scores) * 100
            min_score = min(scores) * 100
            max_score = max(scores) * 100
            spread = max_score - min_score
            
            if spread < 20:
                consensus = "Strong consensus across detection methods"
            elif spread < 40:
                consensus = "Moderate consensus with some variation"
            else:
                consensus = "Significant disagreement between methods - interpret with caution"
        else:
            avg_score = 0
            consensus = "No detection data available"
        
        # v8.3.5: Calculate and note authoritative score
        deep_consensus = deep_analysis.get('consensus', {}).get('ai_percentage', None)
        level1_score = deep_analysis.get('level1_document', {}).get('ai_percentage', None) if deep_analysis else None
        
        # Note about score discrepancy if present
        score_note = ""
        if deep_consensus and abs(deep_consensus - avg_score) > 5:
            score_note = f"""
### ⚠️ Score Discrepancy Note

- **Reported AI Score in Executive Summary**: {deep_consensus:.1f}% (deep analysis consensus)
- **Average of Individual Methods**: {avg_score:.1f}% (simple average)

The Executive Summary uses the **deep analysis consensus score** which applies weighted 
averaging across 6 analysis levels. This is the **authoritative figure**. The method-by-method 
average shown above is for transparency about individual detection methods, but is less accurate 
because it doesn't account for method reliability or domain context.
"""
        
        # v8.4.1: Add consensus breakdown if available
        consensus_breakdown = ""
        consensus_data = deep_analysis.get('consensus', {})
        breakdown = consensus_data.get('breakdown', [])
        if breakdown:
            breakdown_lines = []
            for item in breakdown:
                level_name = item.get('name', item.get('level', 'Unknown'))
                score = item.get('score', 0)
                weight = item.get('weight', 0) * 100
                contribution = item.get('contribution', 0)
                breakdown_lines.append(f"| {level_name} | {score:.1f}% | {weight:.0f}% | {contribution:.2f}% |")
            
            breakdown_table = "\n".join(breakdown_lines)
            formula = consensus_data.get('formula', 'Weighted average of levels')
            
            consensus_breakdown = f"""
### 📊 Consensus Breakdown (v8.4.1)

How the {deep_consensus:.1f}% consensus score was calculated:

| Analysis Level | AI Score | Weight | Contribution |
|----------------|----------|--------|--------------|
{breakdown_table}
| **Total** | | | **{deep_consensus:.1f}%** |

**Formula:** {formula}

**Note:** Different levels have different weights based on reliability. Document-level 
analysis (30%) is weighted highest because it considers overall patterns. Statistical 
analysis (15%) is weighted lower as it can be affected by writing style.
"""
        
        return f"""## DETECTION METHODOLOGY

### How AI Content Was Detected

This analysis employed {len(methods)} detection methods to identify AI-generated content:

| Method | AI Score |
|--------|----------|
{method_table}

### Detection Consensus

**{consensus}**

- Average AI Score: {avg_score:.1f}%
- Score Range: {min_score:.1f}% - {max_score:.1f}%
- Spread: {spread:.1f} percentage points
{score_note}{consensus_breakdown}
### Interpretation

Multiple detection methods provide cross-validation. High agreement between methods 
increases confidence in the AI content estimate. Significant disagreement suggests 
the content may be difficult to classify or contains mixed authorship.
"""
    
    def _generate_model_attribution(self, ai_detection: Dict, deep_analysis: Dict) -> str:
        """Generate model attribution analysis."""
        
        # v8.4.0: Check for INCONCLUSIVE detection
        # v8.4.2: Check if deep consensus is available
        detection_spread = ai_detection.get('detection_spread', 0) * 100
        detection_inconclusive = ai_detection.get('detection_inconclusive', False)
        has_deep_consensus = deep_analysis and 'consensus' in deep_analysis and deep_analysis.get('consensus', {}).get('ai_percentage') is not None
        
        # v8.4.2: Only suppress if INCONCLUSIVE and no deep consensus
        if (detection_inconclusive or detection_spread > 50) and not has_deep_consensus:
            return f"""## MODEL ATTRIBUTION ANALYSIS

### 🚨 ATTRIBUTION SUPPRESSED - Detection Inconclusive

Model attribution is **not available** because AI detection results are inconclusive.

**Detection Spread:** {detection_spread:.0f}% (threshold: 50%)

When detection methods disagree by more than 50 percentage points, it is not possible 
to reliably determine:
1. Whether AI was used at all
2. Which AI model (if any) was involved

**Recommendation:** Do not cite any AI model as likely source. Manual expert review 
is required to make any determination about AI involvement.

### Why This Matters

Claiming "90% confidence in {ai_detection.get('likely_ai_model', {}).get('model', 'ModelX')}" when detection methods 
disagree by {detection_spread:.0f}% would be misleading. The model attribution algorithms can 
only provide useful information when there is consensus that AI content is present.

High detection spread indicates one of:
- The document contains mixed human/AI content
- Domain-specific writing patterns are triggering false positives
- Detection algorithms are not well-suited for this content type
- The underlying analysis data is unreliable

**No model attribution should be cited from this analysis.**
"""
        
        model_info = ai_detection.get('likely_ai_model', {})
        model_scores = model_info.get('model_scores', {})
        
        primary_model = model_info.get('model', 'Unknown')
        primary_confidence = model_info.get('confidence', 0) * 100
        analysis_text = model_info.get('analysis', 'No detailed analysis available')
        
        # Sort models by score
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        
        model_lines = []
        for model, score in sorted_models:
            bar_length = int(score * 100 / 5)  # Scale to 20 chars max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            model_lines.append(f"| {model:20} | {bar} | {score*100:.1f}% |")
        
        model_table = "\n".join(model_lines)
        
        # Model characteristics
        model_traits = {
            'Cohere': "Known for structured, formal language with clear enumeration and professional tone",
            'GPT-4': "Characterized by comprehensive responses, hedging language, and balanced presentation",
            'Claude (Anthropic)': "Notable for thoughtful caveats, ethical considerations, and nuanced language",
            'Ollama/Llama': "Open-source patterns with varied characteristics depending on fine-tuning",
            'Google Gemini': "Technical precision with structured formatting and citation awareness",
            'Mistral AI': "European-trained model with multilingual capabilities and formal tone",
        }
        
        traits = model_traits.get(primary_model, "Specific model characteristics not profiled")
        
        return f"""## MODEL ATTRIBUTION ANALYSIS

### Primary Model Identification

**Most Likely AI Model:** {primary_model}
**Attribution Confidence:** {primary_confidence:.0f}%
**Analysis:** {analysis_text}

### ⚠️ Understanding Confidence Metrics

There are TWO distinct confidence measures in this report:

| Metric | Question Answered | This Report |
|--------|-------------------|-------------|
| **Detection Confidence** | "How certain are we that AI was used at all?" | See detection spread above |
| **Attribution Confidence** | "IF AI was used, which model was it likely?" | {primary_confidence:.0f}% |

**Attribution confidence ({primary_confidence:.0f}%)** indicates pattern match to {primary_model} *assuming* AI was used. 
This does NOT indicate certainty that AI was used - only which model patterns are present IF AI was involved.

### Model Signature Comparison

| Model | Confidence Bar | Score |
|-------|----------------|-------|
{model_table}

### Model Characteristics

**{primary_model}**: {traits}

### What This Means

When content matches a specific model's patterns, it suggests that model (or a model 
trained on similar data) was used to generate portions of the document. This is 
probabilistic - humans can also exhibit similar patterns, especially when writing 
formally or using templates.

### Confidence Interpretation

- **90-100%**: Very high confidence - strong stylistic match to known model
- **70-89%**: High confidence - clear model signatures present
- **50-69%**: Moderate confidence - some matching patterns
- **Below 50%**: Low confidence - mixed or unclear attribution
"""
    
    def _generate_critical_sections_analysis(
        self, 
        ai_detection: Dict, 
        deep_analysis: Dict,
        document_type: str
    ) -> str:
        """Analyze which critical sections may have AI involvement."""
        
        flagged_sections = ai_detection.get('flagged_sections', [])
        
        if not flagged_sections:
            return """## CRITICAL SECTIONS ANALYSIS

### Flagged Sections

No sections were flagged for elevated AI content. This suggests either:
- The document is primarily human-authored
- AI content is evenly distributed without concentration in specific sections
- AI was used for minor assistance throughout rather than generating whole sections
"""
        
        # Analyze flagged sections
        section_lines = []
        critical_findings = []
        
        for i, section in enumerate(flagged_sections[:10], 1):  # Limit to top 10
            section_num = section.get('section', i)
            likelihood = section.get('ai_likelihood', 0) * 100
            text_preview = section.get('text', '')[:100] + "..." if len(section.get('text', '')) > 100 else section.get('text', '')
            
            section_lines.append(f"""
**Section {section_num}** (AI Likelihood: {likelihood:.0f}%)
> {text_preview}
""")
            
            # Flag critical content
            if document_type == 'legislation':
                if any(term in text_preview.lower() for term in ['shall', 'must', 'prohibited', 'penalty', 'offense', 'fine']):
                    critical_findings.append(f"Section {section_num}: Contains binding legal language with {likelihood:.0f}% AI likelihood")
            elif document_type == 'budget':
                if any(term in text_preview.lower() for term in ['billion', 'million', 'allocation', 'revenue', 'expenditure']):
                    critical_findings.append(f"Section {section_num}: Contains fiscal figures with {likelihood:.0f}% AI likelihood")
        
        sections_text = "\n".join(section_lines)
        
        critical_section = ""
        if critical_findings:
            critical_list = "\n".join([f"- ⚠️ {finding}" for finding in critical_findings])
            critical_section = f"""
### ⚠️ Critical Content Flagged

The following sections contain critical content with elevated AI likelihood:

{critical_list}

**Recommendation:** These sections should receive priority professional review to ensure 
accuracy and appropriate human oversight of binding language or fiscal figures.
"""
        
        return f"""## CRITICAL SECTIONS ANALYSIS

### Sections with Elevated AI Content

{len(flagged_sections)} sections were flagged for elevated AI content ({'>'}60% likelihood):

{sections_text}
{critical_section}
### Section Analysis Notes

- Higher AI likelihood doesn't mean content is incorrect
- AI-generated sections may still be accurate and appropriate
- Human review should focus on factual accuracy and policy intent
- Consider disclosure requirements for AI-assisted sections
"""
    
    def _generate_pattern_explanation(self, deep_analysis: Dict) -> str:
        """Explain detected AI patterns in plain language."""
        
        level3 = deep_analysis.get('level3_patterns', {})
        pattern_details = level3.get('pattern_details', {})
        detailed_matches = level3.get('detailed_matches', {})
        
        if not pattern_details:
            return """## PATTERN ANALYSIS

No specific AI writing patterns were detected at the pattern level.
"""
        
        # Pattern explanations
        pattern_explanations = {
            'structured_lists': {
                'name': 'Structured Lists',
                'meaning': 'Numbered or bulleted content organized in formal sequences',
                'ai_indicator': 'AI models often default to list-based organization for clarity',
                'human_context': 'Humans also use lists, but AI tends to over-rely on this format'
            },
            'impact_statements': {
                'name': 'Impact Statements',
                'meaning': 'Phrases describing effects, consequences, or outcomes',
                'ai_indicator': 'AI often generates balanced impact language with hedging',
                'human_context': 'Common in formal writing but AI uses predictable phrasings'
            },
            'stakeholder_focus': {
                'name': 'Stakeholder Focus',
                'meaning': 'References to affected parties, groups, or interests',
                'ai_indicator': 'AI typically includes multiple stakeholder perspectives systematically',
                'human_context': 'May indicate AI-generated balance or genuine policy analysis'
            },
            'action_oriented': {
                'name': 'Action-Oriented Language',
                'meaning': 'Phrases indicating implementation, execution, or directives',
                'ai_indicator': 'AI models generate clear action items and implementation language',
                'human_context': 'Common in legislative/policy drafting regardless of authorship'
            },
            'hedging_language': {
                'name': 'Hedging Language',
                'meaning': 'Qualifiers like "may", "could", "potentially", "it is important to note"',
                'ai_indicator': 'AI safety training encourages cautious, hedged statements',
                'human_context': 'A strong AI signature when appearing with high frequency'
            },
            'formal_connectors': {
                'name': 'Formal Connectors',
                'meaning': 'Transitions like "Furthermore", "Additionally", "Moreover", "In conclusion"',
                'ai_indicator': 'AI uses these to create perceived logical flow',
                'human_context': 'Academic writing also uses these, but AI overuses certain phrases'
            }
        }
        
        pattern_sections = []
        for pattern_key, count in pattern_details.items():
            if count > 0:
                info = pattern_explanations.get(pattern_key, {
                    'name': pattern_key.replace('_', ' ').title(),
                    'meaning': 'Pattern detected',
                    'ai_indicator': 'May indicate AI involvement',
                    'human_context': 'Context-dependent'
                })
                
                # Get samples if available
                samples = detailed_matches.get(pattern_key, {}).get('samples', [])[:3]
                sample_text = ""
                if samples:
                    sample_lines = []
                    for s in samples[:2]:
                        text = s.get('matched_text', '')[:80]
                        sample_lines.append(f"  - \"{text}...\"")
                    sample_text = "\n" + "\n".join(sample_lines)
                
                pattern_sections.append(f"""
### {info['name']} ({count} instances)

**What it means:** {info['meaning']}

**Why it's an AI indicator:** {info['ai_indicator']}

**Context:** {info['human_context']}
{sample_text}
""")
        
        patterns_text = "\n".join(pattern_sections)
        total_patterns = sum(pattern_details.values())
        
        return f"""## PATTERN ANALYSIS EXPLAINED

### Overview

A total of **{total_patterns} AI-indicative patterns** were detected across the document.
These patterns are linguistic signatures that appear more frequently in AI-generated text.

{patterns_text}

### Pattern Interpretation Guide

Pattern detection is probabilistic. A high pattern count suggests AI involvement but is not 
definitive proof. Consider:

1. **Document context** - Formal documents naturally contain some of these patterns
2. **Pattern concentration** - AI content tends to cluster these patterns together
3. **Pattern variety** - AI typically uses multiple pattern types simultaneously
4. **Frequency vs. baseline** - Compare to typical human writing in this domain
"""
    
    def _generate_fingerprint_explanation(self, deep_analysis: Dict) -> str:
        """Explain phrase fingerprints in plain language."""
        
        level5 = deep_analysis.get('level5_fingerprints', {})
        
        if not level5:
            return """## PHRASE FINGERPRINT ANALYSIS

No specific phrase fingerprints were detected at this level.
"""
        
        fingerprints = level5.get('fingerprints', {})
        total = level5.get('total_fingerprints', 0)
        
        if total == 0:
            return """## PHRASE FINGERPRINT ANALYSIS

No AI model-specific phrase fingerprints were detected in this document.
This may indicate primarily human authorship or use of less distinctive AI models.
"""
        
        # Fingerprint explanations by model
        fingerprint_sections = []
        for model, data in fingerprints.items():
            if isinstance(data, dict):
                count = data.get('count', 0)
                phrases = data.get('phrases', [])
                if count > 0:
                    phrase_examples = ", ".join([f'"{p}"' for p in phrases[:5]])
                    fingerprint_sections.append(f"""
### {model} Fingerprints ({count} detected)

**Example phrases:** {phrase_examples}

These are characteristic phrases that appear frequently in {model}-generated content.
""")
        
        fingerprints_text = "\n".join(fingerprint_sections) if fingerprint_sections else "No model-specific fingerprints identified."
        
        return f"""## PHRASE FINGERPRINT ANALYSIS

### What Are Phrase Fingerprints?

Phrase fingerprints are specific word combinations and expressions that are characteristic 
of particular AI models. Each model has "tells" - phrases it uses more frequently than 
humans typically do.

### Total Fingerprints Detected: {total}

{fingerprints_text}

### Fingerprint Interpretation

- **High fingerprint count** for a specific model strongly suggests that model was used
- **Mixed fingerprints** suggest multiple AI tools or human editing of AI content
- **Low fingerprint count** may indicate human writing or heavily edited AI content
"""
    
    def _generate_transparency_assessment(self, analysis_data: Dict, document_type: str) -> str:
        """Generate transparency assessment."""
        
        ai_detection = analysis_data.get('ai_detection', {})
        criteria = analysis_data.get('criteria', {})
        
        ai_percentage = ai_detection.get('ai_detection_score', 0) * 100
        at_score = criteria.get('AT', {}).get('score', 0)
        
        # v8.3.3 FIX: Do NOT claim document "acknowledges AI" based on our detection
        # This is circular reasoning - we detect patterns, claim it's AI, then claim document
        # acknowledges AI based on our own claim
        
        # Check for actual explicit AI disclosure in text (simplified - real implementation 
        # would search for actual disclosure statements)
        explicit_disclosure_terms = [
            'generated by ai', 'ai-assisted', 'artificial intelligence was used',
            'drafted with ai', 'machine learning assisted', 'llm generated',
            'chatgpt', 'claude', 'copilot', 'ai drafting tool'
        ]
        
        # We don't have the raw text here, so we note this limitation
        disclosure_status = (
            "⚠️ DISCLOSURE STATUS UNKNOWN: This analysis cannot verify whether explicit "
            "AI disclosure statements exist in the document. Detection of AI patterns "
            "does not constitute acknowledgment of AI use by the document authors."
        )
        
        disclosure_recommendation = (
            "If AI tools were used in drafting, consider adding an explicit disclosure "
            "statement specifying which tools, for what purposes, and what human "
            "oversight occurred."
        )
        
        # v8.3.3: Add warning about detection limitations
        detection_warning = """
### ⚠️ IMPORTANT: Detection Limitations

This AI detection system identifies patterns that are **statistically associated** with 
AI-generated text. It CANNOT definitively prove AI was used because:

1. **No Ground Truth**: We have no official confirmation of AI use
2. **Domain Conventions**: Legal/legislative writing uses patterns that mimic AI
3. **Detection Disagreement**: Different methods produce divergent results
4. **Pattern ≠ Proof**: Matching AI patterns doesn't prove AI authorship

**The detection score is a probabilistic estimate, not a verified fact.**
"""
        
        # Document type specific requirements
        if document_type == 'legislation':
            requirements = """
**Legislative Transparency Considerations:**
- Parliamentary procedures may require disclosure of drafting assistance
- Legal counsel should review AI involvement in binding language
- Committee records should note significant AI assistance
- Consider public disclosure for accountability"""
        elif document_type == 'budget':
            requirements = """
**Budget Document Transparency Considerations:**
- Fiscal projections should clearly note if AI-assisted
- Treasury guidelines may require methodology disclosure
- Public accountability requires transparency about AI in financial estimates
- Audit trails should document AI involvement in calculations"""
        else:
            requirements = """
**Policy Document Transparency Considerations:**
- Public trust requires disclosure of AI assistance
- Stakeholders should know if analysis was AI-assisted
- Decision-makers need to understand AI involvement
- Regulatory frameworks increasingly require AI disclosure"""
        
        return f"""## TRANSPARENCY ASSESSMENT
{detection_warning}
### Current Disclosure Status

{disclosure_status}

**Detected AI Patterns:** {ai_percentage:.1f}% (estimate, not verified)

### Recommendation

{disclosure_recommendation}

{requirements}

### Best Practice AI Disclosure Elements

If AI was used, a complete disclosure should include:

1. **Acknowledgment** - Statement that AI tools were used
2. **Scope** - What parts of the document involved AI
3. **Role** - How AI was used (drafting, editing, analysis, etc.)
4. **Oversight** - Confirmation of human review and approval
5. **Model** - Optionally, which AI system(s) were used

### Sample Disclosure Statement (if applicable)

> "This document was prepared with AI drafting assistance. All content has been 
> reviewed by [appropriate authority] who takes full responsibility for accuracy 
> and policy intent. AI tools were used for [specific purposes]."
"""
    
    def _generate_recommendations(
        self, 
        ai_detection: Dict, 
        deep_analysis: Dict,
        document_type: str
    ) -> str:
        """Generate actionable recommendations."""
        
        ai_percentage = ai_detection.get('ai_detection_score', 0) * 100
        flagged_count = len(ai_detection.get('flagged_sections', []))
        
        recommendations = []
        priority_actions = []
        
        # Based on AI percentage
        if ai_percentage > 50:
            priority_actions.append("🔴 HIGH PRIORITY: Document has majority AI content - require professional review")
            recommendations.append("1. **Professional Review Required** - Substantial AI content detected. All sections should be reviewed by qualified professionals before finalization.")
        elif ai_percentage > 30:
            recommendations.append("1. **Review Flagged Sections** - Focus professional review on the {0} flagged sections with elevated AI likelihood.".format(flagged_count))
        else:
            recommendations.append("1. **Standard Review** - AI content is within acceptable ranges. Proceed with normal review processes.")
        
        # Based on document type
        if document_type == 'legislation':
            recommendations.append("2. **Legal Review** - Ensure binding legal language (\"shall\", \"must\", penalties) has been reviewed by legal counsel regardless of authorship.")
            recommendations.append("3. **Parliamentary Disclosure** - Consider whether parliamentary procedures require disclosure of AI drafting assistance.")
        elif document_type == 'budget':
            recommendations.append("2. **Fiscal Verification** - Verify all numerical figures and projections against source data, especially in AI-flagged sections.")
            recommendations.append("3. **Audit Trail** - Document AI involvement for audit purposes and future accountability.")
        
        # Based on flagged sections
        if flagged_count > 5:
            recommendations.append(f"4. **Concentrated Review** - {flagged_count} sections flagged. Prioritize review of sections with highest AI likelihood (>70%).")
        
        # Universal recommendations
        recommendations.append("5. **Disclosure Statement** - Add or update AI disclosure statement to reflect analysis findings.")
        recommendations.append("6. **Version Control** - Maintain records of original AI-generated content vs. human-edited final version.")
        
        recs_text = "\n\n".join(recommendations)
        priority_text = "\n".join(priority_actions) if priority_actions else ""
        
        return f"""## RECOMMENDATIONS

{priority_text}

### Action Items

{recs_text}

### Review Checklist

Before finalizing this document, confirm:

- [ ] All flagged sections have been reviewed by appropriate authority
- [ ] Critical content (legal language, fiscal figures) has been verified
- [ ] AI disclosure statement is accurate and complete
- [ ] Human accountability is clearly established
- [ ] Document meets relevant transparency requirements
- [ ] Audit trail documents AI involvement

### Questions to Consider

1. Is the level of AI involvement appropriate for this document type?
2. Have all stakeholders been informed about AI assistance?
3. Does AI involvement meet applicable regulatory requirements?
4. Is there clear human accountability for the final content?
5. Would public disclosure of AI involvement affect trust?
"""
    
    def _compile_report(
        self, 
        sections: List[str], 
        document_title: str,
        analysis_data: Dict
    ) -> str:
        """Compile all sections into final report."""
        
        timestamp = datetime.now().strftime('%B %d, %Y at %H:%M')
        # Use module version, not JSON version (which may be outdated)
        version = self.version
        
        header = f"""{'=' * 80}
AI USAGE EXPLANATION REPORT
{'=' * 80}

Document: {document_title}
Generated: {timestamp}
Analysis Version: Sparrow SPOT Scale™ v{version}

This report provides a detailed explanation of how AI appears to have been used
in the creation of the analyzed document. It synthesizes detection data into
actionable insights for professional review and transparency compliance.

{'=' * 80}

TABLE OF CONTENTS

1. Executive Summary
2. Detection Methodology
3. Model Attribution Analysis
4. Critical Sections Analysis
5. Pattern Analysis Explained
6. Phrase Fingerprint Analysis
7. Transparency Assessment
8. Recommendations

{'=' * 80}
"""
        
        footer = f"""
{'=' * 80}

ABOUT THIS REPORT

This AI Usage Explanation Report was generated by Sparrow SPOT Scale™ v{version}.

The analysis uses multiple detection methods, pattern recognition, and model
attribution algorithms to identify AI-generated content. Results are probabilistic
and should be interpreted as indicators rather than definitive proof.

For questions about methodology or interpretation, consult the full technical
documentation or contact your governance/compliance team.

Report generated: {timestamp}
Analysis framework: NIST AI RMF aligned
Detection methods: Multi-method consensus

{'=' * 80}
"""
        
        return header + "\n\n".join(sections) + footer
    
    def _enhance_with_ollama(
        self, 
        report: str, 
        analysis_data: Dict,
        document_type: str
    ) -> str:
        """Enhance report with Ollama-generated synthesis."""
        
        # Extract key metrics for synthesis
        ai_detection = analysis_data.get('ai_detection', {})
        ai_percentage = ai_detection.get('ai_detection_score', 0) * 100
        model_info = ai_detection.get('likely_ai_model', {})
        primary_model = model_info.get('model', 'Unknown')
        flagged_count = len(ai_detection.get('flagged_sections', []))
        
        # v8.3.5: Get detection spread for uncertainty assessment
        detection_spread = ai_detection.get('detection_spread', 0) * 100
        model_scores = ai_detection.get('model_scores', {})
        if model_scores:
            score_values = [v * 100 for v in model_scores.values() if isinstance(v, (int, float))]
            if score_values:
                min_score = min(score_values)
                max_score = max(score_values)
                detection_spread = max_score - min_score
        
        deep_analysis = analysis_data.get('deep_analysis', {})
        level3 = deep_analysis.get('level3_patterns', {})
        total_patterns = level3.get('total_patterns', 0)
        
        # v8.3.5: Check detection spread FIRST - high spread means high uncertainty
        high_uncertainty = detection_spread > 50
        
        if high_uncertainty:
            # v8.3.5: When detection spread is high, use uncertainty-focused language
            ai_level = "UNCERTAIN"
            role_description = "CANNOT be reliably determined"
            likely_use = "cannot be determined due to conflicting detection results"
            uncertainty_context = f"""
CRITICAL: Detection methods DISAGREE by {detection_spread:.0f} percentage points (range: {min_score:.0f}%-{max_score:.0f}%).
This means different analysis methods produced wildly different results.
The {ai_percentage:.1f}% average OBSCURES this disagreement and should NOT be treated as reliable.
When detection spread exceeds 50%, the analysis is INCONCLUSIVE."""
        else:
            uncertainty_context = ""
            # v8.3.4: Use calibrated language based on actual score (only when certain)
            if ai_percentage < 15:
                ai_level = "minimal"
                role_description = "limited or absent"
                likely_use = "may have assisted with minor formatting or refinement"
            elif ai_percentage < 30:
                ai_level = "moderate" 
                role_description = "limited"
                likely_use = "appears to have assisted with some drafting or structuring"
            elif ai_percentage < 50:
                ai_level = "significant"
                role_description = "substantial"
                likely_use = "likely contributed to drafting portions of the document"
            else:
                ai_level = "extensive"
                role_description = "major"
                likely_use = "appears to have been used extensively for content generation"
        
        # Generate synthesis section with calibrated guidance
        if high_uncertainty:
            prompt = f"""You are an AI transparency analyst writing for government officials and policy professionals.

CRITICAL SITUATION: The AI detection results for this {document_type} are INCONCLUSIVE.
{uncertainty_context}

Write a 200-word synthesis that:
1. CLEARLY states that AI involvement CANNOT be reliably determined
2. Explains that detection methods produced conflicting results (range: {min_score:.0f}%-{max_score:.0f}%)
3. Notes that the average of {ai_percentage:.1f}% should NOT be interpreted as a reliable estimate
4. Suggests manual expert review is required to make any determination
5. Mentions that {document_type} documents use conventions that may trigger false positives

Do NOT claim AI was or wasn't used - the data is inconclusive.
Do NOT treat the average score as if it were reliable.
Do NOT overstate confidence in any direction.

Start with: "Based on the analysis, AI involvement in this document CANNOT be reliably determined."

Write only the synthesis paragraph, no meta-commentary."""
        else:
            prompt = f"""You are an AI transparency analyst writing for government officials and policy professionals.

Based on this AI detection analysis, write a 200-word synthesis paragraph explaining HOW AI was likely used in creating this {document_type} document:

KEY DATA:
- AI Content Detected: {ai_percentage:.1f}%
- Primary Model: {primary_model}
- Sections Flagged: {flagged_count}
- AI Patterns Found: {total_patterns}

CRITICAL GUIDANCE:
- The AI score of {ai_percentage:.1f}% represents {ai_level.upper()} AI involvement
- AI role should be described as: {role_description}
- For a score this level, AI {likely_use}
- Do NOT describe {ai_percentage:.1f}% as "high" or "significant" if it is below 30%
- Do NOT say "AI played a significant role" if the score is below 30%

Write a clear, professional synthesis that:
1. Accurately reflects the {ai_level} level of AI involvement
2. Identifies what types of content MIGHT be AI-assisted (use hedging language)
3. Notes domain-specific context (legislation has formal conventions)
4. Uses accessible language (no jargon)

Start with: "Based on the analysis, this document shows {ai_level} AI involvement ({ai_percentage:.1f}%)."

Do NOT include any meta-commentary or instructions - just the synthesis paragraph."""

        print("   🔄 Generating AI synthesis with Ollama...")
        synthesis = self._call_ollama(prompt, max_tokens=400)
        
        if synthesis:
            # Insert synthesis after executive summary
            synthesis_section = f"""
---

## AI USAGE SYNTHESIS

{synthesis.strip()}

---
"""
            # Find position after executive summary
            exec_end = report.find("## DETECTION METHODOLOGY")
            if exec_end > 0:
                report = report[:exec_end] + synthesis_section + "\n" + report[exec_end:]
        
        return report
    
    def generate_from_json_file(
        self,
        json_file: str,
        output_file: Optional[str] = None
    ) -> str:
        """Generate AI usage report from analysis JSON file."""
        
        with open(json_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        document_title = analysis_data.get('document_title', 'Document')
        
        if not output_file:
            base = json_file.replace('.json', '')
            output_file = f"{base}_ai_usage_explanation.txt"
        
        return self.generate_ai_usage_report(analysis_data, document_title, output_file)


def create_ai_usage_explainer() -> AIUsageExplainer:
    """Factory function to create AI usage explainer instance."""
    return AIUsageExplainer()


if __name__ == '__main__':
    import sys
    
    explainer = AIUsageExplainer()
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"\n📊 Generating AI Usage Explanation from {json_file}...")
        explainer.generate_from_json_file(json_file, output_file)
    else:
        print("AI Usage Explanation Generator v8.3.3")
        print("=" * 50)
        print("\nUsage: python ai_usage_explainer.py <analysis.json> [output.txt]")
        print("\nExample:")
        print("  python ai_usage_explainer.py test_articles/Bill-C15/Bill-C15-08/Bill-C15-08.json")

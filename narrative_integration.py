"""
Narrative Integration Module for v8.6.1+
Orchestrates all narrative modules and appendices auto-generation

v8.6.1: Added automatic appendices generation for transparency
v8.4.1: Added AI contribution tracking for provenance reports

This module:
- Loads v7 analysis JSON
- Ingests external critiques (critique_ingestion_module) - NEW v8
- Generates narrative components (narrative_engine)
- Adapts tone (tone_adaptor)
- Extracts insights (insight_extractor)
- Renders multi-format output (format_renderer)
- Validates quality (narrative_qa)
- Tracks AI contributions for transparency (NEW v8.4.1)
- Generates appendices automatically (NEW v8.6.1)
"""

import json
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path

from narrative_engine import NarrativeEngine, create_narrative_engine
from tone_adaptor import ToneAdaptor, create_tone_adaptor
from insight_extractor import InsightExtractor, create_insight_extractor
from format_renderer import FormatRenderer, create_format_renderer
from narrative_qa import NarrativeQA, create_narrative_qa
from critique_ingestion_module import CritiqueIngestionModule, create_critique_ingestion_module
from ai_disclosure_generator import AIDisclosureGenerator, create_ai_disclosure_generator
from escalation_manager import EscalationManager, create_escalation_manager
from ai_contribution_tracker import AIContributionTracker, create_ai_contribution_tracker
from realtime_fairness_audit import RealTimeFairnessAudit, create_real_time_fairness_audit
from appendices_generator import AppendicesGenerator


class NarrativeGenerationPipeline:
    """
    Complete narrative generation pipeline for v8.
    
    Orchestrates all narrative modules from analysis JSON to multi-format output.
    Includes external critique ingestion for enhanced stakeholder balance.
    """
    
    def __init__(self, ingest_critiques: bool = True, generate_appendices: bool = True):
        """Initialize all narrative modules
        
        Args:
            ingest_critiques: Whether to automatically ingest Budget 2025 critiques
            generate_appendices: Whether to auto-generate appendices (v8.6.1+)
        """
        self.engine = create_narrative_engine()
        self.tone_adaptor = create_tone_adaptor()
        self.insight_extractor = create_insight_extractor()
        self.format_renderer = create_format_renderer()
        self.qa_validator = create_narrative_qa()
        self.critique_module = create_critique_ingestion_module()
        
        # NEW: Governance & transparency modules (Recommendations #3-5)
        self.disclosure_generator = create_ai_disclosure_generator()
        self.escalation_manager = create_escalation_manager()
        self.contribution_tracker = create_ai_contribution_tracker()
        self.fairness_audit = create_real_time_fairness_audit()
        
        # NEW v8.6.1: Appendices auto-generation for transparency
        self.appendices_generator = AppendicesGenerator() if generate_appendices else None
        
        # Auto-load default critiques if requested
        if ingest_critiques:
            self.critique_module.load_budget_2025_critiques()
    
    def get_ai_contribution_log(self) -> Dict:
        """
        v8.4.1: Get log of all AI contributions for provenance reporting.
        
        Returns:
            Dict with contribution log, overall AI %, and component breakdown
        """
        return {
            'overall_ai_percentage': self.contribution_tracker.get_overall_ai_percentage(),
            'contributions': [
                {
                    'component': c.component,
                    'model': c.model_used,
                    'model_version': c.model_version,
                    'type': c.contribution_type,
                    'timestamp': c.timestamp,
                    'confidence': c.confidence_level,
                    'requires_review': c.requires_human_review,
                    'reviewed': c.human_reviewed
                }
                for c in self.contribution_tracker.contributions
            ],
            'components': {
                name: {
                    'ai_percentage': meta.ai_percentage,
                    'primary_model': meta.primary_model,
                    'requires_disclosure': meta.requires_disclosure
                }
                for name, meta in self.contribution_tracker.component_metadata.items()
            }
        }
    
    def generate_complete_narrative(
        self,
        analysis: Dict,
        tone: str = 'journalistic',
        length: str = 'standard',
        ollama_model: str = 'llama3.2',
        formats: Optional[List[str]] = None,
        validate: bool = True,
        ingest_critiques: bool = True
    ) -> Dict:
        """
        Generate complete narrative output from v7 analysis.
        
        Args:
            analysis: v7 analysis JSON
            tone: Narrative tone (journalistic, academic, civic, critical, explanatory)
            length: Detail level (concise, standard, detailed, comprehensive)
            ollama_model: Ollama model for summary generation (llama3.2, mistral, qwen2.5, etc.)
            formats: List of output formats (x_thread, linkedin, social_badge, html_certificate)
            validate: Whether to run QA validation
            ingest_critiques: Whether to ingest external critiques (new v8 feature)
            
        Returns:
            Complete narrative output with components, adapted text, insights, formats, and critiques
        """
        if not formats:
            formats = ['x_thread', 'linkedin', 'social_badge', 'html_certificate']
        
        # Step 0: Ingest external critiques (NEW in v8)
        critique_integration = None
        if ingest_critiques and len(self.critique_module.ingested_critiques) > 0:
            print("🔄 Step 0: Integrating external critiques...")
            critique_integration = self.critique_module.generate_critique_integration_summary(analysis)
            print(f"   ✓ {len(self.critique_module.ingested_critiques)} critiques integrated")
        
        # Step 1: Generate narrative components
        print("🔄 Step 1: Generating narrative components...")
        custom_query = analysis.get('custom_narrative_query', '')
        narrative_components = self.engine.generate(analysis, custom_query=custom_query)
        
        # Step 2: Adapt tone with length control
        print(f"🔄 Step 2: Adapting tone to '{tone}' (length: {length})...")
        narrative_text = self.tone_adaptor.adapt(narrative_components, tone, length=length)
        
        # Step 2.1: Fix #5 - Expand narrative with Ollama for longer formats
        if length in ['detailed', 'comprehensive'] and ollama_model:
            print(f"🔄 Step 2.1: Expanding narrative with {ollama_model}...")
            print(f"   📊 Current narrative: {len(narrative_text.split())} words")
            narrative_text = self._expand_narrative_with_ollama(
                narrative_text, analysis, length, ollama_model
            )
            print(f"   📊 After expansion: {len(narrative_text.split())} words")
        
        # Step 2.5: Add Flags and Contradictions section if contradictions detected (Recommendation #5)
        contradiction_analysis = analysis.get('contradiction_analysis', {})
        contradictions = contradiction_analysis.get('contradictions', [])
        if contradictions:
            print(f"🔄 Step 2.5: Adding Flags and Contradictions section ({len(contradictions)} found)...")
            contradiction_section = self._generate_contradiction_section(contradictions, length)
            narrative_text += "\n\n" + contradiction_section
        
        # Step 3: Extract insights
        print("🔄 Step 3: Extracting key insights...")
        insights = self.insight_extractor.extract(analysis)
        
        # Enrich narrative_components with analysis data needed for format rendering
        narrative_components['ai_detection'] = analysis.get('ai_detection', {})
        narrative_components['deep_analysis'] = analysis.get('deep_analysis', {})  # v8.4.2: Add deep analysis for consensus
        narrative_components['bias_audit'] = analysis.get('bias_audit', {})
        narrative_components['trust_score'] = analysis.get('trust_score', {})
        narrative_components['risk_tier'] = analysis.get('risk_tier', {})
        
        # Step 4: Render formats
        print("🔄 Step 4: Rendering multi-format outputs...")
        rendered_outputs = {}
        for format_type in formats:
            try:
                rendered_outputs[format_type] = self.format_renderer.render(
                    narrative_text,
                    format_type,
                    narrative_components
                )
            except Exception as e:
                rendered_outputs[format_type] = f"Error rendering {format_type}: {str(e)}"
        
        # Step 4.5: Clean up formatting (Recommendation #5)
        narrative_text = self._cleanup_formatting(narrative_text)
        for format_type, content in rendered_outputs.items():
            if isinstance(content, str):
                rendered_outputs[format_type] = self._cleanup_formatting(content)
        
        # Step 5: Validate (optional)
        qa_report = None
        if validate:
            print("🔄 Step 5: Running QA validation...")
            qa_report = self.qa_validator.validate(narrative_text, analysis)
        
        # Step 6: Generate governance & transparency outputs (NEW - Recommendations #3-5)
        print("🔄 Step 6: Generating governance & transparency outputs...")

        # Extract key metrics for governance with fallbacks for different schema versions
        ai_detection_data = analysis.get('ai_detection') or {}
        ai_detection = 0.0
        if isinstance(ai_detection_data, dict):
            if ai_detection_data.get('overall_percentage') is not None:
                ai_detection = ai_detection_data['overall_percentage']
            elif ai_detection_data.get('ai_detection_score') is not None:
                score = ai_detection_data['ai_detection_score']
                ai_detection = score * 100 if score <= 1 else score
            else:
                ai_detection = ai_detection_data.get('percentage', 0.0)

        trust_data = analysis.get('trust_score') or {}
        if isinstance(trust_data, dict):
            trust_score = trust_data.get('trust_score') or trust_data.get('score')
            component_scores = trust_data.get('component_scores') or {}
            fairness_score = component_scores.get('fairness')
            explainability_score = component_scores.get('explainability')
        else:
            trust_score = trust_data if isinstance(trust_data, (int, float)) else None
            fairness_score = None
            explainability_score = None

        if trust_score is None:
            trust_score = analysis.get('composite_score', 66.7)

        # Fall back to fairness metrics from other modules if needed
        if fairness_score is None:
            fairness_score = (analysis.get('bias_audit') or {}).get('overall_fairness_score')
        if fairness_score is None:
            fairness_score = analysis.get('criteria', {}).get('SB', {}).get('score', 70.0)

        if explainability_score is None:
            explainability_score = trust_score  # conservative fallback for escalation logic

        risk_info = analysis.get('risk_tier', 'MEDIUM')
        if isinstance(risk_info, dict):
            risk_tier = risk_info.get('risk_tier') or risk_info.get('tier') or 'MEDIUM'
        else:
            risk_tier = risk_info or 'MEDIUM'
        risk_tier = str(risk_tier).upper()

        document_title = (
            analysis.get('document_title')
            or analysis.get('title')
            or analysis.get('variant')
            or 'Policy Analysis'
        )
        
        # Recommendation #4: AI Disclosure Statements
        ai_disclosures = {
            'standard': self.disclosure_generator.generate_disclosure_statement(
                ai_detection, trust_score, risk_tier, True, None, 'standard'
            ),
            'twitter': self.disclosure_generator.generate_disclosure_statement(
                ai_detection, trust_score, risk_tier, True, None, 'twitter'
            ),
            'linkedin': self.disclosure_generator.generate_disclosure_statement(
                ai_detection, trust_score, risk_tier, True, None, 'linkedin'
            ),
            'extended': self.disclosure_generator.generate_disclosure_statement(
                ai_detection, trust_score, risk_tier, True, None, 'extended'
            )
        }
        
        # Recommendation #5: Escalation Management
        escalation_workflow = self.escalation_manager.evaluate_and_escalate(
            analysis, ai_detection, trust_score, risk_tier,
            fairness_score, explainability_score, document_title
        )
        
        escalation_data = None
        if escalation_workflow.triggers:
            print(f"   ⚠️ {len(escalation_workflow.triggers)} escalation triggers detected")
            escalation_data = {
                'escalation_id': escalation_workflow.escalation_id,
                'severity': escalation_workflow.overall_severity,
                'triggers': [
                    {
                        'type': t.trigger_type,
                        'severity': t.severity,
                        'message': t.message,
                        'action': t.recommended_action
                    }
                    for t in escalation_workflow.triggers
                ],
                'requires_human_review': escalation_workflow.requires_human_review,
                'requires_senior_governance': escalation_workflow.requires_senior_governance,
                'publication_blocked': escalation_workflow.publication_blocked,
                'notify': escalation_workflow.notification_recipients
            }
        
        # Recommendation #3: Real-Time Fairness Audit
        criteria_map = {'FT': 'fiscal_transparency', 'SB': 'stakeholder_balance', 
                       'ER': 'economic_rigor', 'PA': 'public_accessibility', 'PC': 'policy_consequentiality'}
        criteria_data = analysis.get('criteria', {})
        fairness_dashboards = {}
        for criterion_abbr, criterion_name in criteria_map.items():
            if criterion_abbr in criteria_data:
                criterion_score = criteria_data[criterion_abbr].get('score', 50.0)
                dashboard = self.fairness_audit.audit_criterion(
                    criterion_abbr, criterion_score, analysis
                )
                fairness_dashboards[criterion_abbr] = {
                    'score': dashboard.overall_fairness_score,
                    'status': dashboard.status,
                    'alert_level': dashboard.alert_level,
                    'recommendations': dashboard.recommended_actions[:3]
                }
        
        print("   ✓ Governance outputs generated")
        
        # NEW v8.6.1: Generate appendices for transparency (Step 7)
        appendices_output = None
        if self.appendices_generator:
            print("🔄 Step 7: Generating appendices for transparency...")
            doc_title = (
                analysis.get('document_title')
                or analysis.get('title')
                or analysis.get('variant')
                or 'Policy Analysis'
            )
            appendices_output = self.appendices_generator.generate_all_appendices(
                analysis,
                document_title=doc_title,
                include_index=True
            )
            print(f"   ✓ Generated 5 appendices + navigation index (~30K words)")
            
            # Append appendices to narrative_text for comprehensive output
            if appendices_output:
                narrative_text += "\n\n" + "="*80 + "\n"
                narrative_text += "APPENDICES - COMPREHENSIVE TRANSPARENCY DOCUMENTATION\n"
                narrative_text += "="*80 + "\n\n"
                
                # Add all appendices in order
                for appendix_key in ['appendix_a', 'appendix_b', 'appendix_c', 'appendix_d', 'appendix_e']:
                    if appendix_key in appendices_output:
                        narrative_text += appendices_output[appendix_key] + "\n\n"
                
                # Add navigation index if available
                if 'navigation_index' in appendices_output:
                    narrative_text += appendices_output['navigation_index'] + "\n\n"
        
        # Fix #6: Add timestamp for audit trail
        from datetime import datetime
        
        # Compile complete output
        result = {
            'metadata': {
                'version': 'v8.6.1',
                'pipeline': 'NarrativeGenerationPipeline',
                'tone': tone,
                'length': length,
                'ollama_model': ollama_model,
                'formats_generated': list(rendered_outputs.keys()),
                'source_analysis_score': analysis.get('composite_score', 0),
                'source_analysis_grade': analysis.get('grade', 'N/A'),
                'critiques_ingested': len(self.critique_module.ingested_critiques) if ingest_critiques else 0,
                'appendices_generated': appendices_output is not None,
                'generated_at': datetime.utcnow().isoformat() + 'Z'
            },
            'narrative_components': narrative_components,
            'narrative_text': narrative_text,
            'insights': insights,
            'outputs': rendered_outputs,
            'qa_report': qa_report,
            'critique_integration': critique_integration,
            'governance': {
                'ai_disclosures': ai_disclosures,
                'escalation': escalation_data,
                'fairness_audit': fairness_dashboards,
                'escalation_status': 'BLOCKED' if escalation_data and escalation_data.get('publication_blocked') else 'FLAGGED' if escalation_data else 'CLEAR'
            },
            'appendices': appendices_output
        }
        
        print("✅ Narrative generation complete!")
        
        return result
    
    def generate_from_file(
        self,
        analysis_file: str,
        output_file: Optional[str] = None,
        tone: str = 'journalistic',
        formats: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate narrative from analysis JSON file.
        
        Args:
            analysis_file: Path to v7 analysis JSON
            output_file: Optional path to save output JSON
            tone: Narrative tone
            formats: List of output formats
            
        Returns:
            Complete narrative output
        """
        # Load analysis
        with open(analysis_file) as f:
            analysis = json.load(f)
        
        # Generate narrative
        result = self.generate_complete_narrative(analysis, tone, formats)
        
        # Save if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✓ Output saved to {output_file}")
        
        return result
    
    def generate_multi_tone(
        self,
        analysis: Dict,
        formats: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate narratives in all available tones.
        
        Useful for comparing different narrative approaches.
        
        Args:
            analysis: v7 analysis JSON
            formats: List of output formats
            
        Returns:
            Dict with narratives for each tone
        """
        results = {}
        
        for tone in self.tone_adaptor.get_available_tones():
            print(f"\n📝 Generating {tone} tone narrative...")
            results[tone] = self.generate_complete_narrative(analysis, tone, formats, validate=False)
        
        return results
    
    def batch_generate(
        self,
        analysis_files: List[str],
        output_dir: Optional[str] = None,
        tone: str = 'journalistic'
    ) -> List[Dict]:
        """
        Generate narratives for multiple analysis files.
        
        Args:
            analysis_files: List of analysis JSON file paths
            output_dir: Optional directory to save outputs
            tone: Narrative tone
            
        Returns:
            List of results
        """
        results = []
        
        for i, analysis_file in enumerate(analysis_files, 1):
            print(f"\n📄 Processing file {i}/{len(analysis_files)}: {analysis_file}")
            
            try:
                output_file = None
                if output_dir:
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                    base_name = Path(analysis_file).stem
                    output_file = f"{output_dir}/{base_name}_narrative.json"
                
                result = self.generate_from_file(analysis_file, output_file, tone)
                results.append({'file': analysis_file, 'status': 'success', 'result': result})
            except Exception as e:
                results.append({'file': analysis_file, 'status': 'error', 'error': str(e)})
        
        return results
    
    def _cleanup_formatting(self, text: str) -> str:
        """
        Automated formatting cleanup to address QA issues.
        
        Fixes:
        - Double spaces
        - Multiple consecutive newlines
        - Trailing whitespace
        - Missing spaces after punctuation
        """
        import re
        
        # Remove double spaces
        text = re.sub(r'  +', ' ', text)
        
        # Fix multiple consecutive newlines (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing whitespace from each line
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        
        # Ensure space after punctuation (., !, ?, :, ;)
        text = re.sub(r'([.!?:;])([A-Z])', r'\1 \2', text)
        
        # Remove spaces before punctuation
        text = re.sub(r' ([.!?,;:])', r'\1', text)
        
        return text.strip()
    
    def _strip_meta_commentary(self, text: str) -> str:
        """
        v8.3.2 Fix #4: Remove meta-commentary and internal prompts from narrative output.
        
        Strips out:
        - TASK: ... sections
        - ADDITIONAL USER CONTEXT/FOCUS: ... sections
        - Internal prompt markers
        - Analysis Data footers that expose internal structure
        """
        import re
        
        # Remove TASK: sections (including multi-line)
        text = re.sub(r'TASK:.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove ADDITIONAL USER CONTEXT/FOCUS sections
        text = re.sub(r'ADDITIONAL USER CONTEXT/FOCUS:.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove "Analysis Data:" footer sections that expose internal structure
        text = re.sub(r'\nAnalysis Data:\n.*?(?=\n\n[A-Z]|\Z)', '', text, flags=re.DOTALL)
        
        # Remove internal prompt markers
        text = re.sub(r'\[INTERNAL\].*?(?=\n|\Z)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[PROMPT\].*?(?=\n|\Z)', '', text, flags=re.IGNORECASE)
        
        # Clean up any resulting double newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _expand_narrative_with_ollama(self, narrative_text: str, analysis: Dict, 
                                       length: str, ollama_model: str) -> str:
        """
        Fix #5: Expand narrative to target word count using Ollama.
        
        Strategy: Use multi-section generation to reach target word count
        since Ollama may not respect num_predict parameter for long sequences.
        
        Args:
            narrative_text: Base narrative from tone adaptor
            analysis: Full analysis results for context
            length: Target length (detailed=2000, comprehensive=3500)
            ollama_model: Ollama model to use
            
        Returns:
            Expanded narrative text
        """
        import requests
        
        length_targets = {
            'detailed': 2000,
            'comprehensive': 3500
        }
        target_words = length_targets.get(length, 2000)
        current_words = len(narrative_text.split())
        
        # If already at target, return as-is
        if current_words >= target_words * 0.8:  # 80% threshold
            return narrative_text
        
        # Prepare context from analysis
        composite_score = analysis.get('composite_score', 0)
        grade = analysis.get('composite_grade') or analysis.get('grade', 'N/A')
        criteria = analysis.get('criteria', {})
        
        # v8.3.3: Get document type for appropriate framing
        document_type = analysis.get('document_type', 'policy_brief')
        
        # Fix #1: Include custom query if provided
        custom_query = analysis.get('custom_narrative_query', '')
        custom_query_section = ""
        if custom_query:
            custom_query_section = f"\nADDITIONAL USER CONTEXT/FOCUS:\n{custom_query}\n"
        
        criteria_summary = ""
        for key, data in criteria.items():
            if isinstance(data, dict):
                criteria_summary += f"- {key}: {data.get('score', 0):.0f}/100 - {data.get('interpretation', 'N/A')}\n"
        
        # v8.3.3: Document-type-specific prompts
        if document_type == 'legislation':
            doc_type_context = """
DOCUMENT TYPE: LEGISLATION (Bill/Act)
IMPORTANT: This is enacted LAW, not a policy proposal. Do NOT:
- Suggest it needs "revision" or "improvement"
- Recommend "stakeholder consultation" (already occurred in legislative process)
- Critique it as a proposal - analyze it as established legal framework
- Use phrases like "before implementation" (legislation IS implementation)

FOCUS ON:
- Legal clarity and unambiguous language
- Regulatory scope and powers granted/restricted
- Implementation and enforcement provisions
- Citizen rights and obligations created
- Constitutional and jurisdictional alignment"""
        elif document_type == 'budget':
            doc_type_context = """
DOCUMENT TYPE: GOVERNMENT BUDGET
IMPORTANT: This is an official fiscal allocation, not a proposal.

FOCUS ON:
- Fiscal transparency and spending itemization
- Revenue projection realism
- Allocation priorities and trade-offs
- Taxpayer impact and accountability
- Economic assumptions underlying projections"""
        else:
            doc_type_context = f"""
DOCUMENT TYPE: {document_type.upper().replace('_', ' ')}

FOCUS ON:
- Policy implications and effectiveness
- Stakeholder impacts
- Economic rigor and evidence base
- Implementation feasibility"""
        
        # STRATEGY: Since Ollama may not honor num_predict for very long outputs,
        # we'll break the expansion into sections and concatenate them
        sections_needed = max(1, int(target_words / 1000))  # ~1000 words per section
        
        print(f"   🔍 DEBUG: Planning {sections_needed}-section expansion strategy (target: {target_words} words)")
        
        sections = []
        section_targets = [target_words // sections_needed] * sections_needed
        # Add remainder to last section
        section_targets[-1] += target_words % sections_needed
        
        for i, section_target in enumerate(section_targets, 1):
            section_prompt = f"""You are a professional policy analyst. Expand the following narrative section with detailed analysis.

IMPORTANT INSTRUCTIONS:
- Do NOT use generic templates or placeholder language like "[insert specific issue]" or "[relevant sector/region]"
- DO analyze the specific scores and findings provided below
- DO explain why scores are what they are based on the data
- DO be concrete and specific - avoid vague generalizations
- If you don't have document details, focus on what the scores tell us about quality gaps
- Acknowledge specific criterion scores and what they indicate

CONTEXT - Original Narrative ({current_words} words):
{narrative_text}

ANALYSIS DATA:
- Composite Score: {composite_score}/100 ({grade})
{criteria_summary}
{doc_type_context}
{custom_query_section}

SECTION {i} OF {sections_needed}:
Write a detailed {section_target}-word section that:
"""
            
            if i == 1:
                section_prompt += """1. Analyzes the document based on the specific criteria scores shown above
2. Explains what the scores tell us (gaps, strengths, weaknesses)
3. Discusses why certain scores are low or high
4. Explores stakeholder implications of the score profile"""
            elif i == len(section_targets):
                section_prompt += """1. Synthesizes findings from the score analysis
2. Discusses what needs to improve and why
3. Addresses systemic issues revealed by score gaps
4. Concludes with actionable insights based on the data"""
            else:
                section_prompt += f"""1. Analyzes specific criteria in depth based on scores
2. Explains the implications of score gaps
3. Discusses the relationship between different criteria
4. Connects scores to real-world policy impact"""
            
            section_prompt += "\n\nWrite only the section content - be specific to the scores and analysis provided - no meta-commentary or section markers:"
            
            # v8.4.1: Track AI contribution
            start_time = datetime.now()
            
            try:
                print(f"   🔍 DEBUG: Generating section {i}/{sections_needed} (target {section_target} words)...")
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": ollama_model,
                        "prompt": section_prompt,
                        "stream": False,
                        "temperature": 0.7,
                        "num_predict": int(section_target * 3),  # Generous multiplier
                    },
                    timeout=180  # 3 minute timeout per section
                )
                response.raise_for_status()
                
                section_text = response.json().get("response", "")
                section_words = len(section_text.split()) if section_text else 0
                
                if section_text:
                    # Clean up section text
                    section_text = self._strip_meta_commentary(section_text).strip()
                    sections.append(section_text)
                    print(f"   ✓ Section {i} generated: {len(section_text.split())} words")
                else:
                    print(f"   ⚠️ Section {i} was empty")
                    
            except requests.exceptions.Timeout as e:
                print(f"   ⚠️ Section {i} TIMEOUT: {e}")
                continue
            except requests.exceptions.ConnectionError as e:
                print(f"   ⚠️ Section {i} CONNECTION ERROR: {e}")
                print(f"   🔍 DEBUG: Is Ollama running on localhost:11434?")
                # Fall back to using just the original narrative
                return narrative_text
            except Exception as e:
                print(f"   ⚠️ Section {i} error: {e}")
                continue
        
        if not sections:
            print(f"   ⚠️ Failed to generate any sections, using original narrative")
            return narrative_text
        
        # Combine sections
        expanded = "\n\n".join(sections)
        expanded_words = len(expanded.split())
        
        print(f"   🔍 DEBUG: Combined {len(sections)} sections = {expanded_words} words")
        
        # Log AI contribution
        self.contribution_tracker.record_contribution(
            component="narrative_expansion",
            model_used=ollama_model,
            model_version="local",
            prompt_details=f"Expanded narrative from {current_words} to target {target_words} words ({sections_needed} sections)",
            contribution_type="generation",
            confidence_level=0.85,
            requires_review=True
        )
        
        # Check if expansion meets minimum threshold
        min_target = target_words * 0.6  # At least 60% of target
        if expanded_words >= min_target:
            print(f"   ✓ Expanded narrative from {current_words} to {expanded_words} words (target: {target_words})")
            return expanded
        else:
            # Expansion was too short - log warning but return it anyway since it's still an improvement
            percentage = int((expanded_words / target_words) * 100)
            print(f"   ⚠️ Expansion fell short - got {expanded_words} words ({percentage}% of {target_words} target)")
            print(f"   💡 Consider using a larger model or increasing timeout for fuller expansion")
            return expanded if expanded_words > current_words else narrative_text
    
    def _generate_contradiction_section(self, contradictions: List[Dict], length: str) -> str:
        """
        Generate Flags and Contradictions section for narrative (Recommendation #5)
        
        Args:
            contradictions: List of contradiction objects from contradiction_detector
            length: Narrative length (concise/standard/detailed/comprehensive)
        
        Returns:
            Formatted contradiction section text
        """
        if not contradictions:
            return ""
        
        # Count by severity
        high_count = len([c for c in contradictions if c.get('severity') == 'HIGH'])
        medium_count = len([c for c in contradictions if c.get('severity') == 'MEDIUM'])
        low_count = len([c for c in contradictions if c.get('severity') == 'LOW'])
        
        # Build section header
        section = "## ⚠️ Flags and Contradictions\n\n"
        
        if length in ['concise', 'standard']:
            # Brief summary for shorter narratives
            section += f"**{len(contradictions)} numerical inconsistencies detected** "
            if high_count > 0:
                section += f"({high_count} HIGH severity). "
            section += "These discrepancies may indicate calculation errors or conflicting data sources. "
            section += "Review recommended before relying on affected figures.\n\n"
            
            # List top 3 most severe
            sorted_contradictions = sorted(
                contradictions,
                key=lambda c: {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(c.get('severity'), 0),
                reverse=True
            )
            
            for i, contradiction in enumerate(sorted_contradictions[:3], 1):
                severity = contradiction.get('severity', 'UNKNOWN')
                con_type = contradiction.get('type', 'unknown').replace('_', ' ').title()
                message = contradiction.get('message', 'No description')
                section += f"**{i}. [{severity}] {con_type}:** {message}\n\n"
        
        else:  # detailed or comprehensive
            # Full analysis for longer narratives
            section += f"During automated validation, **{len(contradictions)} numerical discrepancies** were identified "
            section += "through cross-referencing stated totals against itemized calculations, temporal consistency checks, "
            section += "and visual-text alignment analysis.\n\n"
            
            if high_count > 0:
                section += f"⚠️ **{high_count} HIGH-severity contradictions** require immediate attention. "
            if medium_count > 0:
                section += f"**{medium_count} MEDIUM-severity** issues warrant review. "
            if low_count > 0:
                section += f"**{low_count} LOW-severity** anomalies noted for completeness. "
            
            section += "\n\n### Detected Issues:\n\n"
            
            # Group by severity
            for severity_level in ['HIGH', 'MEDIUM', 'LOW']:
                severity_contradictions = [c for c in contradictions if c.get('severity') == severity_level]
                if not severity_contradictions:
                    continue
                
                section += f"#### {severity_level} Severity ({len(severity_contradictions)})\n\n"
                
                for contradiction in severity_contradictions:
                    con_type = contradiction.get('type', 'unknown').replace('_', ' ').title()
                    message = contradiction.get('message', 'No description')
                    
                    section += f"- **{con_type}:** {message}\n"
                    
                    # Add context if available (for comprehensive length only)
                    if length == 'comprehensive' and contradiction.get('context'):
                        context = contradiction['context'][:150] + "..." if len(contradiction.get('context', '')) > 150 else contradiction.get('context', '')
                        section += f"  *Context: {context}*\n"
                    
                    # Add specific details based on contradiction type
                    if contradiction.get('type') == 'arithmetic_mismatch':
                        stated = contradiction.get('stated_total', 'N/A')
                        calculated = contradiction.get('calculated_total', 'N/A')
                        diff = contradiction.get('difference', 'N/A')
                        section += f"  *Stated: ${stated}B, Calculated: ${calculated}B, Difference: ${diff}B*\n"
                    
                    section += "\n"
            
            section += "**Impact Assessment:** These contradictions triggered an automatic penalty to the Economic Rigor (ER) score "
            section += "to reflect reduced confidence in the document's numerical integrity. "
            section += "Users should independently verify figures before making policy decisions based on this analysis.\n\n"
        
        return section


def create_pipeline() -> NarrativeGenerationPipeline:
    """Factory function to create narrative pipeline."""
    return NarrativeGenerationPipeline()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        analysis_file = sys.argv[1]
        tone = sys.argv[2] if len(sys.argv) > 2 else 'journalistic'
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        print("=" * 60)
        print("NARRATIVE GENERATION PIPELINE v8.0")
        print("=" * 60)
        print()
        
        pipeline = create_pipeline()
        result = pipeline.generate_from_file(analysis_file, output_file, tone)
        
        print()
        print("=" * 60)
        print("GENERATED NARRATIVE (Preview)")
        print("=" * 60)
        print()
        print(result['narrative_text'][:500] + "..." if len(result['narrative_text']) > 500 else result['narrative_text'])
        print()
        
        if result['qa_report']:
            print("=" * 60)
            print("QA VALIDATION SUMMARY")
            print("=" * 60)
            print()
            print(f"Overall Score: {result['qa_report']['overall_score']:.1f}/100")
            print(f"Status: {result['qa_report']['status']}")
            print(f"Approved: {'✓ Yes' if result['qa_report']['approved'] else '✗ No'}")
            print()
    else:
        print("Usage: python narrative_integration.py <analysis.json> [tone] [output.json]")
        print()
        print("Available tones:")
        pipeline = create_pipeline()
        for tone in pipeline.tone_adaptor.get_available_tones():
            print(f"  • {tone}")
        print()
        print("Example:")
        print("  python narrative_integration.py test_articles/2025_budget/2025-Budget-00.json journalistic output.json")

"""
Ollama-Based Summary Generator for Sparrow SPOT Scale™ Certificates v8.4.0
Generates plain-language summaries for policy and journalism grading reports

v8.4.0 Enhancements:
- INCONCLUSIVE detection awareness in AI Transparency sections
- Standardized narrative voice guidelines across document types
- Consistent messaging when detection spread >50%
"""

import json
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import time

VERSION = "8.4.0"

# v8.4.0: Standardized narrative voice guidelines
NARRATIVE_VOICE_GUIDELINES = """
CRITICAL NARRATIVE VOICE RULES:
1. NEVER claim certainty about AI detection - use "appears to", "may indicate", "patterns suggest"
2. When detection_spread > 50% or detection_inconclusive=True:
   - Do NOT cite AI percentage as fact
   - Say "AI detection was INCONCLUSIVE due to conflicting method results"
   - Do NOT name any AI model as likely source
3. When fairness_score < 50, explicitly note "FAILING" fairness status
4. When trust_score < 70, note limitations in governance assessment
5. Always use accessible language (Grade 8-10 reading level)
6. Start summaries with the document's grade, not AI analysis
"""


class OllamaSummaryGenerator:
    """Generate plain-language summaries using Ollama models."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize with Ollama endpoint."""
        self.ollama_url = ollama_url
        self.model = "granite4:tiny-h"  # Fast, accurate model
        self.fallback_model = "qwen2.5:7b"  # More capable fallback
        
    def _call_ollama(self, prompt: str, model: Optional[str] = None) -> str:
        """Call Ollama API for text generation."""
        model = model or self.model
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "num_predict": 800,
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Ollama error with {model}: {str(e)}")
            return None
    
    def generate_policy_summary(
        self, 
        report: Dict[str, Any],
        document_title: str = "",
        output_file: Optional[str] = None
    ) -> str:
        """Generate plain-language summary for policy document."""
        
        criteria = report.get('criteria', {})
        composite = report.get('composite_score', 0)
        grade = report.get('composite_grade', 'F')
        classification = report.get('classification', '')
        
        # Build context from report
        scores_text = "\n".join([
            f"- {name}: {data.get('score', 'N/A')}/100"
            for name, data in criteria.items()
        ])
        
        # v8.3.3: Include AI Transparency dimension if available
        # v8.4.0: Handle INCONCLUSIVE detection
        ai_transparency_text = ""
        ai_detection = report.get('ai_detection', {})
        detection_inconclusive = ai_detection.get('detection_inconclusive', False)
        detection_spread = ai_detection.get('detection_spread', 0)
        
        deep_analysis = report.get('deep_analysis', {})
        if deep_analysis:
            consensus = deep_analysis.get('consensus', {})
            ai_percentage = consensus.get('ai_percentage', 0)
            transparency_score = consensus.get('transparency_score', 0)
            primary_model = consensus.get('primary_model', 'Unknown')
            
            # v8.4.0: INCONCLUSIVE detection handling
            if detection_inconclusive or detection_spread > 0.50:
                ai_transparency_text = f"""

AI Transparency (AT):
⚠️ AI DETECTION IS INCONCLUSIVE
- Detection methods disagreed by {detection_spread*100:.0f}% (exceeds 50% threshold)
- AI Content: CANNOT BE RELIABLY DETERMINED
- Model Attribution: SUPPRESSED (inconclusive data)
- Note: Professional manual review is recommended"""
                scores_text += f"\n- AT (AI Transparency): INCONCLUSIVE"
            elif transparency_score > 0:
                ai_transparency_text = f"""

AI Transparency (AT):
- AI Content Detected: {ai_percentage:.1f}% (estimate, not verified)
- Likely AI Model: {primary_model}
- Transparency Score: {transparency_score}/100
- Note: AI detection is probabilistic, not definitive"""
                scores_text += f"\n- AT (AI Transparency): {transparency_score}/100"
        
        # v8.4.0: Build INCONCLUSIVE-aware prompt
        if detection_inconclusive or detection_spread > 0.50:
            ai_guidance = """
IMPORTANT: AI detection is INCONCLUSIVE for this document. Do NOT claim any specific
AI percentage as fact. Say "AI detection was inconclusive" and recommend manual review.
Do NOT name any AI model as the likely source."""
        else:
            ai_guidance = """
If AI content was detected, briefly explain what this means for transparency.
Use hedging language: "appears to", "may contain", "patterns suggest"."""
        
        prompt = f"""You are a policy analyst writing for the general public (reading level: Grade 8).

Document: {document_title}
Grade: {grade} | Score: {composite}/100
Classification: {classification}

Criteria Scores:
{scores_text}
{ai_transparency_text}
{ai_guidance}

Write a 400-500 word plain-language summary that:
1. Explains what the SPOT grading means in simple terms
2. Highlights the strongest area
3. Identifies the weakest area
4. Addresses AI transparency as noted above
5. Suggests what this means for the public
6. Is written in accessible language (no jargon)

Start with: "This policy document received a grade of {grade}..."
Focus on clarity over technical accuracy."""

        print("📝 Generating plain-language summary (Ollama)...")
        print(f"   Model: {self.model}")
        print(f"   Document: {document_title}")
        
        summary = self._call_ollama(prompt)
        
        if not summary:
            print("⚠️  Primary model failed, trying fallback...")
            summary = self._call_ollama(prompt, self.fallback_model)
        
        if not summary:
            print("❌ Summary generation failed")
            return None
        
        # Add metadata
        full_summary = f"""PLAIN-LANGUAGE SUMMARY
{'=' * 70}

Title: {document_title}
Grade: {grade} ({composite}/100)
Classification: {classification}
Generated: {datetime.now().strftime('%B %d, %Y')}
Reading Level: Grade 8+ (Flesch Reading Ease: 60+)

{'=' * 70}

{summary.strip()}

{'=' * 70}

About This Summary:
This summary was automatically generated using AI language models to make
the SPOT Scale™ grading understandable to the general public. For technical
details, see the full diagnostic report.

SPOT Scale™ Criteria Explained:
- FT (Fiscal Transparency): How clearly are financial details disclosed?
- SB (Stakeholder Balance): Are different perspectives represented fairly?
- ER (Economic Rigor): Is the economic analysis sound?
- PA (Public Accessibility): How easy is this to understand?
- PC (Policy Consequentiality): How much impact will this have?
- AT (AI Transparency): How much AI assistance was used and is it disclosed?

For full details, visit: https://sparrowspot.example/
"""
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_summary)
            print(f"   ✓ Saved: {output_file}")
            return output_file
        
        return full_summary
    
    def generate_journalism_summary(
        self,
        report: Dict[str, Any],
        document_title: str = "",
        output_file: Optional[str] = None
    ) -> str:
        """Generate plain-language summary for journalism article."""
        
        scores = report.get('sparrow_scores', {})
        composite = scores.get('composite', {}).get('score', 0)
        grade = scores.get('composite', {}).get('grade', ('F', 'Unknown'))[0]
        
        # Build context
        criteria_text = "\n".join([
            f"- {abbr.upper()}: {data.get('score', 'N/A')}/100"
            for abbr, data in scores.items() if abbr != 'composite'
        ])
        
        prompt = f"""You are a media literacy expert writing for general readers.

Article: {document_title}
Grade: {grade} | Score: {composite}/100

SPARROW Scale™ Scores:
{criteria_text}

Write a 300-400 word plain-language summary that:
1. Explains the credibility grade in simple terms
2. Highlights what the article did well
3. Identifies potential concerns
4. Suggests what readers should consider
5. Avoids academic jargon

Start with: "This article received a credibility grade of {grade}..."
Focus on practical guidance for readers."""

        print("📝 Generating credibility summary (Ollama)...")
        print(f"   Model: {self.model}")
        print(f"   Article: {document_title}")
        
        summary = self._call_ollama(prompt)
        
        if not summary:
            print("⚠️  Primary model failed, trying fallback...")
            summary = self._call_ollama(prompt, self.fallback_model)
        
        if not summary:
            print("❌ Summary generation failed")
            return None
        
        # Add metadata
        full_summary = f"""CREDIBILITY ASSESSMENT SUMMARY
{'=' * 70}

Title: {document_title}
Grade: {grade} ({composite}/100)
Generated: {datetime.now().strftime('%B %d, %Y')}
Reading Level: Grade 8+ (General Public)

{'=' * 70}

{summary.strip()}

{'=' * 70}

SPARROW Scale™ Explained:
- SI (Source Integrity): Are sources credible and cited?
- OI (Objectivity Index): How balanced is the reporting?
- TP (Technical Precision): Is information accurate?
- AR (Accessibility): How easy is it to understand?
- IU (Impact Utility): How important is this information?

Reading Tips:
✓ Check the sources cited
✓ Look for multiple viewpoints
✓ Consider what information might be missing
✓ Verify claims with independent sources

For full analysis, visit: https://sparrowspot.example/
"""
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_summary)
            print(f"   ✓ Saved: {output_file}")
            return output_file
        
        return full_summary
    
    def generate_quick_summary(
        self,
        json_file: str,
        variant: str = 'policy',
        document_type: str = None,
        output_file: Optional[str] = None
    ) -> str:
        """Generate summary from existing JSON report.
        
        Args:
            json_file: Path to analysis JSON
            variant: 'policy' or 'journalism'
            document_type: Override document type (legislation, budget, policy_brief, etc.)
            output_file: Optional output path
        """
        
        with open(json_file, 'r') as f:
            report = json.load(f)
        
        doc_title = report.get('document_title', 'Document')
        
        # Auto-detect document type if not provided
        if not document_type:
            document_type = report.get('document_type', 'policy_brief')
        
        if not output_file:
            base = json_file.replace('.json', '')
            output_file = f"{base}_summary.txt"
        
        # Route to appropriate generator based on document type
        if document_type == 'legislation':
            return self.generate_legislative_summary(report, doc_title, output_file)
        elif document_type == 'budget':
            return self.generate_budget_summary(report, doc_title, output_file)
        elif variant == 'journalism':
            return self.generate_journalism_summary(report, doc_title, output_file)
        else:
            return self.generate_policy_summary(report, doc_title, output_file)
    
    def generate_legislative_summary(
        self, 
        report: Dict[str, Any],
        document_title: str = "",
        output_file: Optional[str] = None
    ) -> str:
        """Generate plain-language summary for LEGISLATIVE documents (Bills, Acts).
        
        Legislative documents are PRIMARY SOURCES that create law - they should be
        analyzed for clarity, scope, and implementation rather than policy effectiveness.
        """
        
        criteria = report.get('criteria', {})
        composite = report.get('composite_score', 0)
        grade = report.get('composite_grade', 'F')
        
        # Build context with legislative-appropriate framing
        scores_text = "\n".join([
            f"- {name}: {data.get('score', 'N/A')}/100"
            for name, data in criteria.items()
        ])
        
        # v8.3.3: Include AI Transparency dimension if available
        ai_transparency_text = ""
        deep_analysis = report.get('deep_analysis', {})
        if deep_analysis:
            consensus = deep_analysis.get('consensus', {})
            ai_percentage = consensus.get('ai_percentage', 0)
            primary_model = consensus.get('primary_model', 'Unknown')
            if ai_percentage > 0:
                ai_transparency_text = f"""

AI Content Analysis:
- AI-Assisted Content: {ai_percentage:.1f}%
- Likely AI Model: {primary_model}
Note: AI detection in legislation may reflect drafting assistance rather than substantive issues."""
        
        prompt = f"""You are a legislative analyst writing for the general public (reading level: Grade 10).

Document: {document_title}
Document Type: LEGISLATION (Bill/Act)
Assessment Grade: {grade} | Score: {composite}/100

Analysis Scores:
{scores_text}
{ai_transparency_text}

IMPORTANT CONTEXT: This is a LEGISLATIVE document (a Bill or Act). Unlike policy proposals:
- Legislation CREATES legal framework - it defines what IS law, not what SHOULD be
- Legislation does not need external citations - it IS the primary source
- Economic projections in legislation are authoritative statutory figures, not proposals
- The goal is legal clarity, not policy advocacy

Write a 400-500 word analysis that:
1. Explains the legislative assessment grade in accessible terms
2. Evaluates the LEGAL CLARITY of the bill (is the language unambiguous?)
3. Assesses the REGULATORY SCOPE (what powers does it grant or restrict?)
4. Reviews IMPLEMENTATION PROVISIONS (are enforcement mechanisms clear?)
5. Notes any TRANSPARENCY concerns about how the legislation was drafted
6. Explains what this means for citizens affected by this law

DO NOT:
- Suggest the legislation needs "revision" or "improvement" (it's enacted law)
- Critique it as if it were a policy proposal
- Recommend "stakeholder consultation" (legislative process already occurred)
- Use phrases like "before implementation" (legislation IS implementation)

Start with: "This legislative analysis of {document_title} received a grade of {grade}..."
Focus on helping citizens understand the law's structure and implications."""

        print("📝 Generating legislative analysis summary (Ollama)...")
        print(f"   Model: {self.model}")
        print(f"   Document: {document_title}")
        print(f"   Type: LEGISLATION")
        
        summary = self._call_ollama(prompt)
        
        if not summary:
            print("⚠️  Primary model failed, trying fallback...")
            summary = self._call_ollama(prompt, self.fallback_model)
        
        if not summary:
            print("❌ Summary generation failed")
            return None
        
        # Add metadata with legislative-specific framing
        full_summary = f"""LEGISLATIVE ANALYSIS SUMMARY
{'=' * 70}

Title: {document_title}
Document Type: Legislation (Bill/Act)
Assessment Grade: {grade} ({composite}/100)
Generated: {datetime.now().strftime('%B %d, %Y')}
Reading Level: Grade 10+ (Civic Literacy)

{'=' * 70}

{summary.strip()}

{'=' * 70}

About This Analysis:
This analysis was generated to help citizens understand legislative documents.
Legislation is a PRIMARY SOURCE - it creates law rather than proposing policy.

Assessment Criteria for Legislation:
- FT (Fiscal Transparency): How clearly are budgetary provisions disclosed?
- SB (Stakeholder Balance): Does the legislation consider diverse affected parties?
- ER (Economic Rigor): Are economic provisions well-defined and calculable?
- PA (Public Accessibility): How readable is the legislative language?
- PC (Policy Consequentiality): What real-world changes does this law create?
- AT (AI Transparency): Was AI assistance used in drafting or analysis?

Note: Legislative documents are self-authorizing and do not require external
citations in the same way policy proposals do.

For full technical analysis, see the complete assessment report.
"""
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_summary)
            print(f"   ✓ Saved: {output_file}")
            return output_file
        
        return full_summary
    
    def generate_budget_summary(
        self, 
        report: Dict[str, Any],
        document_title: str = "",
        output_file: Optional[str] = None
    ) -> str:
        """Generate plain-language summary for BUDGET documents.
        
        Budget documents are PRIMARY SOURCES that allocate public funds.
        """
        
        criteria = report.get('criteria', {})
        composite = report.get('composite_score', 0)
        grade = report.get('composite_grade', 'F')
        
        scores_text = "\n".join([
            f"- {name}: {data.get('score', 'N/A')}/100"
            for name, data in criteria.items()
        ])
        
        # AI transparency
        ai_transparency_text = ""
        deep_analysis = report.get('deep_analysis', {})
        if deep_analysis:
            consensus = deep_analysis.get('consensus', {})
            ai_percentage = consensus.get('ai_percentage', 0)
            if ai_percentage > 0:
                ai_transparency_text = f"\n- AI-Assisted Content Detected: {ai_percentage:.1f}%"
        
        prompt = f"""You are a fiscal analyst writing for taxpayers (reading level: Grade 9).

Document: {document_title}
Document Type: GOVERNMENT BUDGET
Assessment Grade: {grade} | Score: {composite}/100

Analysis Scores:
{scores_text}
{ai_transparency_text}

IMPORTANT CONTEXT: This is a BUDGET document - an official allocation of public funds.
- Budget figures are authoritative - they represent actual spending commitments
- Fiscal Transparency is especially important (how clearly is spending itemized?)
- Economic Rigor matters (are projections realistic and well-supported?)

Write a 400-500 word analysis that:
1. Explains the budget assessment grade in plain language
2. Highlights how clearly spending is itemized and explained
3. Assesses whether revenue projections appear realistic
4. Notes any transparency gaps in how funds are allocated
5. Explains what this means for taxpayers

Start with: "This budget analysis of {document_title} received a grade of {grade}..."
Focus on fiscal accountability and taxpayer understanding."""

        print("📝 Generating budget analysis summary (Ollama)...")
        print(f"   Model: {self.model}")
        print(f"   Document: {document_title}")
        print(f"   Type: BUDGET")
        
        summary = self._call_ollama(prompt)
        
        if not summary:
            summary = self._call_ollama(prompt, self.fallback_model)
        
        if not summary:
            return None
        
        full_summary = f"""BUDGET ANALYSIS SUMMARY
{'=' * 70}

Title: {document_title}
Document Type: Government Budget
Assessment Grade: {grade} ({composite}/100)
Generated: {datetime.now().strftime('%B %d, %Y')}
Reading Level: Grade 9+ (Taxpayer Literacy)

{'=' * 70}

{summary.strip()}

{'=' * 70}

Budget Assessment Criteria:
- FT (Fiscal Transparency): How clearly is spending itemized?
- SB (Stakeholder Balance): Are different sectors fairly represented?
- ER (Economic Rigor): Are revenue/spending projections realistic?
- PA (Public Accessibility): Can taxpayers understand the allocations?
- PC (Policy Consequentiality): What real-world impact will spending have?

For full technical analysis, see the complete assessment report.
"""
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_summary)
            print(f"   ✓ Saved: {output_file}")
            return output_file
        
        return full_summary
    
    def test_connection(self) -> bool:
        """Test Ollama connection."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"✓ Ollama connected at {self.ollama_url}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"❌ Cannot connect to Ollama at {self.ollama_url}")
        return False


if __name__ == '__main__':
    import sys
    
    # Test usage
    gen = OllamaSummaryGenerator()
    
    if not gen.test_connection():
        sys.exit(1)
    
    # Example: Load a report and generate summary
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        variant = sys.argv[2] if len(sys.argv) > 2 else 'policy'
        
        print(f"\n📖 Generating {variant} summary from {json_file}...")
        gen.generate_quick_summary(json_file, variant)
    else:
        print("Usage: python ollama_summary_generator.py <report.json> [policy|journalism]")

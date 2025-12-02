"""
Ollama-Based Summary Generator for Sparrow SPOT Scale™ Certificates
Generates plain-language summaries for policy and journalism grading reports
"""

import json
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import time


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
        ai_transparency_text = ""
        deep_analysis = report.get('deep_analysis', {})
        if deep_analysis:
            consensus = deep_analysis.get('consensus', {})
            ai_percentage = consensus.get('ai_percentage', 0)
            transparency_score = consensus.get('transparency_score', 0)
            primary_model = consensus.get('primary_model', 'Unknown')
            if transparency_score > 0:
                ai_transparency_text = f"""

AI Transparency (AT):
- AI Content Detected: {ai_percentage:.1f}%
- Likely AI Model: {primary_model}
- Transparency Score: {transparency_score}/100"""
                scores_text += f"\n- AT (AI Transparency): {transparency_score}/100"
        
        prompt = f"""You are a policy analyst writing for the general public (reading level: Grade 8).

Document: {document_title}
Grade: {grade} | Score: {composite}/100
Classification: {classification}

Criteria Scores:
{scores_text}
{ai_transparency_text}

Write a 400-500 word plain-language summary that:
1. Explains what the SPOT grading means in simple terms
2. Highlights the strongest area
3. Identifies the weakest area
4. If AI content was detected, briefly explain what this means for transparency
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
        output_file: Optional[str] = None
    ) -> str:
        """Generate summary from existing JSON report."""
        
        with open(json_file, 'r') as f:
            report = json.load(f)
        
        doc_title = report.get('document_title', 'Document')
        
        if not output_file:
            base = json_file.replace('.json', '')
            output_file = f"{base}_summary.txt"
        
        if variant == 'policy':
            return self.generate_policy_summary(report, doc_title, output_file)
        else:
            return self.generate_journalism_summary(report, doc_title, output_file)
    
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

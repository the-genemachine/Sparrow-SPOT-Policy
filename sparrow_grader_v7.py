#!/usr/bin/env python3
"""
Sparrow SPOT Scale™ v7.0 - Dual Variant System with Ethical Framework
Combines:
  - SPARROW Scale™ (Journalism evaluation) from v3
  - SPOT-Policy™ (Government policy evaluation) enhanced with Ethical AI Toolkit in v7

Systematic Protocol for Article Reliability, Rigor, and Overall Worth
+ Societal Policy Oversight Tool

Generates professional certification for both journalistic and policy content
"""

import json
import sys
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import re
import statistics
from contextlib import redirect_stdout
from io import StringIO
from article_analyzer import ArticleAnalyzer

# v7: Import ethical framework modules
try:
    from ai_detection_engine import AIDetectionEngine, ProvenanceAnalyzer
    ETHICAL_AI_DETECTION_AVAILABLE = True
except ImportError:
    ETHICAL_AI_DETECTION_AVAILABLE = False

try:
    from nist_risk_mapper import NISTRiskMapper
    ETHICAL_RISK_MAPPER_AVAILABLE = True
except ImportError:
    ETHICAL_RISK_MAPPER_AVAILABLE = False

try:
    from bias_auditor import BiasAuditor
    ETHICAL_BIAS_AUDITOR_AVAILABLE = True
except ImportError:
    ETHICAL_BIAS_AUDITOR_AVAILABLE = False

try:
    from trust_score_calculator import TrustScoreCalculator
    ETHICAL_TRUST_AVAILABLE = True
except ImportError:
    ETHICAL_TRUST_AVAILABLE = False

# Try to import optional Ollama integration
try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Try to import optional PDF support
try:
    from pypdf import PdfReader
    PDF_SUPPORT_AVAILABLE = True
except ImportError:
    PDF_SUPPORT_AVAILABLE = False

# Try to import optional pdfplumber for better PDF extraction
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# v6: Try to import image extraction and processing
try:
    from pdf2image import convert_from_path
    import tempfile
    IMAGE_EXTRACTION_AVAILABLE = True
except ImportError:
    IMAGE_EXTRACTION_AVAILABLE = False

# Try to import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# v7: Import ethical framework modules and SPOTPolicy class
# (SPOTPolicy will be defined in this file)


class MultimodalAnalyzer:
    """v6 Enhancement: Extract and analyze images from policy documents using Granite Vision."""
    
    def __init__(self, ollama_host='http://localhost:11434'):
        """Initialize multimodal analyzer with Ollama connection."""
        self.ollama_host = ollama_host
        self.vision_model = 'granite3.2-vision:2b'
        self.temp_images = []
    
    def extract_images_from_pdf(self, pdf_path, max_pages=None):
        """
        Extract images and pages from PDF document.
        OPTIMIZED: Samples pages strategically (first, middle, last) for large PDFs.
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to extract (default=None, samples intelligently)
        
        Returns:
            List of extracted image paths (PNG format)
        """
        try:
            if not IMAGE_EXTRACTION_AVAILABLE:
                return []
            
            import tempfile
            from pdf2image import convert_from_path
            
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return []
            
            # Create temp directory for images
            temp_dir = tempfile.mkdtemp(prefix='sparrow_v6_')
            image_paths = []
            
            # For large PDFs, intelligently sample pages instead of converting all
            # First, check PDF page count using pdfplumber if available
            page_indices = list(range(0, 20))  # Default: first 20 pages
            
            if PDFPLUMBER_AVAILABLE:
                try:
                    with pdfplumber.open(str(pdf_path)) as pdf:
                        total_pages = len(pdf.pages)
                        if total_pages > 50:
                            # For large PDFs, sample: first 5, middle 3, last 2
                            page_indices = (
                                list(range(0, 5)) +  # First 5 pages
                                [total_pages // 3, total_pages // 2, total_pages * 2 // 3] +  # Middle
                                [total_pages - 2, total_pages - 1]  # Last 2 pages
                            )
                            page_indices = sorted(list(set(page_indices)))[:15]  # Max 15 pages
                except:
                    pass
            
            # Convert selected PDF pages to images
            page_images = convert_from_path(
                str(pdf_path), 
                dpi=100,  # Lower DPI for faster processing
                first_page=page_indices[0] + 1 if page_indices else 1,
                last_page=min(page_indices[-1] + 1, 21) if page_indices else 20
            )
            
            for idx, img in enumerate(page_images):
                try:
                    img_path = Path(temp_dir) / f'page_{page_indices[idx]+1:04d}.png'
                    img.save(str(img_path), 'PNG')
                    image_paths.append(str(img_path))
                except Exception as e:
                    continue  # Skip corrupted pages
            
            self.temp_images = image_paths
            return image_paths
        
        except Exception as e:
            return []
    
    def query_granite_vision(self, image_path):
        """
        Query Granite3.2-Vision to analyze policy document image.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with vision analysis results
        """
        try:
            if not OLLAMA_AVAILABLE or not image_path:
                return {}
            
            import base64
            
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            media_type = 'image/png' if image_path.endswith('.png') else 'image/jpeg'
            
            prompt = """Analyze this policy document image. For scoring purposes, identify:
1. Chart/table types present (budget, revenue, trends, scenarios, sensitivity analysis, etc.)
2. Key fiscal numbers visible (amounts, percentages, years)
3. What economic information is shown
4. Visual clarity and professional quality (1-10 scale)
5. Whether it shows uncertainty/sensitivity analysis

Be concise and specific. Format key findings clearly."""
            
            payload = {
                'model': self.vision_model,
                'prompt': prompt,
                'images': [f'data:{media_type};base64,{image_data}'],
                'stream': False
            }
            
            response = requests.post(
                f'{self.ollama_host}/api/generate',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'analysis': result.get('response', ''),
                    'image_path': image_path
                }
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def classify_image_findings(self, vision_response):
        """
        Parse vision model output and classify findings for scoring.
        
        Args:
            vision_response: Raw response from Granite Vision
        
        Returns:
            Dictionary with structured findings
        """
        findings = {
            'chart_types': [],
            'fiscal_data_found': False,
            'sensitivity_analysis': False,
            'visual_quality': 0,
            'description': vision_response
        }
        
        text = vision_response.lower()
        
        # Detect chart types
        chart_keywords = {
            'fiscal_chart': ['revenue', 'budget', 'spending', 'expenditure', 'income'],
            'sensitivity_table': ['scenario', 'sensitivity', 'stress test', 'base case', 'upside', 'downside'],
            'trend_graph': ['trend', 'growth', 'decline', 'projection', 'forecast'],
            'demographic': ['population', 'age', 'region', 'distribution'],
            'impact_visual': ['impact', 'effect', 'result', 'outcome', 'consequence']
        }
        
        for chart_type, keywords in chart_keywords.items():
            if any(kw in text for kw in keywords):
                findings['chart_types'].append(chart_type)
        
        # Detect fiscal data
        findings['fiscal_data_found'] = any(kw in text for kw in ['$', 'billion', 'million', 'revenue', 'budget', 'spending'])
        
        # Detect sensitivity analysis
        findings['sensitivity_analysis'] = any(kw in text for kw in ['scenario', 'sensitivity', 'stress', 'assumption', 'variation'])
        
        # Extract visual quality (look for ratings/descriptions)
        if 'professional' in text or 'clear' in text or 'good' in text:
            findings['visual_quality'] = 8
        elif 'poor' in text or 'unclear' in text or 'bad' in text:
            findings['visual_quality'] = 3
        else:
            findings['visual_quality'] = 5
        
        return findings
    
    def apply_vision_boosts(self, text_scores, vision_findings_list):
        """
        Apply vision-based score boosts to policy criteria.
        Weighting: 75% text-based + 25% vision-based.
        
        Args:
            text_scores: Dictionary with scores for FT, SB, ER, PA, PC
            vision_findings_list: List of classified vision findings
        
        Returns:
            Updated scores with vision boosts applied
        """
        if not vision_findings_list:
            return text_scores
        
        boosts = {'FT': 0, 'ER': 0, 'PA': 0, 'SB': 0, 'PC': 0}
        
        # Analyze aggregated findings
        for findings in vision_findings_list:
            chart_types = findings.get('chart_types', [])
            fiscal_data = findings.get('fiscal_data_found', False)
            sensitivity = findings.get('sensitivity_analysis', False)
            visual_quality = findings.get('visual_quality', 0)
            
            # FT (Fiscal Transparency): Boost for fiscal charts
            if fiscal_data:
                boosts['FT'] += 5
            if 'fiscal_chart' in chart_types:
                boosts['FT'] += 3
            
            # ER (Economic Rigor): Boost for sensitivity analysis
            if sensitivity:
                boosts['ER'] += 8
            if 'sensitivity_table' in chart_types:
                boosts['ER'] += 5
            
            # PA (Public Accessibility): Boost for visual quality
            boosts['PA'] += visual_quality  # 0-10 scale
            if visual_quality >= 7:
                boosts['PA'] += 2
            
            # SB (Stakeholder Balance): Boost for demographic data
            if 'demographic' in chart_types:
                boosts['SB'] += 4
            
            # PC (Policy Consequentiality): Boost for impact visuals
            if 'impact_visual' in chart_types:
                boosts['PC'] += 5
        
        # Apply boosts with weighting: 75% text + 25% vision
        final_scores = {}
        for criterion in ['FT', 'SB', 'ER', 'PA', 'PC']:
            text_score = text_scores.get(criterion, 0)
            boost = min(boosts[criterion], 15)  # Cap boost at 15 points
            
            # Weighted formula
            final_scores[criterion] = min(100, text_score * 0.75 + boost * 0.25)
        
        return final_scores
    
    def cleanup_temp_images(self):
        """Clean up temporary image files."""
        try:
            import shutil
            for img_path in self.temp_images:
                path = Path(img_path)
                if path.parent.name.startswith('sparrow_v6_'):
                    shutil.rmtree(str(path.parent), ignore_errors=True)
                    break
        except Exception:
            pass


class SPARROWGrader:
    """Journalism grader from v3 with full feature parity."""
    
    def __init__(self):
        """Initialize SPARROW grader with v3 behavior."""
        self.analyzer = ArticleAnalyzer()
        self.grade_categories = {
            'SI': 'Source Integrity',
            'OI': 'Objectivity Index', 
            'TP': 'Technical Precision',
            'AR': 'Accessibility Rating',
            'IU': 'Impact Utility'
        }
        
        # v3: Standardized qualitative grade labels for each category
        self.grade_labels = {
            'SI': {  # Source Integrity
                (90, 100): ('MG', 'Museum Grade', 'Every claim traced to primary sources, perfect documentation'),
                (80, 89): ('VS', 'Verified Superior', 'Comprehensive sourcing with minor gaps'),
                (70, 79): ('WS', 'Well-Sourced', 'Majority of claims sourced from reputable sources'),
                (60, 69): ('AS', 'Adequately Sourced', 'Key claims sourced, some reliance on general knowledge'),
                (0, 59): ('D', 'Deficient', 'Few citations, unverifiable claims, or fabrication'),
            },
            'OI': {  # Objectivity Index
                (90, 100): ('PN', 'Pristine Neutrality', 'Zero detectable bias, all perspectives represented'),
                (80, 89): ('MB', 'Minimal Bias', 'Slight preference controlled, multiple perspectives'),
                (70, 79): ('CP', 'Controlled Perspective', 'Acknowledged perspective, opposing views presented fairly'),
                (60, 69): ('VS', 'Visible Slant', 'Clear editorial perspective, some opposing views'),
                (0, 59): ('SB', 'Strong Bias', 'One-sided presentation with manipulative language'),
            },
            'TP': {  # Technical Precision
                (90, 100): ('FL', 'Flawless', 'Zero factual errors, perfect grammar, accurate terminology'),
                (80, 89): ('NF', 'Near Flawless', 'One or two trivial errors, excellent technical accuracy'),
                (70, 79): ('WE', 'Well-Executed', 'Few minor errors not affecting core claims'),
                (60, 69): ('C', 'Competent', 'Some errors requiring correction, generally accurate'),
                (0, 59): ('F', 'Flawed', 'Multiple errors affecting credibility'),
            },
            'AR': {  # Accessibility Rating
                (90, 100): ('U', 'Universal', 'Readable by general public (8th grade), clear structure'),
                (80, 89): ('HA', 'Highly Accessible', 'High school level, good structure, mostly clear'),
                (70, 79): ('MA', 'Moderately Accessible', 'Some subject knowledge required, clear but dense'),
                (60, 69): ('SA', 'Specialist Accessible', 'Background knowledge required, technical jargon frequent'),
                (0, 59): ('I', 'Impenetrable', 'Expert-only or incomprehensible to target audience'),
            },
            'IU': {  # Impact Utility
                (90, 100): ('E', 'Essential', 'Fills critical info gap, highly actionable, lasting value'),
                (80, 89): ('HV', 'Highly Valuable', 'Significant new information, practical application clear'),
                (70, 79): ('V', 'Valuable', 'Useful synthesis, some actionable elements'),
                (60, 69): ('MU', 'Moderately Useful', 'Covers known information well, limited new insights'),
                (0, 59): ('N', 'Negligible', 'No new information, no practical application'),
            },
        }
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file using best available method."""
        if not PDF_SUPPORT_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            raise ImportError("PDF support requires 'pypdf' or 'pdfplumber' package. Install with: pip install pypdf pdfplumber")
        
        try:
            pdf_path = pdf_path.strip()
            # Try pdfplumber first (better text extraction)
            if PDFPLUMBER_AVAILABLE:
                print("📖 Using pdfplumber for text extraction...")
                return self._extract_with_pdfplumber(pdf_path)
            else:
                print("📖 Using pypdf for text extraction...")
                return self._extract_with_pypdf(pdf_path)
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_with_pdfplumber(self, pdf_path):
        """Extract text using pdfplumber with table detection."""
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"  📄 Processing {total_pages} pages...")
            for page_num, page in enumerate(pdf.pages, 1):
                if page_num % 50 == 0:
                    print(f"    ✓ Processed {page_num}/{total_pages} pages...")
                text += f"\n--- Page {page_num} ---\n"
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                try:
                    tables = page.find_tables()
                    if tables:
                        text += "\n[TABLES FOUND]\n"
                except:
                    pass
        return text.strip()
    
    def _extract_with_pypdf(self, pdf_path):
        """Fallback to pypdf for text extraction."""
        from pypdf import PdfReader
        pdf_reader = PdfReader(pdf_path)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text += f"\n--- Page {page_num} ---\n"
            text += page.extract_text()
        return text.strip()
    
    def split_text_into_chunks(self, text, max_chars=900000):
        """Split text into chunks to stay under size limit."""
        if len(text) <= max_chars:
            return [text]
        chunks = []
        current_chunk = ""
        paragraphs = text.split('\n\n')
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 > max_chars and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += '\n\n'
                current_chunk += paragraph
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    
    def grade_article(self, article_text, doc_type='journalistic', quiet=False, pdf_path=None):
        """Generate SPARROW Scale™ grading for journalism with optional multimodal vision analysis."""
        if not quiet:
            print("🎯 Sparrow SPOT Scale™ Article Grading System")
            print("=" * 60)
            print("📝 Analyzing article for professional certification...")
        
        chunks = self.split_text_into_chunks(article_text)
        if len(chunks) > 1 and not quiet:
            print(f"📊 Large document detected! Processing {len(chunks)} chunks...")
        
        try:
            if quiet:
                with redirect_stdout(StringIO()):
                    base_results = self.analyzer.analyze_single_article(chunks[0], None)
            else:
                base_results = self.analyzer.analyze_single_article(chunks[0], None)
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
        
        # Calculate SPARROW scores using simplified heuristics
        sparrow_scores = self._calculate_sparrow_scores_simple(base_results, doc_type)
        
        report = {
            'variant': 'SPARROW Scale™',
            'version': '5.0',
            'document_type': doc_type,
            'timestamp': datetime.now().isoformat(),
            'sparrow_scores': sparrow_scores,
            'category_grade_labels': self._get_all_grade_labels(sparrow_scores)
        }
        
        # v7: Apply multimodal vision analysis if PDF provided (auto-activated)
        vision_results = {'status': 'skipped', 'reason': 'no pdf_path provided'}
        
        if pdf_path:
            try:
                analyzer = MultimodalAnalyzer()
                
                # Extract images from PDF (max 20 pages for performance)
                image_paths = analyzer.extract_images_from_pdf(pdf_path, max_pages=20)
                
                if image_paths:
                    # Analyze each image with Granite Vision
                    all_findings = []
                    for img_path in image_paths:
                        vision_response = analyzer.query_granite_vision(img_path)
                        if vision_response.get('status') == 'success':
                            findings = analyzer.classify_image_findings(
                                vision_response.get('analysis', '')
                            )
                            all_findings.append(findings)
                    
                    if all_findings:
                        vision_results = {
                            'status': 'success',
                            'images_analyzed': len(all_findings),
                            'findings': all_findings[:3]  # Store first 3 findings
                        }
                else:
                    vision_results = {'status': 'no_images', 'reason': 'No images found in PDF'}
            except Exception as e:
                vision_results = {'status': 'error', 'error': str(e)}
        
        report['vision_analysis'] = vision_results
        
        return report
    
    def _calculate_sparrow_scores_simple(self, base_results, doc_type):
        """Simplified SPARROW scoring using base analysis."""
        scores = {}
        
        # SI: Source Integrity - based on citations detected
        citations = base_results.get('source_analysis', {}).get('direct_quotes', 0)
        si_score = min(100, 50 + (citations * 2))
        scores['SI'] = {'score': si_score, 'grade': self._get_grade_letter(si_score)}
        
        # OI: Objectivity Index - based on bias analysis
        bias_level = base_results.get('bias_analysis', {}).get('overall_bias_level', 'low')
        oi_score = {'very high': 40, 'high': 55, 'medium': 70, 'low': 85, 'none': 95}.get(bias_level.lower(), 75)
        scores['OI'] = {'score': oi_score, 'grade': self._get_grade_letter(oi_score)}
        
        # TP: Technical Precision - based on readability and structure
        readability = base_results.get('readability', {}).get('flesch_reading_ease', 50)
        tp_score = min(100, 50 + (abs(readability - 60) / 2))
        scores['TP'] = {'score': tp_score, 'grade': self._get_grade_letter(tp_score)}
        
        # AR: Accessibility Rating - Flesch reading ease directly
        ar_score = max(0, min(100, readability * 1.5))
        scores['AR'] = {'score': ar_score, 'grade': self._get_grade_letter(ar_score)}
        
        # IU: Impact Utility - word count and entity density
        word_count = base_results.get('metadata', {}).get('word_count', 0)
        iu_score = min(100, 50 + (min(word_count, 3000) / 30))
        scores['IU'] = {'score': iu_score, 'grade': self._get_grade_letter(iu_score)}
        
        # Calculate composite
        if doc_type == 'policy':
            weights = {'SI': 0.25, 'OI': 0.20, 'TP': 0.25, 'AR': 0.05, 'IU': 0.25}
        elif doc_type == 'mixed':
            weights = {'SI': 0.30, 'OI': 0.23, 'TP': 0.22, 'AR': 0.08, 'IU': 0.17}
        else:
            weights = {'SI': 0.35, 'OI': 0.25, 'TP': 0.20, 'AR': 0.10, 'IU': 0.10}
        
        composite = sum(scores[cat]['score'] * weights[cat] for cat in weights)
        
        scores['composite'] = {
            'score': round(composite, 1),
            'grade': self._get_composite_grade(composite)
        }
        
        return scores
    
    def _get_grade_letter(self, score):
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _get_composite_grade(self, score):
        """Get composite grade classification."""
        if score >= 90:
            return ('A+', 'Platinum Standard')
        elif score >= 85:
            return ('A', 'Gold Standard')
        elif score >= 80:
            return ('B+', 'Silver Standard')
        elif score >= 75:
            return ('B', 'Bronze Standard')
        else:
            return (self._get_grade_letter(score), 'Below Standards')
    
    def _get_all_grade_labels(self, sparrow_scores):
        """Get grade labels for all categories."""
        labels = {}
        for category in ['SI', 'OI', 'TP', 'AR', 'IU']:
            score = sparrow_scores[category]['score']
            for (low, high), (code, label, desc) in self.grade_labels[category].items():
                if low <= score <= high:
                    labels[category] = {'code': code, 'label': label, 'description': desc}
                    break
        return labels


class SPOTPolicy:
    """
    ENHANCED in v7: SPOT-Policy™ - Societal Policy Oversight Tool
    
    Evaluates government documents (budgets, legislation, policy briefs) using
    policy-specific criteria aligned with IMF/OECD standards, enhanced with
    ethical transparency framework (AI detection, risk classification, fairness).
    
    Five criteria (FISCAL):
    - FT: Fiscal Transparency (revenue, spending, assumptions, risks)
    - SB: Stakeholder Balance (representation of 5 stakeholder groups)
    - ER: Economic Rigor (soundness of assumptions and forecasts)
    - PA: Public Accessibility (citizen understanding of key points)
    - PC: Policy Consequentiality (real-world binding effect on outcomes)
    """
    
    def __init__(self):
        """Initialize SPOT-Policy grader."""
        self.analyzer = ArticleAnalyzer()
        
        self.grade_categories = {
            'FT': 'Fiscal Transparency',
            'SB': 'Stakeholder Balance',
            'ER': 'Economic Rigor',
            'PA': 'Public Accessibility',
            'PC': 'Policy Consequentiality'
        }
        
        # v7: Grade labels for SPOT-Policy criteria (with ethical framework)
        self.grade_labels = {
            'FT': {  # Fiscal Transparency
                (90, 100): ('ET', 'Exemplary Transparency', 'Full revenue/spending breakdown, explicit assumptions, risk scenarios, reconciliation shown'),
                (75, 89.99): ('CD', 'Clear Disclosure', 'Detailed revenue/spending, assumptions stated, some risk disclosure, minor omissions'),
                (60, 74.99): ('AT', 'Adequate Transparency', 'Major categories disclosed, partial assumptions, limited risk, incomplete reconciliation'),
                (45, 59.99): ('OD', 'Opaque Disclosure', 'Aggregated figures, vague assumptions, minimal risk analysis, no reconciliation'),
                (0, 44.99): ('C', 'Concealed', 'Revenue/spending obscured, no assumptions, actively hides fiscal position'),
            },
            'SB': {  # Stakeholder Balance
                (90, 100): ('MC', 'Multiparty Consensus', 'Gov, opposition, business, labor, NGO represented; tradeoffs acknowledged'),
                (75, 89.99): ('BV', 'Balanced Views', '4+ stakeholder perspectives; tradeoffs acknowledged; advocacy transparent'),
                (60, 74.99): ('PB', 'Partial Balance', '2-3 perspectives; some alternatives acknowledged; advocacy implicit but detectable'),
                (45, 59.99): ('SV', 'Single-Voice Advocacy', 'Primarily government; opposing views minimized; advocacy not transparent'),
                (0, 44.99): ('P', 'Propaganda', 'Only government view; opposition absent/caricatured; advocacy purpose not disclosed'),
            },
            'ER': {  # Economic Rigor
                (90, 100): ('RA', 'Rigorous Analysis', 'Assumptions data-driven, sensitivity analysis provided, model documented, peer-reviewed'),
                (75, 89.99): ('SM', 'Sound Methodology', 'Reasonable assumptions, model described, internal consistency verified, not sensitivity-tested'),
                (60, 74.99): ('AA', 'Acceptable Assumptions', 'Plausible assumptions, model described, evidence of bias (conservative/optimistic), not validated'),
                (45, 59.99): ('QA', 'Questionable Assumptions', 'Assumptions contradict recent data, model opaque, bias likely, validation missing'),
                (0, 44.99): ('FA', 'Flawed Analysis', 'Unrealistic assumptions, model hidden, no validation, likely to be wrong'),
            },
            'PA': {  # Public Accessibility
                (90, 100): ('HA', 'Highly Accessible', 'Executive summary (grade 8), visual aids, FAQ, citizen impact examples'),
                (75, 89.99): ('GC', 'Generally Clear', 'Technical summary (grade 10), headings, appendix for specialists'),
                (60, 74.99): ('MD', 'Moderately Dense', 'Grade 12 reading, some structure, technical sections unexplained'),
                (45, 59.99): ('TL', 'Technical Language', 'Grade 14+ reading, minimal structure, professionals preferred'),
                (0, 44.99): ('I', 'Impenetrable', 'Dense legal/technical language, no structure, hostile to non-specialists'),
            },
            'PC': {  # Policy Consequentiality
                (90, 100): ('T', 'Transformative', 'Addresses major challenge, $10B+, affects millions, binding legislation'),
                (75, 89.99): ('S', 'Substantial Impact', 'Significant reallocation, affects hundreds of thousands, clear causal pathway'),
                (60, 74.99): ('M', 'Meaningful Change', 'Targeted intervention, measurable effects, affects tens of thousands'),
                (45, 59.99): ('MO', 'Modest Effect', 'Incremental adjustment, affects specific programs, limited outcome change'),
                (0, 44.99): ('N', 'Negligible Impact', 'Symbolic gesture, minimal resources, unlikely to change outcomes'),
            },
        }
        
        # Stakeholder keywords for SB criterion
        self.stakeholder_keywords = {
            'government': ['government', 'federal', 'minister', 'parliament', 'department', 'agency', 'official', 'legislation', 'bill'],
            'opposition': ['opposition', 'conservative', 'liberal', 'democrat', 'republican', 'provincial', 'dissent', 'criticism', 'challenge'],
            'business': ['business', 'corporation', 'private sector', 'industry', 'commerce', 'company', 'merchant', 'enterprise', 'capital'],
            'labor': ['union', 'worker', 'labour', 'labor', 'employment', 'wage', 'strike', 'collective', 'bargain'],
            'public_interest': ['ngo', 'civil society', 'activist', 'community', 'public', 'citizen', 'advocacy', 'nonprofit', 'grassroots'],
        }
        
        # Economic keywords for ER criterion
        self.economic_keywords = {
            'gdp': ['gdp', 'gross domestic product', 'economic growth'],
            'inflation': ['inflation', 'cpi', 'consumer price index', 'price level'],
            'interest_rate': ['interest rate', 'rates', 'prime rate', 'fed funds'],
            'employment': ['unemployment', 'employment', 'jobs', 'labor force'],
            'deficit': ['deficit', 'surplus', 'fiscal balance', 'budget balance'],
        }
    
    def score_fiscal_transparency(self, text, document_structure=None):
        """
        Score Fiscal Transparency (FT): 0-100
        
        Measures disclosure of revenue sources, spending categories, assumptions,
        risks, and reconciliation with prior periods.
        """
        score = 0
        max_score = 100
        
        # Check for revenue breakdown
        revenue_keywords = ['revenue', 'income tax', 'corporate tax', 'excise tax', 'tax revenue', 'total revenue']
        revenue_found = sum(1 for kw in revenue_keywords if kw.lower() in text.lower())
        revenue_score = min(20, (revenue_found / len(revenue_keywords)) * 20)
        score += revenue_score
        
        # Check for spending breakdown
        spending_keywords = ['spending', 'expenditure', 'appropriation', 'budget', 'allocat', 'program', 'department', 'ministry']
        spending_found = sum(1 for kw in spending_keywords if kw.lower() in text.lower())
        spending_score = min(20, (spending_found / len(spending_keywords)) * 20)
        score += spending_score
        
        # Check for assumptions (GDP, inflation, rates)
        assumption_keywords = ['assumes', 'assumption', 'projected', 'forecast', 'scenario', 'based on']
        assumptions_found = sum(1 for kw in assumption_keywords if kw.lower() in text.lower())
        assumption_score = min(20, (assumptions_found / len(assumption_keywords)) * 20)
        score += assumption_score
        
        # v5 ENHANCEMENT: Risk disclosure with specific economic variable patterns
        risk_keywords = ['risk', 'downside', 'scenario', 'sensitivity', 'uncertainty', 'recession', 'adverse']
        risk_found = sum(1 for kw in risk_keywords if kw.lower() in text.lower())
        
        # v5: Specific risk patterns for economic variables
        specific_risk_patterns = [
            r'interest\s+rate.{0,40}(sensitivity|risk|impact|shock)',
            r'oil\s+price.{0,40}(sensitivity|risk|impact)',
            r'commodity\s+price.{0,40}(sensitivity|risk)',
            r'exchange\s+rate.{0,40}(sensitivity|risk)',
            r'stress\s+test',
        ]
        specific_risks = sum(1 for pattern in specific_risk_patterns if re.search(pattern, text, re.IGNORECASE))
        risk_score = min(15, ((risk_found + specific_risks * 2) / (len(risk_keywords) + 1)) * 15)
        score += risk_score
        
        # Check for reconciliation (year-over-year comparisons)
        reconciliation_keywords = ['prior', 'previous', 'year-over-year', 'change', 'variance', 'increase', 'decrease', 'comparison']
        reconciliation_found = sum(1 for kw in reconciliation_keywords if kw.lower() in text.lower())
        reconciliation_score = min(10, (reconciliation_found / len(reconciliation_keywords)) * 10)
        score += reconciliation_score
        
        # Bonus for annexes/appendices (indicates detail)
        if 'annex' in text.lower() or 'appendix' in text.lower() or 'technical' in text.lower():
            score = min(100, score + 5)
        
        # v5: Bonus for explicit sensitivity analysis
        if re.search(r'sensitivity\s+(analysis|table)', text, re.IGNORECASE):
            score = min(100, score + 5)
        
        return min(100, score)
    
    def score_stakeholder_balance(self, text):
        """
        Score Stakeholder Balance (SB): 0-100
        
        Measures representation of 5 stakeholder groups:
        - Government/Policy
        - Opposition/Alternative voices
        - Business/Private sector
        - Labor/Workers
        - Public Interest/NGO/Community
        """
        stakeholder_counts = {group: 0 for group in self.stakeholder_keywords}
        
        text_lower = text.lower()
        for group, keywords in self.stakeholder_keywords.items():
            for keyword in keywords:
                stakeholder_counts[group] += text_lower.count(keyword)
        
        # Normalize to 0-100
        total_mentions = sum(stakeholder_counts.values())
        if total_mentions == 0:
            return 0
        
        # Calculate representation percentage for each group
        percentages = {group: (count / total_mentions) * 100 for group, count in stakeholder_counts.items()}
        
        # Ideal: 20% each (balanced)
        ideal_percentage = 20
        
        # Score based on how close to balanced representation
        balance_errors = [abs(pct - ideal_percentage) for pct in percentages.values()]
        avg_error = statistics.mean(balance_errors)
        
        # Convert error to score (lower error = higher score)
        balance_score = max(0, 100 - (avg_error * 2))  # Scale error to 0-100 range
        
        # Bonus if all 5 stakeholders represented
        if all(count > 0 for count in stakeholder_counts.values()):
            balance_score = min(100, balance_score + 10)
        
        # Check for explicit tradeoff acknowledgment
        tradeoff_keywords = ['trade-off', 'tradeoff', 'benefit', 'cost', 'while', 'however', 'but', 'versus', 'versus']
        tradeoffs_found = sum(1 for kw in tradeoff_keywords if kw.lower() in text_lower)
        if tradeoffs_found > 10:
            balance_score = min(100, balance_score + 10)
        
        return min(100, balance_score)
    
    def score_economic_rigor(self, text, analysis_data=None):
        """
        Score Economic Rigor (ER): 0-100
        
        Measures soundness of economic assumptions and projections.
        v7 ENHANCEMENT: Includes sensitivity analysis with confidence intervals.
        
        Checks for:
        - GDP growth assumptions
        - Inflation assumptions
        - Interest rate assumptions
        - Sensitivity analysis (baseline, upside, downside scenarios)
        - Model documentation
        - External validation
        
        Returns score with confidence interval reflecting uncertainty.
        """
        score = 0
        max_score = 100
        confidence_factors = []  # Track confidence factors
        
        # Check for explicit assumptions
        assumption_patterns = [
            r'assumes?\s+(\d+\.?\d*)\s*%?\s*(gdp|growth)',
            r'gdp\s+growth\s+.*?(\d+\.?\d*)\s*%',
            r'inflation\s+.*?(\d+\.?\d*)\s*%',
            r'interest\s+rate\s+.*?(\d+\.?\d*)\s*%',
        ]
        
        assumptions_found = 0
        for pattern in assumption_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            assumptions_found += len(matches)
        
        assumption_score = min(20, (assumptions_found / 3) * 20)  # Up to 3 key assumptions
        score += assumption_score
        confidence_factors.append(0.7 if assumptions_found >= 3 else 0.5)
        
        # v7 ENHANCEMENT: Structured sensitivity analysis with scenarios
        sensitivity_keywords = ['sensitivity', 'scenario', 'downside', 'upside', 'range', 'variance', 'pessimistic', 'optimistic']
        sensitivity_found = sum(1 for kw in sensitivity_keywords if kw.lower() in text.lower())
        
        # Detect structured sensitivity analysis patterns (core strength)
        sensitivity_patterns = [
            r'sensitivity\s+(analysis|table)',
            r'scenario\s+(analysis|table)',
            r'stress\s+test',
            r'(base|central|upside|downside)\s+case',
            r'resilience\s+test',
            r'\+\s*\d+\.?\d*\s*%|\-\s*\d+\.?\d*\s*%',  # Range expressions
        ]
        sensitivity_structured = sum(1 for pattern in sensitivity_patterns if re.search(pattern, text, re.IGNORECASE))
        
        # v7: Calculate sensitivity score with emphasis on structured analysis
        base_sensitivity = min(20, ((sensitivity_found + sensitivity_structured * 2) / (len(sensitivity_keywords) + 1)) * 20)
        
        # Bonus if multiple scenarios detected
        if sensitivity_structured >= 3:
            base_sensitivity = min(25, base_sensitivity + 5)  # Multi-scenario bonus
        
        score += base_sensitivity
        # High confidence if structured analysis present, lower if only keywords
        sensitivity_confidence = 0.85 if sensitivity_structured >= 3 else (0.65 if sensitivity_found > 0 else 0.4)
        confidence_factors.append(sensitivity_confidence)
        
        # Check for data sourcing
        data_keywords = ['data', 'statistics', 'average', 'historical', 'trend', 'baseline', 'current']
        data_found = sum(1 for kw in data_keywords if kw.lower() in text.lower())
        data_score = min(20, (data_found / len(data_keywords)) * 20)
        score += data_score
        confidence_factors.append(0.7 if data_found >= 4 else 0.5)
        
        # Check for model documentation
        model_keywords = ['model', 'methodology', 'approach', 'method', 'formula', 'calculation', 'derived']
        model_found = sum(1 for kw in model_keywords if kw.lower() in text.lower())
        model_score = min(20, (model_found / len(model_keywords)) * 20)
        score += model_score
        confidence_factors.append(0.75 if model_found >= 5 else 0.55)
        
        # Check for external validation
        validation_keywords = ['validated', 'verified', 'peer review', 'audit', 'external', 'independent', 'confirmed']
        validation_found = sum(1 for kw in validation_keywords if kw.lower() in text.lower())
        validation_score = min(15, (validation_found / len(validation_keywords)) * 15)
        score += validation_score
        confidence_factors.append(0.85 if validation_found >= 2 else 0.6)
        
        # Bonus for technical rigor indicators
        if 'annex' in text.lower() or 'appendix' in text.lower() or 'detailed' in text.lower():
            score = min(100, score + 5)
            confidence_factors.append(0.8)
        
        # v7: Bonus for advanced economic techniques (increases confidence)
        advanced_techniques_found = 0
        if re.search(r'counterfactual', text, re.IGNORECASE):
            score = min(100, score + 3)
            advanced_techniques_found += 1
        if re.search(r'monte\s+carlo|probabilistic', text, re.IGNORECASE):
            score = min(100, score + 3)
            advanced_techniques_found += 1
        if re.search(r'bayesian|bayesian\s+analysis', text, re.IGNORECASE):
            score = min(100, score + 3)
            advanced_techniques_found += 1
        
        if advanced_techniques_found > 0:
            confidence_factors.append(0.9)  # High confidence with advanced methods
        
        # v7: Calculate confidence interval based on all factors
        avg_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
        confidence_interval_width = 15 * (1 - avg_confidence)  # Range from 7.5 to 15
        
        final_score = min(100, score)
        
        # v7: Store sensitivity analysis details in report if available
        if hasattr(self, '_sensitivity_data'):
            self._sensitivity_data = {
                'score': final_score,
                'confidence': avg_confidence,
                'confidence_interval': {
                    'lower': max(0, final_score - confidence_interval_width),
                    'upper': min(100, final_score + confidence_interval_width)
                },
                'components': {
                    'assumptions': assumption_score,
                    'sensitivity_analysis': base_sensitivity,
                    'data_sourcing': data_score,
                    'methodology': model_score,
                    'external_validation': validation_score
                },
                'advanced_techniques': advanced_techniques_found
            }
        
        return final_score
    
    def score_public_accessibility(self, text, readability_metrics=None):
        """
        Score Public Accessibility (PA): 0-100
        
        Measures whether non-specialists can understand the document.
        Evaluates:
        - Executive summary presence/quality
        - Reading level (Flesch-Kincaid grade)
        - Document structure (headings, organization)
        - Visual aids and examples
        """
        score = 0
        max_score = 100
        
        # Check for executive summary
        summary_keywords = ['executive summary', 'overview', 'introduction', 'key points', 'highlights', 'summary']
        has_summary = any(kw.lower() in text.lower() for kw in summary_keywords)
        summary_score = 25 if has_summary else 0
        score += summary_score
        
        # Check for reading level indicators
        # Simple proxy: check for frequent technical terms
        technical_keywords = ['fiscal', 'macroeconomic', 'derivative', 'quantitative', 'algorithm', 'regression', 'heterogeneous']
        tech_density = sum(text.lower().count(kw) for kw in technical_keywords) / len(text.split())
        
        if tech_density < 0.001:  # Low technical density
            reading_score = 25
        elif tech_density < 0.002:  # Medium
            reading_score = 15
        elif tech_density < 0.005:  # High
            reading_score = 10
        else:  # Very high
            reading_score = 0
        score += reading_score
        
        # Check for document structure
        structure_keywords = ['contents', 'table of contents', 'chapter', 'section', 'subsection', 'heading', 'outline']
        has_structure = any(kw.lower() in text.lower() for kw in structure_keywords)
        structure_score = 20 if has_structure else 5
        score += structure_score
        
        # Check for visual aids and examples
        visual_keywords = ['figure', 'table', 'chart', 'graph', 'diagram', 'illustration', 'example', 'case study']
        visual_found = sum(1 for kw in visual_keywords if kw.lower() in text.lower())
        visual_score = min(20, (visual_found / len(visual_keywords)) * 20)
        score += visual_score
        
        # Check for FAQ or glossary
        if 'faq' in text.lower() or 'frequently asked' in text.lower() or 'glossary' in text.lower():
            score = min(100, score + 10)
        
        return min(100, score)
    
    def score_policy_consequentiality(self, text):
        """
        Score Policy Consequentiality (PC): 0-100
        
        Measures real-world binding effect and outcome impact.
        Evaluates:
        - Resource magnitude ($ billions)
        - Population reach (% affected)
        - Causal clarity (mechanism documented)
        - Duration (permanent vs. temporary)
        - Binding force (enacted law vs. proposal)
        """
        score = 0
        max_score = 100
        
        # Extract dollar amounts
        dollar_pattern = r'\$\s*(\d+\.?\d*)\s*(billion|million|b|m)'
        dollar_matches = re.findall(dollar_pattern, text, re.IGNORECASE)
        
        total_billion = 0
        for amount, unit in dollar_matches:
            if unit.lower() in ['b', 'billion']:
                total_billion += float(amount)
            elif unit.lower() in ['m', 'million']:
                total_billion += float(amount) / 1000
        
        # Resource magnitude score
        if total_billion > 10:
            resource_score = 20
        elif total_billion > 1:
            resource_score = 15
        elif total_billion > 0.1:
            resource_score = 10
        elif total_billion > 0:
            resource_score = 5
        else:
            resource_score = 0
        score += resource_score
        
        # Check population reach
        reach_keywords = ['million', 'million people', 'millions', 'affects', 'impact', 'beneficiaries', 'coverage']
        reach_found = sum(1 for kw in reach_keywords if kw.lower() in text.lower())
        reach_score = min(20, (reach_found / len(reach_keywords)) * 20)
        score += reach_score
        
        # Causal clarity (mechanism documented)
        causal_keywords = ['will', 'result in', 'lead to', 'cause', 'enable', 'facilitate', 'through', 'mechanism']
        causal_found = sum(1 for kw in causal_keywords if kw.lower() in text.lower())
        causal_score = min(20, (causal_found / len(causal_keywords)) * 20)
        score += causal_score
        
        # Duration (permanent vs. temporary)
        permanent_keywords = ['permanent', 'legislation', 'law', 'statute', 'ongoing', 'continuous', 'indefinite']
        temporary_keywords = ['temporary', 'pilot', 'trial', 'sunset', 'expires', 'limited duration']
        
        permanent_found = sum(1 for kw in permanent_keywords if kw.lower() in text.lower())
        temporary_found = sum(1 for kw in temporary_keywords if kw.lower() in text.lower())
        
        if permanent_found > temporary_found:
            duration_score = 20
        elif permanent_found == temporary_found:
            duration_score = 10
        else:
            duration_score = 0
        score += duration_score
        
        # Binding force (enacted vs. proposal)
        enacted_keywords = ['enacted', 'passed', 'approved', 'signed', 'law', 'legislation', 'statute']
        proposal_keywords = ['propose', 'proposal', 'will', 'recommend', 'suggestion', 'plan']
        
        enacted_found = sum(1 for kw in enacted_keywords if kw.lower() in text.lower())
        proposal_found = sum(1 for kw in proposal_keywords if kw.lower() in text.lower())
        
        if enacted_found > proposal_found:
            binding_score = 20
        elif proposal_found > enacted_found:
            binding_score = 10
        else:
            binding_score = 5
        score += binding_score
        
        return min(100, score)
    
    def grade(self, text, document_type='policy', document_structure=None, pdf_path=None):
        """
        Grade a policy document using SPOT-Policy™ criteria + v7 ethical framework.
        
        v7 Enhancements (Pillars 1-2):
        - Pillar 1: INPUT TRANSPARENCY (AI detection + provenance)
        - Pillar 2: ANALYSIS TRANSPARENCY (risk tier + fairness + trust score)
        
        Args:
            text: Document text content
            document_type: Type of document ('policy', etc.)
            document_structure: Optional document structure info
            pdf_path: Optional path to PDF for image extraction
        
        Returns dict with criteria scores, composite, AND ethical framework results.
        """
        report = {
            'variant': 'SPOT-Policy™',
            'version': '7.0',
            'document_type': document_type,
            'timestamp': datetime.now().isoformat(),
            'criteria': {},
            'vision_findings': None,
            'ethical_framework': {
                'version': '1.0',
                'pillars_active': ['INPUT_TRANSPARENCY', 'ANALYSIS_TRANSPARENCY']
            }
        }
        
        # ============================================================
        # PILLAR 1: INPUT TRANSPARENCY - Detect AI-generated input
        # ============================================================
        
        ai_detection_result = None
        if ETHICAL_AI_DETECTION_AVAILABLE:
            try:
                ai_engine = AIDetectionEngine()
                ai_detection_result = ai_engine.analyze_document(text)
                report['ai_detection'] = ai_detection_result
            except Exception as e:
                report['ai_detection'] = {'status': 'error', 'message': str(e)}
        
        # ============================================================
        # SCORE POLICY CRITERIA (text-based)
        # ============================================================
        
        text_scores = {
            'FT': self.score_fiscal_transparency(text, document_structure),
            'SB': self.score_stakeholder_balance(text),
            'ER': self.score_economic_rigor(text),
            'PA': self.score_public_accessibility(text),
            'PC': self.score_policy_consequentiality(text)
        }
        
        # v6: Apply multimodal enhancements if PDF provided
        final_scores = text_scores.copy()
        vision_results = {'status': 'skipped', 'reason': 'no pdf_path provided'}
        
        if pdf_path:
            try:
                analyzer = MultimodalAnalyzer()
                
                # Extract images from PDF (max 20 pages for performance)
                image_paths = analyzer.extract_images_from_pdf(pdf_path, max_pages=20)
                
                if image_paths:
                    # Analyze each image with Granite Vision
                    all_findings = []
                    for img_path in image_paths:
                        vision_response = analyzer.query_granite_vision(img_path)
                        if vision_response.get('status') == 'success':
                            findings = analyzer.classify_image_findings(
                                vision_response.get('analysis', '')
                            )
                            all_findings.append(findings)
                    
                    if all_findings:
                        # Apply vision-based score boosts
                        final_scores = analyzer.apply_vision_boosts(text_scores, all_findings)
                        vision_results = {
                            'status': 'success',
                            'images_analyzed': len(all_findings),
                            'findings': all_findings[:3]  # Store first 3 findings
                        }
                    
                    # Cleanup temp images
                    analyzer.cleanup_temp_images()
            
            except Exception as e:
                vision_results = {'status': 'error', 'message': str(e)}
        
        report['criteria'] = {
            'FT': {'score': round(final_scores['FT'], 1), 'name': self.grade_categories['FT']},
            'SB': {'score': round(final_scores['SB'], 1), 'name': self.grade_categories['SB']},
            'ER': {'score': round(final_scores['ER'], 1), 'name': self.grade_categories['ER']},
            'PA': {'score': round(final_scores['PA'], 1), 'name': self.grade_categories['PA']},
            'PC': {'score': round(final_scores['PC'], 1), 'name': self.grade_categories['PC']},
        }
        
        report['vision_findings'] = vision_results
        
        # ============================================================
        # PILLAR 2 PART 1: RISK CLASSIFICATION (NIST)
        # ============================================================
        
        risk_tier_result = None
        if ETHICAL_RISK_MAPPER_AVAILABLE:
            try:
                risk_mapper = NISTRiskMapper()
                
                # Determine document characteristics for risk mapping
                characteristics = {
                    'task': 'policy_scoring',
                    'document_type': document_type,
                    'scope': 'national' if 'budget' in document_type.lower() else 'departmental',
                    'decision_criticality': 'strategic' if final_scores['FT'] > 80 else 'operational',
                    'affected_population': 1000000,  # Default estimate
                    'budget_impact': max(final_scores.values()) / 10,  # Heuristic estimate
                    'timeline': 'medium_term'
                }
                
                risk_tier_result = risk_mapper.classify(characteristics)
                report['risk_tier'] = risk_tier_result
            except Exception as e:
                report['risk_tier'] = {'status': 'error', 'message': str(e)}
        
        # ============================================================
        # PILLAR 2 PART 2: FAIRNESS AUDIT (BIAS DETECTION)
        # ============================================================
        
        bias_audit_result = None
        if ETHICAL_BIAS_AUDITOR_AVAILABLE:
            try:
                bias_auditor = BiasAuditor()
                
                # Generate demographic group scores based on policy criteria
                # (In production, these would come from actual demographic data)
                scores_by_group = {
                    'General_Population': [final_scores['FT'], final_scores['SB'], final_scores['ER']],
                    'Vulnerable_Groups': [final_scores['FT'] * 0.9, final_scores['SB'] * 0.85, final_scores['ER'] * 0.88],
                    'Regional_Minority': [final_scores['PA'], final_scores['PC'], (final_scores['FT'] + final_scores['SB']) / 2]
                }
                
                bias_audit_result = bias_auditor.audit_scores(scores_by_group)
                report['bias_audit'] = bias_audit_result
            except Exception as e:
                report['bias_audit'] = {'status': 'error', 'message': str(e)}
        
        # ============================================================
        # COMPOSITE SCORE & GRADE (original algorithm)
        # ============================================================
        
        composite = (
            (final_scores['FT'] * 0.20) +
            (final_scores['SB'] * 0.15) +
            (final_scores['ER'] * 0.25) +
            (final_scores['PA'] * 0.20) +
            (final_scores['PC'] * 0.20)
        )
        
        report['composite_score'] = round(composite, 1)
        report['weighting'] = {
            'FT': 0.20,
            'SB': 0.15,
            'ER': 0.25,
            'PA': 0.20,
            'PC': 0.20,
        }
        
        # Add category grade labels
        report['category_grade_labels'] = {}
        for criterion in ['FT', 'SB', 'ER', 'PA', 'PC']:
            score = final_scores[criterion]
            for (low, high), (code, label, description) in self.grade_labels[criterion].items():
                if low <= score <= high:
                    report['category_grade_labels'][criterion] = {
                        'code': code,
                        'label': label,
                        'description': description,
                        'score': round(score, 1)
                    }
                    break
        
        # Determine composite grade band
        composite_bands = [
            ('A+', 90, 100),
            ('A', 85, 89),
            ('B+', 80, 84),
            ('B', 75, 79),
            ('B-', 70, 74),
            ('C', 60, 69),
            ('D', 50, 59),
            ('F', 0, 49),
        ]
        
        report['composite_grade'] = 'F'  # Default
        for grade, low, high in composite_bands:
            if low <= composite < (high + 1):
                report['composite_grade'] = grade
                break
        
        # Classification
        classifications = {
            'A+': 'Exemplary Policy',
            'A': 'Excellent Policy',
            'B+': 'Good Policy',
            'B': 'Acceptable Policy',
            'B-': 'Questionable Policy',
            'C': 'Problematic Policy',
            'D': 'Flawed Policy',
            'F': 'Unacceptable Policy',
        }
        
        report['classification'] = classifications.get(report['composite_grade'], 'Unclassified')
        
        # ============================================================
        # PILLAR 2 PART 3: TRUST SCORE CALCULATION
        # ============================================================
        
        trust_score_result = None
        if ETHICAL_TRUST_AVAILABLE:
            try:
                trust_calculator = TrustScoreCalculator()
                trust_score_result = trust_calculator.calculate(
                    ai_detection_result=ai_detection_result,
                    bias_audit_result=bias_audit_result,
                    risk_tier=risk_tier_result.get('risk_tier') if risk_tier_result else None,
                    nist_functions=[f['name'] for f in risk_tier_result.get('nist_functions_activated', [])] 
                                  if risk_tier_result else None
                )
                report['trust_score'] = trust_score_result
            except Exception as e:
                report['trust_score'] = {'status': 'error', 'message': str(e)}
        
        # ============================================================
        # GENERATE ETHICAL SUMMARY
        # ============================================================
        
        report['ethical_summary'] = self._generate_ethical_summary(
            ai_detection_result, risk_tier_result, bias_audit_result, trust_score_result
        )
        
        return report
    
    def _generate_ethical_summary(self, ai_detection, risk_tier, bias_audit, trust_score):
        """Generate human-readable ethical framework summary with escalation logic."""
        
        summary = {
            'input_transparency': 'UNKNOWN',
            'analysis_transparency': 'UNKNOWN',
            'output_accountability': 'UNKNOWN',
            'overall_recommendation': 'UNKNOWN',
            'escalation_required': False,
            'escalation_triggers': []
        }
        
        # INPUT TRANSPARENCY assessment
        if ai_detection and ai_detection.get('detected'):
            summary['input_transparency'] = f"AI-generated input detected (Score: {ai_detection.get('ai_detection_score', 0):.2f})"
            summary['escalation_required'] = True
            summary['escalation_triggers'].append("AI-generated input detected")
        elif ai_detection:
            summary['input_transparency'] = f"Human-generated input confirmed (Score: {ai_detection.get('ai_detection_score', 0):.2f})"
        
        # ANALYSIS TRANSPARENCY assessment
        if risk_tier and risk_tier.get('risk_tier') == 'high':
            summary['analysis_transparency'] = f"HIGH-RISK policy (Score: {risk_tier.get('risk_score', 0)}). Comprehensive analysis applied."
            summary['escalation_required'] = True
            summary['escalation_triggers'].append(f"HIGH-risk policy classification (score: {risk_tier.get('risk_score', 0)})")
        elif risk_tier:
            summary['analysis_transparency'] = f"{risk_tier.get('risk_tier', 'UNKNOWN').upper()}-risk policy. Appropriate controls activated."
        
        # OUTPUT ACCOUNTABILITY and TRUST assessment
        if trust_score and trust_score.get('trust_score'):
            score = trust_score['trust_score']
            level = trust_score['trust_level']
            summary['output_accountability'] = f"Trust Score: {score}/100 ({level.upper()})"
            
            # v7: Escalate if trust < 70 OR trust level is critical/low
            if score < 70 or level in ['critical', 'low']:
                summary['escalation_required'] = True
                if score < 70:
                    summary['escalation_triggers'].append(f"Trust Score below 70 threshold (score: {score}/100)")
                if level in ['critical', 'low']:
                    summary['escalation_triggers'].append(f"Trust Level: {level.upper()}")
        
        # Overall recommendation
        if summary['escalation_required']:
            triggers_text = '; '.join(summary['escalation_triggers'])
            summary['overall_recommendation'] = f"⚠️ PROFESSIONAL REVIEW REQUIRED ({triggers_text})"
        else:
            summary['overall_recommendation'] = "✓ Proceed with standard governance review."
        
        return summary


def create_arg_parser():
    """Create CLI argument parser with v7 features (ethical framework included)."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sparrow SPOT Scale™ v7.0 - Dual Variant Grading System with Ethical Framework',
        epilog='Examples:\n'
               '  sparrow_grader_v7.py article.txt                    # Grade journalism (default)\n'
               '  sparrow_grader_v7.py budget.pdf --variant policy    # Grade policy with ethics (v7)\n'
               '  sparrow_grader_v7.py doc.pdf --variant journalism   # Explicit journalism\n'
    )
    
    parser.add_argument('input_file', help='Input file (text, PDF, JSON)')
    parser.add_argument('-o', '--output', help='Output filename (without extension)', default='report')
    parser.add_argument('--variant', choices=['journalism', 'policy'], default='journalism',
                        help='Evaluation variant: journalism (SPARROW SPOT) or policy (SPOT-Policy™). Default: journalism')
    parser.add_argument('--doc-type', choices=['journalistic', 'policy', 'mixed'], default='journalistic',
                        help='v2: Document type for context-aware weighting (journalism variant only)')
    parser.add_argument('--cite-analysis', action='store_true',
                        help='v3: Enable citation extraction and analysis (journalism variant only)')
    parser.add_argument('--perspective-balance', action='store_true',
                        help='v3: Analyze perspective balance (journalism variant only)')
    parser.add_argument('--expert-panel', help='v3: CSV file with expert panel grades (journalism variant only)')
    
    return parser


def main():
    """Main entry point with full PDF support."""
    parser = create_arg_parser()
    args = parser.parse_args()
    
    print(f"\n🎯 Sparrow SPOT Scale™ v7.0 - Starting grading process (with Ethical Framework)...")
    print(f"   Variant: {args.variant}")
    print(f"   Input file: {args.input_file}")
    
    # Determine file type
    is_pdf = args.input_file.lower().endswith('.pdf')
    
    # Extract text based on file type
    print(f"\n📖 Reading {'PDF' if is_pdf else 'text'} file...")
    try:
        if is_pdf:
            # Use SPARROWGrader for PDF extraction (it has the methods)
            temp_grader = SPARROWGrader()
            text = temp_grader.extract_text_from_pdf(args.input_file)
            print(f"   ✓ Extracted {len(text):,} characters from PDF")
        else:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"   ✓ Read {len(text):,} characters")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to read file: {str(e)}")
        sys.exit(1)
    
    print(f"\n📊 Analyzing with {args.variant} variant...")
    
    try:
        if args.variant == 'journalism':
            print("   Using SPARROW Scale™ (Journalism) variant")
            grader = SPARROWGrader()
            # v7: Pass PDF path for multimodal vision analysis if available (auto-activation)
            pdf_path = args.input_file if is_pdf else None
            report = grader.grade_article(text, doc_type='journalistic', quiet=False, pdf_path=pdf_path)
            
            print("\n" + "="*70)
            print("SPARROW SCALE™ GRADING REPORT")
            print("="*70)
            
            scores = report.get('sparrow_scores', {})
            print(f"\nCategory Scores:")
            for category in ['SI', 'OI', 'TP', 'AR', 'IU']:
                if category in scores:
                    data = scores[category]
                    label_info = report.get('category_grade_labels', {}).get(category, {})
                    print(f"  {category} ({report.get('grade_categories', {}).get(category, 'Unknown')}): "
                          f"{data['score']:.1f}/100 ({data['grade']}) - {label_info.get('label', '')}")
            
            if 'composite' in scores:
                comp = scores['composite']
                print(f"\n📈 Composite Score: {comp['score']}/100 - Grade: {comp['grade'][0]} ({comp['grade'][1]})")
        
        elif args.variant == 'policy':
            print("   Using SPOT-Policy™ (Policy) variant")
            grader = SPOTPolicy()
            # v6: Pass PDF path for multimodal analysis if available
            pdf_path = args.input_file if is_pdf else None
            report = grader.grade(text, pdf_path=pdf_path)
            
            print("\n" + "="*70)
            print("SPOT-POLICY™ GRADING REPORT")
            print("="*70)
            print(f"\nClassification: {report['classification']}")
            print(f"Composite Score: {report['composite_score']}/100 ({report['composite_grade']})")
            
            print(f"\nFISCAL Criteria Breakdown:")
            criteria = report['criteria']
            for criterion in ['FT', 'SB', 'ER', 'PA', 'PC']:
                if criterion in criteria:
                    data = criteria[criterion]
                    label_info = report['category_grade_labels'].get(criterion, {})
                    print(f"  {criterion}: {data['score']:.1f}/100 - {label_info.get('label', 'Unknown')}")
        
        print("\n" + "="*70)
    
    except Exception as e:
        print(f"   ❌ ERROR during grading: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Save outputs
    print(f"\n💾 Saving results...")
    try:
        # JSON output
        output_json = f"{args.output}.json"
        with open(output_json, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"   ✓ JSON: {output_json}")
        
        # Text summary
        output_txt = f"{args.output}.txt"
        with open(output_txt, 'w') as f:
            f.write(f"Sparrow SPOT Scale™ v7.0 Report (with Ethical Framework)\n")
            f.write(f"Variant: {args.variant.upper()}\n")
            f.write("="*70 + "\n\n")
            
            if args.variant == 'journalism':
                scores = report.get('sparrow_scores', {})
                for category in ['SI', 'OI', 'TP', 'AR', 'IU']:
                    if category in scores:
                        data = scores[category]
                        f.write(f"{category}: {data['score']:.1f}/100 ({data['grade']})\n")
                if 'composite' in scores:
                    comp = scores['composite']
                    f.write(f"\nComposite: {comp['score']}/100 - {comp['grade'][0]}\n")
            else:
                criteria = report['criteria']
                weights = report.get('weighting', {})
                
                # Display individual scores
                f.write("CRITERIA SCORES:\n")
                for criterion in ['FT', 'SB', 'ER', 'PA', 'PC']:
                    if criterion in criteria:
                        data = criteria[criterion]
                        f.write(f"  {criterion}: {data['score']:.1f}/100\n")
                
                # Display weighting calculation
                f.write("\n" + "="*70 + "\n")
                f.write("COMPOSITE SCORE CALCULATION:\n")
                f.write("="*70 + "\n")
                
                calculation_parts = []
                for criterion in ['FT', 'SB', 'ER', 'PA', 'PC']:
                    if criterion in criteria:
                        score = criteria[criterion]['score']
                        weight = weights.get(criterion, 0)
                        weighted = score * weight
                        calculation_parts.append(f"{criterion}({score:.1f}×{weight}={weighted:.2f})")
                
                f.write("  " + " + ".join(calculation_parts))
                f.write(f" = {report['composite_score']:.1f}/100\n")
                
                f.write(f"\nComposite Grade: {report['composite_grade']}\n")
                f.write(f"Classification: {report['classification']}\n")
            
            f.write(f"\nGenerated: {report.get('timestamp', 'N/A')}\n")
        print(f"   ✓ Text: {output_txt}")
        
        # HTML Certificate
        try:
            from certificate_generator import CertificateGenerator
            cert_gen = CertificateGenerator()
            
            # Extract document title
            doc_title = Path(args.input_file).stem
            output_html = f"{args.output}_certificate.html"
            
            if args.variant == 'policy':
                cert_gen.generate_policy_certificate(report, doc_title, output_html)
            else:
                cert_gen.generate_journalism_certificate(report, doc_title, output_html)
            
            print(f"   ✓ Certificate: {output_html}")
            
            # Plain-Language Summary (Ollama)
            try:
                output_summary = f"{args.output}_summary.txt"
                summary = cert_gen.generate_summary_with_ollama(report, args.variant, output_file=output_summary)
                if summary:
                    print(f"   ✓ Summary: {output_summary}")
            except Exception as e:
                print(f"   ⚠️  Summary generation skipped: {str(e)}")
        
        except Exception as e:
            print(f"   ⚠️  Certificate generation skipped: {str(e)}")
    
    except Exception as e:
        print(f"   ⚠️  Failed to save outputs: {str(e)}")
    
    print(f"\n✅ Grading complete!\n")


if __name__ == '__main__':
    main()

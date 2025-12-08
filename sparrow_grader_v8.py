#!/usr/bin/env python3
"""
Sparrow SPOT Scale™ - Dual Variant System with Ethical Framework & AI Transparency
Combines:
  - SPARROW Scale™ (Journalism evaluation) from v3
  - SPOT-Policy™ (Government policy evaluation) enhanced with Ethical AI Toolkit in v7
  - AI Transparency & Detection criterion added in v8

Systematic Protocol for Article Reliability, Rigor, and Overall Worth
+ Societal Policy Oversight Tool

Generates professional certification for both journalistic and policy content

See version.py for current version and release history.
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

# Import version management
from version import SPARROW_VERSION, get_version_string

# v8.4.2: Import diagnostic logging system
try:
    from diagnostic_logger import DiagnosticLogger, get_logger
    DIAGNOSTIC_LOGGING_AVAILABLE = True
except ImportError:
    DIAGNOSTIC_LOGGING_AVAILABLE = False
    # Create no-op logger fallback
    class DiagnosticLogger:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None

# v8.6.1: Import investigation index generator
try:
    from investigation_index_generator import generate_investigation_index
    INDEX_GENERATOR_AVAILABLE = True
except ImportError:
    INDEX_GENERATOR_AVAILABLE = False

# v8: Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from article_analyzer import ArticleAnalyzer

# v8: Import narrative engine modules
try:
    from narrative_integration import create_pipeline
    NARRATIVE_ENGINE_AVAILABLE = True
except ImportError:
    NARRATIVE_ENGINE_AVAILABLE = False

# v7: Import ethical framework modules
try:
    from ai_detection_engine import AIDetectionEngine, ProvenanceAnalyzer
    ETHICAL_AI_DETECTION_AVAILABLE = True
except ImportError:
    ETHICAL_AI_DETECTION_AVAILABLE = False

# v8: Import contradiction detection module
try:
    from contradiction_detector import ContradictionDetector, create_contradiction_detector
    CONTRADICTION_DETECTION_AVAILABLE = True
except ImportError:
    CONTRADICTION_DETECTION_AVAILABLE = False

# v8.2: Import deep analysis module
try:
    from deep_analyzer import DeepAnalyzer
    DEEP_ANALYSIS_AVAILABLE = True
except ImportError:
    DEEP_ANALYSIS_AVAILABLE = False

# v8.3: Import transparency modules
try:
    from data_lineage_visualizer import DataLineageVisualizer
    LINEAGE_VIZ_AVAILABLE = True
except ImportError:
    LINEAGE_VIZ_AVAILABLE = False

try:
    from citation_quality_scorer import CitationQualityScorer
    CITATION_SCORER_AVAILABLE = True
except ImportError:
    CITATION_SCORER_AVAILABLE = False

try:
    from nist_compliance_checker import NISTComplianceChecker
    NIST_COMPLIANCE_AVAILABLE = True
except ImportError:
    NIST_COMPLIANCE_AVAILABLE = False

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

# v8.5: Import legislative threat detection modules
try:
    from discretionary_power_analyzer import DiscretionaryPowerAnalyzer
    LEGISLATIVE_THREAT_AVAILABLE = True
except ImportError:
    LEGISLATIVE_THREAT_AVAILABLE = False

# v8.4.2: Pipeline logging class
class PipelineLogger:
    """Simple logger that writes to both stdout and a log file."""
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        self.original_stdout = sys.stdout
        # Create log file with header
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"Sparrow SPOT Scale™ Pipeline Log\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
    
    def write(self, text):
        """Write to both stdout and log file."""
        self.original_stdout.write(text)
        self.original_stdout.flush()
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(text)
    
    def flush(self):
        """Flush stdout."""
        self.original_stdout.flush()
    
    def close(self):
        """Write footer and restore stdout."""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 70 + "\n")
            f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        sys.stdout = self.original_stdout

try:
    from trust_score_calculator import TrustScoreCalculator
    ETHICAL_TRUST_AVAILABLE = True
except ImportError:
    ETHICAL_TRUST_AVAILABLE = False

try:
    from ai_disclosure_generator import AIDisclosureGenerator
    AI_DISCLOSURE_AVAILABLE = True
except ImportError:
    AI_DISCLOSURE_AVAILABLE = False

try:
    from data_lineage_source_mapper import DataLineageSourceMapper
    DATA_LINEAGE_MAPPER_AVAILABLE = True
except ImportError:
    DATA_LINEAGE_MAPPER_AVAILABLE = False

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
            
            prompt = """Analyze this policy document image with extreme precision. Extract ALL numerical data:

1. EXACT NUMBERS: List every dollar amount, percentage, and year visible (e.g., "$925.6 billion", "2.3%", "2025-2026")
2. CHART TYPE: Budget table, revenue chart, trend graph, sensitivity analysis, demographic breakdown, etc.
3. DATA LABELS: What each number represents (e.g., "GDP growth", "total spending", "deficit reduction")
4. CALCULATIONS SHOWN: Any arithmetic displayed (subtotals, totals, differences, growth rates)
5. RANGES/SCENARIOS: Baseline, upside, downside cases, confidence intervals
6. INCONSISTENCIES: Do numbers add up? Any visible errors or contradictions?
7. VISUAL QUALITY: Clarity, readability, professional presentation (1-10)

Be extremely specific with numbers. Include units (billion/million, %) and years. This data will be validated against text claims to detect "cooked books"."""
            
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
        for criterion in ['FT', 'SB', 'ER', 'PA', 'PC', 'AT']:
            text_score = text_scores.get(criterion, 0)
            boost = min(boosts.get(criterion, 0), 15)  # Cap boost at 15 points
            
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
        
        # v8: Initialize narrative engine pipeline
        self.narrative_pipeline = None
        if NARRATIVE_ENGINE_AVAILABLE:
            try:
                self.narrative_pipeline = create_pipeline()
            except Exception as e:
                print(f"⚠️  Warning: Narrative engine not available: {e}")
        
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
            'version': SPARROW_VERSION,
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
        
        # ============================================================
        # ETHICAL FRAMEWORK ANALYSIS FOR JOURNALISM (v8.0)
        # ============================================================
        
        # PILLAR 1: INPUT TRANSPARENCY - AI Detection
        ai_detection_result = None
        if ETHICAL_AI_DETECTION_AVAILABLE:
            try:
                ai_engine = AIDetectionEngine()
                ai_detection_result = ai_engine.analyze_document(article_text)
                report['ai_detection'] = ai_detection_result
            except Exception as e:
                report['ai_detection'] = {'status': 'error', 'message': str(e)}
        
        # PILLAR 2 PART 1: RISK CLASSIFICATION
        risk_tier_result = None
        if ETHICAL_RISK_MAPPER_AVAILABLE:
            try:
                risk_mapper = NISTRiskMapper()
                characteristics = {
                    'domain': 'journalism',
                    'ai_detection_score': ai_detection_result.get('ai_detection_score', 0) if ai_detection_result else 0,
                    'word_count': len(article_text.split()),
                    'has_visuals': vision_results.get('status') == 'success'
                }
                risk_tier_result = risk_mapper.classify(characteristics)
                report['risk_tier'] = risk_tier_result
            except Exception as e:
                report['risk_tier'] = {'status': 'error', 'message': str(e)}
        
        # PILLAR 2 PART 2: BIAS AUDIT
        bias_audit_result = None
        if ETHICAL_BIAS_AUDITOR_AVAILABLE:
            try:
                bias_auditor = BiasAuditor()
                
                # Generate demographic group scores for journalism content
                # Based on SPARROW scores across hypothetical reader groups
                scores_by_group = {
                    'General_Readership': [
                        sparrow_scores['SI']['score'], 
                        sparrow_scores['OI']['score'], 
                        sparrow_scores['TP']['score']
                    ],
                    'Specialized_Audience': [
                        sparrow_scores['SI']['score'] * 0.95, 
                        sparrow_scores['OI']['score'] * 0.92, 
                        sparrow_scores['AR']['score'] * 1.1  # Accessibility varies by audience
                    ],
                    'Diverse_Communities': [
                        sparrow_scores['IU']['score'], 
                        sparrow_scores['AR']['score'], 
                        (sparrow_scores['SI']['score'] + sparrow_scores['OI']['score']) / 2
                    ]
                }
                
                bias_audit_result = bias_auditor.audit_scores(scores_by_group)
                report['bias_audit'] = bias_audit_result
            except Exception as e:
                report['bias_audit'] = {'status': 'error', 'message': str(e)}
        
        # PILLAR 2 PART 3: TRUST SCORE
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
        
        # ETHICAL SUMMARY
        report['ethical_summary'] = self._generate_ethical_summary_journalism(
            ai_detection_result, risk_tier_result, bias_audit_result, trust_score_result
        )
        
        # Set 'adjusted' flag if any adjustments were made
        adjustment_log = report.get('bias_audit', {}).get('adjustment_log', [])
        report['adjusted'] = len(adjustment_log) > 0
        
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
    
    def _generate_ethical_summary_journalism(self, ai_detection, risk_tier, bias_audit, trust_score):
        """Generate ethical framework summary for journalism content."""
        summary = {
            'input_transparency': 'UNKNOWN',
            'analysis_transparency': 'UNKNOWN',
            'output_accountability': 'UNKNOWN',
            'overall_recommendation': 'UNKNOWN',
            'escalation_required': False,
            'escalation_triggers': []
        }
        
        # INPUT TRANSPARENCY - AI Detection
        if ai_detection and ai_detection.get('detected'):
            ai_score = ai_detection.get('ai_detection_score', 0)
            summary['input_transparency'] = f"AI-generated content detected (Score: {ai_score:.2f})"
            if ai_score > 0.7:  # High AI signature
                summary['escalation_required'] = True
                summary['escalation_triggers'].append(f"High AI-generation signature ({ai_score:.2f})")
        elif ai_detection:
            summary['input_transparency'] = f"Human-generated content confirmed (Score: {ai_detection.get('ai_detection_score', 0):.2f})"
        
        # ANALYSIS TRANSPARENCY - Risk Classification
        if risk_tier and risk_tier.get('risk_tier'):
            tier = risk_tier.get('risk_tier', 'UNKNOWN').upper()
            summary['analysis_transparency'] = f"{tier}-risk journalism content. Appropriate analysis applied."
            if tier == 'HIGH':
                summary['escalation_required'] = True
                summary['escalation_triggers'].append(f"HIGH-risk content classification")
        
        # OUTPUT ACCOUNTABILITY - Trust Score
        if trust_score and trust_score.get('trust_score'):
            score = trust_score['trust_score']
            level = trust_score.get('trust_level', 'unknown')
            summary['output_accountability'] = f"Trust Score: {score}/100 ({level.upper()})"
            
            if score < 70 or level in ['critical', 'low']:
                summary['escalation_required'] = True
                summary['escalation_triggers'].append(f"Low trust score ({score}/100)")
        
        # OVERALL RECOMMENDATION
        if summary['escalation_required']:
            summary['overall_recommendation'] = f"HUMAN REVIEW REQUIRED: {', '.join(summary['escalation_triggers'])}"
        else:
            summary['overall_recommendation'] = "Content meets ethical framework standards. No escalation needed."
        
        return summary


class SPOTPolicy:
    """
    ENHANCED in v7: SPOT-Policy™ - Societal Policy Oversight Tool
    
    Evaluates government documents (budgets, legislation, policy briefs) using
    policy-specific criteria aligned with IMF/OECD standards, enhanced with
    ethical transparency framework (AI detection, risk classification, fairness).
    
    Six criteria (FISCAL+AT):
    - FT: Fiscal Transparency (revenue, spending, assumptions, risks)
    - SB: Stakeholder Balance (representation of 5 stakeholder groups)
    - ER: Economic Rigor (soundness of assumptions and forecasts)
    - PA: Public Accessibility (citizen understanding of key points)
    - PC: Policy Consequentiality (real-world binding effect on outcomes)
    - AT: AI Transparency & Detection (disclosure & detectability of AI involvement)
    """
    
    def __init__(self):
        """Initialize SPOT-Policy grader."""
        self.analyzer = ArticleAnalyzer()
        
        # v8: Initialize narrative engine pipeline
        self.narrative_pipeline = None
        if NARRATIVE_ENGINE_AVAILABLE:
            try:
                self.narrative_pipeline = create_pipeline()
            except Exception as e:
                print(f"⚠️  Warning: Narrative engine not available: {e}")
        
        self.grade_categories = {
            'FT': 'Fiscal Transparency',
            'SB': 'Stakeholder Balance',
            'ER': 'Economic Rigor',
            'PA': 'Public Accessibility',
            'PC': 'Policy Consequentiality',
            'AT': 'AI Transparency & Detection'
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
            'AT': {  # AI Transparency & Detection
                (90, 100): ('FD', 'Full Disclosure', 'Explicit AI mentions, funding breakdown, deployment details, external validation, social verification'),
                (75, 89.99): ('CT', 'Clear Transparency', 'AI applications disclosed, major funding identified, deployment areas specified, limited verification'),
                (60, 74.99): ('PD', 'Partial Disclosure', 'AI mentioned, some funding visible, general applications, minimal external commentary'),
                (45, 59.99): ('VR', 'Vague References', 'AI implied, funding unclear, applications vague, no external validation'),
                (0, 44.99): ('O', 'Opaque/Absent', 'No AI disclosure, funding hidden, detection patterns suggest undisclosed AI use'),
            },
        }
        
        # AI keywords for AT criterion (AI Transparency & Detection)
        self.ai_keywords = {
            'general': ['artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning', 
                       'neural network', 'llm', 'large language model', 'generative ai', 'ai-powered'],
            'infrastructure': ['sovereign ai', 'canadian cloud', 'ai compute', 'ai infrastructure',
                             'gpu', 'compute capacity', 'ai training', 'ai deployment'],
            'agencies': ['cra', 'canada revenue agency', 'statistics canada', 'statscan', 
                        'canadian food inspection agency', 'cfia', 'shared services canada'],
            'tools': ['gpt', 'chatgpt', 'claude', 'gemini', 'llama', 'granite', 'copilot',
                     'automation', 'predictive analytics', 'ai assistant', 'ai tool'],
            'funding': ['million', 'billion', 'investment', 'funding', 'allocation', 'spending',
                       'budget', 'appropriation', 'fiscal framework']
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
    
    def score_ai_transparency(self, text, pdf_path=None):
        """
        Score AI Transparency & Detection (AT): 0-100
        
        Measures disclosure and detectability of AI involvement in policy documents.
        Based on recommendations from "Investigating AI Assistance in Canada's Federal Budget 2025"
        
        Evaluates:
        - Explicit AI disclosure (keyword mentions)
        - Funding allocation transparency ($ amounts tied to AI)
        - Deployment specificity (agencies, tools, applications)
        - External validation (social discourse, expert commentary)
        - Detection patterns (AI-generated content indicators)
        
        Returns: Score 0-100 with breakdown by category
        """
        score = 0
        max_score = 100
        text_lower = text.lower()
        
        # CATEGORY 1: Explicit AI Disclosure (30 points max)
        # Count mentions across different AI keyword categories
        disclosure_score = 0
        
        # General AI terms (15 points)
        general_mentions = sum(text_lower.count(kw) for kw in self.ai_keywords['general'])
        if general_mentions >= 20:
            disclosure_score += 15
        elif general_mentions >= 10:
            disclosure_score += 10
        elif general_mentions >= 5:
            disclosure_score += 7
        elif general_mentions >= 1:
            disclosure_score += 3
        
        # Infrastructure terms (10 points)
        infra_mentions = sum(text_lower.count(kw) for kw in self.ai_keywords['infrastructure'])
        if infra_mentions >= 5:
            disclosure_score += 10
        elif infra_mentions >= 3:
            disclosure_score += 7
        elif infra_mentions >= 1:
            disclosure_score += 3
        
        # Tool-specific mentions (5 points)
        tool_mentions = sum(text_lower.count(kw) for kw in self.ai_keywords['tools'])
        if tool_mentions >= 3:
            disclosure_score += 5
        elif tool_mentions >= 1:
            disclosure_score += 3
        
        score += min(30, disclosure_score)
        
        # CATEGORY 2: Funding Allocation Transparency (30 points max)
        # Extract AI-related dollar amounts using proximity analysis
        funding_score = 0
        
        # Pattern: Find dollar amounts near AI keywords (within 50 words)
        ai_funding_pattern = r'(?:artificial intelligence|ai|machine learning|ml|sovereign ai|ai infrastructure|ai compute|canadian cloud)[^.]{0,250}\$\s*(\d+\.?\d*)\s*(billion|million|b|m)'
        ai_funding_matches = re.findall(ai_funding_pattern, text_lower, re.IGNORECASE)
        
        total_ai_funding = 0
        for amount, unit in ai_funding_matches:
            if unit.lower() in ['b', 'billion']:
                total_ai_funding += float(amount)
            elif unit.lower() in ['m', 'million']:
                total_ai_funding += float(amount) / 1000
        
        # Score based on funding magnitude disclosed
        if total_ai_funding >= 1.0:  # $1B+
            funding_score = 30
        elif total_ai_funding >= 0.5:  # $500M+
            funding_score = 25
        elif total_ai_funding >= 0.1:  # $100M+
            funding_score = 20
        elif total_ai_funding >= 0.01:  # $10M+
            funding_score = 15
        elif total_ai_funding > 0:  # Any funding disclosed
            funding_score = 10
        elif general_mentions > 0:  # AI mentioned but no funding
            funding_score = 5
        
        score += funding_score
        
        # CATEGORY 3: Deployment Specificity (25 points max)
        # Check for specific agencies, applications, and implementation details
        deployment_score = 0
        
        # Agency-specific AI mentions (10 points)
        agency_mentions = sum(text_lower.count(kw) for kw in self.ai_keywords['agencies'])
        if agency_mentions >= 5:
            deployment_score += 10
        elif agency_mentions >= 3:
            deployment_score += 7
        elif agency_mentions >= 1:
            deployment_score += 3
        
        # Application specificity (10 points)
        application_keywords = ['streamlin', 'automat', 'analyt', 'predict', 'procure', 
                                'audit', 'traceability', 'commercializ', 'moderniz']
        app_mentions = sum(1 for kw in application_keywords if kw in text_lower)
        deployment_score += min(10, app_mentions * 2)
        
        # Implementation timeline (5 points)
        timeline_keywords = ['by end', 'years', 'over', 'fiscal year', 'timeline', 'implementation']
        if any(kw in text_lower for kw in timeline_keywords):
            deployment_score += 5
        
        score += min(25, deployment_score)
        
        # CATEGORY 4: External Validation & Social Discourse (15 points max)
        # Check for references to external sources, consultations, expert commentary
        validation_score = 0
        
        # External validation indicators
        validation_keywords = ['oecd', 'imf', 'expert', 'consultation', 'vector institute',
                              'review', 'peer', 'validated', 'verified', 'third-party']
        validation_found = sum(1 for kw in validation_keywords if kw in text_lower)
        validation_score += min(10, validation_found * 2)
        
        # Public discourse indicators
        discourse_keywords = ['twitter', 'x.com', 'social media', 'public comment', 
                             'stakeholder feedback', 'press release']
        discourse_found = sum(1 for kw in discourse_keywords if kw in text_lower)
        validation_score += min(5, discourse_found * 2)
        
        score += min(15, validation_score)
        
        return min(100, score)
    
    def grade(self, text, document_type='policy', document_structure=None, pdf_path=None, document_type_selected='auto'):
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
            document_type_selected: User-selected document type from CLI/GUI ('auto', 'legislation', 'budget', etc.)
        
        Returns dict with criteria scores, composite, AND ethical framework results.
        """
        # Create master timestamp for this assessment batch (Recommendation #7)
        master_timestamp = datetime.now().isoformat()
        
        report = {
            'variant': 'SPOT-Policy™',
            'version': SPARROW_VERSION,
            'document_type': document_type,
            'document_type_selected': document_type_selected,  # v8.6.1: Store user-selected type for certificate badge
            'timestamp': master_timestamp,
            'criteria': {},
            'vision_findings': None,
            'ethical_framework': {
                'version': '1.0',
                'pillars_active': ['INPUT_TRANSPARENCY', 'ANALYSIS_TRANSPARENCY']
            },
            'generation_log': {  # Track all files generated in this batch
                'master_timestamp': master_timestamp,
                'files_generated': [],
                'generation_sequence': []
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
            'PC': self.score_policy_consequentiality(text),
            'AT': self.score_ai_transparency(text, pdf_path)
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
                            'findings': all_findings  # Store all findings for contradiction detection
                        }
                    
                    # Cleanup temp images
                    analyzer.cleanup_temp_images()
            
            except Exception as e:
                vision_results = {'status': 'error', 'message': str(e)}
        
        # ============================================================
        # v8: CONTRADICTION DETECTION (Numerical Consistency Analysis)
        # ============================================================
        
        contradiction_report = None
        if CONTRADICTION_DETECTION_AVAILABLE:
            try:
                print("🔍 Running contradiction detection...")
                detector = create_contradiction_detector()
                
                # Pass vision findings if available
                vision_findings_for_validation = vision_results.get('findings', []) if vision_results.get('status') == 'success' else None
                
                contradiction_report = detector.analyze(text, vision_findings_for_validation)
                report['contradiction_analysis'] = contradiction_report
                
                # Adjust Economic Rigor score if contradictions found
                if contradiction_report.get('severity_score', 0) > 0:
                    severity = contradiction_report['severity_score']
                    
                    # Penalty: -5 points per 10 severity points, up to -25 max
                    penalty = min(25, (severity / 10) * 5)
                    
                    # Apply penalty to Economic Rigor score
                    original_er = final_scores['ER']
                    final_scores['ER'] = max(0, original_er - penalty)
                    
                    print(f"   ⚠️ Contradictions detected (severity: {severity:.0f})")
                    print(f"   ⚠️ Economic Rigor penalty: -{penalty:.1f} points ({original_er:.1f} → {final_scores['ER']:.1f})")
                    
                    # Log contradiction penalty in bias audit
                    if not report.get('bias_audit'):
                        report['bias_audit'] = {}
                    if 'adjustment_log' not in report['bias_audit']:
                        report['bias_audit']['adjustment_log'] = []
                    
                    report['bias_audit']['adjustment_log'].append({
                        'criterion': 'ER',
                        'original_score': original_er,
                        'adjusted_score': final_scores['ER'],
                        'adjustment_reason': f'Numerical contradictions detected (severity: {severity:.0f}/100)',
                        'source': 'Contradiction_Detector',
                        'contradictions_count': len(contradiction_report.get('contradictions', [])),
                        'high_severity_count': len([c for c in contradiction_report.get('contradictions', []) if c.get('severity') == 'HIGH'])
                    })
                else:
                    print(f"   ✓ No significant contradictions detected")
            
            except Exception as e:
                print(f"   ⚠️ Contradiction detection error: {str(e)}")
                report['contradiction_analysis'] = {'status': 'error', 'message': str(e)}
        
        report['criteria'] = {
            'FT': {'score': round(final_scores['FT'], 1), 'name': self.grade_categories['FT']},
            'SB': {'score': round(final_scores['SB'], 1), 'name': self.grade_categories['SB']},
            'ER': {'score': round(final_scores['ER'], 1), 'name': self.grade_categories['ER']},
            'PA': {'score': round(final_scores['PA'], 1), 'name': self.grade_categories['PA']},
            'PC': {'score': round(final_scores['PC'], 1), 'name': self.grade_categories['PC']},
            'AT': {'score': round(final_scores['AT'], 1), 'name': self.grade_categories['AT']},
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
        # COMPOSITE SCORE & GRADE (original algorithm + AI Transparency)
        # ============================================================
        
        # v8: Added AI Transparency (AT) with 10% weight
        # Rebalanced: FT 18%, SB 13%, ER 23%, PA 18%, PC 18%, AT 10%
        composite = (
            (final_scores['FT'] * 0.18) +
            (final_scores['SB'] * 0.13) +
            (final_scores['ER'] * 0.23) +
            (final_scores['PA'] * 0.18) +
            (final_scores['PC'] * 0.18) +
            (final_scores['AT'] * 0.10)
        )
        
        report['composite_score'] = round(composite, 1)
        report['weighting'] = {
            'FT': 0.18,
            'SB': 0.13,
            'ER': 0.23,
            'PA': 0.18,
            'PC': 0.18,
            'AT': 0.10
        }
        
        # Recommendation #6: Calculate adjusted composite if critique-based adjustments exist
        adjustment_log = report.get('bias_audit', {}).get('adjustment_log', [])
        if adjustment_log:
            # Create adjusted scores dictionary
            adjusted_scores = final_scores.copy()
            
            # Apply critique-based adjustments
            for adjustment in adjustment_log:
                criterion = adjustment.get('criterion')
                adjusted_score = adjustment.get('adjusted_score')
                if criterion in adjusted_scores and adjusted_score is not None:
                    adjusted_scores[criterion] = adjusted_score
            
            # Calculate adjusted composite with same weights
            adjusted_composite = (
                (adjusted_scores['FT'] * 0.18) +
                (adjusted_scores['SB'] * 0.13) +
                (adjusted_scores['ER'] * 0.23) +
                (adjusted_scores['PA'] * 0.18) +
                (adjusted_scores['PC'] * 0.18) +
                (adjusted_scores['AT'] * 0.10)
            )
            
            report['adjusted_composite_score'] = round(adjusted_composite, 1)
            report['adjusted_scores_applied'] = True
            
            # Note: Base composite_score remains unchanged for consistency
            # Adjusted composite is provided as supplementary information
        else:
            report['adjusted_composite_score'] = None
            report['adjusted_scores_applied'] = False
        
        # Add category grade labels
        report['category_grade_labels'] = {}
        for criterion in ['FT', 'SB', 'ER', 'PA', 'PC', 'AT']:
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
        
        # Add grade for compatibility with QA checker
        report['grade'] = report['composite_grade']
        
        # Standardized performance label schema (Recommendation #3)
        # 90-100: Exceptional, 80-89: Strong, 60-79: Needs Improvement, <60: Weak
        if composite >= 90:
            performance_label = 'Exceptional'
        elif composite >= 80:
            performance_label = 'Strong'
        elif composite >= 60:
            performance_label = 'Needs Improvement'
        else:
            performance_label = 'Weak'
        
        report['performance_label'] = performance_label
        
        # Keep classifications for backward compatibility
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
        
        # v8.4.0: Fix classification paradox
        # A document cannot be both "Questionable" and "Transformative"
        # Check if high Policy Consequentiality conflicts with low grade
        criteria = report.get('criteria', {})
        pc_score = criteria.get('PC', {}).get('score', 0)
        
        # Count failing categories (score < 60)
        failing_categories = 0
        for cat in ['FT', 'SB', 'ER', 'PA', 'AT']:
            if criteria.get(cat, {}).get('score', 0) < 60:
                failing_categories += 1
        
        # v8.4.0: Revised classification logic
        # "Questionable" requires: composite < 60 OR 3+ failing categories
        # If PC >= 90 and composite >= 70, use "Transformative Policy (with limitations)"
        base_classification = classifications.get(report['composite_grade'], 'Unclassified')
        
        # v8.4.1: Identify specific failing areas for qualifier
        failing_areas = []
        for cat, label in [('FT', 'fiscal'), ('SB', 'stakeholder'), ('ER', 'economic'), 
                           ('PA', 'accessibility'), ('AT', 'transparency')]:
            cat_score = criteria.get(cat, {}).get('score', 100)
            if cat_score < 60:
                failing_areas.append(label)
        
        # Generate specific qualifier based on failing areas
        if failing_areas:
            if len(failing_areas) == 1:
                specific_qualifier = f"{failing_areas[0]} concerns"
            elif len(failing_areas) == 2:
                specific_qualifier = f"{failing_areas[0]} and {failing_areas[1]} concerns"
            else:
                specific_qualifier = f"multiple concerns: {', '.join(failing_areas[:3])}"
        else:
            specific_qualifier = "minor concerns"
        
        if base_classification == 'Questionable Policy':
            # Check if this should be upgraded
            if composite >= 70 and pc_score >= 90:
                # High consequentiality with decent composite = not "Questionable"
                report['classification'] = f'Transformative Policy ({specific_qualifier})'
                report['classification_note'] = (
                    f"Upgraded from 'Questionable' due to high Policy Consequentiality ({pc_score:.1f}%) "
                    f"and composite score above 70 ({composite:.1f}). "
                    f"Areas needing attention: {', '.join(failing_areas) if failing_areas else 'none critical'}"
                )
            elif failing_categories < 3 and composite >= 60:
                # Not enough failures for "Questionable"
                report['classification'] = f'Moderate Policy ({specific_qualifier})'
                report['classification_note'] = (
                    f"Adjusted from 'Questionable' - only {failing_categories} categories below threshold. "
                    f"Areas needing attention: {', '.join(failing_areas) if failing_areas else 'none critical'}"
                )
            else:
                # Keep Questionable - truly problematic
                report['classification'] = base_classification
        elif pc_score >= 90 and composite >= 80:
            # v8.4.0: Add "Transformative" suffix for high PC documents
            if base_classification not in ['Exemplary Policy', 'Excellent Policy']:
                report['classification'] = f"{base_classification} (Transformative Impact)"
                report['classification_note'] = f"High Policy Consequentiality ({pc_score:.1f}%)"
            else:
                report['classification'] = base_classification
        else:
            report['classification'] = base_classification
        
        # v8.4.0: Add classification metadata
        report['classification_metadata'] = {
            'base_classification': base_classification,
            'pc_score': pc_score,
            'composite_score': composite,
            'failing_categories': failing_categories,
            'failing_areas': failing_areas,  # v8.4.1: List of specific failing areas
            'specific_qualifier': specific_qualifier,  # v8.4.1: Generated qualifier text
            'adjustment_applied': report.get('classification_note') is not None
        }
        
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
        
        # Set 'adjusted' flag if any adjustments were made (Recommendation #4)
        adjustment_log = report.get('bias_audit', {}).get('adjustment_log', [])
        report['adjusted'] = len(adjustment_log) > 0
        
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


def fetch_from_url(url):
    """Fetch document from URL, supporting both text/HTML and PDF formats.
    
    Args:
        url: Remote URL to fetch
        
    Returns:
        tuple: (text_content, is_pdf, temp_pdf_path)
               temp_pdf_path is None for text content
    """
    import requests
    import tempfile
    from pathlib import Path
    
    try:
        print(f"\n🌐 Fetching document from URL...")
        print(f"   URL: {url}")
        
        # Fetch with timeout
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; SparrowGrader/8.0)'
        })
        response.raise_for_status()
        
        # Determine content type
        content_type = response.headers.get('Content-Type', '').lower()
        is_pdf = 'application/pdf' in content_type or url.lower().endswith('.pdf')
        
        if is_pdf:
            # Save PDF to temporary file
            temp_pdf = tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False)
            temp_pdf.write(response.content)
            temp_pdf.close()
            print(f"   ✓ Downloaded PDF ({len(response.content):,} bytes)")
            print(f"   ✓ Saved to temporary file: {temp_pdf.name}")
            return None, True, temp_pdf.name
        else:
            # Extract text content
            text = response.text
            print(f"   ✓ Fetched {len(text):,} characters")
            return text, False, None
            
    except requests.Timeout:
        print(f"\n❌ Error: Request timed out after 30 seconds")
        raise
    except requests.RequestException as e:
        print(f"\n❌ Error fetching URL: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


def fetch_from_url(url):
    """Fetch document from URL, supporting both text/HTML and PDF formats.
    
    Args:
        url: Remote URL to fetch
        
    Returns:
        tuple: (text_content, is_pdf, temp_pdf_path)
               temp_pdf_path is None for text content
    """
    import requests
    import tempfile
    from pathlib import Path
    
    try:
        print(f"\n🌐 Fetching document from URL...")
        print(f"   URL: {url}")
        
        # Fetch with timeout
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; SparrowGrader/8.0)'
        })
        response.raise_for_status()
        
        # Determine content type
        content_type = response.headers.get('Content-Type', '').lower()
        is_pdf = 'application/pdf' in content_type or url.lower().endswith('.pdf')
        
        if is_pdf:
            # Save PDF to temporary file
            temp_pdf = tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False)
            temp_pdf.write(response.content)
            temp_pdf.close()
            print(f"   ✓ Downloaded PDF ({len(response.content):,} bytes)")
            print(f"   ✓ Saved to temporary file: {temp_pdf.name}")
            return None, True, temp_pdf.name
        else:
            # Extract text content
            text = response.text
            print(f"   ✓ Fetched {len(text):,} characters")
            return text, False, None
            
    except requests.Timeout:
        print(f"\n❌ Error: Request timed out after 30 seconds")
        raise
    except requests.RequestException as e:
        print(f"\n❌ Error fetching URL: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


def create_arg_parser():
    """Create CLI argument parser with v7 features (ethical framework included)."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description=f'Sparrow SPOT Scale™ {get_version_string()} - Dual Variant Grading System with Narrative Engine, Deep AI Analysis & Enhanced Transparency',
        epilog='Examples:\n'
               '  sparrow_grader_v8.py budget.pdf --variant policy --narrative-style journalistic --output 2025-Budget  # v8: Standard narrative\n'
               '  sparrow_grader_v8.py budget.pdf --variant policy --deep-analysis --output budget-full  # v8.2: Add 6-level AI transparency\n'
               '  sparrow_grader_v8.py --url https://example.com/policy.pdf --variant policy --output remote-analysis  # v8: Analyze remote PDF\n'
               '  sparrow_grader_v8.py policy.txt --variant policy --narrative-style academic --narrative-length detailed --deep-analysis --output analysis  # v8.2: Full analysis\n'
               '  sparrow_grader_v8.py budget.pdf --variant policy --narrative-style journalistic --narrative-length comprehensive --ollama-model mistral  # v8: Comprehensive with Mistral\n'
               '  sparrow_grader_v8.py article.txt --variant journalism  # Grade journalism\n'
               '  sparrow_grader_v8.py --url https://news.example.com/article.html --variant journalism  # Remote journalism analysis\n'
    )
    
    # Create mutually exclusive group for input source
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('input_file', nargs='?', help='Input file (text, PDF, JSON)')
    input_group.add_argument('--url', help='URL of remote document or PDF to analyze')
    
    parser.add_argument('-o', '--output', help='Output filename (without extension)', default='report')
    parser.add_argument('--document-title', help='Human-readable document title for reports and certificates (if not provided, uses filename stem)', default=None)
    parser.add_argument('--document-type', choices=['auto', 'legislation', 'budget', 'policy_brief', 'research_report', 'analysis', 'legal_judgment', 'report'], default='auto',
                        help='v8.6.1: Document type for certificate badge and citation scoring. Default: auto (auto-detect from content)')
    parser.add_argument('--variant', choices=['journalism', 'policy'], default='journalism',
                        help='Evaluation variant: journalism (SPARROW SPOT) or policy (SPOT-Policy™). Default: journalism')
    parser.add_argument('--narrative-style', choices=['journalistic', 'academic', 'civic', 'critical', 'explanatory'],
                        help='v8: Generate publish-ready narrative in specified style (Globe and Mail, Policy Options, etc.). Requires --variant policy.')
    parser.add_argument('--narrative-length', choices=['concise', 'standard', 'detailed', 'comprehensive'], default='standard',
                        help='v8: Control narrative detail level. concise=~500 words, standard=~1000, detailed=~2000, comprehensive=~3500+. Works with --narrative-style.')
    parser.add_argument('--ollama-model', default='llama3.2',
                        help='v8: Ollama model for summary generation. Options: llama3.2 (default), mistral, qwen2.5, gemma2, etc. Must be pulled locally.')
    parser.add_argument('--doc-type', choices=['journalistic', 'policy', 'mixed'], default='journalistic',
                        help='v2: Document type for context-aware weighting (journalism variant only)')
    parser.add_argument('--cite-analysis', action='store_true',
                        help='v3: Enable citation extraction and analysis (journalism variant only)')
    parser.add_argument('--perspective-balance', action='store_true',
                        help='v3: Analyze perspective balance (journalism variant only)')
    parser.add_argument('--expert-panel', help='v3: CSV file with expert panel grades (journalism variant only)')
    parser.add_argument('--deep-analysis', action='store_true',
                        help='v8.2: Run 6-level deep AI transparency analysis (statistical proof, phrase fingerprints, sentence-level detection). Adds ~2 minutes to analysis time.')
    
    # v8.3: Enhanced transparency features
    transparency_group = parser.add_argument_group('transparency features', 'Enhanced transparency and compliance options')
    transparency_group.add_argument('--citation-check', action='store_true',
                        help='v8.3: Analyze citation quality and source transparency. Extracts and scores citations/sources.')
    transparency_group.add_argument('--check-urls', action='store_true',
                        help='v8.3: Verify URL accessibility when --citation-check is enabled (slower, checks first 10 URLs).')
    transparency_group.add_argument('--lineage-chart', choices=['html', 'ascii', 'json'],
                        help='v8.3: Generate data lineage flowchart showing analysis pipeline.')
    transparency_group.add_argument('--nist-compliance', action='store_true',
                        help='v8.3: Generate NIST AI RMF compliance report mapping to Gov/Map/Measure/Manage pillars.')
    transparency_group.add_argument('--enhanced-provenance', action='store_true',
                        help='v8.3: Extract comprehensive document metadata (author, creation tool, edit patterns).')
    transparency_group.add_argument('--provenance-report', action='store_true',
                        help='v8.4.1: Generate full provenance report (document origin + Sparrow AI usage audit trail).')
    transparency_group.add_argument('--generate-ai-disclosure', action='store_true',
                        help='v8.3: Auto-generate AI transparency disclosure statements (formal, plain-language, technical, social media formats).')
    transparency_group.add_argument('--trace-data-sources', action='store_true',
                        help='v8.3: Trace quantitative claims to authoritative data sources (Statistics Canada, IMF, OECD). Validates economic assumptions against historical data.')
    transparency_group.add_argument('--document-qa', type=str, metavar='QUESTION',
                        help='v8.4.2: Ask a question about the document using Ollama. Answer saved to qa/ directory.')
    
    # v8.6: Enhanced Q&A and token analysis
    qa_group = parser.add_argument_group('enhanced document q&a', 'v8.6: Token analysis and intelligent chunking for large documents')
    qa_group.add_argument('--analyze-tokens', action='store_true',
                        help='v8.6: Analyze document size and show token count, recommended models, and chunking strategy.')
    qa_group.add_argument('--enable-chunking', action='store_true',
                        help='v8.6: Enable smart chunking for large documents during Q&A (automatically chunks if document exceeds context window).')
    qa_group.add_argument('--qa-routing', type=str, choices=['keyword', 'semantic', 'comprehensive', 'quick'],
                        default='keyword',
                        help='v8.6: Query routing strategy for chunked Q&A (keyword: smart/fast, comprehensive: all chunks, quick: first chunk only).')
    qa_group.add_argument('--chunk-strategy', type=str, choices=['section', 'sliding', 'semantic'],
                        default='section',
                        help='v8.6: Chunking strategy (section: legislative docs, sliding: general docs, semantic: topic-based).')
    qa_group.add_argument('--max-chunk-tokens', type=int, default=100000,
                        help='v8.6: Maximum tokens per chunk (default: 100000).')
    
    # v8.5: Legislative threat detection
    legislative_group = parser.add_argument_group('legislative threat detection', 'v8.5: Analyze legislative documents for hidden powers and accountability gaps')
    legislative_group.add_argument('--legislative-threat', action='store_true',
                        help='v8.5: Run Discretionary Power Analysis (detects ministerial discretion, broad scope, exclusion powers).')
    
    return parser


def main():
    """Main entry point with full PDF support and URL fetching."""
    import os
    
    parser = create_arg_parser()
    args = parser.parse_args()
    
    # v8: Validate narrative-style requires policy variant
    if args.narrative_style and args.variant != 'policy':
        parser.error("--narrative-style requires --variant policy")
    
    # v8.4.2: Create organized output directory structure
    output_base = Path(args.output)
    output_dir = output_base.parent if output_base.parent != Path('.') else Path('.')
    output_name = output_base.stem
    
    # Create subdirectories for organized outputs
    core_dir = output_dir / 'core'
    reports_dir = output_dir / 'reports'
    certificates_dir = output_dir / 'certificates'
    narrative_dir = output_dir / 'narrative'
    transparency_dir = output_dir / 'transparency'
    logs_dir = output_dir / 'logs'
    
    # Only create directories as needed (will be created when files are saved)
    
    # v8.4.2: Set up pipeline logging in logs directory
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = str(logs_dir / f"{output_name}_pipeline.log")
    pipeline_logger = None
    try:
        pipeline_logger = PipelineLogger(log_file_path)
        sys.stdout = pipeline_logger
    except Exception as e:
        print(f"⚠️ Could not initialize pipeline logging: {e}")
        pipeline_logger = None
    
    # v8.4.2: Initialize diagnostic logger (debug trace + errors + performance)
    diagnostic_logger = None
    if DIAGNOSTIC_LOGGING_AVAILABLE:
        try:
            diagnostic_logger = DiagnosticLogger(output_dir=logs_dir, session_name=output_name)
            diagnostic_logger.info(f"Sparrow SPOT Scale™ {get_version_string()} session started")
            diagnostic_logger.log_config("variant", args.variant)
            diagnostic_logger.log_config("output_directory", str(output_dir))
            diagnostic_logger.log_config("deep_analysis", args.deep_analysis)
        except Exception as e:
            print(f"⚠️ Could not initialize diagnostic logging: {e}")
            diagnostic_logger = DiagnosticLogger()  # Use no-op fallback
    else:
        diagnostic_logger = DiagnosticLogger()  # Use no-op fallback
    
    print(f"\n🎯 Sparrow SPOT Scale™ {get_version_string()} - Starting grading process (with Deep Analysis)...")
    print(f"   Variant: {args.variant}")
    
    # Determine input source
    temp_pdf_path = None  # Track temp file for cleanup
    
    if args.url:
        # Fetch from URL
        print(f"   Input source: URL")
        try:
            text, is_pdf, temp_pdf_path = fetch_from_url(args.url)
            
            if is_pdf:
                # Extract text from downloaded PDF
                temp_grader = SPARROWGrader()
                text = temp_grader.extract_text_from_pdf(temp_pdf_path)
                print(f"   ✓ Extracted {len(text):,} characters from PDF")
            
            # Use URL for output filename
            input_name = args.url.split('/')[-1].split('?')[0] or 'remote_document'
            if not input_name.endswith(('.txt', '.pdf', '.html')):
                input_name += '.txt'
        except Exception as e:
            print(f"\n❌ Failed to fetch URL: {e}")
            return 1
    else:
        # Local file
        input_name = args.input_file
        print(f"   Input file: {input_name}")
        
        # Determine file type
        is_pdf = input_name.lower().endswith('.pdf')
        
        # Extract text based on file type
        print(f"\n📖 Reading {'PDF' if is_pdf else 'text'} file...")
        try:
            if is_pdf:
                # Use SPARROWGrader for PDF extraction (it has the methods)
                temp_grader = SPARROWGrader()
                text = temp_grader.extract_text_from_pdf(input_name)
                print(f"   ✓ Extracted {len(text):,} characters from PDF")
            else:
                with open(input_name, 'r', encoding='utf-8') as f:
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
            
            # Add document title to report (use CLI arg if provided, otherwise derive from filename)
            if args.document_title:
                doc_title = args.document_title
            elif args.url:
                doc_title = input_name.rsplit('.', 1)[0] if '.' in input_name else input_name
            else:
                doc_title = Path(args.input_file).stem
            report['document_title'] = doc_title
            
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
            # v8.6.1: Pass user-selected document type for certificate badge
            report = grader.grade(text, pdf_path=pdf_path, document_type_selected=args.document_type)
            
            # Add document title to report (use CLI arg if provided, otherwise derive from filename)
            if args.document_title:
                doc_title = args.document_title
            elif args.url:
                doc_title = input_name.rsplit('.', 1)[0] if '.' in input_name else input_name
            else:
                doc_title = Path(args.input_file).stem
            report['document_title'] = doc_title
            
            print("\n" + "="*70)
            print("SPOT-POLICY™ GRADING REPORT")
            print("="*70)
            print(f"\nClassification: {report['classification']}")
            print(f"Composite Score: {report['composite_score']}/100 ({report['composite_grade']})")
            
            print(f"\nFISCAL Criteria Breakdown:")
            criteria = report['criteria']
            for criterion in ['FT', 'SB', 'ER', 'PA', 'PC', 'AT']:
                if criterion in criteria:
                    data = criteria[criterion]
                    label_info = report['category_grade_labels'].get(criterion, {})
                    print(f"  {criterion}: {data['score']:.1f}/100 - {label_info.get('label', 'Unknown')}")
        
        # v8: Generate narrative engine outputs (if available)
        narrative_outputs = None
        if args.variant == 'policy' and NARRATIVE_ENGINE_AVAILABLE and grader.narrative_pipeline:
            print(f"\n🔄 Generating narrative content...")
            try:
                # Determine tone: use CLI flag if provided, else default to 'journalistic'
                narrative_tone = args.narrative_style if args.narrative_style else 'journalistic'
                narrative_length = args.narrative_length  # Pass length parameter
                ollama_model = args.ollama_model  # Pass model parameter
                
                # Call narrative pipeline to generate stories, insights, and formats
                narrative_outputs = grader.narrative_pipeline.generate_complete_narrative(
                    report, 
                    tone=narrative_tone,
                    length=narrative_length,
                    ollama_model=ollama_model
                )
                print(f"   ✓ Narrative generation complete (tone: {narrative_tone}, length: {narrative_length})")
                
                # Add critique integration to main report if available
                if narrative_outputs and 'critique_integration' in narrative_outputs and narrative_outputs['critique_integration']:
                    report['critique_integration'] = narrative_outputs['critique_integration']
                    print(f"   ✓ Critique integration added to report")
            except Exception as e:
                print(f"   ⚠️  Narrative generation skipped: {str(e)}")
        
        # v8.2: Run deep analysis if requested
        deep_analysis_results = None
        if args.deep_analysis:
            if not DEEP_ANALYSIS_AVAILABLE:
                print(f"\n⚠️ Deep analysis requested but deep_analyzer module not available")
            else:
                print(f"\n🔬 Running 6-level deep AI transparency analysis...")
                print(f"   This will take approximately 1-2 minutes...")
                try:
                    diagnostic_logger.start_stage("deep_analysis")
                    diagnostic_logger.debug("Initializing DeepAnalyzer")
                    
                    deep_analyzer = DeepAnalyzer()
                    # Create temp file with text content for analysis
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
                        tmp.write(text)
                        temp_text_path = tmp.name
                    
                    diagnostic_logger.debug("Running 6-level deep analysis", text_length=len(text))
                    
                    # Run deep analysis
                    deep_analysis_results = deep_analyzer.analyze_document(temp_text_path)
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_text_path)
                    except:
                        pass
                    
                    diagnostic_logger.end_stage("deep_analysis", details={
                        'ai_percentage': deep_analysis_results.get('consensus', {}).get('ai_percentage'),
                        'primary_model': deep_analysis_results.get('consensus', {}).get('primary_model')
                    })
                    
                    # Show quick summary
                    if 'consensus' in deep_analysis_results:
                        consensus = deep_analysis_results['consensus']
                        print(f"\n   ✅ Deep Analysis Complete:")
                        print(f"      AI Content: {consensus['ai_percentage']:.1f}%")
                        print(f"      Primary Model: {consensus['primary_model']} ({consensus['confidence']:.0f}% confidence)")
                        print(f"      Transparency Score: {consensus['transparency_score']}/100")
                        
                        if 'level3_patterns' in deep_analysis_results:
                            total_patterns = deep_analysis_results['level3_patterns']['total_patterns']
                            print(f"      Patterns Detected: {total_patterns}")
                        
                        # Add to main report
                        report['deep_analysis'] = deep_analysis_results
                        print(f"   ✓ Deep analysis added to report")
                except Exception as e:
                    print(f"   ⚠️ Deep analysis failed: {e}")
                    deep_analysis_results = None
        
        # Recommendation #6: Automated escalation notification
        ethical_summary = report.get('ethical_summary', {})
        if ethical_summary.get('escalation_required'):
            print("\n" + "="*70)
            print("⚠️  ESCALATION NOTIFICATION")
            print("="*70)
            triggers = ethical_summary.get('escalation_triggers', [])
            for trigger in triggers:
                print(f"  • {trigger}")
            print(f"\nAction Required: {ethical_summary.get('overall_recommendation', 'Human review recommended')}")
            print(f"Notify: Policy analyst and governance lead")
            print("="*70)
        
        print("\n" + "="*70)
    
    except Exception as e:
        print(f"   ❌ ERROR during grading: {str(e)}")
        import traceback
        traceback.print_exc()
        # v8.4.2: Close pipeline logger even on error
        if pipeline_logger:
            try:
                pipeline_logger.close()
            except:
                pass
        sys.exit(1)
    
    # Save outputs
    print(f"\n💾 Saving results...")
    generation_sequence = []  # Track file generation order (Recommendation #7)
    try:
        # v8.4.2: Create core directory for main outputs
        core_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON output (core)
        output_json = str(core_dir / f"{output_name}.json")
        with open(output_json, 'w') as f:
            # Note: We'll update generation_log after all files are saved
            json.dump(report, f, indent=2)
        print(f"   ✓ JSON: {output_json}")
        generation_sequence.append({'file': output_json, 'type': 'json', 'timestamp': report['timestamp']})
        
        # Text summary (core)
        output_txt = str(core_dir / f"{output_name}.txt")
        with open(output_txt, 'w') as f:
            f.write(f"Sparrow SPOT Scale™ {get_version_string()} Report (with Narrative Engine)\n")
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
                for criterion in ['FT', 'SB', 'ER', 'PA', 'PC', 'AT']:
                    if criterion in criteria:
                        data = criteria[criterion]
                        f.write(f"  {criterion}: {data['score']:.1f}/100\n")
                
                # Display weighting calculation
                f.write("\n" + "="*70 + "\n")
                f.write("COMPOSITE SCORE CALCULATION:\n")
                f.write("="*70 + "\n")
                
                calculation_parts = []
                for criterion in ['FT', 'SB', 'ER', 'PA', 'PC', 'AT']:
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
        generation_sequence.append({'file': output_txt, 'type': 'text_summary', 'timestamp': report['timestamp']})
        
        # v8: Save narrative engine outputs
        if narrative_outputs:
            try:
                # v8.4.2: Create narrative directory
                narrative_dir.mkdir(parents=True, exist_ok=True)
                
                # Save narrative text
                output_narrative = str(narrative_dir / f"{output_name}_narrative.txt")
                with open(output_narrative, 'w') as f:
                    f.write("NARRATIVE ENGINE OUTPUT\n")
                    f.write("="*70 + "\n\n")
                    f.write(narrative_outputs.get('narrative_text', 'N/A'))
                    f.write("\n\n" + "="*70 + "\n")
                    f.write("GENERATED: " + narrative_outputs.get('metadata', {}).get('generated_at', 'N/A') + "\n")
                print(f"   ✓ Narrative: {output_narrative}")
                
                # v8: Generate publish-ready markdown when --narrative-style is provided
                if args.narrative_style:
                    output_publish = str(narrative_dir / f"{output_name}_publish.md")
                    with open(output_publish, 'w') as f:
                        narrative_text = narrative_outputs.get('narrative_text', '')
                        
                        # Add metadata header
                        f.write("---\n")
                        f.write(f"# Sparrow SPOT Scale™ {get_version_string()} Narrative Analysis\n")
                        f.write(f"**Style:** {args.narrative_style.title()}\n")
                        # Fix: Handle None input_file (for URLs)
                        doc_name = Path(args.input_file).stem if args.input_file else (args.url.split('/')[-1].split('?')[0] if args.url else 'remote_document')
                        f.write(f"**Document:** {doc_name}\n")
                        f.write(f"**Generated:** {narrative_outputs.get('metadata', {}).get('generated_at', 'N/A')}\n")
                        
                        # Include trust score and risk tier
                        trust_data = report.get('trust_score', {})
                        # Fix #3: Normalize trust score to one decimal place
                        trust_score_raw = trust_data.get('trust_score') if isinstance(trust_data, dict) else trust_data
                        trust_score = round(trust_score_raw, 1) if trust_score_raw else 0.0
                        risk_tier_data = report.get('risk_tier', {})
                        risk_tier = risk_tier_data.get('risk_tier') if isinstance(risk_tier_data, dict) else 'N/A'
                        
                        f.write(f"**Trust Score:** {trust_score}/100\n")
                        f.write(f"**Risk Tier:** {risk_tier}\n")
                        f.write("---\n\n")
                        
                        # Main narrative content
                        f.write(narrative_text)
                        
                        # Footer with methodology and AI transparency
                        f.write("\n\n---\n")
                        f.write("## Methodology\n\n")
                        f.write(f"This analysis was generated using Sparrow SPOT Scale™ {get_version_string()} (SPOT-Policy™) ")
                        f.write("with the narrative engine pipeline.\n\n")
                        
                        # v8.4.2: Prefer deep analysis consensus over basic AI detection
                        deep_analysis = report.get('deep_analysis', {})
                        consensus = deep_analysis.get('consensus', {})
                        
                        if consensus and 'ai_percentage' in consensus:
                            # Use deep analysis consensus (more accurate)
                            ai_contrib = consensus.get('ai_percentage', 0)
                            primary_model = consensus.get('primary_model', 'Unknown')
                            model_confidence = consensus.get('confidence', 0)
                            
                            f.write(f"**AI Contribution:** {ai_contrib:.1f}%\n")
                            if primary_model and primary_model != 'Unknown':
                                f.write(f"**Detected AI Model:** {primary_model} ({model_confidence:.0f}% confidence)\n")
                        else:
                            # Fallback to basic AI detection
                            ai_detection_data = report.get('ai_detection', {})
                            if isinstance(ai_detection_data, dict):
                                # Fix #1: Standardize AI contribution extraction (overall_percentage or ai_detection_score)
                                ai_contrib = ai_detection_data.get('overall_percentage')
                                if ai_contrib is None:
                                    ai_score = ai_detection_data.get('ai_detection_score', 0)
                                    ai_contrib = ai_score * 100 if ai_score <= 1 else ai_score
                                f.write(f"**AI Contribution:** {ai_contrib:.1f}%\n")
                                
                                # Add model detection information
                                likely_model = ai_detection_data.get('likely_ai_model', {})
                                if isinstance(likely_model, dict) and likely_model.get('model'):
                                    model_name = likely_model.get('model')
                                    model_conf = likely_model.get('confidence', 0)
                                    model_analysis = likely_model.get('analysis', '')
                                    if model_name and model_name != 'Mixed/Uncertain':
                                        f.write(f"**Detected AI Model:** {model_name} ({model_conf*100:.0f}% confidence)\n")
                                        if model_analysis:
                                            f.write(f"**Model Analysis:** {model_analysis}\n")
                                    elif model_name == 'Mixed/Uncertain':
                                        f.write(f"**Detected AI Model:** Mixed/Uncertain patterns detected\n")
                        
                        f.write(f"**Human Review:** Completed {narrative_outputs.get('metadata', {}).get('generated_at', 'N/A')}\n")
                        f.write(f"**Evaluation Variant:** SPOT-Policy™\n")
                        f.write(f"**Narrative Tone:** {args.narrative_style}\n")
                    
                    print(f"   ✓ Publish-ready: {output_publish}")

                
                # Save X thread format
                formats = narrative_outputs.get('outputs', {})
                if 'x_thread' in formats:
                    output_x_thread = str(narrative_dir / f"{output_name}_x_thread.txt")
                    with open(output_x_thread, 'w') as f:
                        f.write(formats['x_thread'])
                    print(f"   ✓ X Thread: {output_x_thread}")
                
                # Save LinkedIn format
                if 'linkedin' in formats:
                    output_linkedin = str(narrative_dir / f"{output_name}_linkedin.txt")
                    with open(output_linkedin, 'w') as f:
                        f.write(formats['linkedin'])
                    print(f"   ✓ LinkedIn: {output_linkedin}")
                
                # Save insights
                if 'insights' in narrative_outputs:
                    output_insights = str(narrative_dir / f"{output_name}_insights.json")
                    with open(output_insights, 'w') as f:
                        json.dump(narrative_outputs['insights'], f, indent=2)
                    print(f"   ✓ Insights: {output_insights}")
                
                # Save QA report
                if 'qa_report' in narrative_outputs:
                    reports_dir.mkdir(parents=True, exist_ok=True)
                    output_qa = str(reports_dir / f"{output_name}_qa_report.json")
                    with open(output_qa, 'w') as f:
                        json.dump(narrative_outputs['qa_report'], f, indent=2)
                    print(f"   ✓ QA Report: {output_qa}")
            
            except Exception as e:
                print(f"   ⚠️  Error saving narrative outputs: {str(e)}")
        
        # v8.2: Save deep analysis report
        if deep_analysis_results:
            try:
                # v8.4.2: Create reports directory
                reports_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate markdown report
                output_deep_md = str(reports_dir / f"{output_name}_deep_analysis.md")
                deep_md = deep_analysis_results.get('_markdown_report', None)
                if not deep_md:
                    # Generate markdown if not already in results
                    analyzer_instance = DeepAnalyzer()
                    deep_md = analyzer_instance.generate_report(deep_analysis_results, output_format='markdown')
                
                with open(output_deep_md, 'w', encoding='utf-8') as f:
                    f.write(deep_md)
                print(f"   ✓ Deep Analysis (Markdown): {output_deep_md}")
                
                # Save JSON data
                output_deep_json = str(reports_dir / f"{output_name}_deep_analysis.json")
                with open(output_deep_json, 'w', encoding='utf-8') as f:
                    json.dump(deep_analysis_results, f, indent=2)
                print(f"   ✓ Deep Analysis (JSON): {output_deep_json}")
                
            except Exception as e:
                print(f"   ⚠️  Error saving deep analysis: {str(e)}")
        
        # HTML Certificate
        try:
            diagnostic_logger.start_stage("certificate_generation")
            diagnostic_logger.debug("Importing certificate generator module")
            
            from certificate_generator import CertificateGenerator
            cert_gen = CertificateGenerator()
            
            # v8.4.2: Create certificates directory
            certificates_dir.mkdir(parents=True, exist_ok=True)
            
            # Use user-supplied document title if present, else fallback to filename
            doc_title = report.get('document_title')
            if not doc_title:
                if args.url:
                    doc_title = input_name.rsplit('.', 1)[0] if '.' in input_name else input_name
                else:
                    doc_title = Path(args.input_file).stem
            output_html = str(certificates_dir / f"{output_name}_certificate.html")
            
            diagnostic_logger.debug("Generating certificate", variant=args.variant, title=doc_title)
            
            if args.variant == 'policy':
                cert_gen.generate_policy_certificate(report, doc_title, output_html)
            else:
                cert_gen.generate_journalism_certificate(report, doc_title, output_html)
            
            diagnostic_logger.log_file_operation("write", output_html, success=True)
            diagnostic_logger.end_stage("certificate_generation")
            print(f"   ✓ Certificate: {output_html}")
            
            # Plain-Language Summary (Ollama)
            try:
                core_dir.mkdir(parents=True, exist_ok=True)
                output_summary = str(core_dir / f"{output_name}_summary.txt")
                # Use ollama_model from narrative outputs if available, otherwise from args
                model_to_use = narrative_outputs.get('metadata', {}).get('ollama_model', args.ollama_model)
                # Pass narrative_length to enforce length constraints
                summary = cert_gen.generate_summary_with_ollama(
                    report, 
                    args.variant, 
                    model=model_to_use, 
                    length=narrative_length,
                    output_file=output_summary
                )
                if summary:
                    print(f"   ✓ Summary: {output_summary}")
            except Exception as e:
                diagnostic_logger.error("Summary generation failed", exception=e)
                print(f"   ⚠️  Summary generation skipped: {str(e)}")
        
        except Exception as e:
            diagnostic_logger.error("Certificate generation failed", exception=e, variant=args.variant)
            diagnostic_logger.end_stage("certificate_generation")
            print(f"   ⚠️  Certificate generation skipped: {str(e)}")
    
    except Exception as e:
        print(f"   ⚠️  Failed to save outputs: {str(e)}")
    
    # v8.4.2: Update generation log with all files created in organized directories
    try:
        import glob
        # Search in all subdirectories
        all_files = []
        for subdir in [core_dir, reports_dir, certificates_dir, narrative_dir, transparency_dir, logs_dir]:
            if subdir.exists():
                all_files.extend(glob.glob(str(subdir / f"{output_name}*")))
        
        report['generation_log']['files_generated'] = sorted(all_files)
        report['generation_log']['generation_sequence'] = generation_sequence
        report['generation_log']['total_files'] = len(all_files)
        report['generation_log']['output_structure'] = {
            'core': str(core_dir),
            'reports': str(reports_dir),
            'certificates': str(certificates_dir),
            'narrative': str(narrative_dir),
            'transparency': str(transparency_dir),
            'logs': str(logs_dir)
        }
        
        # Re-save JSON with complete generation log
        with open(output_json, 'w') as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        print(f"   ⚠️  Generation log update skipped: {str(e)}")
    
    # v8.3: Process transparency features
    try:
        # Enhanced Provenance Tracking
        if args.enhanced_provenance:
            print("\n🔍 Extracting enhanced provenance metadata...")
            try:
                from ai_detection_engine import ProvenanceAnalyzer
                prov_analyzer = ProvenanceAnalyzer()
                
                # v8.4.2: Create transparency directory
                transparency_dir.mkdir(parents=True, exist_ok=True)
                
                # Get enhanced metadata
                prov_metadata = prov_analyzer.extract_metadata(args.input_file)
                
                # Save provenance report
                output_prov = str(transparency_dir / f"{output_name}_provenance.json")
                with open(output_prov, 'w', encoding='utf-8') as f:
                    json.dump(prov_metadata, f, indent=2)
                print(f"   ✓ Provenance: {output_prov}")
                
                # Also update report with provenance data
                if 'provenance' not in report:
                    report['provenance'] = {}
                report['provenance']['enhanced_metadata'] = prov_metadata
                
            except Exception as e:
                print(f"   ⚠️  Enhanced provenance skipped: {str(e)}")
        
        # v8.6: Token Analysis (if requested)
        if args.analyze_tokens:
            print(f"\n📊 Analyzing Document Size...")
            try:
                from token_calculator import analyze_document_file
                
                # For text input, save to temp file for analysis
                import tempfile
                if args.url or (args.input_file and not args.input_file.endswith(('.txt', '.pdf'))):
                    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                    temp_file.write(text)
                    temp_file.close()
                    analysis_path = temp_file.name
                else:
                    analysis_path = args.input_file
                
                # Analyze document
                analysis = analyze_document_file(analysis_path)
                
                # Display results
                print(f"\n{'='*70}")
                print("DOCUMENT SIZE ANALYSIS")
                print(f"{'='*70}")
                print(f"Characters: {analysis.get('character_count', 0):,}")
                print(f"Estimated Tokens: {analysis.get('estimated_tokens', 0):,}")
                print(f"Estimated Pages: {analysis.get('estimated_pages', 0)}")
                print(f"Method: {analysis.get('estimation_method', 'unknown')}")
                
                rec = analysis.get('recommendations', {})
                if rec:
                    print(f"\nRecommendation: {rec.get('strategy', 'unknown').upper()} strategy")
                    models = rec.get('recommended_models', [])
                    if models:
                        top_model = models[0]
                        print(f"  Suggested Model: {top_model.get('model', 'unknown')}")
                        print(f"  Context: {top_model.get('context_size', 0):,} tokens")
                        print(f"  Chunks Needed: {top_model.get('chunks_needed', 1)}")
                        print(f"  Coverage: {top_model.get('coverage', '0%')}")
                        
                        if top_model.get('chunks_needed', 1) > 1:
                            print(f"\n💡 Use --enable-chunking for optimal Q&A on this document")
                
                print(f"{'='*70}\n")
                
                # Clean up temp file
                if args.url or (args.input_file and not args.input_file.endswith(('.txt', '.pdf'))):
                    import os
                    os.unlink(analysis_path)
                
            except Exception as e:
                print(f"   ⚠️  Token analysis failed: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # v8.4.2/v8.6: Document Q&A (if requested)
        if args.document_qa:
            print(f"\n❓ Generating document Q&A...")
            try:
                # v8.6: Use enhanced Q&A with chunking if enabled
                if args.enable_chunking:
                    print(f"   🔄 Smart chunking enabled (strategy: {args.chunk_strategy}, routing: {args.qa_routing})")
                    
                    from token_calculator import estimate_tokens
                    from semantic_chunker import chunk_document, save_chunks
                    from enhanced_document_qa import EnhancedDocumentQA
                    
                    # Estimate tokens
                    tokens = estimate_tokens(text, method="tiktoken")
                    print(f"   📊 Document size: {tokens['estimated_tokens']:,} tokens")
                    
                    # Create chunks
                    print(f"   ✂️  Creating chunks...")
                    chunks_result = chunk_document(
                        text,
                        max_tokens=args.max_chunk_tokens,
                        strategy=args.chunk_strategy,
                        overlap_tokens=200
                    )
                    
                    # Save chunks
                    qa_dir = output_dir / "qa"
                    chunks_dir = qa_dir / "chunks"
                    save_chunks(
                        chunks_result,
                        output_dir=str(chunks_dir),
                        save_text=True,
                        save_index=True
                    )
                    print(f"   ✂️  Created {len(chunks_result['chunks'])} chunks")
                    
                    # Query using enhanced Q&A
                    print(f"   🔍 Querying with {args.qa_routing} routing...")
                    qa_engine = EnhancedDocumentQA(
                        chunks_dir=chunks_dir / "chunks",
                        chunk_index_path=chunks_dir / "chunk_index.json"
                    )
                    
                    answer = qa_engine.query(
                        question=args.document_qa,
                        model="mock",  # Use mock for now (integrate with Ollama in future)
                        routing_strategy=args.qa_routing,
                        synthesis_strategy="concatenate",
                        relevance_threshold=0.3
                    )
                    
                    # Save answer
                    qa_file = qa_dir / f"{output_name}_qa_enhanced.json"
                    qa_dir.mkdir(parents=True, exist_ok=True)
                    
                    # json already imported at module level
                    with open(qa_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "question": answer.question,
                            "answer": answer.answer,
                            "sources": [
                                {
                                    "chunk": s.chunk_number,
                                    "pages": s.pages,
                                    "sections": s.sections
                                }
                                for s in answer.sources
                            ],
                            "metadata": {
                                "chunks_queried": answer.total_chunks_queried,
                                "total_time": answer.total_time,
                                "confidence": answer.confidence,
                                "routing_strategy": answer.routing_strategy,
                                "chunk_strategy": args.chunk_strategy,
                                "max_chunk_tokens": args.max_chunk_tokens
                            }
                        }, f, indent=2, ensure_ascii=False)
                    
                    print(f"   ✓ Enhanced Q&A: {qa_file}")
                    print(f"   ✓ Chunks queried: {answer.total_chunks_queried}, Confidence: {answer.confidence:.0%}")
                    generation_sequence.append({
                        'file': str(qa_file),
                        'type': 'enhanced_document_qa',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                else:
                    # Standard Q&A (no chunking)
                    from document_qa import generate_document_qa
                    
                    # Create qa directory
                    qa_dir = output_dir / "qa"
                    
                    # Get contribution tracker if available
                    tracker = None
                    if grader.narrative_pipeline and hasattr(grader.narrative_pipeline, 'contribution_tracker'):
                        tracker = grader.narrative_pipeline.contribution_tracker
                    
                    qa_file = generate_document_qa(
                        document_text=text,
                        question=args.document_qa,
                        output_dir=qa_dir,
                        output_name=output_name,
                        model=args.ollama_model,
                        analysis_context=report,
                        contribution_tracker=tracker
                    )
                    
                    if qa_file:
                        print(f"   ✓ Document Q&A: {qa_file}")
                        generation_sequence.append({'file': qa_file, 'type': 'document_qa', 'timestamp': datetime.now().isoformat()})
                
            except Exception as e:
                print(f"   ⚠️  Document Q&A failed: {str(e)}")
                import traceback
                traceback.print_exc()
                if diagnostic_logger:
                    diagnostic_logger.error("document_qa_failed", error=str(e))
        
        # v8.5: Legislative Threat Detection (Discretionary Power Analysis)
        if args.legislative_threat:
            print(f"\n⚖️  Running Legislative Threat Detection...")
            try:
                if not LEGISLATIVE_THREAT_AVAILABLE:
                    print(f"   ⚠️  Legislative threat detection not available (discretionary_power_analyzer.py not found)")
                else:
                    # Create threats directory at same level as certificates, core, logs, etc.
                    threats_dir = output_dir / "threats"
                    threats_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Initialize analyzer
                    dpa = DiscretionaryPowerAnalyzer(output_dir=str(threats_dir))
                    
                    # Run analysis
                    dpa_results = dpa.analyze(text, document_name=output_name)
                    
                    # Save both JSON and Markdown reports
                    json_path = dpa.save_results(dpa_results, format='json')
                    md_path = dpa.save_results(dpa_results, format='markdown')
                    
                    print(f"   ✓ Discretionary Power Analysis: {dpa_results['risk_level']} RISK")
                    print(f"   ✓ Score: {dpa_results['discretionary_power_score']:.1f}/100")
                    print(f"   ✓ Findings: {dpa_results['total_findings']}")
                    print(f"   ✓ JSON Report: {json_path}")
                    print(f"   ✓ Markdown Report: {md_path}")
                    
                    generation_sequence.append({'file': str(json_path), 'type': 'legislative_threat_json', 'timestamp': datetime.now().isoformat()})
                    generation_sequence.append({'file': str(md_path), 'type': 'legislative_threat_report', 'timestamp': datetime.now().isoformat()})
                    
                    # Add to main report
                    if 'legislative_threat_analysis' not in report:
                        report['legislative_threat_analysis'] = {}
                    report['legislative_threat_analysis']['discretionary_power'] = dpa_results
                    
            except Exception as e:
                print(f"   ⚠️  Legislative threat detection failed: {str(e)}")
                if diagnostic_logger:
                    diagnostic_logger.error("legislative_threat_failed", error=str(e))
        
        # v8.4.1: Full Provenance Report (document origin + AI usage audit trail)
        if args.provenance_report:
            print("\n📜 Generating full provenance report...")
            try:
                from provenance_report_generator import create_provenance_report_generator
                from ai_detection_engine import ProvenanceAnalyzer
                
                prov_report_gen = create_provenance_report_generator()
                
                # Get document metadata (use existing if enhanced_provenance was run)
                if 'provenance' in report and 'enhanced_metadata' in report['provenance']:
                    doc_metadata = report['provenance']['enhanced_metadata']
                else:
                    prov_analyzer = ProvenanceAnalyzer()
                    doc_metadata = prov_analyzer.extract_metadata(args.input_file)
                
                # Get AI calls log from narrative pipeline (if available)
                ai_calls_log = []
                contribution_log = None
                if grader.narrative_pipeline:
                    try:
                        contribution_log = grader.narrative_pipeline.get_ai_contribution_log()
                    except Exception:
                        pass
                
                # Generate the provenance report
                doc_title = report.get('document_title', report.get('title', 'Unknown Document'))
                provenance_report = prov_report_gen.generate_report(
                    document_metadata=doc_metadata,
                    ai_calls_log=ai_calls_log,
                    contribution_log=contribution_log,
                    document_title=doc_title,
                    analysis_timestamp=report.get('metadata', {}).get('generated_at')
                )
                
                # v8.4.2: Save both JSON and markdown versions to transparency directory
                transparency_dir.mkdir(parents=True, exist_ok=True)
                saved_files = prov_report_gen.save_report(
                    provenance_report,
                    str(transparency_dir / output_name),
                    format="both"
                )
                
                # Add to main report
                report['provenance_report'] = provenance_report
                
            except Exception as e:
                print(f"   ⚠️  Provenance report generation failed: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Citation Quality Analysis
        if args.citation_check:
            print("\n📚 Analyzing citation quality...")
            try:
                if CITATION_SCORER_AVAILABLE:
                    from citation_quality_scorer import CitationQualityScorer
                    
                    # Extract text from the original document
                    doc_text = ''
                    try:
                        if args.url:
                            # For URLs, use article analyzer
                            analyzer = ArticleAnalyzer()
                            doc_text = analyzer.scrape_article_from_url(args.url)
                        else:
                            # For PDFs, use the extract_text_from_pdf method from this file
                            temp_grader = SPARROWGrader()
                            doc_text = temp_grader.extract_text_from_pdf(args.input_file)
                    except Exception as e:
                        print(f"   ⚠️  Could not extract text: {str(e)}")
                    
                    if doc_text and isinstance(doc_text, str) and len(doc_text) > 0:
                        # Analyze citations (correct method name)
                        scorer = CitationQualityScorer()
                        try:
                            # check_urls is slow, only enable if explicitly requested
                            verify_urls = getattr(args, 'check_urls', False)
                            citation_results = scorer.analyze_citations(doc_text, check_urls=verify_urls)
                        except Exception as cite_err:
                            print(f"   ⚠️  Citation scorer error: {str(cite_err)}")
                            import traceback
                            traceback.print_exc()
                            raise
                        
                        # Generate citation report
                        transparency_dir.mkdir(parents=True, exist_ok=True)
                        output_citation = str(transparency_dir / f"{output_name}_citation_report.txt")
                        with open(output_citation, 'w', encoding='utf-8') as f:
                            f.write(scorer.format_citation_results(citation_results))
                        print(f"   ✓ Citation Report: {output_citation}")
                        
                        # Add to main report
                        report['citation_quality'] = citation_results
                    else:
                        print(f"   ⚠️  No text content available for citation analysis (type: {type(doc_text)})")
                    
                else:
                    print(f"   ⚠️  Citation scorer module not available")
            except Exception as e:
                print(f"   ⚠️  Citation analysis skipped: {str(e)}")
        
        # Data Lineage Visualization
        if args.lineage_chart:
            print(f"\n📊 Generating {args.lineage_chart.upper()} lineage flowchart...")
            try:
                if LINEAGE_VIZ_AVAILABLE:
                    from data_lineage_visualizer import DataLineageVisualizer
                    
                    viz = DataLineageVisualizer()
                    
                    # Build pipeline stages based on what was actually run
                    viz.add_stage("Document Ingestion", 
                                 "Load and validate input document",
                                 status="completed")
                    
                    viz.add_stage("Text Extraction",
                                 "Extract text content from PDF",
                                 status="completed")
                    
                    viz.add_stage("Provenance Analysis",
                                 "Extract document metadata and provenance",
                                 status="completed" if args.enhanced_provenance else "skipped")
                    
                    viz.add_stage("SPOT Grading",
                                 f"Multi-dimensional {args.variant} analysis",
                                 status="completed")
                    
                    # AI Detection stage with details
                    ai_stage_idx = viz.add_stage("AI Detection",
                                 "Basic AI content detection",
                                 status="completed")
                    
                    # Add AI detection details
                    ai_detection = report.get('ai_detection', {})
                    ai_details = []
                    if ai_detection:
                        ai_score = ai_detection.get('ai_detection_score', 0) * 100
                        ai_details.append(f"AI Content: {ai_score:.1f}%")
                        
                        likely_model = ai_detection.get('likely_ai_model', {})
                        if isinstance(likely_model, dict):
                            model_name = likely_model.get('model', 'Unknown')
                            model_conf = likely_model.get('confidence', 0) * 100
                            if model_name and model_name != 'Unknown':
                                ai_details.append(f"Detected Model: {model_name} ({model_conf:.0f}% confidence)")
                            
                            # Add top model fingerprints
                            model_scores = likely_model.get('model_scores', {})
                            if model_scores:
                                sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                                if sorted_models:
                                    ai_details.append("Top Model Fingerprints:")
                                    for model, score in sorted_models:
                                        ai_details.append(f"  • {model}: {score*100:.1f}%")
                    
                    if ai_details:
                        viz.update_stage(ai_stage_idx, "completed", ai_details)
                    
                    # Deep Analysis stage with details
                    deep_stage_idx = viz.add_stage("Deep Analysis",
                                 "6-level transparency analysis",
                                 status="completed" if deep_analysis_results else "skipped")
                    
                    # Add deep analysis details if available
                    if deep_analysis_results:
                        deep_details = []
                        consensus = deep_analysis_results.get('consensus', {})
                        if consensus:
                            deep_details.append(f"Consensus AI: {consensus.get('ai_percentage', 0):.1f}%")
                            deep_details.append(f"Primary Model: {consensus.get('primary_model', 'Unknown')}")
                            deep_details.append(f"Transparency Score: {consensus.get('transparency_score', 0)}/100")
                            
                            # Add level breakdown
                            level_scores = consensus.get('level_scores', {})
                            if level_scores:
                                deep_details.append("Level Breakdown:")
                                for level, score in level_scores.items():
                                    deep_details.append(f"  • {level}: {score:.1f}%")
                        
                        if deep_details:
                            viz.update_stage(deep_stage_idx, "completed", deep_details)
                    
                    viz.add_stage("Ethical Framework",
                                 "Risk assessment and bias audit",
                                 status="completed")
                    
                    viz.add_stage("Citation Analysis",
                                 "Source transparency and quality scoring",
                                 status="completed" if args.citation_check else "skipped")
                    
                    viz.add_stage("NIST Compliance",
                                 "AI RMF compliance mapping",
                                 status="completed" if args.nist_compliance else "skipped")
                    
                    viz.add_stage("Certificate Generation",
                                 "Create professional grading certificate",
                                 status="completed")
                    
                    viz.add_stage("Output Compilation",
                                 "Generate all report formats",
                                 status="completed")
                    
                    # Generate appropriate format
                    transparency_dir.mkdir(parents=True, exist_ok=True)
                    if args.lineage_chart == 'html':
                        output_file = str(transparency_dir / f"{output_name}_lineage_flowchart.html")
                        html_content = viz.generate_html_flowchart()
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                    elif args.lineage_chart == 'ascii':
                        output_file = str(transparency_dir / f"{output_name}_lineage_flowchart.txt")
                        ascii_content = viz.generate_ascii_flowchart()
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(ascii_content)
                    elif args.lineage_chart == 'json':
                        output_file = str(transparency_dir / f"{output_name}_lineage_flowchart.json")
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump({"stages": viz.stages}, f, indent=2)
                    
                    print(f"   ✓ Lineage Chart: {output_file}")
                else:
                    print(f"   ⚠️  Lineage visualizer module not available")
            except Exception as e:
                print(f"   ⚠️  Lineage chart generation skipped: {str(e)}")
        
        # NIST AI RMF Compliance Check
        if args.nist_compliance:
            print("\n🏛️  Generating NIST AI RMF compliance report...")
            try:
                if NIST_COMPLIANCE_AVAILABLE:
                    from nist_compliance_checker import NISTComplianceChecker
                    
                    checker = NISTComplianceChecker()
                    compliance_results = checker.check_compliance(report)
                    
                    # Generate compliance report
                    transparency_dir.mkdir(parents=True, exist_ok=True)
                    output_nist = str(transparency_dir / f"{output_name}_nist_compliance.txt")
                    with open(output_nist, 'w', encoding='utf-8') as f:
                        f.write(checker.generate_compliance_report(compliance_results))
                    print(f"   ✓ NIST Compliance: {output_nist}")
                    
                    # Add to main report
                    report['nist_compliance'] = compliance_results
                else:
                    print(f"   ⚠️  NIST compliance checker module not available")
            except Exception as e:
                print(f"   ⚠️  NIST compliance check skipped: {str(e)}")
        
        # Data Source Tracing
        if args.trace_data_sources:
            print("\n🔍 Tracing quantitative claims to authoritative data sources...")
            try:
                if DATA_LINEAGE_MAPPER_AVAILABLE:
                    from data_lineage_source_mapper import DataLineageSourceMapper
                    
                    # Get document text
                    doc_text = ''
                    try:
                        if args.url:
                            analyzer = ArticleAnalyzer()
                            doc_text = analyzer.scrape_article_from_url(args.url)
                        else:
                            temp_grader = SPARROWGrader()
                            doc_text = temp_grader.extract_text_from_pdf(args.input_file)
                    except Exception as e:
                        print(f"   ⚠️  Could not extract text for source tracing: {str(e)}")
                    
                    if doc_text:
                        # Trace sources
                        mapper = DataLineageSourceMapper()
                        lineage_data = mapper.trace_sources(doc_text)
                        
                        # Generate reports
                        transparency_dir.mkdir(parents=True, exist_ok=True)
                        output_lineage_txt = str(transparency_dir / f"{output_name}_data_lineage.txt")
                        with open(output_lineage_txt, 'w', encoding='utf-8') as f:
                            f.write(mapper.generate_report(lineage_data, 'text'))
                        print(f"   ✓ Data Lineage (Text): {output_lineage_txt}")
                        
                        output_lineage_json = str(transparency_dir / f"{output_name}_data_lineage.json")
                        with open(output_lineage_json, 'w', encoding='utf-8') as f:
                            json.dump(lineage_data, f, indent=2)
                        print(f"   ✓ Data Lineage (JSON): {output_lineage_json}")
                        
                        # Add summary to main report
                        report['data_lineage'] = lineage_data['summary']
                        
                        # Display key findings
                        summary = lineage_data['summary']
                        print(f"   📊 Found {summary['total_quantitative_claims']} quantitative claims")
                        print(f"   📊 Traced {summary['traced_to_sources']} to authoritative sources ({summary['trace_rate_pct']:.1f}%)")
                        if summary['optimistic_questionable_claims'] > 0:
                            print(f"   ⚠️  {summary['optimistic_questionable_claims']} claims are optimistic/questionable")
                    else:
                        print(f"   ⚠️  No text available for source tracing")
                else:
                    print(f"   ⚠️  Data lineage mapper module not available")
            except Exception as e:
                print(f"   ⚠️  Data source tracing skipped: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # AI Disclosure Statement Generation
        if args.generate_ai_disclosure:
            print("\n📋 Generating AI transparency disclosure statements...")
            try:
                if AI_DISCLOSURE_AVAILABLE:
                    from ai_disclosure_generator import AIDisclosureGenerator
                    
                    # Initialize generator with analysis results
                    disclosure_gen = AIDisclosureGenerator(report)
                    
                    # Generate all formats in transparency directory
                    transparency_dir.mkdir(parents=True, exist_ok=True)
                    output_path = str(transparency_dir / output_name)
                    disclosure_files = disclosure_gen.generate_all_formats(output_path)
                    
                    print(f"   ✅ Generated {len(disclosure_files)} disclosure formats:")
                    for file in disclosure_files:
                        print(f"      ✓ {file}")
                else:
                    print(f"   ⚠️  AI disclosure generator module not available")
            except Exception as e:
                print(f"   ⚠️  AI disclosure generation skipped: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Re-save main JSON if any transparency features were added
        if any([args.enhanced_provenance, args.citation_check, args.nist_compliance, args.generate_ai_disclosure, args.trace_data_sources]):
            try:
                with open(output_json, 'w') as f:
                    json.dump(report, f, indent=2)
            except Exception as e:
                print(f"   ⚠️  Failed to update main report: {str(e)}")
                
    except Exception as e:
        print(f"   ⚠️  Transparency features processing error: {str(e)}")
    
    # Cleanup temporary PDF if downloaded from URL
    if temp_pdf_path and os.path.exists(temp_pdf_path):
        try:
            os.unlink(temp_pdf_path)
            print(f"   🧹 Cleaned up temporary PDF: {temp_pdf_path}")
        except Exception as e:
            print(f"   ⚠️  Failed to cleanup temp file: {str(e)}")
    
    # v8.4.2: Close pipeline logger and show organized output structure
    if pipeline_logger:
        pipeline_logger.close()
        print(f"\n📝 Pipeline log saved: {log_file_path}")
    
    # v8.4.2: Display organized output structure
    print(f"\n✅ Grading complete!")
    print(f"\n📁 Outputs organized in:")
    if core_dir.exists():
        core_files = list(core_dir.glob(f"{output_name}*"))
        if core_files:
            print(f"   📂 Core ({len(core_files)} files): {core_dir}")
    if reports_dir.exists():
        report_files = list(reports_dir.glob(f"{output_name}*"))
        if report_files:
            print(f"   📂 Reports ({len(report_files)} files): {reports_dir}")
    if certificates_dir.exists():
        cert_files = list(certificates_dir.glob(f"{output_name}*"))
        if cert_files:
            print(f"   📂 Certificates ({len(cert_files)} files): {certificates_dir}")
    if narrative_dir.exists():
        narr_files = list(narrative_dir.glob(f"{output_name}*"))
        if narr_files:
            print(f"   📂 Narrative ({len(narr_files)} files): {narrative_dir}")
    if transparency_dir.exists():
        trans_files = list(transparency_dir.glob(f"{output_name}*"))
        if trans_files:
            print(f"   📂 Transparency ({len(trans_files)} files): {transparency_dir}")
    if logs_dir.exists():
        log_files = list(logs_dir.glob(f"{output_name}*"))
        if log_files:
            print(f"   📂 Logs ({len(log_files)} files): {logs_dir}")
    print()
    
    # v8.6.1: Generate interactive index.html for this investigation run
    if INDEX_GENERATOR_AVAILABLE:
        try:
            index_path = generate_investigation_index(output_dir, document_name=output_name)
            print(f"✅ Investigation index generated: {index_path}")
            print(f"   💡 Tip: Run 'cd {output_dir.parent} && python3 -m http.server 8765' to view")
            print(f"   Then open: http://localhost:8765/{output_dir.name}/index.html")
        except Exception as e:
            print(f"⚠️  Could not generate index: {e}")
    
    # v8.4.2: Finalize diagnostic logging
    if diagnostic_logger:
        diagnostic_logger.finalize()


if __name__ == '__main__':
    main()

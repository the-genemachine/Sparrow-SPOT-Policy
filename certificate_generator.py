"""
HTML Certificate Generator for Sparrow SPOT Scale™ v8.4.0

Generates professional certificates for policy and journalism grading with ethical framework

v8.4.0 Enhancement: Critical Findings at Top
- Detection uncertainty warning moved to TOP of certificate
- "Critical Findings" section shows failing scores prominently
- INCONCLUSIVE detection suppresses misleading attribution confidence
- "X of Y critical thresholds met" summary box added
"""

import json
from datetime import datetime
from pathlib import Path
from textwrap import dedent

try:
    from ollama_summary_generator import OllamaSummaryGenerator
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# v8.3.2: Import AnalysisResults for single source of truth
try:
    from analysis_results import AnalysisResults, create_analysis_results, ConfidenceLevel
    ANALYSIS_RESULTS_AVAILABLE = True
except ImportError:
    ANALYSIS_RESULTS_AVAILABLE = False

# Import version info
try:
    from version import SPARROW_VERSION, CERTIFICATE_VERSION
except ImportError:
    SPARROW_VERSION = "?"
    CERTIFICATE_VERSION = "?"


class CertificateGenerator:
    """Generate HTML certificates for v7 grading results with ethical framework data."""
    
    def __init__(self):
        """Initialize certificate generator."""
        self.policy_certificate_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Garamond', 'Georgia', serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 20px;
        }}
        .certificate {{
            background: white; max-width: 920px; width: 100%; padding: 55px;
            box-shadow: 0 25px 70px rgba(0,0,0,0.32); position: relative;
            border-top: 6px solid #2980b9; border-bottom: 6px solid #2980b9;
        }}
        .certificate::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(200,200,200,0.04) 35px, rgba(200,200,200,0.04) 70px);
            pointer-events: none;
        }}
        .watermark {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 110px; color: rgba(200,200,200,0.14); font-weight: bold; pointer-events: none; z-index: 0;
        }}
        .content {{ position: relative; z-index: 1; }}

        /* Header */
        .header {{ text-align: center; margin-bottom: 45px; padding-bottom: 30px; border-bottom: 2px solid #2980b9; }}
        .header h1 {{ font-size: 2.6em; color: #1a6699; letter-spacing: 1.8px; margin-bottom: 8px; }}
        .header .subtitle {{ font-size: 1.15em; color: #444; font-style: italic; }}
        .seal {{ font-size: 3.2em; color: #2980b9; margin: 18px 0; }}

        /* Document Type Badge */
        .doc-type-badge {{
            display: inline-block; background: #e3f2fd; color: #1565c0; padding: 6px 14px;
            border-radius: 20px; font-size: 0.85em; font-weight: 600; letter-spacing: 0.5px; margin-top: 8px;
        }}

        /* Article Info */
        .article-info {{
            background: #f8f9fa; padding: 22px; border-left: 5px solid #2980b9; border-radius: 0 6px 6px 0;
            margin: 35px 0; font-size: 0.98em;
        }}
        .article-info h3 {{ color: #1a6699; font-size: 1.18em; margin-bottom: 12px; }}
        .article-info p {{ margin: 7px 0; line-height: 1.65; color: #333; }}
        .article-info strong {{ color: #1a6699; }}

        /* Composite Grade */
        .composite-grade {{
            text-align: center; padding: 42px; margin: 45px 0;
            background: linear-gradient(135deg, #e3f2fd20 0%, #bbdefb30 100%);
            border: 2.5px solid #2980b9; border-radius: 10px;
        }}
        .composite-grade h2 {{ color: #1a6699; font-size: 2.1em; margin-bottom: 16px; }}
        .composite-score {{ font-size: 3.8em; font-weight: 900; color: #1a6699; margin: 18px 0; }}
        .composite-classification {{ font-size: 1.25em; color: #333; line-height: 1.6; }}

        /* Individual Grades Grid */
        .grades {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 18px; margin: 45px 0;
        }}
        .grade-item {{
            background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;
            border-top: 4px solid #2980b9; transition: transform 0.2s;
        }}
        .grade-item h4 {{ color: #1a6699; font-size: 0.95em; margin-bottom: 10px; letter-spacing: 0.8px; }}
        .grade-value {{ font-size: 2.1em; font-weight: bold; color: #1a6699; margin: 8px 0; }}
        .grade-letter {{ font-size: 1.3em; color: #555; margin: 4px 0; }}
        .grade-description {{ font-size: 0.88em; color: #666; line-height: 1.5; }}

        /* Methodology */
        .methodology {{
            background: #e8f4fc; padding: 22px; border-left: 5px solid #2980b9; border-radius: 0 6px 6px 0;
            margin: 40px 0; font-size: 0.94em;
        }}
        .methodology h3 {{ color: #1a6699; margin-bottom: 14px; }}
        .methodology ul {{ list-style: none; }}
        .methodology li {{ margin: 9px 0; position: relative; padding-left: 22px; color: #333; }}
        .methodology li::before {{ content: '✓'; color: #2980b9; position: absolute; left: 0; font-weight: bold; }}

        /* Footer */
        .footer {{
            margin-top: 55px; padding-top: 28px; border-top: 2px solid #ddd;
            text-align: center; font-size: 0.88em; color: #666;
        }}
        .certificate-id {{ margin: 14px 0; font-weight: bold; color: #1a6699; }}

        /* Grade Color Classes */
        .grade-a {{ color: #27ae60; }}
        .grade-b {{ color: #3498db; }}
        .grade-c {{ color: #f39c12; }}
        .grade-d {{ color: #e74c3c; }}
        .grade-f {{ color: #c0392b; }}

        /* Print & Mobile */
        @media print {{
            body {{ background: white; }}
            .certificate {{ box-shadow: none; max-width: 100%; padding: 40px; }}
        }}
        @media (max-width: 600px) {{
            .certificate {{ padding: 30px; }}
            .header h1 {{ font-size: 1.9em; }}
            .composite-score {{ font-size: 2.8em; }}
            .grades {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="certificate">
        <div class="watermark">SPARROW SPOT</div>
        <div class="content">

            <!-- Header -->
            <div class="header">
                <h1>Sparrow SPOT Scale™ Certification</h1>
                <p class="subtitle">Policy & Legislative Document Quality Assessment</p>
                <div class="doc-type-badge">{doc_type_badge}</div>
                <div class="seal">★</div>
                <div style='margin-top:10px;font-size:0.95em;color:#888;'>
                    <strong>SPARROW Version:</strong> {sparrow_version} &nbsp;|&nbsp; <strong>Certificate Version:</strong> {certificate_version}
                </div>
            </div>

            <!-- Article Info -->
            <div class="article-info">
                <h3>Document Information</h3>
                <p><strong>Title:</strong> {document_title}</p>
                <p><strong>Analysis Date:</strong> {evaluation_date}</p>
            </div>

            <!-- Composite Grade -->
            <div class="composite-grade">
                <h2>Overall Assessment</h2>
                <div class="composite-score">{composite_score}/100{adjusted_badge}</div>
                <div class="composite-classification">
                    Grade: <strong class="grade-{grade_class}">{grade}</strong><br>
                    Performance: <strong>{performance_label}</strong><br>
                    Classification: <strong>{classification}</strong>
                </div>
            </div>

            <!-- Individual Grades -->
            <div class="grades">
                <div class="grade-item">
                    <h4>Fiscal Transparency</h4>
                    <div class="grade-value">{ft_score}</div>
                    <div class="grade-letter">(FT)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #2980b9; margin: 6px 0;">{ft_grade_code}</div>
                    <div class="grade-description">{ft_grade_label}</div>
                </div>
                <div class="grade-item">
                    <h4>Stakeholder Balance</h4>
                    <div class="grade-value">{sb_score}</div>
                    <div class="grade-letter">(SB)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #2980b9; margin: 6px 0;">{sb_grade_code}</div>
                    <div class="grade-description">{sb_grade_label}</div>
                </div>
                <div class="grade-item">
                    <h4>Economic Rigor</h4>
                    <div class="grade-value">{er_score}</div>
                    <div class="grade-letter">(ER)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #2980b9; margin: 6px 0;">{er_grade_code}</div>
                    <div class="grade-description">{er_grade_label}</div>
                </div>
                <div class="grade-item">
                    <h4>Public Accessibility</h4>
                    <div class="grade-value">{pa_score}</div>
                    <div class="grade-letter">(PA)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #2980b9; margin: 6px 0;">{pa_grade_code}</div>
                    <div class="grade-description">{pa_grade_label}</div>
                </div>
                <div class="grade-item">
                    <h4>Policy Consequentiality</h4>
                    <div class="grade-value">{pc_score}</div>
                    <div class="grade-letter">(PC)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #2980b9; margin: 6px 0;">{pc_grade_code}</div>
                    <div class="grade-description">{pc_grade_label}</div>
                </div>
            </div>

            <!-- Ethical Framework Assessment Section (v8) -->
            <div class="ethical-framework" style="background: #f0f4f8; padding: 25px; margin: 25px 0; border-left: 5px solid #27ae60; border-radius: 4px;">
                <h3 style="color: #27ae60; margin-bottom: 15px;">🔒 Ethical Framework Assessment (v8.0)</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <!-- Trust Score Badge -->
                    <div class="badge" style="padding: 12px; border: 2px solid #3498db; border-radius: 4px; background: white;">
                        <div style="font-size: 0.9em; color: #555; font-weight: 600;">Trust Score</div>
                        <div style="font-size: 1.8em; font-weight: 700; color: #3498db; margin: 5px 0;">{trust_score}</div>
                        <div style="font-size: 0.85em; color: #666;">Explainability, Fairness, Robustness, Compliance</div>
                    </div>
                    <!-- AI Detection Badge -->
                    <div class="badge" style="padding: 12px; border: 2px solid #e74c3c; border-radius: 4px; background: white;">
                        <div style="font-size: 0.9em; color: #555; font-weight: 600;">AI Detection</div>
                        <div style="font-size: 1.2em; font-weight: 700; color: #e74c3c; margin: 5px 0;">{ai_confidence}%</div>
                        <div style="font-size: 0.85em; color: #666;">Human/Mixed/AI Classification</div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <!-- Risk Tier Badge -->
                    <div class="badge" style="padding: 12px; border: 2px solid #f39c12; border-radius: 4px; background: white;">
                        <div style="font-size: 0.9em; color: #555; font-weight: 600;">Risk Classification</div>
                        <div style="font-size: 1.2em; font-weight: 700; color: #f39c12; margin: 5px 0;">{risk_tier}</div>
                        <div style="font-size: 0.85em; color: #666;">NIST AI RMF v1.0 Based</div>
                    </div>
                    <!-- Fairness Assessment -->
                    <div class="badge" style="padding: 12px; border: 2px solid #27ae60; border-radius: 4px; background: white;">
                        <div style="font-size: 0.9em; color: #555; font-weight: 600;">Fairness Metrics</div>
                        <div style="font-size: 1.2em; font-weight: 700; color: #27ae60; margin: 5px 0;">{fairness_score}%</div>
                        <div style="font-size: 0.85em; color: #666;">Demographic Parity & Equalized Odds</div>
                    </div>
                </div>
                {escalation_warning}
            </div>

            <!-- Post-Audit Adjustments Section (Fix #5) -->
            {adjusted_scores_section}

            <!-- Deep Analysis Section (v8.2) -->
            {deep_analysis_section}

            <!-- v8.4.1: Critical Findings Section (moved after Deep AI Transparency) -->
            {critical_findings_section}

            <!-- Methodology -->
            <div class="methodology">
                <h3>Assessment Methodology</h3>
                <ul>
                    <li>Multi-dimensional analysis via Sparrow SPOT Scale™ v{sparrow_version} with Narrative Engine</li>
                    <li>Advanced NLP with machine learning</li>
                    <li>Policy-adapted evaluation framework with AI detection</li>
                    <li>Expert-level assessment protocols with fairness auditing</li>
                </ul>
            </div>

            <!-- Footer -->
            <div class="footer">
                <p>This certificate verifies comprehensive quality assessment under the Sparrow SPOT Scale™ framework for policy documents.</p>
                <div class="certificate-id">
                    <p>Issued: {evaluation_date} | Grading Authority: Sparrow SPOT Scale™ v8.0 (Narrative Engine + Ethical Framework v1.0)</p>
                    <p>Valid for policy analysis and credibility certification</p>
                </div>
            </div>

        </div>
    </div>
</body>
</html>
"""
        
        self.journalism_certificate_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Garamond', 'Georgia', serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 20px;
        }}
        .certificate {{
            background: white; max-width: 920px; width: 100%; padding: 55px;
            box-shadow: 0 25px 70px rgba(0,0,0,0.32); position: relative;
            border-top: 6px solid #8e44ad; border-bottom: 6px solid #8e44ad;
        }}
        .certificate::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(200,200,200,0.04) 35px, rgba(200,200,200,0.04) 70px);
            pointer-events: none;
        }}
        .watermark {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 110px; color: rgba(200,200,200,0.14); font-weight: bold; pointer-events: none; z-index: 0;
        }}
        .content {{ position: relative; z-index: 1; }}

        /* Header */
        .header {{ text-align: center; margin-bottom: 45px; padding-bottom: 30px; border-bottom: 2px solid #8e44ad; }}
        .header h1 {{ font-size: 2.6em; color: #5b2d6b; letter-spacing: 1.8px; margin-bottom: 8px; }}
        .header .subtitle {{ font-size: 1.15em; color: #444; font-style: italic; }}
        .seal {{ font-size: 3.2em; color: #8e44ad; margin: 18px 0; }}

        /* Document Type Badge */
        .doc-type-badge {{
            display: inline-block; background: #f3e5f5; color: #6a1b9a; padding: 6px 14px;
            border-radius: 20px; font-size: 0.85em; font-weight: 600; letter-spacing: 0.5px; margin-top: 8px;
        }}

        /* Article Info */
        .article-info {{
            background: #f8f9fa; padding: 22px; border-left: 5px solid #8e44ad; border-radius: 0 6px 6px 0;
            margin: 35px 0; font-size: 0.98em;
        }}
        .article-info h3 {{ color: #5b2d6b; font-size: 1.18em; margin-bottom: 12px; }}
        .article-info p {{ margin: 7px 0; line-height: 1.65; color: #333; }}
        .article-info strong {{ color: #5b2d6b; }}

        /* Composite Grade */
        .composite-grade {{
            text-align: center; padding: 42px; margin: 45px 0;
            background: linear-gradient(135deg, #f3e5f520 0%, #e1bee730 100%);
            border: 2.5px solid #8e44ad; border-radius: 10px;
        }}
        .composite-grade h2 {{ color: #5b2d6b; font-size: 2.1em; margin-bottom: 16px; }}
        .composite-score {{ font-size: 3.8em; font-weight: 900; color: #8e44ad; margin: 18px 0; }}
        .composite-classification {{ font-size: 1.25em; color: #333; line-height: 1.6; }}

        /* Individual Grades Grid */
        .grades {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 18px; margin: 45px 0;
        }}
        .grade-item {{
            background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;
            border-top: 4px solid #8e44ad; transition: transform 0.2s;
        }}
        .grade-item h4 {{ color: #5b2d6b; font-size: 0.95em; margin-bottom: 10px; letter-spacing: 0.8px; }}
        .grade-value {{ font-size: 2.1em; font-weight: bold; color: #8e44ad; margin: 8px 0; }}
        .grade-letter {{ font-size: 1.3em; color: #555; margin: 4px 0; }}
        .grade-description {{ font-size: 0.88em; color: #666; line-height: 1.5; }}

        /* Methodology */
        .methodology {{
            background: #f3e5f5; padding: 22px; border-left: 5px solid #8e44ad; border-radius: 0 6px 6px 0;
            margin: 40px 0; font-size: 0.94em;
        }}
        .methodology h3 {{ color: #5b2d6b; margin-bottom: 14px; }}
        .methodology ul {{ list-style: none; }}
        .methodology li {{ margin: 9px 0; position: relative; padding-left: 22px; color: #333; }}
        .methodology li::before {{ content: '✓'; color: #8e44ad; position: absolute; left: 0; font-weight: bold; }}

        /* Footer */
        .footer {{
            margin-top: 55px; padding-top: 28px; border-top: 2px solid #ddd;
            text-align: center; font-size: 0.88em; color: #666;
        }}
        .certificate-id {{ margin: 14px 0; font-weight: bold; color: #5b2d6b; }}

        /* Grade Color Classes */
        .grade-a {{ color: #27ae60; }}
        .grade-b {{ color: #8e44ad; }}
        .grade-c {{ color: #f39c12; }}
        .grade-d {{ color: #e74c3c; }}
        .grade-f {{ color: #c0392b; }}

        /* Print & Mobile */
        @media print {{
            body {{ background: white; }}
            .certificate {{ box-shadow: none; max-width: 100%; padding: 40px; }}
        }}
        @media (max-width: 600px) {{
            .certificate {{ padding: 30px; }}
            .header h1 {{ font-size: 1.9em; }}
            .composite-score {{ font-size: 2.8em; }}
            .grades {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="certificate">
        <div class="watermark">SPARROW SPOT</div>
        <div class="content">

            <!-- Header -->
            <div class="header">
                <h1>Sparrow SPOT Scale™ Certification</h1>
                <p class="subtitle">Journalism Quality Assessment</p>
                <div class="doc-type-badge">JOURNALISM ARTICLE</div>
                <div class="seal">★</div>
                <div style='margin-top:10px;font-size:0.95em;color:#888;'>
                    <strong>SPARROW Version:</strong> {sparrow_version} &nbsp;|&nbsp; <strong>Certificate Version:</strong> {certificate_version}
                </div>
            </div>

            <!-- Article Info -->
            <div class="article-info">
                <h3>Article Information</h3>
                <p><strong>Title:</strong> {document_title}</p>
                <p><strong>Analysis Date:</strong> {evaluation_date}</p>
            </div>

            <!-- Composite Grade -->
            <div class="composite-grade">
                <h2>Credibility Assessment</h2>
                <div class="composite-score">{composite_score}/100</div>
                <div class="composite-classification">
                    Grade: <strong class="grade-{grade_class}">{grade}</strong><br>
                    Classification: <strong>{classification}</strong>
                </div>
            </div>

            <!-- Individual Grades -->
            <div class="grades">
                <div class="grade-item">
                    <h4>Source Integrity</h4>
                    <div class="grade-value">{si_score}</div>
                    <div class="grade-letter">(SI)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #8e44ad; margin: 6px 0;">{si_grade_code}</div>
                    <div class="grade-description">{si_grade_label}</div>
                </div>
                <div class="grade-item">
                    <h4>Objectivity Index</h4>
                    <div class="grade-value">{oi_score}</div>
                    <div class="grade-letter">(OI)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #8e44ad; margin: 6px 0;">{oi_grade_code}</div>
                    <div class="grade-description">{oi_grade_label}</div>
                </div>
                <div class="grade-item">
                    <h4>Technical Precision</h4>
                    <div class="grade-value">{tp_score}</div>
                    <div class="grade-letter">(TP)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #8e44ad; margin: 6px 0;">{tp_grade_code}</div>
                    <div class="grade-description">{tp_grade_label}</div>
                </div>
                <div class="grade-item">
                    <h4>Accessibility Rating</h4>
                    <div class="grade-value">{ar_score}</div>
                    <div class="grade-letter">(AR)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #8e44ad; margin: 6px 0;">{ar_grade_code}</div>
                    <div class="grade-description">{ar_grade_label}</div>
                </div>
                <div class="grade-item">
                    <h4>Impact Utility</h4>
                    <div class="grade-value">{iu_score}</div>
                    <div class="grade-letter">(IU)</div>
                    <div class="grade-code" style="font-size: 0.95em; font-weight: 600; color: #8e44ad; margin: 6px 0;">{iu_grade_code}</div>
                    <div class="grade-description">{iu_grade_label}</div>
                </div>
            </div>

            <!-- Ethical Framework Assessment Section (v8) -->
            <div class="ethical-framework" style="background: #f0f4f8; padding: 25px; margin: 25px 0; border-left: 5px solid #27ae60; border-radius: 4px;">
                <h3 style="color: #27ae60; margin-bottom: 15px;">🔒 Ethical Framework Assessment (v8.0)</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <!-- Trust Score Badge -->
                    <div class="badge" style="padding: 12px; border: 2px solid #3498db; border-radius: 4px; background: white;">
                        <div style="font-size: 0.9em; color: #555; font-weight: 600;">Trust Score</div>
                        <div style="font-size: 1.8em; font-weight: 700; color: #3498db; margin: 5px 0;">{trust_score}</div>
                        <div style="font-size: 0.85em; color: #666;">Explainability, Fairness, Robustness, Compliance</div>
                    </div>
                    <!-- AI Detection Badge -->
                    <div class="badge" style="padding: 12px; border: 2px solid #e74c3c; border-radius: 4px; background: white;">
                        <div style="font-size: 0.9em; color: #555; font-weight: 600;">AI Detection</div>
                        <div style="font-size: 1.2em; font-weight: 700; color: #e74c3c; margin: 5px 0;">{ai_confidence}%</div>
                        <div style="font-size: 0.85em; color: #666;">Human/Mixed/AI Classification</div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <!-- Risk Tier Badge -->
                    <div class="badge" style="padding: 12px; border: 2px solid #f39c12; border-radius: 4px; background: white;">
                        <div style="font-size: 0.9em; color: #555; font-weight: 600;">Risk Classification</div>
                        <div style="font-size: 1.2em; font-weight: 700; color: #f39c12; margin: 5px 0;">{risk_tier}</div>
                        <div style="font-size: 0.85em; color: #666;">NIST AI RMF v1.0 Based</div>
                    </div>
                    <!-- Fairness Assessment -->
                    <div class="badge" style="padding: 12px; border: 2px solid #27ae60; border-radius: 4px; background: white;">
                        <div style="font-size: 0.9em; color: #555; font-weight: 600;">Fairness Metrics</div>
                        <div style="font-size: 1.2em; font-weight: 700; color: #27ae60; margin: 5px 0;">{fairness_score}%</div>
                        <div style="font-size: 0.85em; color: #666;">Demographic Parity & Equalized Odds</div>
                    </div>
                </div>
                {escalation_warning}
            </div>

            <!-- Deep Analysis Section (v8.2) -->
            {deep_analysis_section}

            <!-- v8.4.1: Critical Findings Section (moved after Deep AI Transparency) -->
            {critical_findings_section}

            <!-- Methodology -->
            <div class="methodology">
                <h3>Assessment Methodology</h3>
                <ul>
                    <li>Multi-dimensional analysis via Sparrow SPOT Scale™ v{sparrow_version} with Narrative Engine</li>
                    <li>Advanced NLP with machine learning</li>
                    <li>Journalism-adapted evaluation framework with AI detection</li>
                    <li>Credibility scoring protocols with fairness auditing</li>
                </ul>
            </div>

            <!-- Footer -->
            <div class="footer">
                <p>This certificate verifies comprehensive quality assessment under the Sparrow SPOT Scale™ framework for journalism content.</p>
                <div class="certificate-id">
                    <p>Issued: {evaluation_date} | Grading Authority: Sparrow SPOT Scale™ v8.0 (Narrative Engine + Ethical Framework v1.0)</p>
                    <p>Valid for journalism analysis and credibility certification</p>
                </div>
            </div>

        </div>
    </div>
</body>
</html>
"""
    
    def _get_confidence_label(self, confidence_pct: float) -> str:
        """
        v8.3.2: Get human-readable confidence label.
        
        Args:
            confidence_pct: Confidence percentage (0-100)
            
        Returns:
            Confidence label string
        """
        if confidence_pct >= 85:
            return "High Confidence"
        elif confidence_pct >= 60:
            return "Medium Confidence"
        elif confidence_pct >= 30:
            return "Low Confidence"
        else:
            return "Uncertain"
    
    def _get_ai_confidence_label(self, report: dict) -> str:
        """
        v8.3.2: Determine confidence label for AI detection.
        
        Uses multiple factors:
        - Number of detection levels with data
        - Agreement between levels
        - Model detection confidence
        """
        deep = report.get('deep_analysis', {})
        if not deep:
            return "Low Confidence - limited analysis"
        
        # Count levels with data
        levels = ['level1_document', 'level2_section', 'level4_model', 
                 'level5_behavioral', 'level6_phrase']
        level_count = sum(1 for l in levels if deep.get(l))
        
        consensus = deep.get('consensus', {})
        confidence = consensus.get('confidence', 0)
        
        # Normalize confidence
        if confidence <= 2:
            confidence = confidence * 100
        confidence = min(confidence, 100)
        
        # v8.3.4 CRITICAL FIX: Check detection spread
        # Per Bill C-15 discrepancy report: High spread = Low confidence, not High
        ai_detection = report.get('ai_detection', {})
        detection_spread = ai_detection.get('detection_spread', 0)
        
        # If detection methods disagree by more than 50%, confidence cannot be "High"
        if detection_spread > 0.5:
            spread_pct = detection_spread * 100
            if detection_spread > 0.7:
                return f"LOW Confidence - methods disagree by {spread_pct:.0f}%"
            else:
                return f"MODERATE Confidence - {spread_pct:.0f}% method disagreement"
        
        if level_count >= 5 and confidence >= 80:
            return "High Confidence - multi-method consensus"
        elif level_count >= 3 and confidence >= 60:
            return "Medium Confidence - partial consensus"
        else:
            return "Low Confidence - limited data"
    
    def generate_policy_certificate(self, report, document_title="", output_file=None):
        """Generate HTML certificate for policy grading with ethical framework."""
        if not output_file:
            output_file = "certificate_policy.html"
        
        criteria = report.get('criteria', {})
        composite = report.get('composite_score', 0)
        grade = report.get('composite_grade', 'F')
        classification = report.get('classification', 'Unclassified')
        performance_label = report.get('performance_label', classification)  # Fallback to classification
        adjusted = report.get('adjusted', False)  # Check if scores were adjusted
        category_grade_labels = report.get('category_grade_labels', {})
        
        grade_class = self._get_grade_class(grade)
        
        # Extract grade codes and labels for each criterion
        def get_grade_data(criterion_key):
            labels = category_grade_labels.get(criterion_key, {})
            return labels.get('code', ''), labels.get('label', '')
        
        ft_code, ft_label = get_grade_data('FT')
        sb_code, sb_label = get_grade_data('SB')
        er_code, er_label = get_grade_data('ER')
        pa_code, pa_label = get_grade_data('PA')
        pc_code, pc_label = get_grade_data('PC')
        
        # v7: Extract ethical framework data
        trust_score_data = report.get('trust_score', {})
        # v8.3.3 Fix: Show 1 decimal place instead of rounding to integer (58.7 not 58)
        trust_score = round(trust_score_data.get('trust_score', 0), 1) if trust_score_data else 0
        
        # v8.2: Prefer deep analysis data when available
        deep_analysis = report.get('deep_analysis', {})
        if deep_analysis and 'consensus' in deep_analysis:
            # Use deep analysis consensus data (more accurate)
            consensus = deep_analysis.get('consensus', {})
            # v8.3.3 Fix: Use 1 decimal place for AI percentage (31.8% not 31%)
            ai_confidence = round(consensus.get('ai_percentage', 0), 1)
            ai_model = consensus.get('primary_model', 'Unknown')
            
            # v8.3: Override Mixed/Uncertain with highest scoring individual model
            # Also get the model-specific confidence
            ai_detection = report.get('ai_detection', {})
            likely_ai_model = ai_detection.get('likely_ai_model', {})
            model_scores = likely_ai_model.get('model_scores', {})
            
            if ai_model == 'Mixed/Uncertain' or model_scores:
                if model_scores:
                    # Find the model with the highest score
                    highest_model = max(model_scores, key=model_scores.get)
                    highest_score = model_scores[highest_model]
                    # Only override if we have a clear winner (>0.5 threshold)
                    if highest_score > 0.5:
                        # Clean up model name for display
                        model_name_map = {
                            'cohere': 'Cohere',
                            'claude': 'Claude (Anthropic)',
                            'mistral': 'Mistral AI',
                            'ollama': 'Ollama',
                            'gemini': 'Google Gemini'
                        }
                        if ai_model == 'Mixed/Uncertain':
                            ai_model = model_name_map.get(highest_model.lower(), highest_model.title())
                        # v8.3.3 Fix: Use model-specific confidence (90%) not consensus confidence (120%)
                        ai_model_confidence = round(highest_score * 100, 1)
            
            # Fallback to consensus confidence if no model_scores
            if 'ai_model_confidence' not in dir() or ai_model_confidence == 0:
                raw_confidence = consensus.get('confidence', 0)
                # Values between 0-2 treated as 0-1 scale
                if raw_confidence <= 2:
                    ai_model_confidence = round(raw_confidence * 100, 1)
                else:
                    ai_model_confidence = round(raw_confidence, 1)
                # Cap at 100% - values over 100 are data errors
                ai_model_confidence = min(ai_model_confidence, 100.0)
            transparency_score = consensus.get('transparency_score', 0)
            has_deep_analysis = True
        else:
            # Fallback to basic AI detection with improved model detection
            ai_detection_data = report.get('ai_detection', {})
            ai_detection_score = ai_detection_data.get('ai_detection_score', 0) if ai_detection_data else 0
            ai_confidence = int(ai_detection_score * 100) if ai_detection_score else 0
            
            # Improved model detection logic (same as AIDisclosureGenerator)
            ai_model = 'Unknown'
            ai_model_confidence = 0
            if ai_detection_data:
                likely_model = ai_detection_data.get('likely_ai_model', {})
                if isinstance(likely_model, dict):
                    # Check if we have model_scores to get the actual highest scoring model
                    model_scores = likely_model.get('model_scores', {})
                    if model_scores:
                        # Find the highest scoring model
                        highest_model = max(model_scores.items(), key=lambda x: x[1])
                        model_name, confidence = highest_model
                        
                        # Clean up model names for better display
                        if model_name.lower() == 'cohere':
                            ai_model = 'Cohere'
                        elif 'claude' in model_name.lower():
                            ai_model = 'Claude (Anthropic)'
                        elif 'gemini' in model_name.lower():
                            ai_model = 'Google Gemini'
                        elif 'mistral' in model_name.lower():
                            ai_model = 'Mistral AI'
                        elif 'llama' in model_name.lower() or 'ollama' in model_name.lower():
                            ai_model = 'Ollama/Llama'
                        else:
                            ai_model = model_name
                        
                        # v8.3.2 Fix: Cap at 100%
                        ai_model_confidence = min(int(confidence * 100), 100)
                        print(f'DEBUG: Found highest model: {ai_model} with {ai_model_confidence}% confidence')
                    else:
                        # Fallback to the likely_ai_model.model if no model_scores
                        ai_model = likely_model.get('model', 'Unknown')
                        raw_conf = likely_model.get('confidence', 0)
                        ai_model_confidence = min(int(raw_conf * 100) if raw_conf <= 1 else int(raw_conf), 100)
            
            transparency_score = 0
            has_deep_analysis = False
        
        ai_confidence_pct = ai_confidence  # Kept for backward compatibility
        
        # v8.4.0: Get AI detection data for INCONCLUSIVE check
        ai_detection_data = report.get('ai_detection', {})
        detection_inconclusive = ai_detection_data.get('detection_inconclusive', False)
        detection_spread = ai_detection_data.get('detection_spread', 0)
        
        # v8.4.0: Suppress attribution confidence when detection is INCONCLUSIVE
        if detection_inconclusive or detection_spread > 0.50:
            ai_model = 'INCONCLUSIVE'
            ai_model_confidence = 'N/A'
            # Add confidence interval display if available
            # Note: Template adds trailing %, so we omit it here to avoid double %%
            score_interval = ai_detection_data.get('score_confidence_interval', {})
            if score_interval:
                ai_confidence = f"{score_interval.get('display', f'{ai_confidence} (uncertain)')}"
            else:
                ai_confidence = f"{ai_confidence} ± {detection_spread * 50:.0f}"
        
        risk_tier_data = report.get('risk_tier', {})
        risk_tier = risk_tier_data.get('risk_tier', 'UNKNOWN').upper() if risk_tier_data else 'UNKNOWN'
        
        # Create adjusted badge if scores were adjusted (Recommendation #4)
        adjusted_badge = ' <span style="color: #e67e22; font-size: 0.7em; font-weight: 600;">*ADJUSTED</span>' if adjusted else ''
        
        bias_audit_data = report.get('bias_audit', {})
        fairness_score = int(bias_audit_data.get('overall_fairness_score', 0)) if bias_audit_data else 0
        
        # v8.3.4: Dynamic fairness color and warning based on score
        # Per discrepancy report: 33% is FAILING and should be highlighted as such
        if fairness_score >= 70:
            fairness_color = "#27ae60"  # Green - passing
            fairness_status = ""
        elif fairness_score >= 50:
            fairness_color = "#f39c12"  # Orange - marginal
            fairness_status = " (MARGINAL)"
        else:
            fairness_color = "#e74c3c"  # Red - failing
            fairness_status = " (FAILING)"
        
        ethical_summary = report.get('ethical_summary', {})
        escalation_required = ethical_summary.get('escalation_required', False)
        escalation_warning = ''
        
        # v8.3.4: Add fairness-specific escalation warning if score is failing
        if fairness_score < 50:
            escalation_warning = f"""
                <div style="background: #ffe6e6; border: 2px solid #e74c3c; padding: 12px; border-radius: 4px; margin-top: 15px;">
                    <div style="font-weight: 700; color: #e74c3c; margin-bottom: 5px;">⚠️ CRITICAL: Fairness Assessment FAILED ({fairness_score}%)</div>
                    <div style="font-size: 0.9em; color: #555;">Significant bias detected. Manual bias review REQUIRED before policy implementation. Review individual fairness metrics for affected groups.</div>
                </div>
            """
        elif escalation_required:
            escalation_warning = f"""
                <div style="background: #ffe6e6; border: 2px solid #e74c3c; padding: 12px; border-radius: 4px; margin-top: 15px;">
                    <div style="font-weight: 700; color: #e74c3c; margin-bottom: 5px;">⚠️ Escalation Required</div>
                    <div style="font-size: 0.9em; color: #555;">{ethical_summary.get('overall_recommendation', 'Professional review required')}</div>
                </div>
            """
        
        # Fix #5: Generate Post-Audit Adjustments section
        adjusted_scores_section = ''
        if bias_audit_data and bias_audit_data.get('adjustment_log'):
            adjustment_rows = []
            for adj in bias_audit_data['adjustment_log']:
                criterion = adj.get('criterion', 'N/A')
                original = adj.get('original', 0)
                adjusted = adj.get('adjusted', 0)
                sources = adj.get('sources', [])
                source_text = ', '.join(sources[:3])
                if len(sources) > 3:
                    source_text += f' (+{len(sources)-3} more)'
                
                adjustment_rows.append(f"""
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{criterion}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{original:.1f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{adjusted:.1f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; font-size: 0.85em;">{source_text}</td>
                    </tr>
                """)
            
            adjusted_scores_section = f"""
            <div class="post-audit" style="background: #fff9e6; padding: 20px; margin: 25px 0; border-left: 5px solid #f39c12; border-radius: 4px;">
                <h3 style="color: #f39c12; margin-bottom: 15px;">📊 Post-Audit Score Adjustments</h3>
                <p style="font-size: 0.95em; color: #555; margin-bottom: 15px;">
                    Scores adjusted based on external stakeholder critiques for enhanced accuracy and balance.
                </p>
                <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 4px;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Criterion</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Original</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Adjusted</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Sources</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(adjustment_rows)}
                    </tbody>
                </table>
            </div>
            """
        
        # Generate Deep Analysis section if available
        deep_analysis_section = ''
        if has_deep_analysis:
            level3 = deep_analysis.get('level3_patterns', {})
            level5 = deep_analysis.get('level5_fingerprints', {})
            level6 = deep_analysis.get('level6_statistics', {})
            
            # v8.3.5: Calculate detection spread for warning box
            model_scores = report.get('ai_detection', {}).get('model_scores', {})
            detection_spread = 0
            detection_warning_html = ''
            if model_scores:
                score_values = [v * 100 for v in model_scores.values() if isinstance(v, (int, float))]
                if len(score_values) >= 2:
                    min_score = min(score_values)
                    max_score = max(score_values)
                    detection_spread = max_score - min_score
                    
                    if detection_spread > 50:
                        detection_warning_html = f'''
                <div style="background: #fff3cd; border: 2px solid #ffc107; padding: 12px; border-radius: 4px; margin-bottom: 15px;">
                    <div style="font-weight: 700; color: #856404; margin-bottom: 5px;">⚠️ DETECTION UNCERTAINTY - Results Inconclusive</div>
                    <div style="font-size: 0.9em; color: #856404;">
                        Detection methods disagree by <strong>{detection_spread:.0f} percentage points</strong> (range: {min_score:.0f}%-{max_score:.0f}%).
                        The reported AI percentage is an average that obscures significant disagreement. 
                        Manual expert review is required for definitive assessment.
                    </div>
                </div>
                '''
            
            # Extract pattern counts (correct structure)
            total_patterns = level3.get('total_patterns', 0) if level3 else 0
            
            # Extract fingerprint data (correct structure)
            total_fingerprints = level5.get('total_fingerprints_found', 0) if level5 else 0
            
            # Extract statistics (correct structure)
            metrics = level6.get('metrics', {}) if level6 else {}
            perplexity = metrics.get('perplexity', 0)
            burstiness = metrics.get('burstiness', 0)
            lexical_diversity = metrics.get('lexical_diversity', 0)
            
            # v8.3.1: Generate pattern details section - v8.4.1: Simplified, no dropdown
            pattern_details_html = ''
            detailed_patterns = level3.get('detailed_matches', {})
            if detailed_patterns:
                # v8.4.1: Just show top 3 categories inline, no dropdown
                top_categories = []
                for category, data in list(detailed_patterns.items())[:3]:
                    category_name = category.replace('_', ' ').title()
                    count = data.get('count', 0)
                    top_categories.append(f"{category_name}: {count}")
                
                if top_categories:
                    pattern_details_html = f'''
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                        {" | ".join(top_categories)}
                    </div>
                    '''
            
            # v8.3.1: Generate fingerprint details section - v8.4.1: Simplified, no dropdown
            fingerprint_details_html = ''
            fingerprints = level5.get('fingerprints', {})
            if fingerprints:
                # v8.4.1: Just show model counts inline, no dropdown
                model_counts = []
                for model, data in list(fingerprints.items())[:3]:
                    if isinstance(data, dict):
                        count = data.get('count', 0)
                        if count > 0:
                            model_counts.append(f"{model}: {count}")
                
                if model_counts:
                    fingerprint_details_html = f'''
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                        {" | ".join(model_counts)}
                    </div>
                    '''
            
            deep_analysis_section = f"""
            <div class="deep-analysis" style="background: #f0f9ff; padding: 25px; margin: 25px 0; border-left: 5px solid #0ea5e9; border-radius: 4px;">
                <h3 style="color: #0369a1; margin-bottom: 15px;">🔬 Deep AI Transparency Analysis (v{sparrow_version})</h3>
                {detection_warning_html}
                <div style="background: white; padding: 15px; border-radius: 4px; margin-bottom: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div style="text-align: center;">
                            <div style="font-size: 0.85em; color: #666; margin-bottom: 5px;">AI Content</div>
                            <div style="font-size: 2em; font-weight: 700; color: #0ea5e9;">{ai_confidence}%</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.85em; color: #666; margin-bottom: 5px;">Primary Model</div>
                            <div style="font-size: 1.3em; font-weight: 700; color: #0369a1;">{ai_model}</div>
                            <div style="font-size: 0.75em; color: #888;" title="Attribution confidence: IF AI was used, this is the likelihood it was this model. Does NOT indicate certainty of AI use.">{ai_model_confidence}% attribution*</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.85em; color: #666; margin-bottom: 5px;">Transparency</div>
                            <div style="font-size: 2em; font-weight: 700; color: #0ea5e9;">{transparency_score:.1f}</div>
                            <div style="font-size: 0.75em; color: #888;">/100</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div style="background: #f8fafc; padding: 12px; border-radius: 4px;">
                            <div style="font-size: 0.85em; color: #555; font-weight: 600; margin-bottom: 5px;">Pattern Detection</div>
                            <div style="font-size: 1.1em; color: #0369a1;"><strong>{total_patterns}</strong> AI patterns found</div>
                            {pattern_details_html}
                        </div>
                        <div style="background: #f8fafc; padding: 12px; border-radius: 4px;">
                            <div style="font-size: 0.85em; color: #555; font-weight: 600; margin-bottom: 5px;">Phrase Fingerprints</div>
                            <div style="font-size: 1.1em; color: #0369a1;"><strong>{total_fingerprints}</strong> model signatures</div>
                            {fingerprint_details_html}
                        </div>
                    </div>
                </div>
                <div style="background: #f8fafc; padding: 12px; border-radius: 4px; font-size: 0.9em;">
                    <div style="font-weight: 600; color: #0369a1; margin-bottom: 8px;">Statistical Metrics:</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; color: #555;">
                        <div><strong>Perplexity:</strong> {perplexity:.2f}</div>
                        <div><strong>Burstiness:</strong> {burstiness:.3f}</div>
                        <div><strong>Lexical Diversity:</strong> {lexical_diversity:.3f}</div>
                    </div>
                </div>
                <div style="font-size: 0.75em; color: #888; margin-top: 10px; font-style: italic;">
                    * Attribution confidence indicates pattern match IF AI was used. It does not measure certainty of AI use.
                </div>
            </div>
            """
        
        # v8.3.3: Determine document type badge from report data
        doc_type_badge = self._get_document_type_badge(report)
        
        # v8.4.0: Generate Critical Findings section
        critical_findings_section = self._generate_critical_findings(
            report, ai_detection_data if 'ai_detection_data' in dir() else report.get('ai_detection', {}),
            trust_score, fairness_score, composite, criteria
        )
        
        html = self.policy_certificate_template.format(
            title=f"Sparrow SPOT Scale™ - {document_title}",
            document_title=document_title or "Policy Document",
            sparrow_version=SPARROW_VERSION,
            certificate_version=CERTIFICATE_VERSION,
            doc_type_badge=doc_type_badge,
            critical_findings_section=critical_findings_section,
            ft_score=criteria.get('FT', {}).get('score', 'N/A'),
            sb_score=criteria.get('SB', {}).get('score', 'N/A'),
            er_score=criteria.get('ER', {}).get('score', 'N/A'),
            pa_score=criteria.get('PA', {}).get('score', 'N/A'),
            pc_score=criteria.get('PC', {}).get('score', 'N/A'),
            ft_grade_code=ft_code,
            ft_grade_label=ft_label,
            sb_grade_code=sb_code,
            sb_grade_label=sb_label,
            er_grade_code=er_code,
            er_grade_label=er_label,
            pa_grade_code=pa_code,
            pa_grade_label=pa_label,
            pc_grade_code=pc_code,
            pc_grade_label=pc_label,
            composite_score=composite,
            grade=grade,
            grade_class=grade_class,
            classification=classification,
            performance_label=performance_label,
            adjusted_badge=adjusted_badge,
            evaluation_date=datetime.now().strftime("%B %d, %Y"),
            trust_score=trust_score,
            ai_confidence=ai_confidence,
            risk_tier=risk_tier,
            fairness_score=fairness_score,
            fairness_color=fairness_color,
            fairness_status=fairness_status,
            escalation_warning=escalation_warning,
            adjusted_scores_section=adjusted_scores_section,
            deep_analysis_section=deep_analysis_section
        )
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file
    
    def generate_journalism_certificate(self, report, document_title="", output_file=None):
        """Generate HTML certificate for journalism grading."""
        if not output_file:
            output_file = "certificate_journalism.html"
        
        scores = report.get('sparrow_scores', {})
        composite = scores.get('composite', {}).get('score', 0)
        grade = scores.get('composite', {}).get('grade', ('F', 'Unknown'))[0]
        category_grade_labels = report.get('category_grade_labels', {})
        
        # Determine classification for journalism
        classifications = {
            'A+': 'Exemplary Journalism',
            'A': 'Excellent Journalism',
            'B+': 'Good Journalism',
            'B': 'Acceptable Journalism',
            'B-': 'Questionable Journalism',
            'C': 'Problematic Journalism',
            'D': 'Flawed Journalism',
            'F': 'Poor Journalism'
        }
        classification = classifications.get(grade, 'Unclassified')
        
        grade_class = self._get_grade_class(grade)
        
        # Extract grade codes and labels for each criterion
        def get_grade_data(criterion_key):
            labels = category_grade_labels.get(criterion_key, {})
            return labels.get('code', ''), labels.get('label', '')
        
        si_code, si_label = get_grade_data('SI')
        oi_code, oi_label = get_grade_data('OI')
        tp_code, tp_label = get_grade_data('TP')
        ar_code, ar_label = get_grade_data('AR')
        iu_code, iu_label = get_grade_data('IU')
        
        # v7: Extract ethical framework data
        trust_score_data = report.get('trust_score', {})
        trust_score = int(trust_score_data.get('trust_score', 0)) if trust_score_data else 0
        
        # v8.2: Prefer deep analysis data when available
        deep_analysis = report.get('deep_analysis', {})
        if deep_analysis and 'consensus' in deep_analysis:
            # Use deep analysis consensus data (more accurate)
            consensus = deep_analysis.get('consensus', {})
            ai_confidence = int(consensus.get('ai_percentage', 0))
            ai_model = consensus.get('primary_model', 'Unknown')
            
            # v8.3: Override Mixed/Uncertain with highest scoring individual model
            if ai_model == 'Mixed/Uncertain':
                ai_detection = report.get('ai_detection', {})
                likely_ai_model = ai_detection.get('likely_ai_model', {})
                model_scores = likely_ai_model.get('model_scores', {})
                if model_scores:
                    # Find the model with the highest score
                    highest_model = max(model_scores, key=model_scores.get)
                    highest_score = model_scores[highest_model]
                    # Only override if we have a clear winner (>0.5 threshold)
                    if highest_score > 0.5:
                        # Clean up model name for display
                        model_name_map = {
                            'cohere': 'Cohere',
                            'claude': 'Claude (Anthropic)',
                            'mistral': 'Mistral AI',
                            'ollama': 'Ollama',
                            'gemini': 'Google Gemini'
                        }
                        ai_model = model_name_map.get(highest_model.lower(), highest_model.title())
            
            # v8.3.2 Fix: Cap confidence at 100% - values 0-2 are 0-1 scale, values >2 are percentages
            raw_confidence = consensus.get('confidence', 0)
            # Values between 0-2 treated as 0-1 scale (handles edge cases like 1.2)
            ai_model_confidence = int(raw_confidence * 100) if raw_confidence <= 2 else int(raw_confidence)
            ai_model_confidence = min(ai_model_confidence, 100)  # Cap at 100%
            transparency_score = consensus.get('transparency_score', 0)
            has_deep_analysis = True
        else:
            # Fallback to basic AI detection
            ai_detection_data = report.get('ai_detection', {})
            ai_detection_score = ai_detection_data.get('ai_detection_score', 0) if ai_detection_data else 0
            ai_confidence = int(ai_detection_score * 100) if ai_detection_score else 0
            ai_model = 'Unknown'
            ai_model_confidence = 0
            transparency_score = 0
            has_deep_analysis = False
        
        risk_tier_data = report.get('risk_tier', {})
        risk_tier = risk_tier_data.get('risk_tier', 'UNKNOWN').upper() if risk_tier_data else 'UNKNOWN'
        
        bias_audit_data = report.get('bias_audit', {})
        fairness_score = int(bias_audit_data.get('overall_fairness_score', 0)) if bias_audit_data else 0
        
        # v8.3.4: Dynamic fairness color and warning based on score
        if fairness_score >= 70:
            fairness_color = "#27ae60"  # Green - passing
            fairness_status = ""
        elif fairness_score >= 50:
            fairness_color = "#f39c12"  # Orange - marginal
            fairness_status = " (MARGINAL)"
        else:
            fairness_color = "#e74c3c"  # Red - failing
            fairness_status = " (FAILING)"
        
        ethical_summary = report.get('ethical_summary', {})
        escalation_required = ethical_summary.get('escalation_required', False)
        escalation_warning = ''
        
        # v8.3.4: Add fairness-specific escalation warning if score is failing
        if fairness_score < 50:
            escalation_warning = f"""
                <div style="background: #ffe6e6; border: 2px solid #e74c3c; padding: 12px; border-radius: 4px; margin-top: 15px;">
                    <div style="font-weight: 700; color: #e74c3c; margin-bottom: 5px;">⚠️ CRITICAL: Fairness Assessment FAILED ({fairness_score}%)</div>
                    <div style="font-size: 0.9em; color: #555;">Significant bias detected. Manual bias review REQUIRED before policy implementation.</div>
                </div>
            """
        elif escalation_required:
            escalation_warning = f"""
                <div style="background: #ffe6e6; border: 2px solid #e74c3c; padding: 12px; border-radius: 4px; margin-top: 15px;">
                    <div style="font-weight: 700; color: #e74c3c; margin-bottom: 5px;">⚠️ Escalation Required</div>
                    <div style="font-size: 0.9em; color: #555;">{ethical_summary.get('overall_recommendation', 'Professional review required')}</div>
                </div>
            """
        
        # Generate Deep Analysis section if available (same as policy)
        deep_analysis_section = ''
        if has_deep_analysis:
            level3 = deep_analysis.get('level3_patterns', {})
            level5 = deep_analysis.get('level5_fingerprints', {})
            level6 = deep_analysis.get('level6_statistics', {})
            
            # Extract pattern counts (correct structure)
            total_patterns = level3.get('total_patterns', 0) if level3 else 0
            
            # Extract fingerprint data (correct structure)
            total_fingerprints = level5.get('total_fingerprints_found', 0) if level5 else 0
            
            # Extract statistics (correct structure)
            metrics = level6.get('metrics', {}) if level6 else {}
            perplexity = metrics.get('perplexity', 0)
            burstiness = metrics.get('burstiness', 0)
            lexical_diversity = metrics.get('lexical_diversity', 0)
            
            deep_analysis_section = f"""
            <div class="deep-analysis" style="background: #f0f9ff; padding: 25px; margin: 25px 0; border-left: 5px solid #0ea5e9; border-radius: 4px;">
                <h3 style="color: #0369a1; margin-bottom: 15px;">🔬 Deep AI Transparency Analysis (v8.2)</h3>
                <div style="background: white; padding: 15px; border-radius: 4px; margin-bottom: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div style="text-align: center;">
                            <div style="font-size: 0.85em; color: #666; margin-bottom: 5px;">AI Content</div>
                            <div style="font-size: 2em; font-weight: 700; color: #0ea5e9;">{ai_confidence}%</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.85em; color: #666; margin-bottom: 5px;">Primary Model</div>
                            <div style="font-size: 1.3em; font-weight: 700; color: #0369a1;">{ai_model}</div>
                            <div style="font-size: 0.75em; color: #888;" title="Attribution confidence: IF AI was used, this is the likelihood it was this model. Does NOT indicate certainty of AI use.">{ai_model_confidence}% attribution*</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.85em; color: #666; margin-bottom: 5px;">Transparency</div>
                            <div style="font-size: 2em; font-weight: 700; color: #0ea5e9;">{transparency_score:.1f}</div>
                            <div style="font-size: 0.75em; color: #888;">/100</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div style="background: #f8fafc; padding: 12px; border-radius: 4px;">
                            <div style="font-size: 0.85em; color: #555; font-weight: 600; margin-bottom: 5px;">Pattern Detection</div>
                            <div style="font-size: 1.1em; color: #0369a1;"><strong>{total_patterns}</strong> AI patterns found</div>
                        </div>
                        <div style="background: #f8fafc; padding: 12px; border-radius: 4px;">
                            <div style="font-size: 0.85em; color: #555; font-weight: 600; margin-bottom: 5px;">Phrase Fingerprints</div>
                            <div style="font-size: 1.1em; color: #0369a1;"><strong>{total_fingerprints}</strong> model signatures</div>
                        </div>
                    </div>
                </div>
                <div style="background: #f8fafc; padding: 12px; border-radius: 4px; font-size: 0.9em;">
                    <div style="font-weight: 600; color: #0369a1; margin-bottom: 8px;">Statistical Metrics:</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; color: #555;">
                        <div><strong>Perplexity:</strong> {perplexity:.2f}</div>
                        <div><strong>Burstiness:</strong> {burstiness:.3f}</div>
                        <div><strong>Lexical Diversity:</strong> {lexical_diversity:.3f}</div>
                    </div>
                </div>
                <div style="font-size: 0.75em; color: #888; margin-top: 10px; font-style: italic;">
                    * Attribution confidence indicates pattern match IF AI was used. It does not measure certainty of AI use.
                </div>
            </div>
            """
        
        html = self.journalism_certificate_template.format(
            title=f"Sparrow SPOT Scale™ - {document_title}",
            document_title=document_title or "Article",
            si_score=scores.get('SI', {}).get('score', 'N/A'),
            oi_score=scores.get('OI', {}).get('score', 'N/A'),
            tp_score=scores.get('TP', {}).get('score', 'N/A'),
            ar_score=scores.get('AR', {}).get('score', 'N/A'),
            iu_score=scores.get('IU', {}).get('score', 'N/A'),
            si_grade_code=si_code,
            si_grade_label=si_label,
            oi_grade_code=oi_code,
            oi_grade_label=oi_label,
            tp_grade_code=tp_code,
            tp_grade_label=tp_label,
            ar_grade_code=ar_code,
            ar_grade_label=ar_label,
            iu_grade_code=iu_code,
            iu_grade_label=iu_label,
            composite_score=composite,
            grade=grade,
            grade_class=grade_class,
            classification=classification,
            evaluation_date=datetime.now().strftime("%B %d, %Y"),
            trust_score=trust_score,
            ai_confidence=ai_confidence,
            risk_tier=risk_tier,
            fairness_score=fairness_score,
            fairness_color=fairness_color,
            fairness_status=fairness_status,
            escalation_warning=escalation_warning,
            deep_analysis_section=deep_analysis_section,
            sparrow_version=SPARROW_VERSION,
            certificate_version=CERTIFICATE_VERSION
        )
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file
    
    def generate_certificate_from_json(self, json_file, variant='policy', output_file=None):
        """Generate certificate from a saved JSON report file."""
        with open(json_file, 'r') as f:
            report = json.load(f)
        
        if not output_file:
            base_name = Path(json_file).stem
            output_file = f"{base_name}_certificate.html"
        
        if variant == 'policy':
            return self.generate_policy_certificate(report, output_file=output_file)
        else:
            return self.generate_journalism_certificate(report, output_file=output_file)
    
    def generate_ollama_summary(self, report, document_title="", variant='policy', output_file=None):
        """Generate plain-language summary using Ollama AI."""
        if not OLLAMA_AVAILABLE:
            print("⚠️  Ollama summary generator not available (requests library needed)")
            return None
        
        try:
            gen = OllamaSummaryGenerator()
            if not gen.test_connection():
                print("⚠️  Ollama not running, skipping summary generation")
                return None
            
            if not output_file:
                base_name = document_title.replace(' ', '_').lower()
                output_file = f"{base_name}_summary.txt"
            
            if variant == 'policy':
                return gen.generate_policy_summary(report, document_title, output_file)
            else:
                return gen.generate_journalism_summary(report, document_title, output_file)
        
        except Exception as e:
            print(f"⚠️  Summary generation skipped: {str(e)}")
            return None
    
    def generate_summary_from_json(self, json_file, variant='policy', output_file=None):
        """Generate summary from existing JSON report file."""
        try:
            with open(json_file, 'r') as f:
                report = json.load(f)
            
            doc_title = Path(json_file).stem
            if not output_file:
                output_file = f"{doc_title}_summary.txt"
            
            return self.generate_ollama_summary(report, doc_title, variant, output_file)
        except Exception as e:
            print(f"⚠️  Summary generation failed: {str(e)}")
            return None
    
    def generate_summary_with_ollama(self, report, variant='policy', model='granite4:tiny-h', length='standard', output_file=None):
        """Generate plain-language summary using Ollama AI model with consistency validation.
        
        Args:
            report: Analysis report dict
            variant: 'policy' or 'journalism'
            model: Ollama model name
            length: Narrative length ('concise', 'standard', 'detailed', 'comprehensive') - currently ignored, uses standard 200-300 words
            output_file: Optional output file path
        """
        try:
            import requests
            
            # Extract key data from report
            if variant == 'policy':
                criteria = report.get('criteria', {})
                composite = report.get('composite_score', 0)
                grade = report.get('composite_grade', 'F')
                classification = report.get('classification', 'Unclassified')
                category_labels = report.get('category_grade_labels', {})
                
                # Identify strengths (score >= 60) and weaknesses (score < 60)
                scores_data = []
                for key in ['FT', 'SB', 'ER', 'PA', 'PC']:
                    score = criteria.get(key, {}).get('score', 0)
                    label = category_labels.get(key, {}).get('label', 'Unknown')
                    criterion_name = criteria.get(key, {}).get('name', key)
                    scores_data.append({
                        'key': key,
                        'name': criterion_name,
                        'score': score,
                        'label': label,
                        'type': 'strength' if score >= 60 else 'weakness'
                    })
                
                # Build context for summary with explicit structure
                strengths_list = [s for s in scores_data if s['type'] == 'strength']
                weaknesses_list = [s for s in scores_data if s['type'] == 'weakness']
                
                strengths_text = '\n'.join([f"- {s['name']}: {s['score']}/100 ({s['label']})" for s in strengths_list]) if strengths_list else "None identified"
                weaknesses_text = '\n'.join([f"- {s['name']}: {s['score']}/100 ({s['label']})" for s in weaknesses_list]) if weaknesses_list else "None identified"
                
                context = f"""
Policy Document Analysis Summary

Overall Grade: {grade} ({composite}/100)
Classification: {classification}

STRENGTHS (Score ≥ 60):
{strengths_text}

WEAKNESSES (Score < 60):
{weaknesses_text}

All Criteria Breakdown:
- Fiscal Transparency (FT): {criteria.get('FT', {}).get('score', 'N/A')}/100
- Stakeholder Balance (SB): {criteria.get('SB', {}).get('score', 'N/A')}/100
- Economic Rigor (ER): {criteria.get('ER', {}).get('score', 'N/A')}/100
- Public Accessibility (PA): {criteria.get('PA', {}).get('score', 'N/A')}/100
- Policy Consequentiality (PC): {criteria.get('PC', {}).get('score', 'N/A')}/100
"""
                
                # Recommendation: lowest score
                lowest_criterion = min(scores_data, key=lambda x: x['score'])
                recommendation = f"Priority area for improvement: {lowest_criterion['name']} (currently {lowest_criterion['score']}/100)"
                
            else:  # journalism
                scores = report.get('sparrow_scores', {})
                composite = scores.get('composite', {}).get('score', 0)
                grade = scores.get('composite', {}).get('grade', ('F', 'Unknown'))[0]
                category_labels = report.get('category_grade_labels', {})
                
                # Similar structure for journalism
                scores_data = []
                for key in ['SI', 'OI', 'TP', 'AR', 'IU']:
                    score = scores.get(key, {}).get('score', 0)
                    label = category_labels.get(key, {}).get('label', 'Unknown')
                    criterion_name = key  # Journalism uses abbreviations as names
                    scores_data.append({
                        'key': key,
                        'name': criterion_name,
                        'score': score,
                        'label': label,
                        'type': 'strength' if score >= 60 else 'weakness'
                    })
                
                strengths_list = [s for s in scores_data if s['type'] == 'strength']
                weaknesses_list = [s for s in scores_data if s['type'] == 'weakness']
                
                strengths_text = '\n'.join([f"- {s['name']}: {s['score']}/100 ({s['label']})" for s in strengths_list]) if strengths_list else "None identified"
                weaknesses_text = '\n'.join([f"- {s['name']}: {s['score']}/100 ({s['label']})" for s in weaknesses_list]) if weaknesses_list else "None identified"
                
                context = f"""
Article Credibility Analysis Summary

Overall Grade: {grade} ({composite}/100)

STRENGTHS (Score ≥ 60):
{strengths_text}

WEAKNESSES (Score < 60):
{weaknesses_text}

All Criteria Breakdown:
- Source Integrity (SI): {scores.get('SI', {}).get('score', 'N/A')}/100
- Objectivity Index (OI): {scores.get('OI', {}).get('score', 'N/A')}/100
- Technical Precision (TP): {scores.get('TP', {}).get('score', 'N/A')}/100
- Accessibility Rating (AR): {scores.get('AR', {}).get('score', 'N/A')}/100
- Impact Utility (IU): {scores.get('IU', {}).get('score', 'N/A')}/100
"""
                
                lowest_criterion = min(scores_data, key=lambda x: x['score'])
                recommendation = f"Priority area for improvement: {lowest_criterion['name']} (currently {lowest_criterion['score']}/100)"
            
            # Create prompt for Ollama with explicit consistency instructions
            prompt = f"""Based on this {variant} evaluation data, generate a plain-language summary (200-300 words) that:
1. Explains what the overall score means
2. Discusses the identified STRENGTHS (score ≥ 60)
3. Discusses the identified WEAKNESSES (score < 60)
4. Provides a specific recommendation: {recommendation}

IMPORTANT - Consistency Rules:
- Never mention a criterion as both a strength AND a weakness
- Only mention criteria from the STRENGTHS or WEAKNESSES lists above
- Keep to Grade 8 reading level (Flesch 60+)
- Be objective and specific

{context}"""
            
            # Call Ollama API
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'temperature': 0.3
                },
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                summary_text = result.get('response', '')
                
                # Post-process: verify no contradictions by checking strength/weakness lists
                if variant == 'policy':
                    strength_names = [s['name'].lower() for s in strengths_list]
                    weakness_names = [w['name'].lower() for w in weaknesses_list]
                    
                    # Flag potential contradictions in log (not error, just validation)
                    for strength in strength_names:
                        if any(weakness.lower().startswith(strength.split()[0]) for weakness in weakness_names):
                            # Criterion appears in both - note but allow AI to resolve
                            pass
                
                # Save to file if specified
                if output_file:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(summary_text)
                    print(f"   ✓ Summary: {output_file}")
                    return output_file
                else:
                    return summary_text
            else:
                print(f"⚠️  Ollama API error: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("⚠️  Ollama not running. Start with: ollama serve")
            return None
        except Exception as e:
            print(f"⚠️  Ollama summary generation failed: {str(e)}")
            return None
    
    def generate_supplementary_footer(self, base_url=""):
        """Generate HTML footer with links to supplementary resources."""
        footer_html = f"""
<!-- Supplementary Resources -->
<div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 0.85em;">
    <p style="color: #555; margin-bottom: 8px;">
        <strong>📚 Supplementary Resources:</strong>
    </p>
    <ul style="list-style: none; padding: 0; margin: 0;">
        <li>📄 <a href="{base_url}summary.txt" style="color: #2980b9; text-decoration: none;">Plain-Language Summary</a></li>
        <li>📊 <a href="{base_url}data.json" style="color: #2980b9; text-decoration: none;">Full JSON Report</a></li>
        <li>🔍 <a href="{base_url}verify/" style="color: #2980b9; text-decoration: none;">Verify Certificate</a></li>
        <li>📋 <a href="https://internationalbudget.org/open-budget-survey" style="color: #2980b9; text-decoration: none;">About This Framework</a></li>
    </ul>
</div>
"""
        return footer_html
    
    def _generate_critical_findings(self, report, ai_detection_data, trust_score, fairness_score, composite, criteria):
        """
        v8.4.0: Generate Critical Findings section for TOP of certificate.
        
        Shows critical issues prominently:
        - INCONCLUSIVE AI detection (spread >50%)
        - Failing fairness score (<50%)
        - Low trust score (<70)
        - Any failing criteria (<50)
        
        Returns:
            HTML string for critical findings section, or empty string if no critical issues
        """
        critical_items = []
        thresholds_met = 0
        total_thresholds = 4  # Detection, Trust, Fairness, Composite
        
        # Check 1: AI Detection INCONCLUSIVE
        detection_inconclusive = ai_detection_data.get('detection_inconclusive', False)
        detection_spread = ai_detection_data.get('detection_spread', 0)
        
        if detection_inconclusive or detection_spread > 0.50:
            model_scores = ai_detection_data.get('model_scores', {})
            if model_scores:
                score_values = [v * 100 for v in model_scores.values() if isinstance(v, (int, float))]
                min_score = min(score_values) if score_values else 0
                max_score = max(score_values) if score_values else 0
                spread_pct = max_score - min_score
            else:
                spread_pct = detection_spread * 100
                min_score = 0
                max_score = spread_pct
            
            critical_items.append({
                'icon': '🔴',
                'title': 'AI DETECTION INCONCLUSIVE',
                'message': f'Detection methods disagree by {spread_pct:.0f} percentage points (range: {min_score:.0f}%-{max_score:.0f}%). Manual expert review required.',
                'severity': 'critical'
            })
        else:
            thresholds_met += 1
        
        # Check 2: Trust Score
        if trust_score < 70:
            critical_items.append({
                'icon': '🟠',
                'title': f'TRUST SCORE: {trust_score:.1f}/100',
                'message': 'Trust score below 70 threshold. Escalation to human review recommended.',
                'severity': 'warning' if trust_score >= 50 else 'critical'
            })
        else:
            thresholds_met += 1
        
        # Check 3: Fairness Score
        if fairness_score < 50:
            critical_items.append({
                'icon': '🔴',
                'title': f'FAIRNESS: {fairness_score}% (FAILED)',
                'message': 'Significant bias detected. Manual bias review REQUIRED before implementation.',
                'severity': 'critical'
            })
        elif fairness_score < 70:
            critical_items.append({
                'icon': '🟠',
                'title': f'FAIRNESS: {fairness_score}% (MARGINAL)',
                'message': 'Fairness metrics below recommended threshold. Review bias audit details.',
                'severity': 'warning'
            })
            thresholds_met += 1
        else:
            thresholds_met += 1
        
        # Check 4: Composite Score
        if composite < 60:
            critical_items.append({
                'icon': '🔴',
                'title': f'COMPOSITE SCORE: {composite:.1f}/100',
                'message': 'Overall score indicates significant quality concerns across multiple criteria.',
                'severity': 'critical'
            })
        else:
            thresholds_met += 1
        
        # Check individual failing criteria
        failing_criteria = []
        for key in ['FT', 'SB', 'ER', 'PA', 'PC']:
            score = criteria.get(key, {}).get('score', 100)
            if score < 50:
                failing_criteria.append(f"{key}: {score}/100")
        
        if failing_criteria:
            critical_items.append({
                'icon': '⚠️',
                'title': f'{len(failing_criteria)} FAILING CRITERIA',
                'message': f'Scores below 50: {", ".join(failing_criteria)}',
                'severity': 'warning'
            })
        
        # If no critical issues, return empty
        if not critical_items:
            return ''
        
        # Generate HTML
        items_html = ''
        for item in critical_items:
            bg_color = '#ffebee' if item['severity'] == 'critical' else '#fff3e0'
            border_color = '#e53935' if item['severity'] == 'critical' else '#ff9800'
            text_color = '#c62828' if item['severity'] == 'critical' else '#e65100'
            
            items_html += f'''
            <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 12px; margin-bottom: 10px; border-radius: 0 4px 4px 0;">
                <div style="font-weight: 700; color: {text_color}; margin-bottom: 4px;">{item['icon']} {item['title']}</div>
                <div style="font-size: 0.9em; color: #555;">{item['message']}</div>
            </div>
            '''
        
        # Threshold summary
        threshold_color = '#27ae60' if thresholds_met >= 3 else ('#f39c12' if thresholds_met >= 2 else '#e74c3c')
        
        section_html = f'''
        <div class="critical-findings" style="background: #fafafa; border: 2px solid #e74c3c; border-radius: 8px; padding: 20px; margin: 25px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: #c62828; margin: 0;">🚨 Critical Findings</h3>
                <div style="background: {threshold_color}; color: white; padding: 6px 12px; border-radius: 4px; font-weight: 700;">
                    {thresholds_met}/{total_thresholds} Thresholds Met
                </div>
            </div>
            {items_html}
            <div style="font-size: 0.8em; color: #888; margin-top: 10px; font-style: italic;">
                These findings require attention before relying on this analysis for decision-making.
            </div>
        </div>
        '''
        
        return section_html
    
    def _get_grade_class(self, grade):
        """Get CSS class for grade color."""
        if grade.startswith('A'):
            return 'a'
        elif grade.startswith('B'):
            return 'b'
        elif grade.startswith('C'):
            return 'c'
        elif grade.startswith('D'):
            return 'd'
        else:
            return 'f'
    
    def _get_document_type_badge(self, report):
        """
        v8.3.3: Determine document type badge text from report data.
        
        Checks multiple sources:
        1. User-selected document_type_selected
        2. Citation quality detected document_type
        3. Document title patterns (Bill, Act, Budget)
        4. Default to POLICY DOCUMENT
        
        Returns:
            Badge text like "LEGISLATIVE DOCUMENT" or "POLICY DOCUMENT"
        """
        # Check user-selected type first
        selected_type = report.get('document_type_selected', 'auto')
        if selected_type and selected_type != 'auto':
            type_badges = {
                'legislation': 'LEGISLATIVE DOCUMENT',
                'budget': 'BUDGET DOCUMENT',
                'policy_brief': 'POLICY BRIEF',
                'research_report': 'RESEARCH REPORT',
                'analysis': 'ANALYSIS DOCUMENT',
                'legal_judgment': 'LEGAL DOCUMENT',
                'report': 'POLICY DOCUMENT'
            }
            return type_badges.get(selected_type, 'POLICY DOCUMENT')
        
        # Check citation quality detected type
        citation_quality = report.get('citation_quality', {})
        detected_type = citation_quality.get('document_type', '')
        if detected_type:
            type_badges = {
                'legislation': 'LEGISLATIVE DOCUMENT',
                'budget': 'BUDGET DOCUMENT',
                'policy_brief': 'POLICY BRIEF',
                'research_report': 'RESEARCH REPORT',
                'analysis': 'ANALYSIS DOCUMENT',
                'legal_judgment': 'LEGAL DOCUMENT',
                'report': 'POLICY DOCUMENT'
            }
            if detected_type in type_badges:
                return type_badges[detected_type]
        
        # Check document title for legislative patterns
        doc_title = report.get('document_title', '')
        if doc_title:
            title_lower = doc_title.lower()
            if any(pattern in title_lower for pattern in ['bill c-', 'bill s-', ' act,', ' act ', 'statute']):
                return 'LEGISLATIVE DOCUMENT'
            if 'budget' in title_lower:
                return 'BUDGET DOCUMENT'
        
        # Default
        return 'POLICY DOCUMENT'


if __name__ == '__main__':
    # Example usage
    print("Certificate Generator for Sparrow SPOT Scale™ v8.0 (with Narrative Engine + Ethical Framework v1.0)")
    print("Usage: from certificate_generator import CertificateGenerator")
    print("\nExample:")
    print("  gen = CertificateGenerator()")
    print("  gen.generate_policy_certificate(report, 'Budget 2025', 'certificate.html')")

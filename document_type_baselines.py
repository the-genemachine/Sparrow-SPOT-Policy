"""
Document Type Baselines for Sparrow SPOT Scale™ v8.4.0

Each document type has its own conventions that may trigger false positives in AI detection.
This module provides calibration for:

1. LEGISLATION - Parliamentary bills, acts, statutes
2. BUDGET - Fiscal documents, appropriations, estimates
3. LEGAL_JUDGMENT - Court decisions, rulings, opinions
4. POLICY_BRIEF - Policy proposals, white papers
5. RESEARCH_REPORT - Academic/institutional research
6. NEWS_ARTICLE - Journalism, press releases
7. ANALYSIS - Audits, evaluations, assessments
8. REPORT - General government/corporate reports

Each baseline includes:
- Expected patterns for that document type
- Score adjustments to reduce false positives
- Confidence penalties based on domain characteristics
- Domain-specific warnings

v8.4.0 Enhancement: Stronger Legislative Calibration
- Increased legislative adjustment from -30% to -50% when pattern count >500
- Legislative documents heavily use enumeration, cross-references, and formulaic
  language that is REQUIRED by drafting conventions (not AI-generated)
- Stakeholder focus, structured lists, and enumeration are EXCLUDED from AI signals
- Fixes Bill-C15-12 discrepancy: legislation falsely flagged as AI content

Reference: "The AI Detection Paradox" analysis identified document-type calibration
as essential for accurate AI detection.
"""

import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class DocumentType(Enum):
    """Supported document types with detection calibration."""
    LEGISLATION = "legislation"
    BUDGET = "budget"
    LEGAL_JUDGMENT = "legal_judgment"
    POLICY_BRIEF = "policy_brief"
    RESEARCH_REPORT = "research_report"
    NEWS_ARTICLE = "news_article"
    ANALYSIS = "analysis"
    REPORT = "report"
    UNKNOWN = "unknown"


@dataclass
class BaselineResult:
    """Result of baseline pattern analysis."""
    document_type: str
    is_specialized: bool
    pattern_count: int
    patterns_by_category: Dict[str, int]
    ai_score_adjustment: float  # Negative to reduce AI score
    confidence_penalty: float   # 0-1, reduces confidence
    warnings: List[str]
    detected_conventions: List[str]


class DocumentTypeBaseline:
    """
    Base class for document type-specific pattern detection.
    Each document type has conventions that may be falsely flagged as AI.
    """
    
    def __init__(self):
        self.version = "8.3.3"
        self.patterns: Dict[str, List[str]] = {}
        self.compiled: Dict[str, List[re.Pattern]] = {}
        
    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        for category, patterns in self.patterns.items():
            self.compiled[category] = [
                re.compile(p, re.IGNORECASE | re.MULTILINE) 
                for p in patterns
            ]
    
    def count_patterns(self, text: str) -> Dict[str, int]:
        """Count pattern matches by category."""
        counts = {}
        for category, patterns in self.compiled.items():
            count = 0
            for pattern in patterns:
                count += len(pattern.findall(text))
            counts[category] = count
        return counts
    
    def analyze(self, text: str) -> BaselineResult:
        """Analyze text for document-type-specific patterns."""
        raise NotImplementedError


class LegislationBaseline(DocumentTypeBaseline):
    """
    Baseline patterns for legislative documents.
    Based on Driedger's Manual of Instructions for Legislative and Legal Writing.
    
    v8.4.0: Enhanced calibration with stronger score adjustments.
    Legislative documents MUST use enumeration, cross-references, and formulaic
    language by convention - these are NOT AI signatures.
    """
    
    def __init__(self):
        super().__init__()
        self.patterns = {
            'enumeration': [
                r'\([a-z]\)',                    # (a), (b), (c)
                r'\([a-z]\.\d+\)',               # (a.1), (b.2)
                r'\(i+\)',                       # (i), (ii), (iii)
                r'^\s*\d+\.\s',                  # 1. 2. 3.
                r'paragraph\s+\([a-z]\)',
                r'subparagraph\s+\([a-z]\)\(i+\)',
            ],
            'section_structure': [
                r'Section\s+\d+',
                r'Subsection\s+\d+\(\d+\)',
                r'Part\s+[IVXLC]+',
                r'Division\s+\d+',
                r'Schedule\s+[A-Z0-9]+',
            ],
            'legislative_phrases': [
                r'for the purposes? of this (Act|section|subsection|Part)',
                r'notwithstanding (anything|any other|the)',
                r'subject to (this section|subsection|the regulations?)',
                r'shall come into force',
                r'is deemed to have come into force',
                r'no person (shall|may)',
                r'every person (shall|who)',
            ],
            'amendment_phrases': [
                r'is (hereby )?amended',
                r'is (hereby )?repealed',
                r'is replaced (by|with)',
                r'by (adding|deleting|striking out|replacing)',
            ],
            'common_law_terms': [
                r'\bnotwithstanding\b',
                r'\bhereby\b',
                r'\bthereof\b',
                r'\btherein\b',
                r'\bpursuant to\b',
            ],
            # v8.4.0: Patterns that are EXCLUDED from AI signals (conventions only)
            'convention_only': [
                r'stakeholder',                  # Legislative focus on stakeholders
                r'whereas',                      # Preamble language
                r'Her Majesty|His Majesty',      # Crown references
                r'enacted as follows',           # Enacting formula
            ],
        }
        self._compile_patterns()
    
    def analyze(self, text: str) -> BaselineResult:
        counts = self.count_patterns(text)
        total = sum(counts.values())
        
        # Determine if text is legislative
        is_legislative = (
            counts.get('enumeration', 0) > 10 or
            counts.get('section_structure', 0) > 5 or
            counts.get('amendment_phrases', 0) > 5
        )
        
        # v8.4.0: Stronger adjustments for legislative documents
        # Legislative conventions are NOT AI signatures
        if total > 500:
            adjustment = -0.50  # v8.4.0: Increased from -0.30 to -0.50
            penalty = 0.50      # v8.4.0: Increased from 0.40 to 0.50
        elif total > 200:
            adjustment = -0.35  # v8.4.0: Increased from -0.20 to -0.35
            penalty = 0.40      # v8.4.0: Increased from 0.30 to 0.40
        elif total > 100:
            adjustment = -0.25  # v8.4.0: Increased from -0.15 to -0.25
            penalty = 0.30      # v8.4.0: Increased from 0.20 to 0.30
        elif total > 50:
            adjustment = -0.15  # v8.4.0: Increased from -0.10 to -0.15
            penalty = 0.20      # v8.4.0: Increased from 0.10 to 0.20
        else:
            adjustment = 0.0
            penalty = 0.0
        
        warnings = []
        conventions = []
        
        if is_legislative:
            warnings.append(
                "📋 LEGISLATIVE TEXT: Uses standard drafting conventions (enumerated "
                "provisions, legal terminology) that are REQUIRED by law. These patterns "
                "are NOT AI signatures. AI detection is less reliable for this document type."
            )
            conventions.append("Parliamentary/statutory drafting format")
            
        if counts.get('amendment_phrases', 0) > 30:
            warnings.append(
                "📝 AMENDING ACT: Heavy use of amendment language ('is replaced by', "
                "'is amended') is REQUIRED for budget implementation and omnibus bills. "
                "This is a drafting convention, NOT an AI signature."
            )
            conventions.append("Budget implementation/omnibus bill structure")
            
        # v8.4.0: Add explicit note about enumeration being excluded
        if counts.get('enumeration', 0) > 50:
            warnings.append(
                "🔢 LEGISLATIVE ENUMERATION: Heavy use of (a), (b), (c) and (i), (ii), (iii) "
                "is REQUIRED by legislative drafting rules. This is NOT an indicator of "
                "AI-generated content."
            )
            conventions.append("Required enumeration format")
        
        return BaselineResult(
            document_type="legislation",
            is_specialized=is_legislative,
            pattern_count=total,
            patterns_by_category=counts,
            ai_score_adjustment=adjustment,
            confidence_penalty=penalty,
            warnings=warnings,
            detected_conventions=conventions
        )


class BudgetBaseline(DocumentTypeBaseline):
    """
    Baseline patterns for budget and fiscal documents.
    Budget documents use specific fiscal terminology and formats.
    """
    
    def __init__(self):
        super().__init__()
        self.patterns = {
            'fiscal_terms': [
                r'\$\d+(\.\d+)?\s*(billion|million|thousand)',
                r'(fiscal year|FY)\s*\d{4}',
                r'(appropriation|allocation|expenditure)s?',
                r'(revenue|deficit|surplus|debt)',
                r'(estimates|projections|forecasts?)',
            ],
            'budget_structure': [
                r'Vote\s+\d+',
                r'Program\s+\d+(\.\d+)?',
                r'Main Estimates',
                r'Supplementary Estimates',
                r'Budget\s+\d{4}',
            ],
            'fiscal_phrases': [
                r'year-over-year',
                r'per cent (increase|decrease|change)',
                r'compared to (the )?previous',
                r'(planned|actual) spending',
                r'operating (budget|expenditures)',
                r'capital (budget|expenditures)',
            ],
            'accountability_terms': [
                r'(performance|result)s?\s+(indicator|measure)',
                r'(target|objective|outcome)s?',
                r'(deliverable|milestone)s?',
                r'accountability',
            ],
            'table_indicators': [
                r'\(\d+\)\s*$',  # Table footnotes
                r'^\s*[-–—]\s*$',  # Table separators
                r'Total\s*$',
                r'Subtotal\s*$',
            ],
        }
        self._compile_patterns()
    
    def analyze(self, text: str) -> BaselineResult:
        counts = self.count_patterns(text)
        total = sum(counts.values())
        
        is_budget = (
            counts.get('fiscal_terms', 0) > 10 or
            counts.get('budget_structure', 0) > 3 or
            counts.get('fiscal_phrases', 0) > 5
        )
        
        if total > 300:
            adjustment = -0.25
            penalty = 0.35
        elif total > 150:
            adjustment = -0.15
            penalty = 0.25
        elif total > 75:
            adjustment = -0.10
            penalty = 0.15
        else:
            adjustment = 0.0
            penalty = 0.0
        
        warnings = []
        conventions = []
        
        if is_budget:
            warnings.append(
                "💰 BUDGET DOCUMENT: Uses standardized fiscal terminology and tabular "
                "formats that may appear repetitive but are required for government accounting."
            )
            conventions.append("Treasury Board/government fiscal format")
            
        if counts.get('table_indicators', 0) > 20:
            warnings.append(
                "📊 TABULAR DATA: Contains extensive tables with standardized headers "
                "and footers that may trigger pattern detection."
            )
            conventions.append("Structured financial tables")
        
        return BaselineResult(
            document_type="budget",
            is_specialized=is_budget,
            pattern_count=total,
            patterns_by_category=counts,
            ai_score_adjustment=adjustment,
            confidence_penalty=penalty,
            warnings=warnings,
            detected_conventions=conventions
        )


class LegalJudgmentBaseline(DocumentTypeBaseline):
    """
    Baseline patterns for court decisions and legal judgments.
    Judicial writing has distinct conventions.
    """
    
    def __init__(self):
        super().__init__()
        self.patterns = {
            'case_citations': [
                r'\[\d{4}\]\s+\d+\s+S\.C\.R\.',  # SCR citations
                r'\d{4}\s+SCC\s+\d+',            # SCC citations
                r'\[\d{4}\]\s+\d+\s+F\.C\.',     # Federal Court
                r'v\.\s+[A-Z]',                  # Case names
                r'supra|infra|ibid',
            ],
            'judicial_phrases': [
                r'I (would|must|cannot) (dismiss|allow|conclude)',
                r'(the|this) Court (finds|holds|concludes)',
                r'in my (view|opinion|judgment)',
                r'for (these|the following) reasons',
                r'the (appellant|respondent|applicant)',
            ],
            'legal_structure': [
                r'^\s*\[\d+\]',                  # Paragraph numbers
                r'(REASONS FOR|JUDGMENT)',
                r'(HELD|ORDERED|DISMISSED|ALLOWED)',
                r'(Facts|Issues?|Analysis|Conclusion)',
            ],
            'latin_terms': [
                r'stare decisis',
                r'res judicata',
                r'prima facie',
                r'inter alia',
                r'mutatis mutandis',
            ],
            'procedural_terms': [
                r'(motion|application|appeal)',
                r'(judicial review|certiorari)',
                r'(injunction|mandamus|habeas corpus)',
                r'(plaintiff|defendant|petitioner)',
            ],
        }
        self._compile_patterns()
    
    def analyze(self, text: str) -> BaselineResult:
        counts = self.count_patterns(text)
        total = sum(counts.values())
        
        is_judgment = (
            counts.get('case_citations', 0) > 3 or
            counts.get('judicial_phrases', 0) > 5 or
            counts.get('legal_structure', 0) > 5
        )
        
        if total > 200:
            adjustment = -0.25
            penalty = 0.35
        elif total > 100:
            adjustment = -0.15
            penalty = 0.20
        elif total > 50:
            adjustment = -0.10
            penalty = 0.10
        else:
            adjustment = 0.0
            penalty = 0.0
        
        warnings = []
        conventions = []
        
        if is_judgment:
            warnings.append(
                "⚖️ JUDICIAL DOCUMENT: Uses formulaic legal reasoning structure and "
                "citation conventions that are standard in court decisions."
            )
            conventions.append("Judicial reasoning format")
            
        if counts.get('case_citations', 0) > 10:
            warnings.append(
                "📚 CITATION-HEAVY: Extensive case citations follow standardized formats "
                "that may appear repetitive but are required legal practice."
            )
            conventions.append("Legal citation conventions")
        
        return BaselineResult(
            document_type="legal_judgment",
            is_specialized=is_judgment,
            pattern_count=total,
            patterns_by_category=counts,
            ai_score_adjustment=adjustment,
            confidence_penalty=penalty,
            warnings=warnings,
            detected_conventions=conventions
        )


class PolicyBriefBaseline(DocumentTypeBaseline):
    """
    Baseline patterns for policy briefs and white papers.
    """
    
    def __init__(self):
        super().__init__()
        self.patterns = {
            'policy_structure': [
                r'(Executive Summary|Key (Findings|Recommendations))',
                r'(Background|Context|Introduction)',
                r'(Policy Options?|Recommendations?)',
                r'(Implementation|Next Steps)',
                r'(Conclusion|Summary)',
            ],
            'policy_phrases': [
                r'(stakeholder|affected part(y|ies))',
                r'(policy (option|alternative|recommendation))',
                r'(pros? and cons?|advantages? and disadvantages?)',
                r'(cost[- ]benefit|impact assessment)',
                r'(best practice|lessons learned)',
            ],
            'hedging_language': [
                r'(may|might|could|should) (be|have|require)',
                r'(it is (important|essential|critical) to)',
                r'(consideration should be given)',
                r'(further (study|analysis|research))',
            ],
            'recommendation_markers': [
                r'(recommend(ation)?s?\s*:)',
                r'(we recommend|it is recommended)',
                r'(option \d|alternative \d)',
            ],
        }
        self._compile_patterns()
    
    def analyze(self, text: str) -> BaselineResult:
        counts = self.count_patterns(text)
        total = sum(counts.values())
        
        is_policy = (
            counts.get('policy_structure', 0) > 3 or
            counts.get('policy_phrases', 0) > 5
        )
        
        # Policy briefs have moderate adjustment - hedging IS an AI indicator
        # but structure is conventional
        if total > 100:
            adjustment = -0.10
            penalty = 0.15
        elif total > 50:
            adjustment = -0.05
            penalty = 0.10
        else:
            adjustment = 0.0
            penalty = 0.0
        
        warnings = []
        conventions = []
        
        if is_policy:
            warnings.append(
                "📋 POLICY BRIEF: Uses standard policy analysis structure (options, "
                "recommendations, stakeholder analysis) common to the genre."
            )
            conventions.append("Policy analysis format")
            
        # Note: Hedging language IS a valid AI indicator in policy briefs
        # We don't reduce score for it
        if counts.get('hedging_language', 0) > 20:
            warnings.append(
                "⚠️ HEDGING LANGUAGE: High use of qualifiers ('may', 'could', 'should') "
                "detected. This IS associated with AI but also common in cautious policy writing."
            )
        
        return BaselineResult(
            document_type="policy_brief",
            is_specialized=is_policy,
            pattern_count=total,
            patterns_by_category=counts,
            ai_score_adjustment=adjustment,
            confidence_penalty=penalty,
            warnings=warnings,
            detected_conventions=conventions
        )


class ResearchReportBaseline(DocumentTypeBaseline):
    """
    Baseline patterns for academic and research reports.
    """
    
    def __init__(self):
        super().__init__()
        self.patterns = {
            'academic_structure': [
                r'(Abstract|Introduction|Literature Review)',
                r'(Methodology|Methods|Data)',
                r'(Results|Findings|Discussion)',
                r'(Conclusion|References|Bibliography)',
                r'(Appendix|Annex)\s*[A-Z0-9]?',
            ],
            'citation_patterns': [
                r'\([A-Z][a-z]+,?\s*\d{4}\)',    # (Author, 2024)
                r'\([A-Z][a-z]+\s+et al\.,?\s*\d{4}\)',  # (Smith et al., 2024)
                r'\[\d+\]',                       # [1] numbered refs
                r'(ibid|op\.?\s*cit)',
            ],
            'research_phrases': [
                r'(this (study|research|paper|analysis))',
                r'(we (found|observed|conclude|argue))',
                r'(the (results|findings|data) (show|suggest|indicate))',
                r'(statistically significant|p\s*[<>=]\s*0?\.\d+)',
                r'(sample size|n\s*=\s*\d+)',
            ],
            'methodology_terms': [
                r'(qualitative|quantitative|mixed[- ]method)',
                r'(regression|correlation|ANOVA)',
                r'(interview|survey|questionnaire)',
                r'(hypothesis|null hypothesis)',
            ],
        }
        self._compile_patterns()
    
    def analyze(self, text: str) -> BaselineResult:
        counts = self.count_patterns(text)
        total = sum(counts.values())
        
        is_research = (
            counts.get('academic_structure', 0) > 3 or
            counts.get('citation_patterns', 0) > 10 or
            counts.get('research_phrases', 0) > 5
        )
        
        if total > 150:
            adjustment = -0.15
            penalty = 0.20
        elif total > 75:
            adjustment = -0.10
            penalty = 0.15
        elif total > 30:
            adjustment = -0.05
            penalty = 0.05
        else:
            adjustment = 0.0
            penalty = 0.0
        
        warnings = []
        conventions = []
        
        if is_research:
            warnings.append(
                "🔬 RESEARCH REPORT: Uses standard academic structure (abstract, "
                "methodology, results) and citation conventions."
            )
            conventions.append("Academic/research paper format")
            
        if counts.get('citation_patterns', 0) > 30:
            warnings.append(
                "📚 CITATION-DENSE: Heavy citation use follows academic conventions "
                "that create repetitive patterns."
            )
            conventions.append("Academic citation style")
        
        return BaselineResult(
            document_type="research_report",
            is_specialized=is_research,
            pattern_count=total,
            patterns_by_category=counts,
            ai_score_adjustment=adjustment,
            confidence_penalty=penalty,
            warnings=warnings,
            detected_conventions=conventions
        )


class NewsArticleBaseline(DocumentTypeBaseline):
    """
    Baseline patterns for news articles and journalism.
    """
    
    def __init__(self):
        super().__init__()
        self.patterns = {
            'journalistic_structure': [
                r'^[A-Z][A-Z\s,]+—',              # CITY — dateline
                r'(said|told|according to)',
                r'(reported|announced|stated)',
                r'(in a (statement|press release|interview))',
            ],
            'attribution': [
                r'",?\s+(said|told|added|noted)\s+[A-Z]',
                r'[A-Z][a-z]+\s+(said|told|added)',
                r'(a spokesperson|official|source)\s+(said|told)',
                r'(declined to comment|could not be reached)',
            ],
            'news_phrases': [
                r'(breaking|developing|exclusive)',
                r'(sources (say|indicate|confirm))',
                r'(as (first )?reported by)',
                r'(UPDATE|CORRECTION|EDITOR\'S NOTE)',
            ],
            'temporal_markers': [
                r'(today|yesterday|this (morning|afternoon|week))',
                r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)',
                r'(earlier|later|at the time)',
            ],
        }
        self._compile_patterns()
    
    def analyze(self, text: str) -> BaselineResult:
        counts = self.count_patterns(text)
        total = sum(counts.values())
        
        is_news = (
            counts.get('attribution', 0) > 5 or
            counts.get('journalistic_structure', 0) > 3
        )
        
        # News has minimal adjustment - less formulaic than legal/govt docs
        if total > 50:
            adjustment = -0.05
            penalty = 0.10
        elif total > 25:
            adjustment = -0.03
            penalty = 0.05
        else:
            adjustment = 0.0
            penalty = 0.0
        
        warnings = []
        conventions = []
        
        if is_news:
            warnings.append(
                "📰 NEWS ARTICLE: Uses journalistic conventions (attribution, "
                "inverted pyramid structure) common to professional reporting."
            )
            conventions.append("Journalistic style")
        
        return BaselineResult(
            document_type="news_article",
            is_specialized=is_news,
            pattern_count=total,
            patterns_by_category=counts,
            ai_score_adjustment=adjustment,
            confidence_penalty=penalty,
            warnings=warnings,
            detected_conventions=conventions
        )


class AnalysisReportBaseline(DocumentTypeBaseline):
    """
    Baseline patterns for analysis, audit, and evaluation reports.
    """
    
    def __init__(self):
        super().__init__()
        self.patterns = {
            'analysis_structure': [
                r'(Scope|Objective|Purpose)',
                r'(Findings|Observations)',
                r'(Recommendations|Action Items)',
                r'(Risk|Assessment|Evaluation)',
                r'(Audit|Review|Examination)',
            ],
            'assessment_phrases': [
                r'(we (found|observed|noted|identified))',
                r'(our (review|analysis|assessment) (found|revealed))',
                r'(based on our (review|analysis|testing))',
                r'(in our (opinion|view|assessment))',
            ],
            'rating_indicators': [
                r'(high|medium|low)\s+(risk|priority|impact)',
                r'(satisfactory|unsatisfactory|needs improvement)',
                r'(compliant|non-compliant|partially compliant)',
                r'(strength|weakness|opportunity|threat)',
            ],
            'audit_terms': [
                r'(internal control|segregation of duties)',
                r'(material (weakness|finding))',
                r'(management response|corrective action)',
                r'(follow[- ]up|remediation)',
            ],
        }
        self._compile_patterns()
    
    def analyze(self, text: str) -> BaselineResult:
        counts = self.count_patterns(text)
        total = sum(counts.values())
        
        is_analysis = (
            counts.get('analysis_structure', 0) > 3 or
            counts.get('assessment_phrases', 0) > 5 or
            counts.get('audit_terms', 0) > 3
        )
        
        if total > 100:
            adjustment = -0.15
            penalty = 0.20
        elif total > 50:
            adjustment = -0.10
            penalty = 0.15
        elif total > 25:
            adjustment = -0.05
            penalty = 0.05
        else:
            adjustment = 0.0
            penalty = 0.0
        
        warnings = []
        conventions = []
        
        if is_analysis:
            warnings.append(
                "🔍 ANALYSIS/AUDIT REPORT: Uses standardized assessment structure "
                "and professional auditing terminology."
            )
            conventions.append("Audit/evaluation report format")
            
        if counts.get('rating_indicators', 0) > 10:
            warnings.append(
                "📊 RATING FRAMEWORK: Uses structured rating language (high/medium/low) "
                "that is conventional in assessment reports."
            )
            conventions.append("Risk/rating framework")
        
        return BaselineResult(
            document_type="analysis",
            is_specialized=is_analysis,
            pattern_count=total,
            patterns_by_category=counts,
            ai_score_adjustment=adjustment,
            confidence_penalty=penalty,
            warnings=warnings,
            detected_conventions=conventions
        )


class GeneralReportBaseline(DocumentTypeBaseline):
    """
    Baseline patterns for general government/corporate reports.
    """
    
    def __init__(self):
        super().__init__()
        self.patterns = {
            'report_structure': [
                r'(Table of Contents|Executive Summary)',
                r'(Introduction|Background|Overview)',
                r'(Key (Findings|Highlights|Messages))',
                r'(Appendix|Annex|Attachment)',
            ],
            'corporate_phrases': [
                r'(fiscal year|reporting period)',
                r'(strategic (plan|priority|objective))',
                r'(key performance indicator|KPI)',
                r'(year[- ]over[- ]year|quarter[- ]over[- ]quarter)',
            ],
            'formal_transitions': [
                r'(furthermore|moreover|additionally)',
                r'(in addition|as well as|along with)',
                r'(however|nevertheless|nonetheless)',
                r'(therefore|consequently|as a result)',
            ],
        }
        self._compile_patterns()
    
    def analyze(self, text: str) -> BaselineResult:
        counts = self.count_patterns(text)
        total = sum(counts.values())
        
        is_report = counts.get('report_structure', 0) > 2
        
        # General reports have minimal adjustment
        if total > 75:
            adjustment = -0.05
            penalty = 0.10
        elif total > 40:
            adjustment = -0.03
            penalty = 0.05
        else:
            adjustment = 0.0
            penalty = 0.0
        
        warnings = []
        conventions = []
        
        if is_report:
            warnings.append(
                "📄 FORMAL REPORT: Uses standard report structure and formal "
                "transition language common in official documents."
            )
            conventions.append("Formal report format")
        
        return BaselineResult(
            document_type="report",
            is_specialized=is_report,
            pattern_count=total,
            patterns_by_category=counts,
            ai_score_adjustment=adjustment,
            confidence_penalty=penalty,
            warnings=warnings,
            detected_conventions=conventions
        )


class DocumentTypeDetector:
    """
    Main class for document type detection and baseline calibration.
    Automatically detects document type and applies appropriate baseline.
    
    v8.4.0: Enhanced calibration with stronger adjustments for legislative documents.
    """
    
    def __init__(self):
        self.version = "8.4.0"
        self.baselines = {
            'legislation': LegislationBaseline(),
            'budget': BudgetBaseline(),
            'legal_judgment': LegalJudgmentBaseline(),
            'policy_brief': PolicyBriefBaseline(),
            'research_report': ResearchReportBaseline(),
            'news_article': NewsArticleBaseline(),
            'analysis': AnalysisReportBaseline(),
            'report': GeneralReportBaseline(),
        }
        
        # Encoding corruption patterns
        self.corruption_patterns = [
            re.compile(r'Ã©'),            # é corrupted
            re.compile(r'Ã¨'),            # è corrupted
            re.compile(r'Ã '),            # à corrupted
            re.compile(r'â€™'),           # ' corrupted
            re.compile(r'â€œ'),           # " corrupted
            re.compile(r'[^\x00-\x7F]{5,}'),  # Long non-ASCII sequences
        ]
    
    def detect_document_type(self, text: str, hint: Optional[str] = None) -> str:
        """
        Auto-detect document type from text content.
        
        Args:
            text: Document text
            hint: Optional type hint from user
            
        Returns:
            Detected document type string
        """
        if hint and hint in self.baselines:
            return hint
        
        # Run all baselines and pick the best match
        results = {}
        for doc_type, baseline in self.baselines.items():
            result = baseline.analyze(text)
            if result.is_specialized:
                results[doc_type] = result.pattern_count
        
        if results:
            # Return type with highest pattern count
            return max(results, key=results.get)
        
        return 'report'  # Default
    
    def analyze(self, text: str, document_type: Optional[str] = None) -> BaselineResult:
        """
        Analyze text with appropriate document type baseline.
        
        Args:
            text: Document text
            document_type: Optional explicit document type
            
        Returns:
            BaselineResult with calibration data
        """
        # Check for encoding corruption first
        corruption_count = sum(
            len(p.findall(text)) for p in self.corruption_patterns
        )
        
        # Detect or use provided type
        detected_type = self.detect_document_type(text, document_type)
        
        # Get baseline for this type
        baseline = self.baselines.get(detected_type, self.baselines['report'])
        result = baseline.analyze(text)
        
        # Add corruption warning if needed
        if corruption_count > 5:
            result.warnings.insert(0,
                f"⚠️ ENCODING CORRUPTION: {corruption_count} instances of corrupted "
                f"characters detected. Text extraction may have failed. AI detection "
                f"on corrupted text is unreliable."
            )
            # Further reduce confidence
            result.confidence_penalty = min(0.50, result.confidence_penalty + 0.15)
        
        return result
    
    def get_calibration(
        self, 
        text: str, 
        document_type: Optional[str] = None
    ) -> Dict:
        """
        Get calibration data suitable for JSON serialization.
        
        Args:
            text: Document text
            document_type: Optional explicit document type
            
        Returns:
            Dict with calibration data
        """
        result = self.analyze(text, document_type)
        
        return {
            'document_type': result.document_type,
            'is_specialized': result.is_specialized,
            'pattern_count': result.pattern_count,
            'patterns_by_category': result.patterns_by_category,
            'ai_score_adjustment': result.ai_score_adjustment,
            'confidence_penalty': result.confidence_penalty,
            'warnings': result.warnings,
            'detected_conventions': result.detected_conventions,
            'calibration_version': self.version,
        }


def create_detector() -> DocumentTypeDetector:
    """Factory function for document type detector."""
    return DocumentTypeDetector()


def get_document_calibration(text: str, document_type: Optional[str] = None) -> Dict:
    """
    Convenience function to get document calibration.
    
    Args:
        text: Document text
        document_type: Optional document type hint
        
    Returns:
        Calibration dict
    """
    detector = DocumentTypeDetector()
    return detector.get_calibration(text, document_type)


if __name__ == '__main__':
    # Test with sample text
    test_texts = {
        'legislation': """
            1. This Act may be cited as the Budget Implementation Act.
            2. (1) For the purposes of this Act, "Minister" means the Minister of Finance.
            (2) Subject to subsection (3), every person shall comply with this Act.
            3. Paragraph 12(1)(t) of the Income Tax Act is replaced by the following:
        """,
        'budget': """
            Fiscal Year 2024-25 Estimates
            Vote 1: Operating expenditures $2.5 billion
            Program 1.1: Policy Development
            Year-over-year increase of 3.2 per cent
            Total planned spending: $45.6 million
        """,
        'legal_judgment': """
            [1] This is an appeal from a judgment of the Federal Court.
            [2] The appellant seeks judicial review of the decision.
            [3] In my view, the appeal should be dismissed for the following reasons.
            See: Smith v. Canada, 2024 SCC 15 at para 23.
        """,
        'news_article': """
            OTTAWA — The Prime Minister announced today a new climate initiative.
            "This is a historic moment," said the Minister of Environment.
            Sources say the plan has been in development for months.
            The opposition declined to comment on the proposal.
        """,
    }
    
    detector = DocumentTypeDetector()
    
    for doc_type, text in test_texts.items():
        print(f"\n{'='*60}")
        print(f"Testing: {doc_type.upper()}")
        print('='*60)
        
        result = detector.get_calibration(text, doc_type)
        
        print(f"Detected Type: {result['document_type']}")
        print(f"Is Specialized: {result['is_specialized']}")
        print(f"Pattern Count: {result['pattern_count']}")
        print(f"AI Score Adjustment: {result['ai_score_adjustment']:.1%}")
        print(f"Confidence Penalty: {result['confidence_penalty']:.1%}")
        print(f"Conventions: {', '.join(result['detected_conventions'])}")
        if result['warnings']:
            print(f"Warnings: {result['warnings'][0][:80]}...")

"""
Citation Quality Scorer for Sparrow SPOT Scale™ v8.3.3

Extracts and verifies citations/sources from documents for transparency.

v8.3.3: Enhanced document type detection with legislative and analysis variants.
"""

import re
from typing import Dict, List, Tuple
from urllib.parse import urlparse
import requests
from datetime import datetime
from enum import Enum


class DocumentType(Enum):
    """
    Document type classification for context-aware scoring.
    
    v8.3.3: Added comprehensive document type taxonomy.
    
    PRIMARY SOURCES (Self-Authoritative):
        - LEGISLATION: Bills, Acts, Statutes - IS the source, doesn't need citations
        - BUDGET: Government financial documents - authoritative fiscal data
        - LEGAL_JUDGMENT: Court rulings, judicial decisions
    
    SECONDARY SOURCES (Citation-Dependent):
        - POLICY_BRIEF: Policy recommendations, white papers
        - RESEARCH_REPORT: Academic/research analysis
        - NEWS_ARTICLE: Journalism, reporting
    
    META-EVALUATIVE SOURCES (Analysis):
        - ANALYSIS: Fact-checks, audits, trust assessments
        - REPORT: General reports (default)
    """
    # Primary Sources - self-authoritative
    LEGISLATION = "legislation"
    BUDGET = "budget"
    LEGAL_JUDGMENT = "legal_judgment"
    
    # Secondary Sources - citation-dependent  
    POLICY_BRIEF = "policy_brief"
    RESEARCH_REPORT = "research_report"
    NEWS_ARTICLE = "news_article"
    
    # Meta-Evaluative Sources
    ANALYSIS = "analysis"
    REPORT = "report"  # Default fallback


# Document type scoring configuration
DOCUMENT_TYPE_CONFIG = {
    # Primary sources: high base score, bonus for references
    DocumentType.LEGISLATION: {
        "base_score": 75.0,
        "description": "Legislative document (Bill, Act, Statute)",
        "citation_expectation": "LOW",
        "rationale": "Self-authoritative primary source; creates law rather than citing it"
    },
    DocumentType.BUDGET: {
        "base_score": 70.0,
        "description": "Government budget/fiscal document",
        "citation_expectation": "LOW",
        "rationale": "Authoritative fiscal data; internal references expected"
    },
    DocumentType.LEGAL_JUDGMENT: {
        "base_score": 70.0,
        "description": "Court ruling or judicial decision",
        "citation_expectation": "MEDIUM",
        "rationale": "Cites precedents but is itself authoritative"
    },
    
    # Secondary sources: standard scoring, citations required
    DocumentType.POLICY_BRIEF: {
        "base_score": 0.0,
        "description": "Policy analysis or recommendations",
        "citation_expectation": "HIGH",
        "rationale": "Must cite evidence to support recommendations"
    },
    DocumentType.RESEARCH_REPORT: {
        "base_score": 0.0,
        "description": "Academic or research report",
        "citation_expectation": "HIGH",
        "rationale": "Academic standards require extensive citations"
    },
    DocumentType.NEWS_ARTICLE: {
        "base_score": 0.0,
        "description": "News or journalism",
        "citation_expectation": "MEDIUM",
        "rationale": "Should attribute claims to sources"
    },
    
    # Meta-evaluative sources: methodology-focused
    DocumentType.ANALYSIS: {
        "base_score": 50.0,
        "description": "Analysis, audit, or fact-check",
        "citation_expectation": "MODERATE",
        "rationale": "References analyzed document + methodology standards"
    },
    DocumentType.REPORT: {
        "base_score": 0.0,
        "description": "General report (default)",
        "citation_expectation": "MEDIUM",
        "rationale": "Standard citation expectations"
    }
}


class CitationQualityScorer:
    """Extract and analyze citations for source transparency."""
    
    def __init__(self):
        """Initialize citation scorer."""
        self.url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
        self.citation_patterns = [
            r'\[[0-9]+\]',  # [1], [2], etc.
            r'\([A-Z][a-z]+,?\s+\d{4}\)',  # (Smith, 2024)
            r'according to [A-Z][a-z]+',  # according to Smith
            r'[A-Z][a-z]+ states?',  # Smith states
            r'reported by [A-Z][a-z]+',  # reported by Reuters
        ]
        
        # v8.3.3: Enhanced document type patterns
        self._init_document_patterns()
    
    def _init_document_patterns(self):
        """Initialize document type detection patterns."""
        
        # Legislative document patterns (Bills, Acts, Statutes)
        self.legislative_patterns = [
            r'\bBill\s+[A-Z]?-?\d+\b',  # Bill C-15, Bill S-20
            r'\bAct\s+to\s+(implement|amend|repeal|establish)',  # Act to implement
            r'\bSection\s+\d+(\.\d+)?',  # Section 42, Section 3.2
            r'\bsubsection\s+\(\d+\)',  # subsection (1)
            r'\bparagraph\s+\([a-z]\)',  # paragraph (a)
            r'\bSchedule\s+[A-Z0-9]',  # Schedule A
            r'\b(Her|His)\s+Majesty\b',  # Royal reference
            r'\bParliament\s+of\s+Canada\b',
            r'\benacted\s+by\b',  # enacted by
            r'\bChapter\s+\d+\s+of\s+the\s+Statutes\b',  # Chapter 12 of the Statutes
            r'\bStatutes\s+of\s+Canada\b',
            r'\bS\.C\.\s+\d{4}',  # S.C. 2024 (Statutes of Canada)
            r'\bR\.S\.C\.\s+\d{4}',  # R.S.C. 1985 (Revised Statutes)
            r'\bFirst\s+Reading\b',  # Legislative stages
            r'\bRoyal\s+Assent\b',
            r'\bHouse\s+of\s+Commons\b',
            r'\bSenate\s+of\s+Canada\b',
            r'\bcoming\s+into\s+force\b',  # Legislative language
            r'\bGovernor\s+(General|in\s+Council)\b',
        ]
        
        # Budget/fiscal document patterns
        self.budget_patterns = [
            r'\bBudget\s+\d{4}\b',  # Budget 2025
            r'\bfiscal\s+(year|framework|outlook)\b',
            r'\bappropriation\b',
            r'\bexpenditure\s+(plan|estimate)\b',
            r'\brevenue\s+projection\b',
            r'\bMain\s+Estimates\b',
            r'\bSupplementary\s+Estimates\b',
            r'\bDepartmental\s+Plan\b',
            r'\bPublic\s+Accounts\b',
            r'\bDebt\s+Management\s+Strategy\b',
        ]
        
        # Legal judgment patterns
        self.legal_judgment_patterns = [
            r'\b\d{4}\s+(SCC|FC|FCA|ONCA|BCCA)\s+\d+\b',  # 2024 SCC 1
            r'\bthe\s+(Honourable|Hon\.)\s+Justice\b',
            r'\bplaintiff|defendant|appellant|respondent\b',
            r'\bREASONS\s+FOR\s+JUDGMENT\b',
            r'\bORDER\s+OF\s+THE\s+COURT\b',
            r'\bcosts\s+awarded\b',
            r'\b(dismiss|allow)\s+the\s+appeal\b',
        ]
        
        # Policy brief patterns
        self.policy_brief_patterns = [
            r'\bexecutive\s+summary\b',
            r'\brecommendations?\b',
            r'\bkey\s+findings\b',
            r'\bpolicy\s+options?\b',
            r'\bimpact\s+assessment\b',
            r'\bstakeholder\s+analysis\b',
            r'\bpolicy\s+brief\b',
            r'\bwhite\s+paper\b',
        ]
        
        # Research report patterns
        self.research_report_patterns = [
            r'\bmethodology\b',
            r'\bliterature\s+review\b',
            r'\breferences\b',
            r'\babstract\b',
            r'\b(table|figure)\s+\d+\b',
            r'\bdata\s+analysis\b',
            r'\bsample\s+size\b',
            r'\bp\s*[<>=]\s*0?\.\d+\b',  # p-value notation
            r'\bconfidence\s+interval\b',
        ]
        
        # Analysis/audit patterns
        self.analysis_patterns = [
            r'\bfact[\s-]?check\b',
            r'\baudit\s+(report|findings)\b',
            r'\btrust\s+(score|assessment)\b',
            r'\bbias\s+(audit|assessment)\b',
            r'\bverification\s+results?\b',
            r'\banalysis\s+of\b',
            r'\bevaluation\s+criteria\b',
            r'\bNIST\s+(SP|Framework)\b',
            r'\bcompliance\s+(check|assessment)\b',
            r'\bSPOT\s+Scale\b',  # Our own analysis tool
        ]
    
    def _detect_document_type(self, text: str) -> DocumentType:
        """
        v8.3.3: Enhanced document type detection for context-aware scoring.
        
        Detects document type to apply appropriate citation expectations:
        - Legislative documents are self-authoritative (don't need external citations)
        - Policy briefs require citations to support recommendations
        - Analysis documents focus on methodology, not traditional citations
        
        Returns:
            DocumentType enum value
        """
        # Use first 8000 chars for efficiency (covers most headers/intros)
        sample = text[:8000]
        sample_lower = sample.lower()
        
        # Score each document type
        type_scores = {}
        
        # Check legislative patterns
        leg_matches = sum(1 for p in self.legislative_patterns 
                         if re.search(p, sample, re.IGNORECASE))
        type_scores[DocumentType.LEGISLATION] = leg_matches
        
        # Check budget patterns
        budget_matches = sum(1 for p in self.budget_patterns 
                            if re.search(p, sample, re.IGNORECASE))
        type_scores[DocumentType.BUDGET] = budget_matches
        
        # Check legal judgment patterns
        legal_matches = sum(1 for p in self.legal_judgment_patterns 
                           if re.search(p, sample, re.IGNORECASE))
        type_scores[DocumentType.LEGAL_JUDGMENT] = legal_matches
        
        # Check policy brief patterns
        policy_matches = sum(1 for p in self.policy_brief_patterns 
                            if re.search(p, sample_lower))
        type_scores[DocumentType.POLICY_BRIEF] = policy_matches
        
        # Check research report patterns
        research_matches = sum(1 for p in self.research_report_patterns 
                              if re.search(p, sample_lower))
        type_scores[DocumentType.RESEARCH_REPORT] = research_matches
        
        # Check analysis patterns
        analysis_matches = sum(1 for p in self.analysis_patterns 
                              if re.search(p, sample, re.IGNORECASE))
        type_scores[DocumentType.ANALYSIS] = analysis_matches
        
        # Determine best match with threshold requirements
        # Primary sources need strong evidence (3+ matches)
        if type_scores[DocumentType.LEGISLATION] >= 4:
            return DocumentType.LEGISLATION
        if type_scores[DocumentType.BUDGET] >= 3:
            return DocumentType.BUDGET
        if type_scores[DocumentType.LEGAL_JUDGMENT] >= 3:
            return DocumentType.LEGAL_JUDGMENT
        
        # Secondary sources need 2+ matches
        if type_scores[DocumentType.RESEARCH_REPORT] >= 3:
            return DocumentType.RESEARCH_REPORT
        if type_scores[DocumentType.POLICY_BRIEF] >= 2:
            return DocumentType.POLICY_BRIEF
        
        # Analysis documents
        if type_scores[DocumentType.ANALYSIS] >= 2:
            return DocumentType.ANALYSIS
        
        # Weak legislative match (2-3 patterns) - still likely legislation
        if type_scores[DocumentType.LEGISLATION] >= 2:
            return DocumentType.LEGISLATION
        
        # Default to general report
        return DocumentType.REPORT
    
    def get_document_type_info(self, doc_type: DocumentType) -> Dict:
        """
        Get detailed information about a document type.
        
        Args:
            doc_type: DocumentType enum value
            
        Returns:
            Dict with description, citation expectations, and rationale
        """
        config = DOCUMENT_TYPE_CONFIG.get(doc_type, DOCUMENT_TYPE_CONFIG[DocumentType.REPORT])
        return {
            "type": doc_type.value,
            "description": config["description"],
            "citation_expectation": config["citation_expectation"],
            "rationale": config["rationale"],
            "base_score": config["base_score"]
        }
    
    def analyze_citations(self, text: str, check_urls: bool = False) -> Dict:
        """
        Analyze all citations in document.
        
        v8.3.3: Enhanced document type detection with full taxonomy.
        Legislative, budget, and legal documents are self-authoritative.
        Analysis documents focus on methodology rather than citations.
        
        Args:
            text: Document text
            check_urls: Whether to verify URL accessibility (slow)
        
        Returns:
            Dictionary with citation analysis results
        """
        # Validate input
        if not isinstance(text, str):
            raise TypeError(f"Expected string for text parameter, got {type(text)}")
        
        # v8.3.3: Enhanced document type detection
        document_type = self._detect_document_type(text)
        doc_type_info = self.get_document_type_info(document_type)
        
        # Extract URLs
        urls = self.url_pattern.findall(text)
        
        # Extract citation markers
        citation_markers = []
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citation_markers.extend(matches)
        
        # Fix #3: Deduplicate and clean citation markers
        citation_markers = self._deduplicate_citations(citation_markers)
        
        # Analyze URL quality
        url_analysis = self._analyze_urls(urls, check_urls)
        
        # Calculate citation density
        words = len(text.split())
        citations_per_1000_words = (len(urls) + len(citation_markers)) / words * 1000 if words > 0 else 0
        
        # v8.3.3: Generate quality score with full document type awareness
        quality_score = self._calculate_quality_score(url_analysis, citations_per_1000_words, document_type)
        
        return {
            "total_urls": len(urls),
            "total_citation_markers": len(citation_markers),
            "total_citations": len(urls) + len(citation_markers),
            "citations_per_1000_words": round(citations_per_1000_words, 2),
            "url_analysis": url_analysis,
            "citation_markers": citation_markers[:20],  # Sample
            "document_type": document_type.value,  # v8.3.3: String value for JSON compatibility
            "document_type_info": doc_type_info,  # v8.3.3: Full type information
            "quality_score": quality_score,
            "quality_level": self._get_quality_level(quality_score),
            "summary": self._generate_citation_summary(url_analysis, citations_per_1000_words, quality_score, document_type)
        }
    
    def _analyze_urls(self, urls: List[str], check_accessibility: bool = False) -> Dict:
        """Analyze URLs for source quality."""
        if not urls:
            return {
                "total": 0,
                "unique": 0,
                "accessible": 0,
                "broken": 0,
                "source_types": {}
            }
        
        unique_urls = list(set(urls))
        source_types = self._categorize_sources(unique_urls)
        
        accessible = 0
        broken = 0
        
        if check_accessibility:
            # Check first 10 URLs to avoid slowdown
            for url in unique_urls[:10]:
                if self._check_url_accessible(url):
                    accessible += 1
                else:
                    broken += 1
        
        return {
            "total": len(urls),
            "unique": len(unique_urls),
            "accessible": accessible if check_accessibility else "Not checked",
            "broken": broken if check_accessibility else "Not checked",
            "source_types": source_types,
            "sample_urls": unique_urls[:5]
        }
    
    def _categorize_sources(self, urls: List[str]) -> Dict:
        """Categorize URLs by source type."""
        categories = {
            "government": 0,
            "academic": 0,
            "news": 0,
            "social_media": 0,
            "other": 0
        }
        
        gov_domains = ['.gov', '.gc.ca', '.gouv']
        academic_domains = ['.edu', '.ac.', 'scholar.google', 'arxiv.org', 'researchgate']
        news_domains = ['bbc.', 'cnn.', 'reuters.', 'ap.org', 'nytimes', 'washingtonpost', 'theguardian', 'cbc.ca']
        social_domains = ['twitter.com', 'x.com', 'facebook.com', 'linkedin.com', 'instagram.com', 'youtube.com']
        
        for url in urls:
            url_lower = url.lower()
            
            if any(domain in url_lower for domain in gov_domains):
                categories["government"] += 1
            elif any(domain in url_lower for domain in academic_domains):
                categories["academic"] += 1
            elif any(domain in url_lower for domain in news_domains):
                categories["news"] += 1
            elif any(domain in url_lower for domain in social_domains):
                categories["social_media"] += 1
            else:
                categories["other"] += 1
        
        return categories
    
    def _deduplicate_citations(self, citations: List[str]) -> List[str]:
        """
        Deduplicate and clean citation markers.
        
        Fix #3: Removes duplicates and filters out OCR artifacts like:
        - Truncated words (e.g., 'nancial state' instead of 'financial state')
        - Repetitive patterns from poor PDF text extraction
        - Very short or garbled text
        
        Args:
            citations: Raw list of citation markers
            
        Returns:
            Cleaned and deduplicated list
        """
        if not citations:
            return []
        
        # Count occurrences for frequency analysis
        from collections import Counter
        citation_counts = Counter(citations)
        
        cleaned = []
        seen = set()
        
        for citation in citations:
            # Skip if already seen (deduplication)
            citation_lower = citation.lower().strip()
            if citation_lower in seen:
                continue
            
            # Skip very short citations (likely OCR artifacts)
            if len(citation.strip()) < 4:
                continue
            
            # Skip if this looks like a truncated word (starts with lowercase and matches a fragment)
            # e.g., 'nancial state' is a truncation of 'financial state'
            if citation_lower[0].islower() and not citation_lower.startswith(('according', 'reported')):
                # Check if it might be part of a longer citation we already have
                is_fragment = False
                for seen_cit in seen:
                    if citation_lower in seen_cit or seen_cit.endswith(citation_lower):
                        is_fragment = True
                        break
                if is_fragment:
                    continue
            
            # Skip citations that appear too frequently (likely OCR false positives)
            # More than 10 occurrences of the same pattern is suspicious
            if citation_counts.get(citation, 0) > 10:
                continue
            
            # Skip garbled text (contains unusual character patterns)
            if self._is_garbled_text(citation):
                continue
            
            seen.add(citation_lower)
            cleaned.append(citation)
        
        return cleaned
    
    def _is_garbled_text(self, text: str) -> bool:
        """
        Check if text appears to be OCR-garbled.
        
        Returns True for text that:
        - Has excessive consecutive consonants
        - Contains unusual diacritics patterns (bilingual OCR artifacts)
        - Has very low vowel-to-consonant ratio
        """
        if not text or len(text) < 3:
            return True
        
        # Check for unusual character patterns
        garbled_patterns = [
            r'[bcdfghjklmnpqrstvwxz]{5,}',  # 5+ consecutive consonants
            r'[àâäèéêëîïôùûüÿç]{3,}',  # 3+ consecutive French diacritics (bilingual OCR issue)
            r'[A-Z]{2}[a-z][A-Z]',  # Mixed case gibberish like "ABcD"
        ]
        
        for pattern in garbled_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check vowel ratio - very low ratio suggests garbled text
        vowels = sum(1 for c in text.lower() if c in 'aeiouàâäèéêëîïôùûüÿ')
        if len(text) > 5 and vowels / len(text) < 0.15:
            return True
        
        return False
    
    def _check_url_accessible(self, url: str, timeout: int = 5) -> bool:
        """Check if URL is accessible."""
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code < 400
        except:
            return False
    
    def _calculate_quality_score(self, url_analysis: Dict, citations_per_1000: float, 
                                   document_type: DocumentType = DocumentType.REPORT) -> float:
        """
        Calculate overall citation quality score (0-100).
        
        v8.3.3: Full document type taxonomy support.
        
        PRIMARY SOURCES (self-authoritative):
        - Legislation: Base 75, bonus for government refs
        - Budget: Base 70, bonus for fiscal refs
        - Legal Judgment: Base 70, considers precedent citations
        
        SECONDARY SOURCES (citation-dependent):
        - Policy Brief: Standard scoring, high citation expectation
        - Research Report: Academic standards, highest expectation
        - News Article: Standard scoring
        
        META-EVALUATIVE:
        - Analysis: Base 50, methodology-focused
        - Report: Standard scoring (default)
        
        Scoring components:
        - Source diversity: 40 points
        - Citation density: 30 points  
        - URL accessibility: 30 points
        """
        config = DOCUMENT_TYPE_CONFIG.get(document_type, DOCUMENT_TYPE_CONFIG[DocumentType.REPORT])
        base_score = config["base_score"]
        source_types = url_analysis.get("source_types", {})
        
        # PRIMARY SOURCES: Self-authoritative, high base score
        if document_type in (DocumentType.LEGISLATION, DocumentType.BUDGET, DocumentType.LEGAL_JUDGMENT):
            # Start with high base score - these documents ARE the source
            
            if document_type == DocumentType.LEGISLATION:
                # Legislation: Bonus for government/official references
                gov_bonus = min(source_types.get("government", 0) * 5, 15)
                ref_bonus = min(citations_per_1000 * 3, 10)
                return round(min(base_score + gov_bonus + ref_bonus, 100), 1)
            
            elif document_type == DocumentType.BUDGET:
                # Budget: Bonus for government and news coverage
                gov_bonus = min(source_types.get("government", 0) * 5, 15)
                coverage_bonus = min(source_types.get("news", 0) * 3, 10)
                return round(min(base_score + gov_bonus + coverage_bonus, 100), 1)
            
            elif document_type == DocumentType.LEGAL_JUDGMENT:
                # Legal: Bonus for precedent citations (typically marked as academic)
                precedent_bonus = min(citations_per_1000 * 5, 20)
                gov_bonus = min(source_types.get("government", 0) * 3, 10)
                return round(min(base_score + precedent_bonus + gov_bonus, 100), 1)
        
        # META-EVALUATIVE: Analysis documents
        if document_type == DocumentType.ANALYSIS:
            # Analysis: Focus on methodology references, not traditional citations
            # Base 50 + bonuses for standards refs
            gov_bonus = min(source_types.get("government", 0) * 8, 20)
            academic_bonus = min(source_types.get("academic", 0) * 8, 20)
            density_bonus = min(citations_per_1000 * 2, 10)
            return round(min(base_score + gov_bonus + academic_bonus + density_bonus, 100), 1)
        
        # SECONDARY SOURCES: Standard citation-dependent scoring
        score = base_score
        
        # Source diversity (40 points)
        gov_score = min(source_types.get("government", 0) * 10, 15)
        academic_score = min(source_types.get("academic", 0) * 10, 15)
        news_score = min(source_types.get("news", 0) * 5, 10)
        score += gov_score + academic_score + news_score
        
        # Citation density (30 points)
        # Research reports have higher expectations
        if document_type == DocumentType.RESEARCH_REPORT:
            if citations_per_1000 >= 15:
                density_score = 30
            elif citations_per_1000 >= 10:
                density_score = 25
            elif citations_per_1000 >= 5:
                density_score = 15
            else:
                density_score = citations_per_1000 * 2
        else:
            # Standard density scoring
            if citations_per_1000 >= 10:
                density_score = 30
            elif citations_per_1000 >= 5:
                density_score = 20
            elif citations_per_1000 >= 2:
                density_score = 10
            else:
                density_score = citations_per_1000 * 2
        score += density_score
        
        # URL accessibility (30 points) - only if checked
        if url_analysis.get("accessible") != "Not checked":
            total = url_analysis.get("accessible", 0) + url_analysis.get("broken", 0)
            if total > 0:
                accessibility_rate = url_analysis.get("accessible", 0) / total
                score += accessibility_rate * 30
        else:
            # Give partial credit if not checked
            score += 15
        
        return round(min(score, 100), 1)
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level label from score."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Very Poor"
    
    def _generate_citation_summary(self, url_analysis: Dict, citations_per_1000: float, 
                                     score: float, document_type: DocumentType = DocumentType.REPORT) -> str:
        """Generate human-readable summary with document type context."""
        parts = []
        
        # Add document type context
        config = DOCUMENT_TYPE_CONFIG.get(document_type, DOCUMENT_TYPE_CONFIG[DocumentType.REPORT])
        parts.append(f"Document Type: {config['description']}")
        
        total = url_analysis.get("total", 0)
        unique = url_analysis.get("unique", 0)
        
        # Handle zero citations differently based on document type
        if total == 0:
            if document_type in (DocumentType.LEGISLATION, DocumentType.BUDGET, DocumentType.LEGAL_JUDGMENT):
                parts.append(f"No external citations (expected for {document_type.value})")
            else:
                parts.append("No citations found - document lacks source attribution")
        else:
            parts.append(f"Found {total} citations ({unique} unique)")
            parts.append(f"{citations_per_1000:.1f} citations per 1,000 words")
        
        source_types = url_analysis.get("source_types", {})
        if source_types.get("government", 0) > 0:
            parts.append(f"{source_types['government']} government sources")
        if source_types.get("academic", 0) > 0:
            parts.append(f"{source_types['academic']} academic sources")
        
        quality_level = self._get_quality_level(score)
        parts.append(f"Overall quality: {quality_level} ({score}/100)")
        
        # Add citation expectation context
        parts.append(f"Citation expectation: {config['citation_expectation']}")
        
        return " | ".join(parts)
    
    def format_citation_results(self, analysis: Dict) -> str:
        """Format citation analysis results into a report.
        
        Args:
            analysis: Results dict from analyze_citations()
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("  CITATION QUALITY REPORT")
        report.append("=" * 80)
        report.append("")
        report.append(f"Total Citations: {analysis['total_citations']}")
        report.append(f"  • URLs: {analysis['total_urls']}")
        report.append(f"  • Citation Markers: {analysis['total_citation_markers']}")
        report.append(f"  • Density: {analysis['citations_per_1000_words']:.2f} per 1,000 words")
        report.append("")
        report.append(f"Quality Score: {analysis['quality_score']}/100 ({analysis['quality_level']})")
        report.append("")
        
        if analysis['url_analysis']['total'] > 0:
            report.append("Source Type Distribution:")
            for source_type, count in analysis['url_analysis']['source_types'].items():
                if count > 0:
                    report.append(f"  • {source_type.replace('_', ' ').title()}: {count}")
            report.append("")
        
        if isinstance(analysis['url_analysis']['accessible'], int):
            report.append(f"URL Accessibility:")
            report.append(f"  • Accessible: {analysis['url_analysis']['accessible']}")
            report.append(f"  • Broken: {analysis['url_analysis']['broken']}")
            report.append("")
        
        report.append("Summary:")
        report.append(f"  {analysis['summary']}")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_citation_report(self, text: str, check_urls: bool = False) -> str:
        """Generate formatted citation quality report."""
        analysis = self.analyze_citations(text, check_urls)
        return self.format_citation_results(analysis)


if __name__ == "__main__":
    import sys
    
    scorer = CitationQualityScorer()
    
    # Test with different document types
    print("=" * 80)
    print("  DOCUMENT TYPE DETECTION TEST")
    print("=" * 80)
    
    # Legislative document sample
    legislative_sample = """
    Bill C-15: An Act to implement certain provisions of the budget
    
    Her Majesty, by and with the advice and consent of the Senate and House of Commons 
    of Canada, enacts as follows:
    
    Section 1. Short Title
    This Act may be cited as the Budget Implementation Act, 2025.
    
    Section 2. Interpretation
    In this Act, unless the context otherwise requires:
    (a) "Minister" means the Minister of Finance;
    (b) "prescribed" means prescribed by regulation.
    
    subsection (1) The Governor in Council may make regulations...
    
    Schedule A - Tax Rate Amendments
    Coming into force: Royal Assent
    """
    
    # Policy brief sample
    policy_sample = """
    Executive Summary
    
    This policy brief provides recommendations for improving fiscal transparency.
    Key findings indicate that stakeholder engagement is critical.
    
    According to Smith (2024), budget transparency has improved.
    Research from https://transparency.gc.ca supports these findings.
    
    Policy Options:
    1. Implement real-time reporting
    2. Enhance stakeholder consultation
    
    Impact Assessment indicates positive outcomes.
    """
    
    # Analysis document sample
    analysis_sample = """
    SPOT Scale™ Trust Assessment Report
    
    Bias Audit Results:
    This analysis of Bill C-15 reveals the following:
    
    Verification Results:
    - Trust Score: 72/100
    - NIST SP 800-53 Compliance: Partial
    
    Evaluation Criteria applied per methodology.
    Fact-check complete.
    """
    
    print("\n1. LEGISLATIVE DOCUMENT:")
    result = scorer.analyze_citations(legislative_sample)
    print(f"   Type: {result['document_type']}")
    print(f"   Info: {result['document_type_info']['description']}")
    print(f"   Citation Expectation: {result['document_type_info']['citation_expectation']}")
    print(f"   Quality Score: {result['quality_score']}/100")
    
    print("\n2. POLICY BRIEF:")
    result = scorer.analyze_citations(policy_sample)
    print(f"   Type: {result['document_type']}")
    print(f"   Info: {result['document_type_info']['description']}")
    print(f"   Citation Expectation: {result['document_type_info']['citation_expectation']}")
    print(f"   Quality Score: {result['quality_score']}/100")
    
    print("\n3. ANALYSIS DOCUMENT:")
    result = scorer.analyze_citations(analysis_sample)
    print(f"   Type: {result['document_type']}")
    print(f"   Info: {result['document_type_info']['description']}")
    print(f"   Citation Expectation: {result['document_type_info']['citation_expectation']}")
    print(f"   Quality Score: {result['quality_score']}/100")
    
    print("\n" + "=" * 80)
    print("  DOCUMENT TYPE TAXONOMY")
    print("=" * 80)
    for doc_type in DocumentType:
        config = DOCUMENT_TYPE_CONFIG[doc_type]
        print(f"\n{doc_type.value.upper()}:")
        print(f"  Description: {config['description']}")
        print(f"  Base Score: {config['base_score']}")
        print(f"  Citation Expectation: {config['citation_expectation']}")
        print(f"  Rationale: {config['rationale']}")
    
    print("\n" + "=" * 80)

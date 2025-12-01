"""
Citation Quality Scorer for Sparrow SPOT Scale™ v8.2

Extracts and verifies citations/sources from documents for transparency.
"""

import re
from typing import Dict, List, Tuple
from urllib.parse import urlparse
import requests
from datetime import datetime


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
        
        # v8.3.2: Document type patterns for scoring adjustment
        self.legislative_patterns = [
            r'\bBill\s+[A-Z]?-?\d+\b',  # Bill C-15, Bill S-20
            r'\bAct\s+[A-Z]',  # Act of Parliament
            r'\bSection\s+\d+',  # Section 42
            r'\bsubsection\s+\(\d+\)',  # subsection (1)
            r'\bSchedule\s+[A-Z0-9]',  # Schedule A
            r'\bHer Majesty|His Majesty\b',  # Royal reference
            r'\bParliament\s+of\s+Canada\b',
            r'\benacted\s+by\b',  # enacted by
            r'\bChapter\s+\d+\b',  # Chapter 12 (in legislation)
            r'\bStatutes\s+of\s+Canada\b',
        ]
    
    def _detect_document_type(self, text: str) -> str:
        """v8.3.2: Detect document type for appropriate scoring.
        
        Legislative documents (bills, acts) are self-authoritative and 
        shouldn't be penalized for low external citations.
        
        Returns:
            'legislation': Bills, Acts, legal documents
            'policy_brief': Policy analysis, recommendations
            'report': General reports and analysis
            'unknown': Cannot determine
        """
        text_lower = text[:5000].lower()  # Check first 5000 chars for efficiency
        
        # Count legislative pattern matches
        leg_matches = 0
        for pattern in self.legislative_patterns:
            if re.search(pattern, text[:5000], re.IGNORECASE):
                leg_matches += 1
        
        # Legislation typically has 3+ pattern matches
        if leg_matches >= 3:
            return 'legislation'
        
        # Check for policy brief indicators
        policy_indicators = ['executive summary', 'recommendations', 'key findings', 
                            'policy options', 'impact assessment', 'stakeholder']
        policy_matches = sum(1 for ind in policy_indicators if ind in text_lower)
        if policy_matches >= 2:
            return 'policy_brief'
        
        return 'report'  # Default to general report
    
    def analyze_citations(self, text: str, check_urls: bool = False) -> Dict:
        """
        Analyze all citations in document.
        
        v8.3.2: Added document type detection for context-aware scoring.
        Legislative documents are not penalized for low external citations.
        
        Args:
            text: Document text
            check_urls: Whether to verify URL accessibility (slow)
        
        Returns:
            Dictionary with citation analysis results
        """
        # Validate input
        if not isinstance(text, str):
            raise TypeError(f"Expected string for text parameter, got {type(text)}")
        
        # v8.3.2: Detect document type for context-aware scoring
        document_type = self._detect_document_type(text)
        
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
        
        # v8.3.2: Generate quality score with document type awareness
        quality_score = self._calculate_quality_score(url_analysis, citations_per_1000_words, document_type)
        
        return {
            "total_urls": len(urls),
            "total_citation_markers": len(citation_markers),
            "total_citations": len(urls) + len(citation_markers),
            "citations_per_1000_words": round(citations_per_1000_words, 2),
            "url_analysis": url_analysis,
            "citation_markers": citation_markers[:20],  # Sample
            "document_type": document_type,  # v8.3.2: Include detected type
            "quality_score": quality_score,
            "quality_level": self._get_quality_level(quality_score),
            "summary": self._generate_citation_summary(url_analysis, citations_per_1000_words, quality_score)
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
                                   document_type: str = 'report') -> float:
        """
        Calculate overall citation quality score (0-100).
        
        v8.3.2: Added document type awareness.
        - Legislative documents (bills, acts) are self-authoritative
        - Policy briefs require external citations for credibility
        - Reports use standard scoring
        
        Scoring:
        - Source diversity: 40 points
        - Citation density: 30 points  
        - URL accessibility: 30 points
        
        For legislation: Base score starts at 60 (self-authoritative)
        """
        # v8.3.2: Legislative documents are self-authoritative
        if document_type == 'legislation':
            # Legislation doesn't need external citations - it IS the source
            # Start with high base score, add bonus for any external references
            base_score = 70.0  # Legislation is authoritative by definition
            
            # Bonus points for any government/official references (up to 30)
            source_types = url_analysis.get("source_types", {})
            gov_bonus = min(source_types.get("government", 0) * 5, 15)
            other_bonus = min(citations_per_1000 * 3, 15)
            
            return round(min(base_score + gov_bonus + other_bonus, 100), 1)
        
        # Standard scoring for policy briefs and reports
        score = 0.0
        
        # Source diversity (40 points)
        source_types = url_analysis.get("source_types", {})
        gov_score = min(source_types.get("government", 0) * 10, 15)
        academic_score = min(source_types.get("academic", 0) * 10, 15)
        news_score = min(source_types.get("news", 0) * 5, 10)
        score += gov_score + academic_score + news_score
        
        # Citation density (30 points)
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
    
    def _generate_citation_summary(self, url_analysis: Dict, citations_per_1000: float, score: float) -> str:
        """Generate human-readable summary."""
        parts = []
        
        total = url_analysis.get("total", 0)
        unique = url_analysis.get("unique", 0)
        
        if total == 0:
            return "No citations found. Document lacks source attribution."
        
        parts.append(f"Found {total} citations ({unique} unique)")
        parts.append(f"{citations_per_1000:.1f} citations per 1,000 words")
        
        source_types = url_analysis.get("source_types", {})
        if source_types.get("government", 0) > 0:
            parts.append(f"{source_types['government']} government sources")
        if source_types.get("academic", 0) > 0:
            parts.append(f"{source_types['academic']} academic sources")
        
        quality_level = self._get_quality_level(score)
        parts.append(f"Overall quality: {quality_level} ({score}/100)")
        
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
    
    # Test with sample text
    sample_text = """
    According to Smith (2024), the Canadian government allocated $250 million for AI development.
    This was reported by Reuters [1] and confirmed on the official website https://budget.gc.ca/2025.
    Research from MIT (https://mit.edu/research/ai) supports these findings.
    
    [1] https://reuters.com/article/canada-budget-2025
    """
    
    scorer = CitationQualityScorer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check-urls":
        print("Checking URL accessibility (this may take a moment)...")
        print(scorer.generate_citation_report(sample_text, check_urls=True))
    else:
        print(scorer.generate_citation_report(sample_text, check_urls=False))

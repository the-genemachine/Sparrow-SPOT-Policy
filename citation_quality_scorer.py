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
    
    def analyze_citations(self, text: str, check_urls: bool = False) -> Dict:
        """
        Analyze all citations in document.
        
        Args:
            text: Document text
            check_urls: Whether to verify URL accessibility (slow)
        
        Returns:
            Dictionary with citation analysis results
        """
        # Validate input
        if not isinstance(text, str):
            raise TypeError(f"Expected string for text parameter, got {type(text)}")
        
        # Extract URLs
        urls = self.url_pattern.findall(text)
        
        # Extract citation markers
        citation_markers = []
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citation_markers.extend(matches)
        
        # Analyze URL quality
        url_analysis = self._analyze_urls(urls, check_urls)
        
        # Calculate citation density
        words = len(text.split())
        citations_per_1000_words = (len(urls) + len(citation_markers)) / words * 1000 if words > 0 else 0
        
        # Generate quality score
        quality_score = self._calculate_quality_score(url_analysis, citations_per_1000_words)
        
        return {
            "total_urls": len(urls),
            "total_citation_markers": len(citation_markers),
            "total_citations": len(urls) + len(citation_markers),
            "citations_per_1000_words": round(citations_per_1000_words, 2),
            "url_analysis": url_analysis,
            "citation_markers": citation_markers[:20],  # Sample
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
    
    def _check_url_accessible(self, url: str, timeout: int = 5) -> bool:
        """Check if URL is accessible."""
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code < 400
        except:
            return False
    
    def _calculate_quality_score(self, url_analysis: Dict, citations_per_1000: float) -> float:
        """
        Calculate overall citation quality score (0-100).
        
        Scoring:
        - Source diversity: 40 points
        - Citation density: 30 points
        - URL accessibility: 30 points
        """
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

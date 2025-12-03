"""
Legislative Baseline Patterns for Sparrow SPOT Scale™ v8.3.3

This module defines patterns that are STANDARD in legislative drafting and should NOT
be counted as AI indicators. Based on:
- "Manual of Instructions for Legislative and Legal Writing" (Driedger, 1982)
- Justice Canada "Legistics" drafting guidelines
- Standard parliamentary drafting conventions

KEY INSIGHT: Legislative text by design uses:
1. Enumerated provisions (a), (b), (c)...
2. Restricted vocabulary (legal terms of art)
3. Formulaic syntax ("notwithstanding", "for the purposes of")
4. Intentional repetition for legal precision

These characteristics MIMIC AI patterns while actually representing human expertise
in specialized drafting. AI detection on legislative text without calibration
produces high false positive rates.

Reference: "The AI Detection Paradox" analysis identified this as a critical flaw.
"""

import re
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field


@dataclass
class LegislativePatternMatch:
    """A match of a legislative drafting pattern."""
    pattern_name: str
    matched_text: str
    start_pos: int
    end_pos: int
    category: str  # 'structural', 'formulaic', 'reference', 'definition'


@dataclass
class LegislativeBaselineResult:
    """Result of legislative baseline analysis."""
    is_legislative: bool
    legislative_pattern_count: int
    legislative_patterns: Dict[str, int]
    pattern_matches: List[LegislativePatternMatch]
    ai_score_adjustment: float  # Negative value to reduce AI score
    confidence_penalty: float  # Reduce confidence due to domain mismatch
    warnings: List[str]
    

class LegislativePatternDetector:
    """
    Detects standard legislative drafting patterns that should NOT be
    flagged as AI indicators.
    
    Based on Driedger's Manual of Instructions for Legislative and Legal Writing:
    - "The original is a good example of common law lawyers' writing. It is
      loaded with whosoevers and whatsoevers and there is much repetition..."
    - "The language of the common law should be used to modify the common law"
    - "A restriction followed by an enumeration of persons excluded from restriction"
    """
    
    # ============================================================
    # STRUCTURAL PATTERNS - Required by legislative format
    # ============================================================
    
    # Enumerated provisions - REQUIRED in legislation
    ENUMERATION_PATTERNS = [
        r'\([a-z]\)',                    # (a), (b), (c)
        r'\([a-z]\.\d+\)',               # (a.1), (b.2)
        r'\(i+\)',                        # (i), (ii), (iii)
        r'\(i+\.\d+\)',                   # (i.1), (ii.2)
        r'^\s*\d+\.\s',                   # 1. 2. 3. at line start
        r'^\s*\d+\(\d+\)',                # 1(1), 2(3) subsection refs
        r'paragraph\s+\([a-z]\)',         # paragraph (a)
        r'subparagraph\s+\([a-z]\)\(i+\)', # subparagraph (a)(i)
        r'clause\s+\([A-Z]\)',            # clause (A)
    ]
    
    # Section/subsection structure - REQUIRED
    SECTION_STRUCTURE_PATTERNS = [
        r'Section\s+\d+',
        r'Subsection\s+\d+\(\d+\)',
        r'Part\s+[IVXLC]+',               # Part I, Part II, etc.
        r'Division\s+\d+',
        r'Schedule\s+[A-Z0-9]+',
        r'Appendix\s+[A-Z0-9]+',
        r'Article\s+\d+',
    ]
    
    # ============================================================
    # FORMULAIC PHRASES - Standard legal language per Driedger
    # ============================================================
    
    # Purpose/scope phrases - Standard legislative openings
    PURPOSE_PHRASES = [
        r'for the purposes? of this (Act|section|subsection|Part)',
        r'for the purposes? of',
        r'subject to (this section|subsection|the regulations?)',
        r'notwithstanding (anything|any other|the)',
        r'despite (anything|any other|the)',
        r'without limiting the generality of',
        r'for greater certainty',
        r'nothing in this (Act|section) (shall|is)',
        r'this Act may be cited as',
        r'shall come into force',
        r'is deemed to have come into force',
        r'has the same meaning as in',
    ]
    
    # Obligation/prohibition phrases - Driedger Ch. III "Simple Prohibitions"
    OBLIGATION_PHRASES = [
        r'shall (not )?',
        r'must (not )?',
        r'may (not )?',
        r'is (not )?entitled to',
        r'is (not )?liable (to|for)',
        r'is (not )?required to',
        r'is (not )?permitted to',
        r'is (not )?authorized to',
        r'is prohibited from',
        r'no person (shall|may)',
        r'every person (shall|who)',
        r'a person who',
        r'any person who',
    ]
    
    # Definition/reference phrases
    DEFINITION_PHRASES = [
        r'means',
        r'includes',
        r'does not include',
        r'has the meaning (assigned|given)',
        r'in this (Act|section|Part)',
        r'as defined in',
        r'within the meaning of',
        r'referred to in',
        r'mentioned in',
        r'set out in',
        r'described in',
        r'specified in',
    ]
    
    # Cross-reference phrases - Heavy in amendments
    REFERENCE_PHRASES = [
        r'under (this|the) (Act|section|subsection|regulations?)',
        r'pursuant to',
        r'in accordance with',
        r'as provided (in|by|for)',
        r'by virtue of',
        r'in respect of',
        r'with respect to',
        r'relating to',
        r'pertaining to',
        r'in relation to',
        r'on behalf of',
        r'as the case may be',
    ]
    
    # Amendment phrases - Dominant in budget implementation acts
    AMENDMENT_PHRASES = [
        r'is (hereby )?amended',
        r'is (hereby )?repealed',
        r'is replaced (by|with)',
        r'the following (is|are) (substituted|added)',
        r'by (adding|deleting|striking out|replacing)',
        r'after (section|subsection|paragraph)',
        r'before (section|subsection|paragraph)',
        r'by renumbering',
        r'comes? into force',
        r'effective (on|from)',
    ]
    
    # ============================================================
    # COMMON LAW TERMINOLOGY - Driedger emphasizes these
    # ============================================================
    
    COMMON_LAW_TERMS = [
        r'whosoever',
        r'whatsoever',
        r'whomsoever',
        r'heretofore',
        r'hereinafter',
        r'thereunder',
        r'thereto',
        r'thereof',
        r'therein',
        r'hereby',
        r'forthwith',
        r'notwithstanding',
        r'the said',
        r'the same',
        r'aforesaid',
        r'hereinbefore',
    ]
    
    # ============================================================
    # BILINGUAL LEGISLATION PATTERNS (Canada-specific)
    # ============================================================
    
    BILINGUAL_PATTERNS = [
        r'\([A-Z][a-z]+\s+\d+\)',         # (Loi de 2025)
        r'—\s*Page\s+\d+\s*—',            # Page markers
        r'SUMMARY\s*/?\s*SOMMAIRE',
        r'(Sa Majesté|Her Majesty)',
        r'(Governor in Council|gouverneur en conseil)',
        r'(Parliament of Canada|Parlement du Canada)',
    ]
    
    # ============================================================
    # ENCODING CORRUPTION DETECTION
    # v8.3.3: Critical fix for flagging garbled text as AI
    # ============================================================
    
    ENCODING_CORRUPTION_PATTERNS = [
        r'Ã©',            # é corrupted
        r'Ã¨',            # è corrupted
        r'Ã ',            # à corrupted
        r'â€™',           # ' corrupted
        r'â€œ',           # " corrupted
        r'â€',            # various corrupted
        r'[^\x00-\x7F]{5,}',  # Long sequences of non-ASCII
        r'[a-z]{20,}',    # Unusually long "words" (garbled)
    ]
    
    def __init__(self):
        """Initialize pattern detector."""
        self.version = "8.3.3"
        
        # Compile all patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile all regex patterns."""
        self.compiled = {
            'enumeration': [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in self.ENUMERATION_PATTERNS],
            'section_structure': [re.compile(p, re.IGNORECASE) for p in self.SECTION_STRUCTURE_PATTERNS],
            'purpose': [re.compile(p, re.IGNORECASE) for p in self.PURPOSE_PHRASES],
            'obligation': [re.compile(p, re.IGNORECASE) for p in self.OBLIGATION_PHRASES],
            'definition': [re.compile(p, re.IGNORECASE) for p in self.DEFINITION_PHRASES],
            'reference': [re.compile(p, re.IGNORECASE) for p in self.REFERENCE_PHRASES],
            'amendment': [re.compile(p, re.IGNORECASE) for p in self.AMENDMENT_PHRASES],
            'common_law': [re.compile(r'\b' + p + r'\b', re.IGNORECASE) for p in self.COMMON_LAW_TERMS],
            'bilingual': [re.compile(p, re.IGNORECASE) for p in self.BILINGUAL_PATTERNS],
            'corruption': [re.compile(p) for p in self.ENCODING_CORRUPTION_PATTERNS],
        }
    
    def analyze(self, text: str, document_type: str = None) -> LegislativeBaselineResult:
        """
        Analyze text for legislative patterns.
        
        Args:
            text: Document text to analyze
            document_type: Optional document type hint
            
        Returns:
            LegislativeBaselineResult with analysis
        """
        patterns_found: Dict[str, int] = {}
        matches: List[LegislativePatternMatch] = []
        warnings: List[str] = []
        
        # Check for encoding corruption first
        corruption_count = 0
        for pattern in self.compiled['corruption']:
            corruption_matches = pattern.findall(text)
            corruption_count += len(corruption_matches)
        
        if corruption_count > 5:
            warnings.append(
                f"⚠️ ENCODING CORRUPTION DETECTED: {corruption_count} instances of corrupted "
                f"characters found. AI detection on corrupted text is unreliable. "
                f"Consider re-extracting source document with proper encoding."
            )
        
        # Count all pattern categories
        total_patterns = 0
        
        for category, patterns in self.compiled.items():
            if category == 'corruption':
                continue  # Already handled
                
            category_count = 0
            for pattern in patterns:
                found = pattern.findall(text)
                category_count += len(found)
                
                # Store detailed matches (first 5 per category)
                if len(found) > 0:
                    for match_text in found[:5]:
                        if isinstance(match_text, tuple):
                            match_text = match_text[0]
                        matches.append(LegislativePatternMatch(
                            pattern_name=pattern.pattern[:50],
                            matched_text=str(match_text)[:100],
                            start_pos=0,
                            end_pos=0,
                            category=category
                        ))
            
            patterns_found[category] = category_count
            total_patterns += category_count
        
        # Determine if text is legislative
        is_legislative = self._is_legislative_text(patterns_found, document_type)
        
        # Calculate AI score adjustment
        # More legislative patterns = larger negative adjustment
        ai_score_adjustment = self._calculate_ai_adjustment(patterns_found, is_legislative)
        
        # Calculate confidence penalty
        # If text is legislative, detection confidence should be reduced
        confidence_penalty = self._calculate_confidence_penalty(patterns_found, is_legislative)
        
        # Add domain warnings
        if is_legislative:
            warnings.append(
                "📋 LEGISLATIVE TEXT DETECTED: This document uses standard legislative "
                "drafting conventions (enumerated lists, legal terminology, formulaic phrases) "
                "that may trigger false positives in AI detection. Pattern-based detection "
                "methods are NOT calibrated for legal text and should be interpreted with caution."
            )
            warnings.append(
                "⚠️ BASELINE COMPARISON UNAVAILABLE: Without comparison to known human-drafted "
                "legislation from the same jurisdiction, claims about AI involvement cannot be "
                "verified. Consider comparing to historical budget implementation acts."
            )
        
        if patterns_found.get('amendment', 0) > 50:
            warnings.append(
                "📝 HIGH AMENDMENT DENSITY: This appears to be an amending act with extensive "
                "cross-references. The repetitive structure of amendments (\"is replaced by\", "
                "\"is amended\") is a drafting convention, not an AI signature."
            )
        
        return LegislativeBaselineResult(
            is_legislative=is_legislative,
            legislative_pattern_count=total_patterns,
            legislative_patterns=patterns_found,
            pattern_matches=matches,
            ai_score_adjustment=ai_score_adjustment,
            confidence_penalty=confidence_penalty,
            warnings=warnings
        )
    
    def _is_legislative_text(self, patterns: Dict[str, int], document_type: str = None) -> bool:
        """Determine if text is legislative based on patterns."""
        
        # Explicit document type
        if document_type in ['legislation', 'bill', 'act', 'statute']:
            return True
        
        # Heuristic detection based on patterns
        indicators = 0
        
        if patterns.get('enumeration', 0) > 10:
            indicators += 1
        if patterns.get('section_structure', 0) > 5:
            indicators += 1
        if patterns.get('purpose', 0) > 5:
            indicators += 1
        if patterns.get('obligation', 0) > 10:
            indicators += 1
        if patterns.get('amendment', 0) > 5:
            indicators += 2  # Strong signal
        if patterns.get('common_law', 0) > 3:
            indicators += 1
        
        return indicators >= 3
    
    def _calculate_ai_adjustment(self, patterns: Dict[str, int], is_legislative: bool) -> float:
        """
        Calculate adjustment to AI detection score.
        
        Returns negative value to REDUCE AI score for legislative text.
        """
        if not is_legislative:
            return 0.0
        
        # Each category of legislative patterns reduces the AI score
        adjustment = 0.0
        
        # Enumeration is THE key false positive trigger
        enum_count = patterns.get('enumeration', 0)
        if enum_count > 50:
            adjustment -= 0.15  # Heavy reduction
        elif enum_count > 20:
            adjustment -= 0.10
        elif enum_count > 5:
            adjustment -= 0.05
        
        # Amendment patterns indicate budget implementation style
        amend_count = patterns.get('amendment', 0)
        if amend_count > 30:
            adjustment -= 0.10
        elif amend_count > 10:
            adjustment -= 0.05
        
        # Formulaic phrases are expected
        formulaic = sum([
            patterns.get('purpose', 0),
            patterns.get('obligation', 0),
            patterns.get('definition', 0),
            patterns.get('reference', 0),
        ])
        if formulaic > 100:
            adjustment -= 0.10
        elif formulaic > 50:
            adjustment -= 0.05
        
        # Cap the adjustment
        return max(adjustment, -0.30)  # Don't reduce by more than 30%
    
    def _calculate_confidence_penalty(self, patterns: Dict[str, int], is_legislative: bool) -> float:
        """
        Calculate penalty to detection confidence.
        
        Returns value between 0 and 1 to REDUCE reported confidence.
        """
        if not is_legislative:
            return 0.0
        
        total_patterns = sum(patterns.values())
        
        # More legislative patterns = less confidence in AI detection
        if total_patterns > 500:
            return 0.40  # Reduce confidence by 40%
        elif total_patterns > 200:
            return 0.30
        elif total_patterns > 100:
            return 0.20
        elif total_patterns > 50:
            return 0.10
        
        return 0.0


def create_legislative_detector() -> LegislativePatternDetector:
    """Factory function for legislative pattern detector."""
    return LegislativePatternDetector()


def analyze_for_legislative_baseline(text: str, document_type: str = None) -> Dict:
    """
    Convenience function to analyze text for legislative patterns.
    
    Returns dict suitable for JSON serialization.
    """
    detector = LegislativePatternDetector()
    result = detector.analyze(text, document_type)
    
    return {
        'is_legislative': result.is_legislative,
        'legislative_pattern_count': result.legislative_pattern_count,
        'legislative_patterns': result.legislative_patterns,
        'ai_score_adjustment': result.ai_score_adjustment,
        'confidence_penalty': result.confidence_penalty,
        'warnings': result.warnings,
        'pattern_samples': [
            {
                'category': m.category,
                'pattern': m.pattern_name,
                'matched': m.matched_text
            }
            for m in result.pattern_matches[:20]  # First 20 samples
        ]
    }


if __name__ == '__main__':
    # Test with sample legislative text
    sample = """
    An Act to implement certain provisions of the budget tabled in Parliament
    
    1. This Act may be cited as the Budget 2025 Implementation Act, No. 1.
    
    2. (1) For the purposes of this Act, "Minister" means the Minister of Finance.
    
    (2) Subject to subsection (3), every person who is entitled to receive benefits
    under this Act shall file a return in accordance with the regulations.
    
    3. Paragraph 12(1)(t) of the Income Tax Act is replaced by the following:
    
    (t) any amount included in computing the taxpayer's income for the year
        (i) under paragraph (a), or
        (ii) under paragraph (b) as the case may be.
    
    4. Notwithstanding anything in this Act, the Governor in Council may make regulations
    for the purposes of this section.
    """
    
    result = analyze_for_legislative_baseline(sample, 'legislation')
    
    print("=" * 60)
    print("LEGISLATIVE BASELINE ANALYSIS")
    print("=" * 60)
    print(f"\nIs Legislative: {result['is_legislative']}")
    print(f"Pattern Count: {result['legislative_pattern_count']}")
    print(f"AI Score Adjustment: {result['ai_score_adjustment']:.2%}")
    print(f"Confidence Penalty: {result['confidence_penalty']:.2%}")
    print(f"\nPattern Breakdown:")
    for category, count in result['legislative_patterns'].items():
        print(f"  {category}: {count}")
    print(f"\nWarnings:")
    for warning in result['warnings']:
        print(f"  {warning}")

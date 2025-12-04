# Bill C-15-10 Output Analysis & Refinement Proposals

**Analysis Date:** December 2025  
**Version Analyzed:** 8.3.2 outputs (pre-v8.3.4 full integration)  
**Analyst:** Sparrow SPOT Scale™ QA Review

---

## Executive Summary

After examining the Bill-C15-10 analysis outputs (JSON, AI Usage Explanation, Narrative, Certificate HTML), several significant issues have been identified that require immediate attention. The most critical issue is **bilingual PDF extraction corruption**, which is causing cascading problems throughout the analysis pipeline.

### Priority Issues Identified

| Issue | Severity | Impact | Fix Complexity |
|-------|----------|--------|----------------|
| Bilingual PDF Extraction Corruption | 🔴 Critical | All pattern analysis | Medium |
| Pattern Detection on Garbled Text | 🔴 Critical | False pattern matches | Low |
| Version Inconsistency in Report | 🟡 Medium | User confusion | Trivial |
| AI Usage Report Contradictions | 🟡 Medium | Report credibility | Low |
| Narrative Missing Document Context | 🟡 Medium | Generic output | Low |
| Certificate Shows Old AI Score | 🟡 Medium | Inconsistent data | Low |

---

## Critical Issue #1: Bilingual PDF Extraction Corruption

### Evidence

The JSON output shows severely corrupted text samples in the pattern detection:

```json
{
  "matched_text": "000. le ministre des Finances peut verser à la Banque de l'infrastruc- lme amy ipnaisyt rteo dthees",
  "context": "sro mofm Feinsa qnucee may pay to the Canada Infrastructure Bank to $45,000,000,000. le ministre des Finances peut verser à la Banque de l'infrastruc- lme amy ipnaisyt rteo dthees CFainnaandcae sIn pfreaustt rvuecrtsuerer àB alan kB taon $q4u5e, 0d0e0 ,l0'i0n0fr,0a0st0r.uc-"
}
```

### Root Cause Analysis

Bill C-15 is a **bilingual document** (English and French in parallel columns). The PDF extraction process is **interleaving characters from both columns**, producing gibberish like:
- `"lme amy ipnaisyt rteo dthees"` → should be `"the Minister may pay to the"`
- `"CFainnaandcae sIn pfreaustt rvuecrtsuerer"` → English + French mixed

### Impact

1. **Pattern detection matches garbage text** - finding "structured lists" in corrupted fragments
2. **Statistical analysis skewed** - lexical diversity, perplexity based on corrupted text
3. **False confidence in pattern counts** - 629 patterns found, but many are artifacts
4. **Context samples unusable** - the "evidence" shown is meaningless

### Proposed Fix

```python
# In article_analyzer.py or PDF extraction pipeline

def detect_bilingual_corruption(text: str) -> Dict:
    """Detect if extracted text shows bilingual interleaving corruption."""
    indicators = {
        'interleaved_chars': 0,
        'suspicious_fragments': [],
        'corruption_score': 0.0
    }
    
    # Pattern: Lowercase letters followed by uppercase then lowercase in tight sequence
    # e.g., "lme amy" or "sro mofm" - indicates column interleaving
    interleave_pattern = r'\b[a-z]{2,4}\s[a-z]{2,4}\b(?:\s[a-z]{2,4}){2,}'
    matches = re.findall(interleave_pattern, text)
    
    # Check for mixed language fragments
    french_english_mix = r'(?:the|of|to|and)\s+(?:le|la|de|du|des|à)\s+(?:the|of|to|and)'
    
    # Calculate corruption score
    if len(matches) > 50:
        indicators['corruption_score'] = min(1.0, len(matches) / 500)
        indicators['is_corrupted'] = True
        
    return indicators

def handle_bilingual_document(text: str) -> str:
    """Attempt to separate or clean bilingual corruption."""
    # Option 1: Try to identify and extract only English content
    # Option 2: Mark document as unsuitable for pattern analysis
    # Option 3: Use OCR with column detection for bilingual PDFs
    pass
```

**Recommended Actions:**
1. Add corruption detection BEFORE pattern analysis
2. If corruption > threshold, skip Level 3 pattern analysis
3. Add prominent warning to all outputs: "⚠️ Bilingual PDF extraction issues detected"
4. Consider using layout-aware PDF extraction (pdfplumber with column detection)

---

## Critical Issue #2: Pattern Detection on Corrupted Text

### Evidence

The "detailed_matches" in JSON shows pattern samples that are meaningless:

```json
"samples": [
  {
    "matched_text": "2024. gueur le 16 avril 2024. fgourecuer o lne 1A6p arvilr 1il6 2, 022042.4.",
    "line_number": 1446
  }
]
```

This is matching "2024." at the start as a "structured list" but the context is garbage.

### Proposed Fix

```python
def validate_pattern_sample(sample: str, context: str) -> bool:
    """Validate that a pattern match is not from corrupted text."""
    
    # Check 1: Character entropy - corrupted text has unusual patterns
    def char_entropy(s):
        from collections import Counter
        freq = Counter(s.lower())
        total = sum(freq.values())
        return -sum((c/total) * math.log2(c/total) for c in freq.values() if c > 0)
    
    # Check 2: Word validity - corrupted text has non-dictionary fragments
    valid_word_ratio = count_valid_words(context) / len(context.split())
    
    # Check 3: Character sequence patterns indicating interleaving
    has_suspicious_patterns = bool(re.search(r'[a-z]{1,2}[A-Z][a-z]{1,2}[A-Z]', context))
    
    # Reject if context appears corrupted
    if valid_word_ratio < 0.5 or has_suspicious_patterns:
        return False
        
    return True
```

---

## Medium Issue #3: AI Usage Report Contradictions

### Evidence

The AI Usage Explanation report contains internal contradictions:

**Executive Summary says:**
> "This document shows patterns consistent with primarily human authorship."

**But the AI Usage Synthesis says:**
> "Based on the analysis, AI appears to have played a **significant role** in creating this legislation document. The **high percentage** of AI content detected (11.8%)..."

11.8% is NOT "high" - it's in the "minimal" range. The synthesis text contradicts the executive summary.

### Root Cause

The narrative synthesis is generated by Ollama/LLM and isn't properly calibrated to the actual scores. The LLM is being too dramatic about what 11.8% means.

### Proposed Fix

In `ai_usage_explainer.py`, add score-calibrated prompting:

```python
def generate_synthesis(self, ai_score: float, document_type: str) -> str:
    """Generate synthesis with score-calibrated language."""
    
    # Calibrated terminology
    if ai_score < 0.15:
        intensity = "minimal"
        role_description = "minor or absent"
    elif ai_score < 0.30:
        intensity = "moderate"
        role_description = "limited"
    elif ai_score < 0.50:
        intensity = "significant"
        role_description = "substantial"
    else:
        intensity = "extensive"
        role_description = "major"
    
    # Include calibration in prompt
    prompt = f"""
    Generate a synthesis for a {document_type} with {ai_score*100:.1f}% AI detection score.
    
    CRITICAL: Use language appropriate for the score level:
    - Score level: {intensity}
    - AI role was: {role_description}
    
    Do NOT describe 11.8% as "high" or "significant" - it is minimal.
    """
```

---

## Medium Issue #4: Version Inconsistency

### Evidence

- JSON shows: `"version": "8.3.2"`
- AI Usage Report says: `"Analysis Version: Sparrow SPOT Scale™ v8.3.4"`
- Certificate says: `"v8.3 with Narrative Engine"`

### Proposed Fix

Ensure all outputs pull version from a single source:

```python
# In config.py or version.py
SPARROW_VERSION = "8.3.4"

# All generators should use:
from sparrow_grader_v8 import VERSION
```

---

## Medium Issue #5: Narrative Missing Document Context

### Evidence

The narrative output (`Bill-C15-10_narrative.txt`) is entirely generic:

> "This comprehensive analysis of the recently enacted legislation, designated as Bill/Act [Title]..."

It doesn't mention:
- This is Bill C-15 (Budget Implementation Act)
- It's a bilingual document
- It's an omnibus bill
- The specific score interpretation for legislative documents

### Proposed Fix

The narrative engine should receive document type calibration context:

```python
def generate_narrative(analysis: dict) -> str:
    """Generate narrative with document-type awareness."""
    
    doc_type = analysis.get('document_type', 'general')
    doc_baseline = analysis.get('ai_detection', {}).get('document_baseline', {})
    
    context_additions = []
    
    if doc_type == 'legislation':
        context_additions.append(
            f"This is legislative text with {doc_baseline.get('pattern_count', 0):,} "
            f"standard drafting patterns detected."
        )
        
        if 'omnibus' in str(doc_baseline.get('conventions', [])).lower():
            context_additions.append(
                "As an omnibus/budget implementation bill, it contains multiple "
                "diverse policy areas in a single document."
            )
```

---

## Medium Issue #6: Certificate Shows Inconsistent AI Detection Score

### Evidence

- JSON `ai_detection.ai_detection_score`: `0.118` (11.8%)
- Certificate Ethical Framework shows: `"AI Detection: 18.0%"`

The certificate is showing a different (higher) score than the JSON.

### Root Cause

The certificate may be pulling from a different field or using an un-adjusted score.

### Proposed Fix

Audit the certificate generator to ensure it uses the adjusted/calibrated score:

```python
# In certificate_generator.py
def generate_certificate(analysis: dict) -> str:
    # Use the ADJUSTED score from ai_detection
    ai_score = analysis.get('ai_detection', {}).get('ai_detection_score', 0)
    # NOT the raw un-calibrated score
```

---

## Additional Observations

### Pattern Count Seems Excessive

The analysis claims **15,532 legislative patterns** detected. This seems high for a ~760,000 word document. While Bill C-15 is large (omnibus budget bill), the pattern detection may be:

1. Double-counting patterns that appear in both EN and FR text
2. Counting corrupted fragments as patterns
3. Using overly broad regex patterns

**Recommendation:** Add deduplication and language filtering to pattern counting.

### Phrase Fingerprints Show Generic Matches

The 52 "model signatures" are mostly matches to generic phrases like "to enable" which appear in any formal document. These should be weighted lower or excluded for legislative text.

### Statistical Metrics May Be Skewed

- Perplexity: 4369.05 (extremely high, possibly due to corrupted bilingual text)
- Burstiness: 0.180 (normal)
- Lexical Diversity: 0.150 (normal for legal text)

The perplexity score is abnormally high, likely because the language model is confused by the interleaved EN/FR text.

---

## Recommended Implementation Priority

### Phase 1: Critical (Immediate)

1. **Add bilingual corruption detection** in PDF extraction
2. **Skip pattern analysis** if corruption score > threshold
3. **Add prominent warnings** to all outputs when corruption detected
4. **Fix version number consistency** across all outputs

### Phase 2: High Priority (This Week)

1. **Calibrate AI Usage synthesis language** to score levels
2. **Fix certificate score source** to use adjusted score
3. **Add document context** to narrative generator
4. **Filter out corrupted samples** from pattern display

### Phase 3: Medium Priority (This Sprint)

1. **Implement layout-aware PDF extraction** for bilingual documents
2. **Add language detection** to separate EN/FR content
3. **Deduplicate patterns** across languages
4. **Weight phrase fingerprints** by document type

---

## Appendix: Key Files to Modify

| File | Changes Needed |
|------|----------------|
| `article_analyzer.py` | Add corruption detection |
| `deep_analyzer.py` | Skip pattern analysis on corrupted text |
| `ai_usage_explainer.py` | Calibrate synthesis language |
| `certificate_generator.py` | Fix score source |
| `narrative_engine.py` | Add document context |
| `document_type_baselines.py` | Add bilingual handling |

---

## Conclusion

The Bill-C15-10 output analysis reveals that **bilingual PDF extraction corruption** is the root cause of multiple downstream issues. Fixing the extraction pipeline will resolve the pattern detection problems, improve statistical metrics accuracy, and provide meaningful evidence samples in reports.

The system's calibration for legislative documents (v8.3.4) is working as designed - the AI detection score was appropriately reduced to 11.8% with proper warnings about detection method disagreement. However, the corrupted source text is undermining the quality of pattern evidence and statistical analysis.

**Priority Action:** Implement corruption detection and skip pattern analysis for documents with detected extraction issues.

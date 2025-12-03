# Document Type Calibration System

**Version:** 8.3.4  
**Date:** December 2, 2025  
**Purpose:** Reduce AI detection false positives through domain-specific baseline calibration

---

## Executive Summary

Version 8.3.4 introduces comprehensive document type calibration to address a critical issue identified in "The AI Detection Paradox" analysis: specialized documents (legislation, budgets, legal judgments) use standard conventions that may incorrectly trigger AI detection.

### The Problem

Traditional AI detection methods flag patterns such as:
- Enumerated lists with (a), (b), (c) formatting
- Legal terminology ("notwithstanding", "subject to", "pursuant to")
- Formulaic phrases ("comes into force", "is replaced by")
- Structured sections with consistent formatting
- Hedging language ("may", "should", "could")

**However, these patterns are STANDARD CONVENTIONS in specialized domains**, not indicators of AI authorship.

### The Solution

Document type baselines:
1. **Detect document type** automatically from content
2. **Identify domain-specific patterns** that are expected for that type
3. **Apply score adjustments** to reduce false positives
4. **Add confidence penalties** when results are unreliable
5. **Generate warnings** explaining limitations

---

## Supported Document Types

| Type | Description | Max Score Adjustment | Max Confidence Penalty |
|------|-------------|---------------------|----------------------|
| `legislation` | Bills, acts, statutes | -30% | 40% |
| `budget` | Fiscal documents, estimates | -25% | 35% |
| `legal_judgment` | Court decisions, rulings | -25% | 35% |
| `policy_brief` | Policy proposals, white papers | -20% | 30% |
| `research_report` | Academic/institutional research | -20% | 30% |
| `news_article` | Journalism, press releases | -15% | 25% |
| `analysis` | Audits, evaluations | -15% | 25% |
| `report` | General government/corporate | -10% | 20% |

---

## Pattern Categories by Document Type

### Legislation

Based on Driedger's "Manual of Instructions for Legislative and Legal Writing" (1982):

- **Enumeration Patterns**: (a), (b), (c); (i), (ii), (iii); 1., 2., 3.
- **Section Structure**: Section X, subsection (Y), paragraph (z)
- **Legislative Phrases**: "comes into force", "is amended", "is replaced by"
- **Obligation Words**: "shall", "must", "may", "is entitled to"
- **Definition Patterns**: '"X" means', 'for the purposes of this Act'
- **Amendment Phrases**: 'is replaced by the following', 'before paragraph'
- **Common Law Terms**: 'notwithstanding', 'subject to', 'pursuant to'
- **Bilingual Patterns**: (French) / (English) alternation

### Budget Documents

- **Fiscal Terms**: "appropriation", "estimates", "fiscal year"
- **Budget Structure**: "Vote 1", "Program", "Departmental"
- **Percentage Phrases**: "per cent increase", "percentage of GDP"
- **Table Indicators**: "Total", "$X billion", column headers
- **Fiscal Phrases**: "year-over-year", "projected spending"
- **Accountability Terms**: "Minister of Finance", "Treasury Board"

### Legal Judgments

- **Paragraph Citations**: [1], [2], [3], [para 23]
- **Case Citations**: "v.", "SCC", "FC", "ONCA", "[2024]"
- **Legal Reasoning**: "In my view", "I conclude", "accordingly"
- **Latin Terms**: "prima facie", "stare decisis", "obiter dicta"
- **Court Structure**: "appellant", "respondent", "intervenor"
- **Judgment Phrases**: "appeal is dismissed", "order that"

### Policy Briefs

- **Executive Summary**: "Executive Summary", "Key Findings"
- **Recommendation Format**: "Recommendation 1:", "We recommend"
- **Policy Language**: "stakeholder", "consultation", "implementation"
- **Impact Assessment**: "cost-benefit", "expected outcomes"
- **Structure Markers**: "Background", "Options", "Conclusion"

### Research Reports

- **Academic Structure**: "Introduction", "Methodology", "Results"
- **Citation Markers**: "(Author, Year)", "[1]", "et al."
- **Statistical Language**: "p < 0.05", "confidence interval"
- **Hedging**: "suggests", "indicates", "may be"
- **Limitation Acknowledgment**: "limitations include"

### News Articles

- **Dateline Format**: "OTTAWA — ", "WASHINGTON —"
- **Attribution**: "said", "according to", "sources say"
- **Quote Integration**: direct quotes with said/stated
- **AP Style**: numbers, abbreviations, titles

---

## How Calibration Works

### 1. Pattern Detection

```python
from document_type_baselines import DocumentTypeDetector

detector = DocumentTypeDetector()
result = detector.get_calibration(text, document_type='legislation')
```

### 2. Result Structure

```python
{
    'document_type': 'legislation',
    'is_specialized': True,
    'pattern_count': 12970,
    'patterns_by_category': {
        'enumeration': 7536,
        'section_structure': 4240,
        'amendment_phrases': 1037,
        ...
    },
    'ai_score_adjustment': -0.30,  # -30%
    'confidence_penalty': 0.40,     # 40%
    'detected_conventions': [
        'Parliamentary/statutory drafting format',
        'Budget implementation/omnibus bill structure'
    ],
    'warnings': [
        '📋 LEGISLATIVE TEXT: Uses standard drafting conventions...'
    ]
}
```

### 3. Score Application

The AI detection engine applies calibration:

```python
# Original score before calibration
consensus_score = 0.42  # 42%

# Apply score adjustment
adjusted_score = consensus_score + result.ai_score_adjustment
# 0.42 + (-0.30) = 0.12 (12%)

# Apply confidence penalty
confidence = original_confidence * (1 - result.confidence_penalty)
# 0.95 * 0.60 = 0.57 (57%)
```

---

## Test Results

### Bill C-15 (Budget Implementation Act)

| Metric | Before Calibration | After Calibration |
|--------|-------------------|-------------------|
| AI Score | 42% | 12% |
| Confidence | 95% | 27% |
| Warning | None | Legislative text warning |
| Patterns | Not detected | 12,970 standard patterns |

### 2025 Federal Budget

| Metric | Before Calibration | After Calibration |
|--------|-------------------|-------------------|
| AI Score | ~50% | 26% |
| Auto-detected Type | N/A | "budget" |
| Patterns | Not detected | 2,184 fiscal patterns |

---

## Integration Points

### AI Detection Engine

```python
# ai_detection_engine.py
from document_type_baselines import DocumentTypeDetector

class AIDetectionEngine:
    def __init__(self):
        self.document_type_detector = DocumentTypeDetector()
    
    def analyze_document(self, text, document_type=None):
        # Comprehensive detection + calibration
        baseline = self.document_type_detector.analyze(text, document_type)
        # Apply adjustments...
```

### AI Usage Explainer

The explainer now includes baseline context in reports:

```markdown
⚠️ **SPECIALIZED DOCUMENT**: This legislation uses standard domain 
conventions (Parliamentary/statutory drafting format) that may trigger 
false positives. Detected 12,970 standard patterns. Score adjusted by 
-30% to reduce false positives.
```

---

## Limitations

1. **Not exhaustive**: New document types may need additional baselines
2. **Language-specific**: Currently optimized for English/French Canadian documents
3. **Pattern-based**: Cannot detect semantic AI indicators
4. **Threshold-based**: Adjustment amounts are approximations

---

## Future Enhancements

1. **Baseline validation**: Compare against known human-authored documents
2. **Machine learning calibration**: Learn optimal adjustments from training data
3. **International standards**: Add patterns for other jurisdictions
4. **Hybrid detection**: Combine pattern-based with semantic analysis

---

## References

- Driedger, E.A. (1982). *Manual of Instructions for Legislative and Legal Writing*. Department of Justice Canada.
- "The AI Detection Paradox: A Critical Analysis of Algorithmic Claims About Bill C-15" (2025). Internal critique document.
- NIST AI Risk Management Framework (AI RMF 1.0).

---

## Files

| File | Purpose |
|------|---------|
| `document_type_baselines.py` | Comprehensive baseline definitions |
| `legislative_baseline.py` | Legacy legislation-only baseline |
| `ai_detection_engine.py` | Integration with detection |
| `ai_usage_explainer.py` | Report generation with context |

---

*Document Type Calibration System — Sparrow SPOT Scale™ v8.3.4*

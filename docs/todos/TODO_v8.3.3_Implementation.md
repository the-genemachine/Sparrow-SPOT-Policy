# Sparrow SPOT Scale™ v8.3.3 - Implementation TODO

**Created:** December 1, 2025  
**Status:** Pending Implementation  
**Source:** Follow-Up Document Set Analysis Report: Bill C-15-05  
**Previous Version:** v8.3.2 (all 14 items completed)

---

## Executive Summary

The Sparrow's follow-up analysis of Bill C-15-05 identified 4 new issues and 4 unresolved issues from prior recommendations. System health improved from 45/100 to 78/100, but refinement is needed.

**Priority Focus Areas:**
1. Trust score display precision
2. Robustness score non-determinism
3. Warning system granularity
4. Pattern detection context validation

---

## Priority 1: Quick Fixes (Week 1)

### 1.1 Fix Trust Score Display Precision

**Severity:** MEDIUM  
**File(s):** `certificate_generator.py`  
**Est. Time:** 15 minutes

**Current Behavior:**
- Certificate HTML: 58
- JSON: 58.7

**Root Cause:** Certificate template rounds to integer, JSON uses full precision.

**Fix:**
```python
# Display with 1 decimal place instead of integer rounding
trust_score_display = f"{trust_score:.1f}"  # Shows 58.7
```

---

### 1.2 Fix Model Confidence Display Accuracy

**Severity:** LOW  
**File(s):** `certificate_generator.py`  
**Est. Time:** 10 minutes

**Current Behavior:**
- Certificate shows: 100% confidence (capped)
- JSON shows: 90.0% confidence (actual)

**Root Cause:** Display logic caps at 100% instead of showing actual value.

**Fix:**
```python
# Show actual confidence, not capped maximum
display_confidence = model_confidence  # Not min(model_confidence, 100)
```

---

### 1.3 Fix Stakeholder Balance Minor Variance

**Severity:** LOW  
**File(s):** `gui/sparrow_gui.py`, `ollama_summary_generator.py`  
**Est. Time:** 15 minutes

**Current Behavior:**
- Certificate/JSON: 76.6
- Ollama/Narrative: 77.0

**Root Cause:** Different rounding in Ollama summary generation.

**Fix:** Standardize rounding to 1 decimal place across all outputs.

---

## Priority 2: Robustness Determinism (Week 2)

### 2.1 Investigate Non-Deterministic Robustness Scores

**Severity:** HIGH  
**File(s):** `trust_score_calculator.py`, related modules  
**Est. Time:** 2-4 hours

**Current Behavior:**
- Bill-C15-04: Robustness 64.3/100
- Bill-C15-05: Robustness 74.3/100 (+10 points)
- Same source document, different scores

**Investigation Steps:**
1. Add debug logging to robustness calculation
2. Run analysis 5 times on identical PDF
3. Compare intermediate values
4. Identify variance source

**Potential Causes:**
- Random seed not fixed
- Timestamp-dependent logic
- Memory state affecting calculations
- Different evaluation criteria between versions

**Fix Pattern:**
```python
import random
import numpy as np

def calculate_robustness(data, seed=42):
    """Calculate robustness with fixed seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    
    # ... calculation logic ...
```

---

### 2.2 Add Reproducibility Regression Tests

**Severity:** MEDIUM  
**File(s):** New `test_determinism.py`  
**Est. Time:** 1 hour

**Test Cases:**
```python
def test_same_pdf_same_scores():
    """Same input must produce identical output."""
    pdf = 'test_articles/sample.pdf'
    run1 = analyze(pdf)
    run2 = analyze(pdf)
    
    assert run1.robustness == run2.robustness
    assert run1.trust_score == run2.trust_score
    assert run1.pattern_counts == run2.pattern_counts
```

---

## Priority 3: Warning System Enhancement (Week 3)

### 3.1 Implement Detailed Warning Generation

**Severity:** MEDIUM  
**File(s):** `escalation_manager.py`, `trust_score_calculator.py`  
**Est. Time:** 3 hours

**Current Behavior:**
```json
"escalation_triggers": [
  "Trust Score below 70 threshold (score: 58.7/100)"
]
```

**Target Behavior:**
```json
"escalation_triggers": [
  "Trust Score below 70 threshold (58.7/100)",
  "Bias detected: Fairness score critical (33.3/100)",
  "Disparate Impact Ratio failed for Vulnerable_Groups (DIR: 0.00)",
  "Equalized Odds Difference exceeded threshold (EOD: 0.667)"
]
```

**Implementation:**
```python
def generate_detailed_warnings(analysis_results):
    warnings = []
    
    # Trust score warnings
    ts = analysis_results.get('trust_score', {})
    score = ts.get('trust_score', 100)
    if score < 70:
        warnings.append({
            'severity': 'HIGH',
            'category': 'TRUST',
            'message': f'Trust Score below threshold: {score}/100 (minimum: 70)'
        })
    
    # Bias warnings with specifics
    ba = analysis_results.get('bias_audit', {})
    if ba.get('bias_detected'):
        warnings.append({
            'severity': 'HIGH',
            'category': 'BIAS',
            'message': f'Fairness score critical: {ba.get("overall_fairness_score", 0)}/100'
        })
        
        for metric in ba.get('fairness_metrics', []):
            if metric.get('status') == 'fail':
                warnings.append({
                    'severity': 'MEDIUM',
                    'category': 'FAIRNESS_METRIC',
                    'message': f'{metric["metric_name"]}: {metric["interpretation"]}',
                    'affected_group': metric.get('comparison_group')
                })
    
    return warnings
```

---

### 3.2 Update Certificate Warning Display

**Severity:** LOW  
**File(s):** `certificate_generator.py`  
**Est. Time:** 30 minutes

**Enhancement:** Display detailed warnings in certificate HTML with severity indicators.

---

## Priority 4: Pattern Detection Validation (Week 4)

### 4.1 Add OCR Corruption Detection

**Severity:** MEDIUM-HIGH  
**File(s):** `ai_section_analyzer.py`  
**Est. Time:** 2 hours

**Current Issue:** 629 patterns flagged, many are OCR garbage.

**Example False Positive:**
```
"000. le ministre des Finances lme amy ipnaisyt rteo dthees"
```

**Fix - OCR Quality Pre-Filter:**
```python
def is_ocr_corrupted(text: str) -> bool:
    """Detect OCR corruption in text segment."""
    # Check for isolated single letters
    if re.search(r'\s[a-z]\s[a-z]\s[a-z]\s', text):
        return True
    
    # Check for mixed case chaos
    if re.search(r'[A-Z]{2,}[a-z]{2,}[A-Z]{2,}', text):
        return True
    
    # Check vowel ratio (corrupted text has low vowels)
    vowels = sum(1 for c in text.lower() if c in 'aeiouàâäèéêëîïôùûüÿ')
    if len(text) > 20 and vowels / len(text) < 0.15:
        return True
    
    return False
```

---

### 4.2 Add Pattern Confidence Scoring

**Severity:** MEDIUM  
**File(s):** `ai_section_analyzer.py`, `deep_analyzer.py`  
**Est. Time:** 2 hours

**Enhancement:** Assign confidence levels to each pattern match.

```python
@dataclass
class PatternMatch:
    pattern_type: str
    matched_text: str
    line_number: int
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    context_quality: float  # 0.0-1.0

def assess_pattern_confidence(match, context):
    """Determine confidence level for a pattern match."""
    if is_ocr_corrupted(context):
        return 'LOW', 0.2
    
    if has_clear_structure(match):
        return 'HIGH', 0.9
    
    return 'MEDIUM', 0.6
```

---

### 4.3 Display Pattern Confidence in Outputs

**Severity:** LOW  
**File(s):** `certificate_generator.py`, `format_renderer.py`  
**Est. Time:** 1 hour

**Target Output:**
```
Pattern Detection: 629 AI patterns found
  - Structured Lists: 303 (High: 245, Medium: 42, Low: 16)
  - Impact Statements: 5 (High: 5)
  - Stakeholder Focus: 229 (High: 180, Medium: 35, Low: 14)
```

---

## Priority 5: Document Type Recognition (Week 5)

### 5.1 Implement Document Type Classifier

**Severity:** MEDIUM  
**File(s):** `citation_quality_scorer.py` (enhance existing)  
**Est. Time:** 2 hours

**Note:** Basic document type detection was added in v8.3.2. This task enhances it.

**Enhancement - More Pattern Types:**
```python
DOCUMENT_TYPE_PATTERNS = {
    'legislation': [
        r'(?i)bill\s+[A-Z]-?\d+',
        r'(?i)act\s+to\s+(implement|amend|repeal)',
        r'(?i)house\s+of\s+(commons|representatives)',
        r'(?i)(section|subsection)\s+\d+\(\d+\)',
        r'(?i)enacted\s+by\s+parliament',
        r'(?i)schedule\s+[A-Z0-9]',
    ],
    'policy_brief': [
        r'(?i)policy\s+(brief|recommendation|proposal)',
        r'(?i)executive\s+summary',
        r'(?i)key\s+(findings|recommendations)',
        r'(?i)impact\s+assessment',
    ],
    'research_report': [
        r'(?i)methodology',
        r'(?i)literature\s+review',
        r'(?i)references',
        r'(?i)abstract',
        r'(?i)(table|figure)\s+\d+',
    ],
    'budget_document': [
        r'(?i)fiscal\s+(year|framework)',
        r'(?i)appropriation',
        r'(?i)expenditure',
        r'(?i)revenue\s+projection',
    ]
}
```

---

### 5.2 Integrate Type-Specific Scoring

**Severity:** MEDIUM  
**File(s):** `citation_quality_scorer.py`, `trust_score_calculator.py`  
**Est. Time:** 2 hours

**Purpose:** Prevent inappropriate scoring based on document type.

**Example - Legislation Shouldn't Be Penalized for No Citations:**
```python
def calculate_citation_score(doc_type, citations):
    if doc_type == 'legislation':
        # Legislation is a primary source
        return {
            'score': 100 if citations == 0 else 80,
            'interpretation': 'Primary legislation - citations not expected'
        }
    elif doc_type == 'research_report':
        # Research needs citations
        return standard_citation_scoring(citations)
```

---

## Priority 6: Regression Testing (Week 6)

### 6.1 Create Comprehensive Test Suite

**Severity:** HIGH  
**File(s):** New `tests/` directory  
**Est. Time:** 4 hours

**Test Categories:**

```python
# tests/test_score_consistency.py
class TestScoreConsistency:
    """Ensure all output files contain identical scores."""
    
    def test_trust_score_matches_across_files(self):
        """Trust score in JSON must match certificate."""
        pass
    
    def test_criteria_scores_match(self):
        """All 6 criteria must be identical across outputs."""
        pass
    
    def test_ai_percentage_consistent(self):
        """AI detection % must be same in all files."""
        pass

# tests/test_determinism.py
class TestDeterminism:
    """Same input must produce same output."""
    
    def test_robustness_reproducible(self):
        """Robustness score must be identical across runs."""
        pass
    
    def test_pattern_counts_reproducible(self):
        """Pattern detection must be deterministic."""
        pass

# tests/test_pattern_detection.py
class TestPatternDetection:
    """Validate pattern matching accuracy."""
    
    def test_ocr_corruption_excluded(self):
        """OCR garbage must not match as patterns."""
        pass
    
    def test_genuine_patterns_detected(self):
        """Real AI patterns must be caught."""
        pass

# tests/test_document_types.py
class TestDocumentTypeRecognition:
    """Document type detection accuracy."""
    
    def test_legislation_detected(self):
        """Bill text must be classified as legislation."""
        pass
    
    def test_policy_brief_detected(self):
        """Policy briefs must be correctly classified."""
        pass
```

---

### 6.2 Add CI/CD Integration

**Severity:** MEDIUM  
**File(s):** New `.github/workflows/test.yml` or similar  
**Est. Time:** 2 hours

**Purpose:** Run tests automatically on code changes.

---

## Implementation Summary Table

| # | Issue | Severity | Week | File(s) | Est. Time |
|---|-------|----------|------|---------|-----------|
| 1.1 | Trust Score Display Precision | MEDIUM | 1 | `certificate_generator.py` | 15 min |
| 1.2 | Model Confidence Accuracy | LOW | 1 | `certificate_generator.py` | 10 min |
| 1.3 | Stakeholder Balance Variance | LOW | 1 | `gui/sparrow_gui.py`, `ollama_summary_generator.py` | 15 min |
| 2.1 | Robustness Non-Determinism | HIGH | 2 | `trust_score_calculator.py` | 2-4 hrs |
| 2.2 | Reproducibility Tests | MEDIUM | 2 | New `test_determinism.py` | 1 hr |
| 3.1 | Detailed Warning Generation | MEDIUM | 3 | `escalation_manager.py` | 3 hrs |
| 3.2 | Certificate Warning Display | LOW | 3 | `certificate_generator.py` | 30 min |
| 4.1 | OCR Corruption Detection | MEDIUM-HIGH | 4 | `ai_section_analyzer.py` | 2 hrs |
| 4.2 | Pattern Confidence Scoring | MEDIUM | 4 | `ai_section_analyzer.py` | 2 hrs |
| 4.3 | Pattern Confidence Display | LOW | 4 | `certificate_generator.py` | 1 hr |
| 5.1 | Document Type Classifier (Enhance) | MEDIUM | 5 | `citation_quality_scorer.py` | 2 hrs |
| 5.2 | Type-Specific Scoring | MEDIUM | 5 | Various | 2 hrs |
| 6.1 | Comprehensive Test Suite | HIGH | 6 | New `tests/` directory | 4 hrs |
| 6.2 | CI/CD Integration | MEDIUM | 6 | New workflow file | 2 hrs |

**Total Items:** 14  
**Total Estimated Time:** ~22 hours

---

## Verification Checklist

After implementation, verify:

- [ ] Trust score shows 1 decimal in certificate (58.7, not 58)
- [ ] Model confidence shows actual value (90%), not capped (100%)
- [ ] All criteria scores match across JSON, TXT, HTML
- [ ] Same PDF produces identical scores on repeated runs
- [ ] Warning messages include specific metric failures
- [ ] OCR garbage is not counted as AI patterns
- [ ] Pattern matches have confidence levels
- [ ] Legislation documents are correctly classified
- [ ] Legislation not penalized for zero citations
- [ ] All regression tests pass

---

## Version History

| Version | Date | Items | Status |
|---------|------|-------|--------|
| v8.3.2 | Dec 1, 2025 | 14/14 | ✅ Complete |
| v8.3.3 | Pending | 0/14 | ⏳ Not Started |

---

## Notes

1. **Pattern Detection (4.1):** Already partially implemented in v8.3.2 with `is_quality_context()`. This task enhances with more OCR-specific checks.

2. **Document Type Recognition (5.1):** Already implemented in v8.3.2 with `_detect_document_type()`. This task adds more document types.

3. **The Sparrow's Guidance:** "Focus on determinism first (Priority 2). A system that produces different results for the same input cannot be trusted, regardless of other improvements."

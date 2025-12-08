# Sparrow SPOT Scale™ v8.3.2 - Consolidated Implementation Plan

**Created:** December 1, 2025  
**Status:** Pending Implementation  
**Document Set Reference:** `/test_articles/Bill-C15/Bill-C15-04/`  
**Analysis Source:** The Sparrow's Bill C-15 Evaluation System Analysis Report

---

## Executive Summary

Critical issues identified in Bill-C15-04 document set requiring immediate attention:
- Score contradictions across output files (FT shows "N/A" in TXT but 53.8 elsewhere)
- 120% confidence display (mathematically impossible)
- Empty data lineage flowchart (0 stages)
- Meta-commentary exposed in narrative output (internal prompts visible)
- False positives in pattern detection (OCR errors, common words)
- OCR artifacts in data lineage claim contexts

---

## Priority 1: Critical Fixes (Week 1)

### 1.1 Fix Fiscal Transparency Score Contradiction

**Severity:** CRITICAL  
**File(s):** `gui/sparrow_gui.py`

**Current Behavior:**
- Certificate: 53.8/100 (correct)
- JSON: 53.8/100 (correct)  
- TXT Summary: "N/A - Fiscal Transparency" (WRONG)

**Root Cause:** The `format_policy_summary()` function is not correctly extracting criteria scores from the results dict.

**Fix:** Ensure criteria scores are properly accessed from `results['criteria']` dict.

---

### 1.2 Fix 120% Confidence Display (Invalid Value)

**Severity:** CRITICAL  
**File(s):** `certificate_generator.py`

**Current Behavior:**
- Certificate shows: "120% confidence" for Cohere detection
- JSON shows: `"confidence": 0.9` (90%)

**Root Cause:** The value 0.90 (already a percentage as decimal) is being incorrectly processed. Possibly multiplied by 100 again or combined with another factor.

**Fix:**
```python
# Cap confidence at 100% and handle both decimal and percentage inputs
if model_confidence <= 1.0:
    display_confidence = round(model_confidence * 100)
else:
    display_confidence = min(round(model_confidence), 100)
```

---

### 1.3 Populate Data Lineage Flowchart (0 Stages Bug)

**Severity:** CRITICAL  
**File(s):** `data_lineage_visualizer.py`, `gui/sparrow_gui.py`

**Current Behavior:**
- Shows: "Total Stages: 0", "Completed: 0", "Failed: 0"
- No actual pipeline stages rendered
- Version shows "v8.2" instead of "v8.3.1"

**Root Cause:** Flowchart generator not receiving pipeline stage data from analysis.

**Fix:**
1. Create stage tracking that logs each processing step
2. Pass stage data to flowchart generator  
3. Generate flowchart AFTER analysis completion, not before
4. Update version string to "v8.3.1"

---

### 1.4 Remove Meta-Commentary from Narrative

**Severity:** CRITICAL  
**File(s):** `narrative_integration.py`

**Current Behavior:**
Narrative contains internal prompts visible to users:
```
TASK: Expand this narrative to approximately 3500 words while:
1. Maintaining the same tone and style
[...instructions...]
Write the expanded narrative now. Do not include any meta-commentary
```

**Root Cause:** Ollama echoes the prompt in its response when expanding narratives.

**Fix:**
1. Strip content between meta-instruction markers before saving
2. Pattern match and remove: "TASK:", "INSTRUCTION:", "ADDITIONAL USER CONTEXT", "Write the expanded narrative now"
3. Add post-processing cleanup function

---

### 1.5 Fix AI Percentage Inconsistency

**Severity:** HIGH  
**File(s):** `ai_disclosure_generator.py`

**Current Behavior:**
- Formal: "Overall AI Content: 31.8%"
- Plain Language: "about 32%"
- Certificate: "31%"
- JSON Level 1: "41.8%"

**Root Cause:** Different sources (consensus vs level1_document) and different rounding logic.

**Fix:**
1. Standardize on `consensus.ai_percentage` as the authoritative value
2. Use consistent formatting across all outputs: either "32%" (rounded) or "31.8%" (1 decimal)
3. Document the methodology for users

---

## Priority 2: High-Impact Improvements (Week 2)

### 2.1 Enhance Pattern Detection Accuracy

**Severity:** HIGH  
**File(s):** `ai_section_analyzer.py`, `deep_analyzer.py`

**Current Problem:**
- 629 patterns flagged, many are false positives
- Matching OCR errors: `"000. le ministre des Finances peut verser à la Ban"`
- Matching common legislative words: "business" (246 occurrences)

**Fix - Multi-stage Validation:**
1. **OCR Error Detection:** Skip patterns found in garbled text
2. **Context Validation:** Verify surrounding text structure is valid
3. **Frequency Filtering:** Exclude patterns appearing in >30% of human legislative texts
4. **Common Word Exclusion:** Don't flag single common words like "business", "government"

---

### 2.2 Implement Document Type Recognition

**Severity:** HIGH  
**File(s):** `citation_quality_scorer.py`, `data_lineage_source_mapper.py`

**Current Problem:**
- Citation report shows 0/100 for legislative document (primary source)
- Data lineage attempts to trace "5% tax rate" as empirical claim needing validation

**Fix:**
```python
document_types = {
    'legislation': {'citations_required': False, 'trace_definitions': False},
    'policy_brief': {'citations_required': True, 'trace_definitions': False},
    'research_report': {'citations_required': True, 'academic_standards': True}
}
```

**Add Legislative Reference Patterns:**
- `r'section \d+'`
- `r'paragraph \([a-z]\)'`  
- `r'subsection \d+\(\d+\)'`
- `r'Act, S\.C\. \d+'`
- `r'clause \d+'`

---

### 2.3 Separate Claim Types in Data Lineage

**Severity:** MEDIUM  
**File(s):** `data_lineage_source_mapper.py`

**Current Problem:** Trying to validate legislative definitions like "the rate shall be 5%"

**Fix - Classify Claims:**
- **Empirical claims:** Require external validation (e.g., "GDP grew by 3%")
- **Legislative definitions:** No validation needed (e.g., "the rate shall be 5%")
- **Policy projections:** Require methodology disclosure only

---

### 2.4 Fix Trust Score Warning System

**Severity:** MEDIUM  
**File(s):** `trust_score_calculator.py`

**Current Problem:**
- `warnings_present: FALSE` despite `bias_detected: TRUE` and `fairness_score: 33.3%`

**Fix:**
```python
if fairness_score < 50:
    warnings_present = True
    warnings.append("FAIRNESS: Score below acceptable threshold")
if bias_detected:
    warnings_present = True
    warnings.append("BIAS: Detected in fairness audit")
```

---

### 2.5 Clean OCR Artifacts from Data Lineage Claims

**Severity:** MEDIUM  
**File(s):** `data_lineage_source_mapper.py`

**Current Problem:**
JSON contains garbled claim contexts:
- `"aapfrte\u00e8rs aent adv baenfto 2re0 317"`
- `"smueb pda\u00e9rtaegrrmapinh\u00e9"`

**Fix:**
1. Apply `_clean_ocr_artifacts()` to claim context strings before saving
2. Skip claims where context is >50% garbled (low vowel ratio)
3. Add "ocr_quality" flag to claims indicating confidence in text quality

---

## Priority 3: Quality Enhancements (Week 3)

### 3.1 Add Validation Middleware

**Severity:** MEDIUM  
**File(s):** New file `validation_middleware.py` or add to existing

**Purpose:** Catch errors before file generation

**Checks:**
- All score fields populated (no "N/A" unless intentional)
- Confidence values ≤ 100%
- AI percentage values consistent across output files
- Required JSON fields present before template rendering
- Percentages in valid range 0-100

---

### 3.2 Improve Contradiction Detection

**Severity:** MEDIUM  
**File(s):** `contradiction_detector.py`

**Current Problem:** Reports "No contradictions detected" but document set has obvious issues

**Enhancements:**
1. **Cross-File Validation:** Check score consistency across generated files
2. **Value Range Validation:** Catch confidence >100%, invalid percentages
3. **Numerical Consistency:** Flag same metric with different values
4. **Self-Contradiction Detection:** Compare outputs before saving

---

### 3.3 Reduce File Redundancy (Optional)

**Severity:** LOW  
**File(s):** `gui/sparrow_gui.py`, various generators

**Current Problem:**
- 4 AI disclosure files (HTML + 3 TXT) with overlapping content

**Options:**
1. Keep HTML (all formats) + single TXT (formal only)
2. Add configuration for users to select output formats
3. Make separate TXT files opt-in rather than default

---

### 3.4 Clarify NIST Compliance Scope

**Severity:** LOW  
**File(s):** `nist_compliance_checker.py`

**Current Problem:** System grades itself as NIST compliant (circular validation)

**Fix:**
- Label as "Analysis System NIST AI RMF Compliance"
- Clarify this assesses the Sparrow tool, not the analyzed document

---

## Priority 4: Architecture Improvements (Week 4+)

### 4.1 Implement Single Source of Truth Pattern

**Problem:** Scores calculated/formatted in multiple places → inconsistencies

**Solution:** All output generators read from single validated results object
```python
class AnalysisResults:
    def __init__(self):
        self._validated_scores = {}  # Single source
    
    def get_score(self, criterion):
        return self._validated_scores[criterion]  # All exporters use this
```

---

### 4.2 Add Analysis Confidence Indicators

**Purpose:** Qualify findings with confidence levels for transparency

**Example Output:**
```
AI Content: 31.8% (High Confidence - multi-method consensus)
Primary Model: Cohere (Medium Confidence - 90% match)  
Pattern Count: 629 (Low Confidence - includes false positives)
```

---

### 4.3 Memory Optimization (Deferred)

**Issue:** Python process uses 10GB+ memory  
**Status:** User requested to keep in mind for later  
**Solution:** Add `gc.collect()` calls, clear large objects after disk write

---

## Implementation Summary Table

| # | Issue | Severity | Week | File(s) | Est. Time |
|---|-------|----------|------|---------|-----------|
| 1.1 | FT Score "N/A" in TXT | CRITICAL | 1 | `gui/sparrow_gui.py` | 15 min |
| 1.2 | 120% Confidence | CRITICAL | 1 | `certificate_generator.py` | 20 min |
| 1.3 | Empty Flowchart + Version | CRITICAL | 1 | `data_lineage_visualizer.py` | 2 hrs |
| 1.4 | Meta-Commentary in Narrative | CRITICAL | 1 | `narrative_integration.py` | 30 min |
| 1.5 | AI % Inconsistent | HIGH | 1 | `ai_disclosure_generator.py` | 20 min |
| 2.1 | Pattern False Positives | HIGH | 2 | `ai_section_analyzer.py` | 2 hrs |
| 2.2 | Document Type Recognition | HIGH | 2 | `citation_quality_scorer.py` | 1 hr |
| 2.3 | Claim Type Classification | MEDIUM | 2 | `data_lineage_source_mapper.py` | 1 hr |
| 2.4 | Warning System | MEDIUM | 2 | `trust_score_calculator.py` | 30 min |
| 2.5 | OCR in Claims | MEDIUM | 2 | `data_lineage_source_mapper.py` | 30 min |
| 3.1 | Validation Middleware | MEDIUM | 3 | New/existing | 2 hrs |
| 3.2 | Contradiction Detection | MEDIUM | 3 | `contradiction_detector.py` | 2 hrs |
| 3.3 | File Redundancy | LOW | 3 | Various | 1 hr |
| 3.4 | NIST Scope | LOW | 3 | `nist_compliance_checker.py` | 30 min |
| 4.1 | Single Source of Truth | HIGH | 4 | Architecture | 4 hrs |
| 4.2 | Confidence Indicators | LOW | 4 | Various | 2 hrs |

---

## Recommended Testing

### Test Documents to Create

1. **Known Human Document:** Should score low on AI detection
2. **Known AI Document:** Should detect accurately with correct model
3. **Hybrid Document:** Known mix percentage for validation
4. **Legislative Document:** Should not penalize for missing citations
5. **Contradiction Document:** Intentional errors to test detection

### Validation Checks After Each Fix

- [ ] All files show consistent scores
- [ ] No confidence values exceed 100%
- [ ] No meta-commentary in narrative output
- [ ] Flowchart shows actual pipeline stages
- [ ] AI percentages match across all outputs
- [ ] Legislative documents not penalized for citations

---

## Files to Examine

```
/test_articles/Bill-C15/Bill-C15-04/
├── Bill-C15-04.json                    # Source of truth - 41.8% vs 31.8%
├── Bill-C15-04.txt                     # Shows "N/A" for FT score
├── Bill-C15-04_certificate.html        # 120% confidence bug
├── Bill-C15-04_narrative.txt           # Meta-commentary visible
├── Bill-C15-04_lineage_flowchart.html  # 0 stages, wrong version
├── Bill-C15-04_data_lineage.json       # Garbled OCR in claim contexts
├── Bill-C15-04_citation_report.txt     # 0/100 (expected for legislation)
└── Bill-C15-04_ai_disclosure_all.html  # Inconsistent percentages
```

---

## The Sparrow's Assessment

> "The system shows **architecturally sound but operationally flawed**. With systematic attention to the identified issues, this tool can achieve its intended purpose of providing trustworthy, transparent AI-assisted policy analysis. The foundation is strong; the implementation requires refinement."

**Positive Aspects Noted:**
- Comprehensive multi-level analysis framework
- Strong theoretical foundation in AI detection methodology
- Extensive output format options
- Thoughtful integration of fairness and bias auditing

**Critical Issues to Address First:**
1. Score contradictions (trust issue)
2. 120% confidence (credibility issue)
3. Empty flowchart (functionality issue)
4. Meta-commentary (polish issue)

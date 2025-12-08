# Analysis of Bill C-15 Document Set - Discrepancy Report

After examining the complete document set, I've identified several critical discrepancies and areas requiring correction. The Sparrow's analysis reveals inconsistencies between different output files and methodological concerns.

## Critical Discrepancies Identified

### 1. **AI Content Detection Score Mismatch**

**Primary Discrepancy:**
- JSON file (`Bill-C15-10.json`): Reports AI detection score of **11.8%**
- Certificate (`Bill-C15-10_certificate.html`): Reports **18.0%**
- AI Disclosure files: All report **18.0%**
- Narrative file: References **11.8%**

**Location Evidence:**
- JSON: `"ai_detection_score": 0.118` (line in ai_detection section)
- Certificate: `<div>18.0%</div>` (in AI Detection Badge)
- Deep Analysis consensus: `"ai_percentage": 18.0`

**Root Cause:** The deep analysis consensus score (18.0%) differs from the base AI detection score (11.8%). The certificate and disclosure files use the consensus score, while the summary text file uses the base score.

**Recommendation:** Standardize on a single authoritative score. The consensus score (18.0%) incorporates multi-level analysis and should be the primary figure, but this should be clearly documented.

---

### 2. **Trust Score Threshold Confusion**

**Discrepancy:**
The ethical summary states:
> "⚠️ PROFESSIONAL REVIEW REQUIRED (Trust Score below 70 threshold (score: 53.0/100))"

However, the trust score interpretation classifies 53.0 as "MEDIUM" which typically means "suitable with human review" rather than requiring professional review.

**Location:** 
- JSON file, ethical_summary section
- Certificate, Ethical Framework Assessment section

**Recommendation:** Clarify the distinction between:
- Automatic escalation threshold (appears to be 70)
- Trust level classifications (LOW/MEDIUM/HIGH)
- When "professional review" vs. "standard review" is required

---

### 3. **Detection Method Disagreement Warning**

**Major Issue:**
The AI detection shows an 85 percentage point spread between methods (5% to 90%), yet the final outputs present this as "High Confidence - multi-method consensus."

**Location Evidence:**
- Detection spread: 0.849 (84.9 percentage points)
- Individual scores range: GPTZero (5.1%) to Cohere (90%)
- Domain warnings explicitly state: "⚠️ DETECTION DISAGREEMENT: Methods disagree by 85 percentage points"

**But disclosure files state:**
> "High Confidence - multi-method consensus"

**Recommendation:** This is misleading. With 85% disagreement, confidence should be classified as LOW or UNCERTAIN, not HIGH. The disclosure language contradicts the technical analysis.

---

### 4. **Document Type Baseline Adjustment Not Reflected**

**Discrepancy:**
The JSON shows:
```json
"document_baseline": {
    "score_adjustment": -0.3,
    "confidence_penalty": 0.4,
    "patterns_by_category": {
        "enumeration": 10280,
        "section_structure": 3992,
        "legislative_phrases": 142
    }
}
```

This indicates a **30% downward adjustment** was applied due to legislative document conventions, plus a 40% confidence penalty.

However, nowhere in the narrative or certificate is this critical adjustment explained to users. The 18% figure shown is post-adjustment, but users don't know the raw score was much higher (~48% before adjustment).

**Recommendation:** Transparently disclose:
- Raw detection score before domain adjustment
- Amount of adjustment applied
- Rationale for adjustment specific to this document type

---

### 5. **Fairness Metrics Interpretation Issues**

**Problem:**
The bias audit shows:
- Overall fairness score: **33.3%** (failing)
- 4 out of 6 fairness metrics **FAILED**
- Significant disparate impact detected

Yet the certificate presents this neutrally without sufficient emphasis on the severity. A 33% fairness score is extremely poor.

**Location:** Certificate, Ethical Framework Assessment section

**Recommendation:** Add clearer warning language:
> "⚠️ CRITICAL: Fairness assessment FAILED (33.3/100). Significant bias detected affecting Vulnerable_Groups. Manual bias review REQUIRED before policy implementation."

---

### 6. **Contradiction Analysis Empty Despite Claims**

**Discrepancy:**
```json
"contradiction_analysis": {
    "contradictions": [],
    "warnings": [],
    "validated_claims": [],
    "severity_score": 0.0,
    "summary": "No contradictions or inconsistencies detected."
}
```

However, the data lineage report shows **12 untraced quantitative claims** with 0% trace rate. This represents potential contradictions or unsupported claims that weren't detected.

**Recommendation:** The contradiction analysis appears non-functional. Either fix the analysis or remove it from outputs to avoid false assurance.

---

### 7. **Pattern Count Discrepancies**

**Issue:**
- Level 3 patterns: **629 total**
- Certificate shows: "629 AI patterns found"
- But breakdown shows: 303 + 5 + 229 + 62 = **599 patterns**

Missing 30 patterns in the detailed breakdown.

**Location:** Deep analysis section, pattern_details

**Recommendation:** Verify pattern counting logic and ensure all detected patterns are included in categorical breakdowns.

---

### 8. **Model Attribution Confidence Mismatch**

**Discrepancy:**
- Primary model confidence shown: **90%**
- But detection confidence shown: **24.8%**

These appear to be different metrics:
- 90% = "If AI was used, it was probably Cohere"
- 24.8% = "We're 24.8% confident AI was actually used"

**Location:** ai_detection section in JSON

**Recommendation:** Clearly differentiate:
- **Detection confidence** (is it AI at all?)
- **Attribution confidence** (which model if AI?)

Current outputs conflate these two distinct metrics.

---

### 9. **Grade Label Inconsistencies**

**Minor Issue:**
The composite grade is "B-" which corresponds to "Needs Improvement" and "Questionable Policy."

However, individual components show:
- Policy Consequentiality: 92.1% (T - Transformative) 
- Public Accessibility: 82.5% (GC - Generally Clear)

There's a disconnect between having "Transformative" policy consequentiality and an overall "Questionable Policy" classification.

**Recommendation:** Review the weighting and classification logic to ensure composite grades align sensibly with component scores.

---

### 10. **Missing Provenance Analysis**

**Critical Gap:**
The lineage flowchart shows Stage 3 as "Pending":
> "Stage 3: Provenance Analysis - PENDING"

But there's no explanation for why this stage wasn't completed or what impact that has on the overall analysis.

**Recommendation:** Either complete provenance analysis or document why it was skipped and what limitations this creates.

---

## Structural Recommendations

### 1. **Add Uncertainty Quantification Section**
Given the massive detection disagreement (85%), add a prominent section explaining:
```
UNCERTAINTY NOTICE
==================
Detection confidence is LOW due to:
- 85% disagreement between detection methods
- Specialized document type (legislation)
- Domain-specific language patterns
- Score adjusted -30% for legislative conventions

The 18% figure should be interpreted as:
"Possible range: 5% to 48% (before adjustment)"
```

### 2. **Standardize on Single Authoritative Metrics**
Create hierarchy:
- **Primary Score:** Deep analysis consensus (currently 18%)
- **Supporting Scores:** Individual method scores (for transparency)
- **Adjusted Score:** After domain corrections
- **Confidence Band:** Min-max range given disagreement

### 3. **Fix Disclosure Language**
Current: "High Confidence - multi-method consensus"
Should be: "MODERATE confidence with significant method disagreement (5%-90% range)"

### 4. **Add Legislative Document Disclaimer**
```
⚠️ LEGISLATIVE DOCUMENT DETECTION LIMITATIONS
This document type uses formal conventions that resemble AI patterns:
- Enumerated provisions (10,280 detected)
- Standardized legal phrases (142 detected)  
- Structured formatting requirements

Base score adjusted -30% to account for domain conventions.
Human legislative drafters naturally produce these patterns.
```

### 5. **Separate Technical from Public-Facing Outputs**
- **Technical JSON:** Keep all raw data, disagreements, adjustments
- **Public Certificate:** Show final consensus with appropriate caveats
- **Disclosure:** Brief, clear, with confidence qualifiers

---

## Priority Fixes (Ranked)

1. **CRITICAL:** Fix "High Confidence" claim when detection spread is 85%
2. **CRITICAL:** Explain document baseline adjustments transparently  
3. **HIGH:** Reconcile 11.8% vs 18.0% score discrepancy
4. **HIGH:** Add clear uncertainty language about detection limitations
5. **MEDIUM:** Fix fairness score presentation (33% is failing, not neutral)
6. **MEDIUM:** Clarify trust score threshold vs. classification confusion
7. **LOW:** Resolve pattern count arithmetic (629 vs 599)
8. **LOW:** Add explanation for skipped provenance analysis

---

## Conclusion

The analysis system is sophisticated but has critical presentation issues that could mislead users. The core problem is **insufficient transparency about uncertainty**. When methods disagree by 85%, users must understand this represents highly uncertain detection, not "high confidence consensus."

The Sparrow's assessment: These discrepancies don't invalidate the analysis but require clearer communication about limitations, especially for a legislative document where false positives are likely due to formal drafting conventions.
# Sparrow SPOT Scale™ v8.3.1 - Implementation Plan

**Created:** November 30, 2025  
**Status:** Pending Implementation  
**Document Set Reference:** `/test_articles/Bill-C15/Bill-C15-03/`

---

## Overview

This document outlines 7 fixes and enhancements identified during analysis of the Bill-C15-03 document set. Issues range from critical bugs affecting output accuracy to new feature requests.

---

## Todo Items

### 1. Add Ollama Query Textbox to Narrative Tab

**Priority:** Enhancement  
**File(s) to Modify:** `gui/sparrow_gui.py`  
**Complexity:** Medium

**Description:**  
Add a text input in the Narrative Settings tab where users can enter custom questions or context prompts to communicate with the Ollama model beyond the preset narrative styles.

**Current Behavior:**  
- Users can only select from preset styles: Explanatory, Critical, Journalistic, Policy Brief
- No way to provide custom prompts or ask specific questions

**Desired Behavior:**  
- Add a textbox labeled "Custom Query/Context (Optional)"
- Allow users to type questions like "Focus on economic impacts" or "Compare to previous budgets"
- Pass this custom prompt to the Ollama model along with the document text

**Implementation Notes:**
```python
# In gui/sparrow_gui.py, add after narrative_style radio buttons:
custom_ollama_query = gr.Textbox(
    label="Custom Query/Context (Optional)",
    placeholder="e.g., 'Focus on tax implications for small businesses' or 'What are the key risks?'",
    lines=3,
    info="Enter a custom question or context to guide the Ollama narrative generation."
)
```

---

### 2. Standardize Version Numbers Across Outputs

**Priority:** High  
**File(s) to Modify:** `sparrow_grader_v8.py`  
**Complexity:** Low

**Description:**  
Version inconsistency across outputs. JSON shows `version: 8.0` but we're on v8.3.1.

**Current Behavior:**  
- JSON: `"version": "8.0"`
- Certificates: Mix of "v8.0", "v8.2", "v8.3"
- Text reports: Various versions

**Desired Behavior:**  
- All outputs should show `"version": "8.3.1"`
- Consistent version string across JSON, certificates, text reports, and disclosures

**Implementation Notes:**
```python
# Add at top of sparrow_grader_v8.py:
SPARROW_VERSION = "8.3.1"

# Update all hardcoded version strings to use:
'version': SPARROW_VERSION
```

**Files with version references to update:**
- `sparrow_grader_v8.py` - Lines with `'version': '8.0'` or similar
- `certificate_generator.py` - Version display in HTML
- `ai_disclosure_generator.py` - Version in disclosure text

---

### 3. Fix Citation Markers - Repetitive/Truncated Words

**Priority:** Medium  
**File(s) to Modify:** `citation_quality_scorer.py`  
**Complexity:** Medium

**Description:**  
Citation report shows repetitive "financial state" (19x) and truncated "nancial state" (missing 'fi'). These are false positives from PDF OCR artifacts.

**Current Output (Problematic):**
```
citation_markers: ['foreign state', 'financial state', 'nancial state', 
'financial state', 'financial state', ... (19 more)]
```

**Root Cause:**  
- The regex pattern for citation detection is matching partial words from bilingual PDF OCR
- "nancial state" is a truncated "financial state" 
- Same phrase detected multiple times due to bilingual duplicates

**Desired Behavior:**  
- Deduplicate citation markers
- Filter out truncated/partial words
- Ignore likely OCR artifacts (words under 3 chars at start, garbled text)

**Implementation Notes:**
```python
# In citation_quality_scorer.py, add deduplication and filtering:
def clean_citation_markers(markers):
    """Remove duplicates and OCR artifacts from citation markers."""
    seen = set()
    cleaned = []
    for marker in markers:
        # Skip if too short or likely truncated
        if len(marker) < 5:
            continue
        # Skip if starts with lowercase (likely mid-word truncation)
        if marker[0].islower() and not marker.startswith('et al'):
            continue
        # Deduplicate (case-insensitive)
        marker_lower = marker.lower().strip()
        if marker_lower not in seen:
            seen.add(marker_lower)
            cleaned.append(marker)
    return cleaned
```

---

### 4. Fix Data Lineage JSON - OCR Artifacts/Misspellings

**Priority:** Medium  
**File(s) to Modify:** `data_lineage_source_mapper.py`  
**Complexity:** Medium-High

**Description:**  
Data lineage contains garbled text from bilingual PDF OCR:
- "axation years" (missing 't' → "taxation")
- "smueb pdaértaegrrmapinhé" (garbled)
- "aapftrèrs Dlee" (garbled)

**Root Cause:**  
- Bill C-15 PDF is bilingual (English/French) with text overlaid
- OCR extraction interleaves both languages
- Result is garbled text that appears in claims analysis

**Options for Fix:**

**Option A: Pre-clean text before lineage analysis**
```python
def clean_ocr_text(text):
    """Remove obvious OCR artifacts from bilingual PDFs."""
    import re
    # Remove lines with excessive non-ASCII or mixed language artifacts
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        # Skip lines with too many non-word characters
        word_chars = sum(1 for c in line if c.isalnum() or c.isspace())
        if len(line) > 0 and word_chars / len(line) < 0.6:
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)
```

**Option B: Add OCR quality flag to output**
```python
# Add to lineage output:
"ocr_quality_warning": "Bilingual PDF detected. Some text may contain OCR artifacts.",
"artifact_indicators": ["interleaved_languages", "truncated_words"]
```

**Recommended:** Implement both options - clean when possible, flag when uncertain.

---

### 5. Fix Narrative Length - Not Meeting Comprehensive Option

**Priority:** High  
**File(s) to Modify:** `gui/sparrow_gui.py`, `narrative_engine.py`, `ollama_summary_generator.py`  
**Complexity:** Medium

**Description:**  
User selected 'Comprehensive' (3500 words) but narrative is only **259 words**.

**Current Output:**
```
$ wc -w Bill-C15-03_narrative.txt
259
```

**Root Cause Analysis Needed:**
1. Check if GUI passes length parameter to narrative generator
2. Check if narrative_engine.py respects the length parameter
3. Check if Ollama prompt includes word count instruction
4. Ollama may be ignoring length instructions

**Implementation Notes:**

**Step 1: Verify GUI parameter passing**
```python
# In gui/sparrow_gui.py, ensure narrative_length is passed:
narrative_length = gr.Radio(
    choices=["Brief", "Standard", "Comprehensive"],
    value="Standard",
    ...
)
# Verify this is included in the function call
```

**Step 2: Update Ollama prompt with explicit length**
```python
# In ollama_summary_generator.py or narrative_engine.py:
length_instructions = {
    "Brief": "Write a concise summary of approximately 500 words.",
    "Standard": "Write a detailed analysis of approximately 1500 words.",
    "Comprehensive": "Write a comprehensive, in-depth analysis of approximately 3500 words. Cover all major aspects including background, key provisions, stakeholder impacts, economic implications, and recommendations."
}

prompt = f"""
{length_instructions[narrative_length]}

Document to analyze:
{document_text[:15000]}

{style_instructions[narrative_style]}
"""
```

**Step 3: Consider chunking for long narratives**
- Ollama has context limits
- May need to generate sections separately and combine

---

### 6. Fix Primary Model Display - Show Cohere Instead of Mixed/Uncertain

**Priority:** High  
**File(s) to Modify:** `ai_detection_engine.py`  
**Complexity:** Low

**Description:**  
Analysis shows "Mixed/Uncertain (90% confidence)" but model_scores clearly show Cohere=0.9 is the highest.

**Current JSON Output:**
```json
"likely_ai_model": {
    "model": "Mixed/Uncertain",
    "confidence": 0.9,
    "analysis": "Multiple model patterns detected. Cohere is most likely but margin is low.",
    "model_scores": {
        "Ollama/Llama": 0.7,
        "Google Gemini": 0.35,
        "Claude (Anthropic)": 0.3,
        "Mistral AI": 0.8,
        "Cohere": 0.9  // <-- Highest score!
    }
}
```

**Root Cause:**  
The logic classifies as "Mixed/Uncertain" when multiple models score above a threshold, even if one is clearly highest.

**Desired Behavior:**  
- If one model has the highest score with >10% margin over second-highest, report that model
- Only report "Mixed/Uncertain" when top 2+ models are within 10% of each other

**Implementation Notes:**
```python
# In ai_detection_engine.py, update model selection logic:
def determine_primary_model(model_scores):
    """Determine primary AI model from scores."""
    if not model_scores:
        return {"model": "Unknown", "confidence": 0}
    
    sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
    top_model, top_score = sorted_models[0]
    
    if len(sorted_models) > 1:
        second_model, second_score = sorted_models[1]
        margin = top_score - second_score
        
        # If margin > 10%, report top model confidently
        if margin > 0.10:
            return {
                "model": top_model,
                "confidence": top_score,
                "analysis": f"{top_model} detected with {margin*100:.0f}% margin over {second_model}."
            }
    
    # If margin is low, still report top model but note uncertainty
    if top_score > 0.5:
        return {
            "model": top_model,
            "confidence": top_score,
            "analysis": f"{top_model} is most likely but margin is low. Multiple model patterns detected."
        }
    
    return {"model": "Mixed/Uncertain", "confidence": top_score}
```

---

### 7. Fix Bill-C15-03.txt - Unknown/N/A Values

**Priority:** High  
**File(s) to Modify:** `gui/sparrow_gui.py` (format_policy_summary function)  
**Complexity:** Low

**Description:**  
Text report shows placeholder values instead of actual data.

**Current Output:**
```
Document: Unknown
Analysis Date: Unknown
Letter Grade: N/A
```

**Desired Output:**
```
Document: Bill C-15: Budget Implementation Act, 2025
Analysis Date: November 30, 2025
Letter Grade: B-
```

**Implementation Notes:**
```python
# In gui/sparrow_gui.py, update format_policy_summary():
def format_policy_summary(results):
    """Format results as text summary."""
    # Get actual values from results
    document_title = results.get('document_title', 'Policy Document')
    timestamp = results.get('timestamp', datetime.now().isoformat())
    composite_score = results.get('composite_score', 0)
    
    # Calculate letter grade from score
    def score_to_grade(score):
        if score >= 93: return 'A+'
        elif score >= 90: return 'A'
        elif score >= 87: return 'B+'
        elif score >= 83: return 'B'
        elif score >= 80: return 'B-'
        elif score >= 77: return 'C+'
        elif score >= 73: return 'C'
        elif score >= 70: return 'C-'
        elif score >= 67: return 'D+'
        elif score >= 63: return 'D'
        elif score >= 60: return 'D-'
        else: return 'F'
    
    letter_grade = score_to_grade(composite_score)
    
    # Format date nicely
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp)
        formatted_date = dt.strftime('%B %d, %Y')
    except:
        formatted_date = timestamp
    
    summary = f"""============================================================
SPOT POLICY™ - POLICY DOCUMENT ANALYSIS
============================================================

Document: {document_title}
Analysis Date: {formatted_date}

Composite Score: {composite_score}/100
Letter Grade: {letter_grade}
...
"""
    return summary
```

---

## Implementation Order (Recommended)

1. **#2 - Version Numbers** (5 min) - Quick win, improves consistency
2. **#7 - Unknown/N/A Values** (10 min) - Quick win, improves output quality  
3. **#6 - Primary Model Display** (15 min) - High impact, fixes misleading info
4. **#5 - Narrative Length** (30 min) - Critical user-facing bug
5. **#3 - Citation Markers** (20 min) - Quality improvement
6. **#4 - OCR Artifacts** (30 min) - Quality improvement, complex
7. **#1 - Ollama Query Textbox** (45 min) - New feature, lowest priority

**Estimated Total Time:** ~2.5 hours

---

## Testing Plan

After implementation, create a new document set `Bill-C15-04` with the same input file to verify:

- [ ] Version shows "8.3.1" in JSON, certificate, and text outputs
- [ ] Text report shows actual document title, date, and letter grade
- [ ] Primary model shows "Cohere" instead of "Mixed/Uncertain"
- [ ] Narrative length is approximately 3500 words when Comprehensive selected
- [ ] Citation markers are deduplicated and cleaned
- [ ] Data lineage has OCR warning or cleaned text
- [ ] (If implemented) Ollama query textbox appears and works

---

## Files Reference

| File | Todos |
|------|-------|
| `gui/sparrow_gui.py` | #1, #5, #7 |
| `sparrow_grader_v8.py` | #2 |
| `certificate_generator.py` | #2 |
| `ai_disclosure_generator.py` | #2 |
| `citation_quality_scorer.py` | #3 |
| `data_lineage_source_mapper.py` | #4 |
| `narrative_engine.py` | #5 |
| `ollama_summary_generator.py` | #5 |
| `ai_detection_engine.py` | #6 |

---

## Notes

- All issues were identified from the Bill-C15-03 document set
- The bilingual PDF (Bill C-15) causes many OCR-related artifacts
- Some fixes may require testing with different document types to ensure no regressions

# Sparrow SPOT Scale™ v8.3.2 - Implementation Plan

**Created:** December 1, 2025  
**Status:** Pending Implementation  
**Document Set Reference:** `/test_articles/Bill-C15/Bill-C15-04/`

---

## Overview

Issues identified during analysis of the Bill-C15-04 document set. Focus areas: percentage consistency, confidence display, flowchart generation, OCR artifact cleaning, and citation detection accuracy.

---

## Summary Table

| # | Issue | Priority | File(s) | Complexity |
|---|-------|----------|---------|------------|
| 1 | AI Percentage Inconsistency (31.8% vs 32%) | High | `ai_disclosure_generator.py` | Low |
| 2 | 120% Confidence Display (should be 90%) | High | `certificate_generator.py` | Medium |
| 3 | Flowchart Empty (0 stages) | Medium | `data_lineage_visualizer.py` | Medium |
| 4 | Flowchart Version Wrong (v8.2 vs v8.3.1) | Low | `data_lineage_visualizer.py` | Low |
| 5 | OCR Garbled Text Still in JSON | High | `data_lineage_source_mapper.py` | Medium |
| 6 | Citation Report All Zeros | Medium | `citation_quality_scorer.py` | Medium |
| 7 | Memory Optimization (10GB usage) | Low | `gui/sparrow_gui.py` | Medium |

---

## Todo Items

### 1. AI Percentage Inconsistency

**Priority:** High  
**File(s) to Modify:** `ai_disclosure_generator.py`

**Current Behavior:**
- Government Formal: "Overall AI Content: 31.8%"
- Plain Language: "about 32% of this document"
- Social Media: "~32% AI-generated"

**Desired Behavior:**
- All formats should use the same precise value: "31.8%" or "32%"
- Decide on a standard: Either always round to nearest integer, or always show 1 decimal

**Root Cause:**
Different disclosure formats use different rounding/formatting logic.

**Fix:**
Standardize percentage display in `_generate_*_disclosure()` methods to use consistent formatting.

---

### 2. 120% Confidence Display (Invalid Value)

**Priority:** High  
**File(s) to Modify:** `certificate_generator.py`, `deep_analyzer.py`

**Current Behavior:**
- Certificate shows: "Primary Model: Cohere" with "120% confidence"
- JSON shows: `"confidence": 0.9` (90%)

**Desired Behavior:**
- Display "90% confidence" (from the model detection result)
- Never exceed 100%

**Root Cause:**
Certificate generator is multiplying confidence by some factor, or combining multiple values incorrectly.

**Investigation Needed:**
Check `certificate_generator.py` for where deep analysis confidence is formatted.

---

### 3. Flowchart Empty (0 Stages)

**Priority:** Medium  
**File(s) to Modify:** `data_lineage_visualizer.py`

**Current Behavior:**
- Flowchart HTML shows: "Total Stages: 0", "Completed: 0", "Failed: 0"
- No actual flowchart content rendered

**Desired Behavior:**
- Show actual pipeline stages (Document Input → Text Extraction → Analysis → etc.)
- Display real processing stages from the analysis run

**Root Cause:**
`DataLineageVisualizer` is not receiving or not using the lineage data from `DataLineageSourceMapper`.

---

### 4. Flowchart Version Wrong

**Priority:** Low  
**File(s) to Modify:** `data_lineage_visualizer.py`

**Current Behavior:**
- Shows: "Sparrow SPOT Scale™ v8.2 Analysis Pipeline"

**Desired Behavior:**
- Shows: "Sparrow SPOT Scale™ v8.3.1 Analysis Pipeline"

**Fix:**
Update hardcoded version string in `generate_html_flowchart()`.

---

### 5. OCR Garbled Text Still in Data Lineage JSON

**Priority:** High  
**File(s) to Modify:** `data_lineage_source_mapper.py`

**Current Behavior:**
JSON contains garbled bilingual OCR text:
- `"aapfrte\u00e8rs aent adv baenfto 2re0 317"`
- `"smueb pda\u00e9rtaegrrmapinh\u00e9 e(a s)e(il)o nor l e(isi )s"`
- `"suoro dl easn adl iDmreungt sR eegt udlartoigouness"`

**Desired Behavior:**
- Either clean the text before extracting claims
- Or filter out claims with garbled context

**Root Cause:**
The `_clean_ocr_artifacts()` method added in v8.3.1 cleans input for `trace_sources()` but claims are extracted with their original context, which may still be garbled.

**Fix Options:**
1. Apply OCR cleaning to claim context strings before saving
2. Add garbled text detection to filter out invalid claims
3. Flag claims as "OCR_ARTIFACT" instead of including garbled text

---

### 6. Citation Report All Zeros

**Priority:** Medium  
**File(s) to Modify:** `citation_quality_scorer.py`

**Current Behavior:**
```
total_urls: 0
total_citation_markers: 0
total_citations: 0
quality_score: 0.0
quality_level: Very Poor
```

**Investigation Needed:**
1. Does the Bill-C15 PDF actually contain URLs or citation markers?
2. Is the PDF text extraction losing citation information?
3. Are the citation patterns too restrictive?

**Possible Causes:**
- Bill is a legislative document that may not use traditional academic citations
- PDF OCR may have corrupted URL patterns
- Citation patterns may not match legislative reference styles (e.g., "section 123" or "paragraph (a)")

**Potential Fix:**
Add legislative-style citation patterns:
- `r'section \d+'`
- `r'paragraph \([a-z]\)'`
- `r'subsection \d+\(\d+\)'`
- `r'Act, S\.C\. \d+'`

---

### 7. Memory Optimization (Future Task)

**Priority:** Low  
**File(s) to Modify:** `gui/sparrow_gui.py`, various analysis modules

**Current Behavior:**
- Python process uses 10GB+ memory after multiple analyses

**Desired Behavior:**
- Memory usage stays under 2GB
- Garbage collection after each analysis

**Deferred:** User requested to keep this in mind for later.

---

## Implementation Order

1. **#4 - Flowchart Version** (2 min) - Quick fix
2. **#1 - AI Percentage** (10 min) - Standardize formatting
3. **#2 - 120% Confidence** (15 min) - Find and fix calculation
4. **#3 - Flowchart Empty** (30 min) - Wire up data correctly
5. **#5 - OCR Garbled Text** (20 min) - Clean claim context
6. **#6 - Citation Patterns** (20 min) - Add legislative patterns

---

## Notes for AI Review

User is running the document set through AI for additional recommendations. Updates to this todo may be added based on that analysis.

---

## Files to Examine

- `/test_articles/Bill-C15/Bill-C15-04/Bill-C15-04_ai_disclosure_all.html` - Shows percentage inconsistency
- `/test_articles/Bill-C15/Bill-C15-04/Bill-C15-04_certificate.html` - Shows 120% confidence
- `/test_articles/Bill-C15/Bill-C15-04/Bill-C15-04_lineage_flowchart.html` - Empty flowchart
- `/test_articles/Bill-C15/Bill-C15-04/Bill-C15-04_data_lineage.json` - Garbled OCR text
- `/test_articles/Bill-C15/Bill-C15-04/Bill-C15-04_citation_report.txt` - All zeros

# Troubleshooting: Q&A Analysis & Narrative Generation Issues
**Session Duration**: December 9-12, 2025  
**Status**: IN PROGRESS - Core functionality fixed, answer quality issues remaining  
**Last Updated**: December 12, 2025, 04:47 UTC

---

## Executive Summary

Extended debugging session addressing multiple interconnected issues with the Document Q&A system and Q&A narrative auto-generation. Most infrastructure issues resolved; model-level answer quality issues persist.

**Issues Fixed**: 7/9  
**Issues Remaining**: 2 (answer quality, chunk routing accuracy)

---

## Issues Identified & Status

### ✅ RESOLVED ISSUES

#### 1. Q&A Narrative Not Auto-Generating (CODE PATH ISSUE)
**Discovered**: December 12, 04:28 UTC  
**Severity**: HIGH  
**Root Cause**: Q&A logic exists in TWO places but narrative generation was only added to GUI code path, not sparrow_grader_v8.py subprocess path.

**The Problem**:
- GUI (`sparrow_gui.py`) has Q&A code at line 877-945
- sparrow_grader_v8.py has DUPLICATE Q&A code at line 3009-3060
- Actual execution always uses sparrow_grader_v8.py (runs as subprocess)
- Narrative generation code I added to GUI never executes
- Test file created at `/test_articles/undrip_and_bill_c15_combined.txt` but new analyses using it

**Solution Applied**:
1. Added `generate_qa_narrative()` call to sparrow_grader_v8.py after line 3040
2. Added debug print statements to track execution
3. File now auto-generates as `{output_name}_qa_analysis.md` in qa/ directory

**Status**: ✅ FIXED - Narrative markdown files now auto-generate

---

#### 2. Undefined Variable: `ollama_url` in Narrative Expansion
**Discovered**: December 12, 03:15 UTC  
**Severity**: CRITICAL  
**Root Cause**: Variable used but never defined in function scope of `_expand_narrative_with_ollama()`

**Error Message**:
```
Section 1 error: name 'ollama_url' is not defined
```

**Location**: `narrative_integration.py`, line 689

**Solution Applied**:
Added variable definition at start of function (line 559):
```python
ollama_url = "http://localhost:11434"
```

**Status**: ✅ FIXED

---

#### 3. Undefined Variable: `model` in Narrative Expansion
**Discovered**: December 12, 03:20 UTC  
**Severity**: CRITICAL  
**Root Cause**: Wrong parameter name used - code referenced `model` but parameter is `ollama_model`

**Error Message**:
```
Section 2 error: name 'model' is not defined
```

**Location**: `narrative_integration.py`, line 690

**Solution Applied**:
Changed `"model": model,` to `"model": ollama_model,`

**Status**: ✅ FIXED

---

#### 4. Ollama Request Timeout During Narrative Expansion
**Discovered**: December 12, 02:45 UTC  
**Severity**: HIGH  
**Symptoms**: 
- "HTTPConnectionPool read timed out" errors
- Narrative expansion only produced 630 words (18% of 3500 word target)
- Multiple sections timing out with large models like qwen2.5:14b

**Root Cause**: Default timeout of 60-180 seconds insufficient for large models generating long responses

**Solution Applied**:
Changed timeout tuples in two locations:
1. `ollama_summary_generator.py` line 138: `timeout=60` → `timeout=(10, 300)` (connect, read)
2. `narrative_integration.py` line 695: `timeout=180` → `timeout=(10, 600)`

**Status**: ✅ FIXED - Narrative expansion now completes without timeouts

---

#### 5. Undefined Attribute: `args.title` in Q&A Narrative Generation
**Discovered**: December 12, 04:45 UTC  
**Severity**: CRITICAL  
**Error Message**:
```
'Namespace' object has no attribute 'title'
```

**Location**: `sparrow_grader_v8.py`, line 3048

**Root Cause**: Wrong attribute name - argparse converts `--document-title` to `args.document_title` (hyphens become underscores)

**Solution Applied**:
Changed `args.title` to `args.document_title`

**Status**: ✅ FIXED - Narrative generation now executes successfully

---

#### 6. Default Chunk Token Size Too Large
**Discovered**: December 12, 04:15 UTC  
**Severity**: MEDIUM  
**Symptoms**: 
- 67KB combined UNDRIP+Bill-C15 document created as single chunk
- Model couldn't analyze content properly when all articles in one chunk
- Keyword routing failed to locate specific articles

**Original Setting**: `default=100000` tokens

**Solution Applied**:
Reduced to `default=4000` tokens to force multiple chunks

**Current Setting**: `--max-chunk-tokens default=4000`

**Status**: ✅ FIXED - Now creates 5 chunks from 67KB document

---

#### 7. Chunking Strategy Lost Section Boundaries
**Discovered**: December 12, 04:30 UTC  
**Severity**: HIGH  
**Symptoms**: 
- Changed from "section" to "sliding" strategy to create smaller chunks
- Sliding windows don't respect article boundaries
- Lost ability to track "Article 28" in chunk_index.json sections
- All chunks showed empty sections array

**Solution Applied**:
Reverted to `default='section'` strategy to preserve legislative article boundaries

**Current Setting**: `--chunk-strategy default='section'`

**Status**: ✅ FIXED - Now properly identifies Article 28 in Chunk 2

---

### ⚠️ ISSUES REMAINING (OPEN)

#### 8. Q&A Answer Quality - Wrong Content & Hallucination
**Status**: IN PROGRESS  
**Severity**: HIGH  
**Discovered**: December 12, 04:47 UTC

**Symptoms**:
- Question: "What criticisms exist regarding UNDRIP Article 28's redress provisions..."
- Answer: Claims Article 28 is about "traditional medicines" and "dispute resolution"
- Actual Article 28: About land redress, restitution, compensation
- Model is **hallucinating** content not in the document

**Evidence**:
- Chunk 2 DOES contain Article 28 ✓
- All 5 responses labeled as "Chunk 1" ✗
- Different wrong answers for each chunk queried
- Model confidence: 100% (false confidence)

**Root Causes** (Hypotheses):
1. Keyword routing selected wrong chunks despite querying 5 total
2. Model (qwen2.5:14b) struggling with large articles in context
3. Chunk content not properly passed to model
4. Chunk labeling/tracking broken in Q&A system

**Potential Solutions** (To Test):
1. Switch routing from "keyword" to "comprehensive" (query all chunks)
2. Simplify question to focus on specific content
3. Extract Article 28 only into separate minimal document
4. Try different model (qwen2.5:7b, mistral:8x7b)
5. Reduce chunk size further (2000 tokens instead of 4000)

**Status**: BLOCKED - Awaiting comprehensive routing implementation

---

#### 9. Chunk Reference Tracking Inconsistency
**Status**: IN PROGRESS  
**Severity**: MEDIUM  
**Discovered**: December 12, 04:45 UTC

**Symptoms**:
- JSON shows 5 chunks queried: `"chunks_queried": 5`
- But all answers reference "Chunk 1, Pages unknown"
- Chunk index shows Article 28 in Chunk 2, not Chunk 1
- Source references not reflecting actual chunk numbers

**Evidence**:
```json
"chunks_queried": 5,  // 5 chunks analyzed
"sources": [{"chunk": 1}, {"chunk": 1}, {...}]  // All labeled as Chunk 1
```

**Root Cause** (Hypothesis):
Chunk numbering/labeling logic broken in QueryRouter or answer synthesis

**Impact**: Users can't trace which content came from which chunk

**Status**: BLOCKED - Awaiting comprehensive routing investigation

---

## Timeline of Changes Made

| Date/Time | File | Change | Impact |
|-----------|------|--------|--------|
| Dec 12, 02:45 | ollama_summary_generator.py | timeout: 60→(10,300) | Fixed timeouts |
| Dec 12, 02:45 | narrative_integration.py | timeout: 180→(10,600) | Fixed timeouts |
| Dec 12, 03:15 | narrative_integration.py | Added ollama_url definition | Fixed undefined var |
| Dec 12, 03:20 | narrative_integration.py | Changed model→ollama_model | Fixed undefined var |
| Dec 12, 04:15 | sparrow_grader_v8.py | max_chunk_tokens: 100000→4000 | Created multiple chunks |
| Dec 12, 04:30 | sparrow_grader_v8.py | chunk_strategy: sliding→section | Preserved boundaries |
| Dec 12, 04:40 | sparrow_grader_v8.py | Added narrative generation code | Auto-generates .md |
| Dec 12, 04:45 | sparrow_grader_v8.py | args.title→args.document_title | Fixed attribute error |
| Dec 12, 04:47 | gui/sparrow_gui.py | Added debug output | Improved logging |

---

## System Configuration

**Hardware**:
- RAM: 32 GB
- GPU: 8 GB (VRAM)
- Estimated suitable models: qwen2.5:7b, qwen2.5:14b

**Software**:
- Ollama: localhost:11434
- Framework: Sparrow SPOT Scale v8.6.1+
- Python: 3.9+

**Documents Tested**:
- `/Investigations/undrip_and_bill_c15_combined.txt` (67 KB, ~17,500 tokens)
  - Part 1: UNDRIP Declaration (32 pages)
  - Part 2: Bill C-15 (21 pages)

---

## Test Cases & Results

### Test 1: Narrative Expansion with Timeout Issues
**Model**: qwen2.5:14b  
**Result**: FAILED - Multiple timeouts (FIXED ✅)

### Test 2: Q&A with 100K token chunk
**Chunks**: 1 (all content in single chunk)  
**Result**: Wrong answer - "Article 28 not found" (FIXED ✅)

### Test 3: Q&A with sliding window chunks
**Chunks**: 4 (but lost section boundaries)  
**Result**: Wrong answer - "Article 28 in Chunk 1" but Chunk 1 has Articles 1-9 (FIXED ✅)

### Test 4: Q&A with section strategy, 4K tokens
**Chunks**: 5 (properly bounded at articles)  
**Result**: Narrative generated ✓, but answer quality poor - hallucinations (OPEN ⚠️)

---

## Next Steps (PLANNED)

1. ✅ **COMPLETED**: Implement comprehensive routing strategy
2. **PENDING**: Test with comprehensive routing ("query all chunks" mode)
3. **PENDING**: Simplify test question and rerun
4. **PENDING**: Compare answer quality across models
5. **PENDING**: Verify chunk reference tracking in QueryRouter
6. **PENDING**: Consider semantic chunking vs. section chunking

---

## Code Files Modified

1. **`narrative_integration.py`** (3 changes)
   - Line 559: Added `ollama_url = "http://localhost:11434"`
   - Line 690: Changed `model` to `ollama_model`
   - Line 695: Changed timeout tuple

2. **`ollama_summary_generator.py`** (1 change)
   - Line 138: Changed timeout tuple

3. **`sparrow_grader_v8.py`** (4 changes)
   - Line 2197: Changed default chunk_strategy
   - Line 2200: Changed default max_chunk_tokens
   - Line 3040+: Added narrative generation code
   - Line 3048: Fixed args.document_title

4. **`gui/sparrow_gui.py`** (1 change)
   - Line 923+: Added debug output

---

## Known Limitations

1. **Model Context Window**: Even large models struggle with 17KB of legislative text containing 46 articles
2. **Keyword Routing**: May not reliably select chunks containing specific articles
3. **Hardware Constraints**: 8GB GPU limits model choices to 7B-14B range
4. **Answer Hallucination**: Models generating content not in source material

---

## References & Artifacts

**Test Analysis Directory**: 
- `/Investigations/Bill-C-15-UNDRIP/Bill-C15-11/`
- Q&A results: `qa/analysis_qa_enhanced.json`
- Generated narrative: `qa/analysis_qa_analysis.md`
- Chunks: `qa/chunks/chunk_index.json`, `chunk_metadata.json`
- Logs: `logs/analysis_pipeline.log`

**Combined Document**:
- `/Investigations/undrip_and_bill_c15_combined.txt` (67 KB)

---

## Status Summary

**Infrastructure**: ✅ MOSTLY FIXED
- Timeouts fixed
- Narrative auto-generation working
- Chunking properly configured
- Debug logging in place

**Answer Quality**: ⚠️ NEEDS WORK
- Hallucinations present
- Chunk routing unreliable
- Answer accuracy low (~0%)

**Recommendation**: Implement comprehensive routing before next user-facing iteration to ensure all relevant content is available to model.


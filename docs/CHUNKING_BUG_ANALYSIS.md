# Critical Bug: Document Q&A Chunking Returns Mock Answers

## Problem Summary

When users enable **"Use Smart Chunking"** for Document Q&A in the GUI, the system:
1. ✅ **Correctly chunks the document** into multiple pieces
2. ✅ **Correctly saves the chunks** to disk
3. ✅ **Correctly routes the query** to relevant chunks
4. ❌ **Returns MOCK/PLACEHOLDER answers** instead of real Ollama responses

This means Bill C-15 Document Q&A with chunking enabled likely returned generated/fictional answers instead of actual analysis of the document.

## Root Cause

**File:** `gui/sparrow_gui.py`  
**Line:** 784

```python
answer = qa_engine.query(
    question=document_qa_question.strip(),
    model="mock",  # ← HARDCODED TO "mock"
    routing_strategy=qa_routing_strategy,
    synthesis_strategy="concatenate",
    relevance_threshold=0.3
)
```

The code is hardcoded to use `model="mock"`, which triggers this behavior in `enhanced_document_qa.py` (line 476):

```python
if model == "mock" or not ollama_client:
    answer = self._mock_query(question, chunk_ref, chunk_text)  # ← Returns fake data
```

## Why This Happened

The comment on line 784 explains the intent:
```python
model="mock",  # Use mock for now (GUI uses document_qa for Ollama)
```

This appears to be:
- A placeholder during development
- Testing code that was never replaced with production code
- **The enhanced_document_qa.py module was never properly integrated with actual Ollama calls**

## Impact

### For Bill C-15 Analysis:
- ❌ Chunking path: Returns **mock/generated answers** (useless)
- ✅ Non-chunking path: Returns **real Ollama answers** (works correctly)
- **Result:** User got fake answers when checkin "Use Smart Chunking" checkbox

### For Large Documents:
The chunking system correctly:
1. Breaks the document into manageable chunks
2. Routes queries to relevant sections
3. But then asks a **mock model** instead of the real Ollama model

This defeats the entire purpose of chunking (working with large documents that exceed token limits).

## Two Code Paths in GUI

### Path 1: With Chunking (lines 750-810) ❌ BROKEN
```
Enable Chunking Checkbox? Yes
          ↓
Use EnhancedDocumentQA class
          ↓
Query with model="mock"  ← Mock answers, not real
          ↓
Result: Chunk metadata is perfect, but answers are fake
```

### Path 2: Without Chunking (lines 815-830) ✅ WORKS
```
Enable Chunking Checkbox? No (or missing imports)
          ↓
Use generate_document_qa() function
          ↓
Query with actual Ollama model parameter
          ↓
Result: Full document sent to Ollama, real answers
```

## Token Metrics Implication

Your earlier question: **"Will token metrics reflect chunking?"**

**Answer:** They can, but currently don't because:

1. **In chunking path:** Token metrics show chunk sizes correctly, but answers are mock
2. **In non-chunking path:** Token metrics would show whole document size, but no visibility into model's actual token consumption

Neither path currently tracks what the model actually received/processed.

## Solution Options

### Option A: Fix Chunking Path (Recommended)
Replace `model="mock"` with real Ollama integration:

```python
# Import Ollama client
import requests
from datetime import datetime

# Create Ollama client wrapper
class OllamaClient:
    def __init__(self, url="http://localhost:11434"):
        self.url = url
    
    def query(self, model, prompt, temperature=0.3):
        response = requests.post(
            f"{self.url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "num_predict": 2000
            },
            timeout=180
        )
        return response.json().get("response", "")

# In GUI line 784, replace:
ollama_client = OllamaClient()
answer = qa_engine.query(
    question=document_qa_question.strip(),
    model=ollama_model,  # Use the selected Ollama model
    routing_strategy=qa_routing_strategy,
    synthesis_strategy="concatenate",
    relevance_threshold=0.3,
    ollama_client=ollama_client  # Pass real client
)
```

### Option B: Use Non-Chunking Path for Now
Until chunking is fixed, disable the "Use Smart Chunking" option and always use the standard `generate_document_qa()` path which calls real Ollama.

### Option C: Hybrid Approach
- Keep chunking for **document analysis** (identifying sections, building index)
- But use full document for **Q&A** (avoid mock answers)
- Document gets chunked for analysis but sent whole to Q&A model

## Evidence

### Chunking Code Exists (Works)
- `semantic_chunker.py` - Correctly chunks documents
- `token_calculator.py` - Correctly estimates tokens per chunk
- `enhanced_document_qa.py` - Correctly routes queries to chunks
- GUI lines 760-773: Chunks are created, saved, indexed ✅

### Ollama Integration Exists (Works)
- `document_qa.py` - Successfully calls Ollama API
- GUI uses `ollama_model` variable successfully elsewhere
- `generate_document_qa()` at line 822 calls real Ollama ✅

### But They're Disconnected
The chunking infrastructure (enhanced_document_qa.py) was **never connected to real Ollama calls**. It was left in "mock" mode.

## Recommendation

**Immediate:** If Bill C-15 used "Use Smart Chunking", those Document Q&A results are unreliable. Re-run without chunking to get real answers.

**Short-term:** Fix GUI line 784 to pass real `ollama_client` instead of hardcoding `model="mock"`

**Long-term:** As part of token metrics implementation, add full token tracking across both chunking and non-chunking paths so users can see:
- Document size in tokens
- Tokens consumed per chunk
- Total tokens sent to model
- Model capacity remaining

## Files Involved

| File | Issue | Status |
|------|-------|--------|
| `gui/sparrow_gui.py` line 784 | Hardcoded `model="mock"` | ❌ Broken |
| `enhanced_document_qa.py` line 476 | Falls back to mock if no real client | Works as designed, but GUI doesn't pass one |
| `document_qa.py` | Has real Ollama integration | ✅ Works |
| `semantic_chunker.py` | Chunks correctly | ✅ Works |

## Next Steps

1. ✅ You now understand why Bill C-15 Document Q&A might have looked weird
2. Decide: Fix chunking path OR disable "Use Smart Chunking" option
3. Re-test Document Q&A on Bill C-15 with the chosen approach
4. Implement token metrics system (design already complete) to prevent future confusion

---

**Created:** Analysis of chunking vs mock answer bug  
**Status:** Bug identified, solution options provided  
**Severity:** High - Document Q&A with chunking enabled returns unreliable answers

# Quick Reference: Exact Code Changes

## Change 1: Backend Mock Mode → Real Ollama
**File:** `sparrow_grader_v8.py`
**Lines:** 2895-2944
**Status:** ✅ COMPLETED

### Before:
```python
answer = qa_engine.query(
    question=args.document_qa,
    model="mock",  # Use mock for now (integrate with Ollama in future)
    routing_strategy=args.qa_routing,
    synthesis_strategy="concatenate",
    relevance_threshold=0.3
)
```

### After:
```python
# Create Ollama client for chunked Q&A (v8.6)
import requests as req_module
import time

class OllamaChunkClient:
    """Simple Ollama client for enhanced Q&A."""
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.queries_made = 0
    
    def generate(self, model: str, prompt: str, options: dict = None):
        """Query Ollama API."""
        opts = options or {}
        self.queries_made += 1
        try:
            query_start = time.time()
            response = req_module.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": opts.get('temperature', 0.3),
                    "num_predict": opts.get('num_predict', 500),
                },
                timeout=180
            )
            response.raise_for_status()
            query_time = time.time() - query_start
            print(f"      🔗 Ollama query #{self.queries_made}: {query_time:.1f}s")
            return response.json()
        except Exception as e:
            print(f"      ⚠️  Ollama query failed: {str(e)}")
            return {"response": f"Error: {str(e)}"}

ollama_client = OllamaChunkClient()

answer = qa_engine.query(
    question=args.document_qa,
    model=args.ollama_model,
    routing_strategy=args.qa_routing,
    synthesis_strategy="concatenate",
    relevance_threshold=0.3,
    ollama_client=ollama_client
)
```

**Why:** Backend was using mock queries instead of real Ollama. Now uses args.ollama_model with real HTTP requests.

---

## Change 2: GUI Pass --enable-chunking Flag
**File:** `gui/sparrow_gui.py`
**Lines:** 1130-1136
**Status:** ✅ COMPLETED

### Before:
```python
if enable_document_qa and document_qa_question and document_qa_question.strip():
    cmd.extend(["--document-qa", document_qa_question.strip()])
if enhanced_provenance:
```

### After:
```python
if enable_document_qa and document_qa_question and document_qa_question.strip():
    cmd.extend(["--document-qa", document_qa_question.strip()])
    if enable_chunking:
        cmd.append("--enable-chunking")
        if qa_routing_strategy and qa_routing_strategy != "keyword":
            cmd.extend(["--qa-routing", qa_routing_strategy])
if enhanced_provenance:
```

**Why:** GUI wasn't telling backend to enable chunking. Checkbox was checked but flag wasn't passed.

---

## Change 3: pdfplumber File Type Check (Part 1)
**File:** `sparrow_grader_v8.py`
**Lines:** 548-556
**Status:** ✅ COMPLETED

### Before:
```python
def _extract_with_pdfplumber(self, pdf_path):
    """Extract text using pdfplumber with table detection."""
    import pdfplumber
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
```

### After:
```python
def _extract_with_pdfplumber(self, pdf_path):
    """Extract text using pdfplumber with table detection."""
    import pdfplumber
    
    # v8.6: Check if file is actually a PDF before attempting extraction
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError(f"File does not appear to be a PDF: {pdf_path}")
    
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
```

**Why:** Text files were triggering pdfplumber warnings. Now checks extension first.

---

## Change 4: pdfplumber File Type Check (Part 2)
**File:** `sparrow_grader_v8.py`
**Lines:** 576-583
**Status:** ✅ COMPLETED

### Before:
```python
def _extract_with_pypdf(self, pdf_path):
    """Fallback to pypdf for text extraction."""
    from pypdf import PdfReader
    pdf_reader = PdfReader(pdf_path)
```

### After:
```python
def _extract_with_pypdf(self, pdf_path):
    """Fallback to pypdf for text extraction."""
    from pypdf import PdfReader
    
    # v8.6: Check if file is actually a PDF before attempting extraction
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError(f"File does not appear to be a PDF: {pdf_path}")
    
    pdf_reader = PdfReader(pdf_path)
```

**Why:** Same as part 1, applies to fallback pypdf method.

---

## Summary Statistics
- **Files Modified:** 2
- **Functions Modified:** 4
- **Lines Added:** ~50
- **Complexity:** Low (mostly duplicating existing GUI pattern)
- **Breaking Changes:** None
- **Backward Compatibility:** 100%

## Testing Command
```bash
cd /home/gene/Sparrow-SPOT-Policy
python sparrow_grader_v8.py Investigations/Bill-C-15/Bill-C15-00/documents/bill-c-15.txt \
    --variant policy \
    --document-qa "What are the key provisions?" \
    --enable-chunking \
    --qa-routing keyword \
    --output test-chunking-v8.6.2
```

## Expected Output
✅ Chunking messages in log
✅ Ollama query logs with timing
✅ `qa/test-chunking-v8.6.2_qa_enhanced.json` with metrics
✅ `qa/chunks/chunk_*.txt` files
✅ No pdfplumber errors for text files

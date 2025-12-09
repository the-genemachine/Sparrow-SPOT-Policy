# Quick Testing Guide: Document Q&A Chunking Fix

## Prerequisites

### 1. Make sure Ollama is Running
```bash
ollama serve
```

Output should show:
```
Listening on 127.0.0.1:11434 (HTTP)
```

### 2. Verify Bill C-15 is Available
Check you have the document in: `/home/gene/Sparrow-SPOT-Policy/test_articles/Bill-C15/`

## Test Scenario 1: Chunking Enabled (The Fix)

### Run the GUI
```bash
cd /home/gene/Sparrow-SPOT-Policy/gui
python sparrow_gui.py
```

Opens at: http://localhost:7860

### Upload & Test
1. **Upload:** Select Bill-C15 document (English)
2. **Enable Features:**
   - ✅ Check "Enable Document Q&A"
   - ✅ Check "Use Smart Chunking" 
   - ✅ Check "Enable Narratives" (to see full output)
3. **Ask a Question:** 
   - Try: "What are the main objectives of this bill?"
   - Or: "What new powers does this grant?"
4. **Select Ollama Model:** Keep default (usually `llama3.2` or `mistral`)
5. **Analyze**

### Expected Output (✅ Real Answers Now!)
- **Console shows:** "Ollama query succeeded" or similar positive message
- **JSON output** (in `*_qa.json`):
  ```json
  {
    "question": "What are the main objectives?",
    "answer": "The bill establishes...",  // Real answer from Ollama
    "sources": [
      {"chunk": 1, "pages": "1-5", "sections": [...]},
      {"chunk": 2, "pages": "6-10", "sections": [...]}
    ],
    "metadata": {
      "chunks_queried": 2,
      "confidence": 0.85,
      "routing_strategy": "keyword"
    }
  }
  ```
- **Confidence score:** Shows 0-100% (indicates model's confidence)
- **Chunks listed:** Shows which document sections were used

### ❌ If Something Goes Wrong
1. **Error: "Cannot connect to Ollama"**
   - Run `ollama serve` in separate terminal
   - Check it's listening on 11434

2. **Error: "Connection refused"**
   - Kill any existing Ollama processes: `pkill ollama`
   - Restart: `ollama serve`

3. **Mock answers still appearing**
   - Hard refresh browser (Ctrl+Shift+R)
   - Stop GUI (Ctrl+C) and restart: `python sparrow_gui.py`

## Test Scenario 2: Chunking Disabled (Should Still Work)

### Repeat Test But:
1. **Uncheck** "Use Smart Chunking"
2. Everything else same as above

### Expected Output (Different Path, Still Real)
- Uses standard `generate_document_qa()` (non-chunking path)
- Answer uses **whole document** instead of chunks
- No chunk references in JSON output
- May be slower for very large documents (Bill C-15 might struggle)

## Comparison: Before vs After

### Before (Broken)
```
Input: Bill C-15 (1.15M chars, 286K tokens)
With Smart Chunking: ❌ Mock answer
  "answer": "Based on the document... [generic placeholder text]"

Without Smart Chunking: ✅ Real answer  
  "answer": "The Act grants the Minister broad powers to..."
```

### After (Fixed)
```
Input: Bill C-15 (1.15M chars, 286K tokens)
With Smart Chunking: ✅ Real answer
  "answer": "The Act grants the Minister broad powers to..."
  "chunks_queried": 4
  "confidence": 0.82

Without Smart Chunking: ✅ Real answer
  "answer": "The Act grants the Minister broad powers to..."
```

## Detailed Test Checklist

- [ ] Ollama running (`ollama serve`)
- [ ] GUI started (`python sparrow_gui.py`)
- [ ] Bill C-15 uploaded
- [ ] Document Q&A enabled
- [ ] Smart Chunking **enabled**
- [ ] Ollama model selected
- [ ] Question entered (clear, specific question)
- [ ] Analysis completed
- [ ] No errors in console
- [ ] Check output JSON file exists
- [ ] Answer is NOT generic/mock text
- [ ] Answer references specific sections
- [ ] Confidence score shown (not 0%)
- [ ] Chunks count > 0
- [ ] Source attribution includes chunk numbers

## Performance Expectations

| Metric | Value |
|--------|-------|
| Chunking time (Bill C-15) | 2-5 seconds |
| Per-chunk query time | 5-30 seconds each |
| Total time (4 chunks) | ~20-120 seconds |
| Ollama GPU load | Medium (with chunking) |

## Files Modified

- `gui/sparrow_gui.py` - Line 784-820 (OllamaChunkClient added)

## Rollback (If Needed)

If the fix causes issues, revert to previous version:
```bash
git checkout HEAD -- gui/sparrow_gui.py
```

This reverts to using `model="mock"` (the broken version).

---

**Created:** December 8, 2025  
**Status:** Ready for testing  
**Next:** After successful test, move to token metrics implementation

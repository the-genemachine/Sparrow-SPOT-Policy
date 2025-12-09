# Chunking Metrics and Logging Guide

## What You'll Now See

When you run Document Q&A with "Use Smart Chunking" enabled, the system now generates two files with comprehensive metrics:

### File 1: `*_qa.json` (Q&A Results)
Contains the question, answer, and execution metadata.

**Example structure:**
```json
{
  "question": "What are the main objectives of this bill?",
  "answer": "The Act establishes...",
  "sources": [
    {
      "chunk": 2,
      "pages": "5-10",
      "sections": ["Definitions", "Powers and Duties"]
    },
    {
      "chunk": 4,
      "pages": "15-18",
      "sections": ["Implementation"]
    }
  ],
  "metadata": {
    "chunks_queried": 2,
    "total_chunks_available": 4,
    "confidence": 0.75,
    "routing_strategy": "keyword",
    "model": "mistral",
    "ollama_queries_made": 2,
    "qa_processing_time_seconds": 24.5
  }
}
```

### File 2: `*_chunking_metrics.json` (Detailed Metrics)
Contains complete chunking analysis, document statistics, and proof of chunking.

**Example structure:**
```json
{
  "document_size": {
    "characters": 1150000,
    "tokens": 286000
  },
  "chunking": {
    "strategy": "section",
    "max_tokens_per_chunk": 100000,
    "overlap_tokens": 200,
    "total_chunks": 4
  },
  "chunks": [
    {
      "chunk_id": 0,
      "chunk_number": 1,
      "pages": "1-4",
      "sections": ["Title", "Preamble"],
      "tokens": 85000,
      "characters": 425000,
      "keywords": ["bill", "act", "parliament", "regulations", "minister"]
    },
    {
      "chunk_id": 1,
      "chunk_number": 2,
      "pages": "5-10",
      "sections": ["Definitions", "Powers and Duties"],
      "tokens": 92000,
      "characters": 460000,
      "keywords": ["definitions", "powers", "minister", "authority", "regulations"]
    },
    {
      "chunk_id": 2,
      "chunk_number": 3,
      "pages": "11-14",
      "sections": ["Implementation", "Timelines"],
      "tokens": 88000,
      "characters": 440000,
      "keywords": ["implementation", "timeline", "month", "date", "effective"]
    },
    {
      "chunk_id": 3,
      "chunk_number": 4,
      "pages": "15-18",
      "sections": ["Review", "Amendments"],
      "tokens": 89000,
      "characters": 445000,
      "keywords": ["review", "amendments", "parliament", "legislation", "changes"]
    }
  ],
  "query": {
    "question": "What are the main objectives of this bill?",
    "routing_strategy": "keyword",
    "model": "mistral",
    "ollama_queries_executed": 2,
    "total_time_seconds": 45.3
  },
  "chunks_used_in_answer": [
    {
      "chunk_number": 2,
      "pages": "5-10",
      "sections": ["Definitions", "Powers and Duties"]
    },
    {
      "chunk_number": 4,
      "pages": "15-18",
      "sections": ["Review", "Amendments"]
    }
  ]
}
```

## Console Output

You'll see detailed logging in the console:

```
   📊 Analyzing document size...
   📊 Document stats: 1,150,000 chars, 286,000 tokens
   ✂️  Creating intelligent chunks...
   ✂️  Created 4 chunks
   🔍 Routing strategy: keyword
      🔗 Ollama query #1: 12.3s
      🔗 Ollama query #2: 11.8s
   ✓ Enhanced Q&A: .../path_to_qa.json
   ✓ Chunking metrics: .../path_to_chunking_metrics.json
   ✓ Confidence: 75%, Chunks queried: 2/4
   ✓ Ollama API calls: 2
   ✓ Total processing time: 45.3s
```

## How to Interpret the Metrics

### Proof of Chunking
✅ **Chunking definitely happened if:**
1. `"total_chunks"` > 1 (in chunking_metrics.json)
2. `"chunks"` array contains multiple chunk objects with token/character counts
3. Each chunk has `"pages"` and `"sections"` assigned
4. `"chunks_queried"` < `"total_chunks_available"` (smart routing working)

### Proof of Real Ollama Queries
✅ **Real Ollama queries definitely happened if:**
1. `"ollama_queries_made"` > 0 in metadata
2. Console shows "🔗 Ollama query #X: Ys" timing entries
3. Answer is specific to document content (not generic)
4. `"qa_processing_time_seconds"` is significant (10+ seconds typically)

### Chunk Routing Efficiency
- **Query Time:** Shows how long Ollama took for each query
- **Chunks Queried vs Available:** If queried < available, smart routing filtered irrelevant chunks
- **Confidence Score:** Higher confidence = more relevant answer
- **Routing Strategy:** Shows which method was used (keyword/semantic/comprehensive)

## Example Interpretation

**For Bill C-15 with 4 chunks:**

```
Document: 1.15M chars, 286K tokens
Chunked into: 4 chunks (~71-73K tokens each)
Query: "What are the main objectives?"
Smart routing selected: 2 chunks (50% of document)
Ollama queries made: 2 (one per relevant chunk)
Total time: 45 seconds
Confidence: 75%
```

**What this proves:**
- ✅ Document WAS successfully chunked
- ✅ Smart routing identified 2 relevant chunks
- ✅ Each chunk was sent to Ollama (2 queries)
- ✅ Answers were synthesized from both chunks
- ✅ Not using mocks - real Ollama queries

## File Locations

Both files appear in the same directory as your analysis output:

```
test_articles/Bill-C15/
├── Bill-C15_analysis.json
├── Bill-C15_certificate.html
├── chunks/                           # Chunked document
│   ├── chunk_001.txt
│   ├── chunk_002.txt
│   ├── chunk_003.txt
│   ├── chunk_004.txt
│   ├── chunk_index.json              # Metadata about chunks
│   └── chunks/                       # Subfolder
│       ├── chunk_001.txt
│       └── ...
├── Bill-C15_qa.json                  # ✨ NEW: Q&A results with metadata
└── Bill-C15_chunking_metrics.json    # ✨ NEW: Detailed chunking proof
```

## Quick Verification Checklist

After running analysis with Smart Chunking enabled:

- [ ] Find `*_chunking_metrics.json` in output directory
- [ ] Open it and check `"total_chunks"` > 1
- [ ] Verify each chunk has tokens and character counts
- [ ] Check `"ollama_queries_executed"` > 0
- [ ] Compare chunks_queried vs total_chunks_available
- [ ] Look at answer - is it specific to document?
- [ ] Check console output for "🔗 Ollama query" timing entries
- [ ] Verify processing time is significant (20+ seconds)

## Troubleshooting

### If metrics show `"total_chunks": 1`
- Document might be too small to need chunking
- Try a larger document (Bill C-15 should chunk into 4)

### If `"ollama_queries_made": 0`
- Ollama might not be running
- Check console for "⚠️ Ollama query failed" messages
- Verify Ollama is listening on 11434

### If answer looks generic
- Might have used wrong routing strategy
- Try different "qa_routing_strategy" option
- Check if "confidence" is very low (< 0.3)

---

**Created:** December 8, 2025  
**Purpose:** Document chunking metrics and logging system  
**Files:** gui/sparrow_gui.py (enhanced logging added)

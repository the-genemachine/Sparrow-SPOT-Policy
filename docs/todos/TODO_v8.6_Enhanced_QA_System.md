# TODO: Sparrow SPOT v8.6 - Enhanced Document Q&A System

**Priority:** HIGH  
**Target Version:** 8.6.0  
**Created:** 2025-12-07  
**Status:** PLANNING

---

## Executive Summary

The current Q&A system (`document_qa.py`, `narrative_qa.py`) has limitations when handling large documents that exceed LLM context windows. Bill C-15 (632 pages, 1.15M characters) and similar legislative documents cannot fit entirely into typical Ollama model contexts (4K-128K tokens).

This TODO outlines enhancements to enable intelligent document chunking, model selection based on document size, and comprehensive Q&A coverage across the full document scope.

---

## Problem Statement

### Current Limitations:
1. **Context Window Overflow** - Large documents (>100 pages) exceed most model contexts
2. **No Token Calculation** - System doesn't estimate tokens before model selection
3. **No Chunking Strategy** - Can't intelligently split documents for Q&A
4. **No Model Recommendation** - Users don't know which Ollama model fits their document
5. **Poor Coverage** - Questions may only access beginning of document if truncated
6. **No Semantic Retrieval** - No ability to find relevant sections for specific queries

### Impact:
- Bill C-15 (1.15M chars ≈ 290K tokens) exceeds even large models (llama3.1:70b = 128K context)
- Users get incomplete answers from partial document access
- Critical information in later sections gets missed
- No guidance on optimal model selection

---

## Phase 1: Token Calculator & Model Advisor

### 1.1 Token Counter Module
**Priority:** P0 - Critical Foundation  
**Estimated Effort:** 1 day  
**File:** `token_calculator.py`

#### Requirements:

**A. Character-to-Token Estimation**
```python
def estimate_tokens(text: str, method: str = "precise") -> dict:
    """
    Estimate token count using multiple methods.
    
    Methods:
        - "quick": chars / 4 (rough estimate, ~75% accurate)
        - "tiktoken": OpenAI tiktoken library (GPT-like tokenization)
        - "precise": Actual Ollama model tokenization (API call)
    
    Returns:
        {
            "character_count": int,
            "estimated_tokens": int,
            "method": str,
            "accuracy": "rough|good|precise"
        }
    """
```

**B. Model Context Database**
```python
OLLAMA_MODEL_CONTEXTS = {
    # Small models (good for testing)
    "llama3.2:1b": 128000,
    "llama3.2:3b": 128000,
    "phi3:mini": 4096,
    "phi3:medium": 128000,
    
    # Medium models (good balance)
    "llama3.1:8b": 128000,
    "mistral:7b": 8192,
    "gemma2:9b": 8192,
    
    # Large models (maximum context)
    "llama3.1:70b": 128000,
    "qwen2.5:72b": 131072,
    "mixtral:8x7b": 32768,
    
    # Specialized models
    "codellama:13b": 16384,
    "deepseek-coder:33b": 16384,
}
```

**C. Model Recommendation Engine**
```python
def recommend_model(document_tokens: int, available_models: list) -> dict:
    """
    Recommend best model(s) for document size.
    
    Returns:
        {
            "strategy": "single|chunked|summarize-first",
            "recommended_models": [
                {
                    "model": "llama3.1:70b",
                    "context_size": 128000,
                    "fit": "full|partial",
                    "coverage": "100%|85%|...",
                    "chunks_needed": 1,
                }
            ],
            "warning": "Document exceeds all available contexts" or None
        }
    """
```

**D. CLI Tool**
```bash
python token_calculator.py bill_c15_english_only.txt
# Output:
# Document Analysis:
#   - Characters: 1,152,779
#   - Estimated Tokens: 288,195 (tiktoken method)
#   - Pages: ~632
# 
# Model Recommendations:
#   ✅ llama3.1:70b (128K context) - Requires 3 chunks (33% per chunk)
#   ✅ qwen2.5:72b (131K context) - Requires 3 chunks (33% per chunk)
#   ⚠️  llama3.1:8b (128K context) - Requires 3 chunks (33% per chunk)
#   ❌ mistral:7b (8K context) - Requires 36 chunks (NOT RECOMMENDED)
# 
# Recommended Strategy: CHUNKED Q&A with llama3.1:70b (3 chunks)
```

#### Implementation Notes:
- Use `tiktoken` library for accurate GPT-style token counting
- Add Ollama API call option for precise model-specific counts
- Cache token counts to avoid recalculation
- Include in GUI as "Document Size Analysis" tool

---

## Phase 2: Intelligent Document Chunking

### 2.1 Semantic Chunker Module
**Priority:** P0 - Critical for Large Docs  
**Estimated Effort:** 2-3 days  
**File:** `semantic_chunker.py`

#### Requirements:

**A. Smart Chunking Strategies**

1. **Section-Based Chunking** (Legislative Documents)
   - Split on section headers (## Part 1, ## Division 2, etc.)
   - Preserve section context boundaries
   - Maintain hierarchical structure

2. **Sliding Window Chunking** (General Documents)
   - Overlap between chunks (10-20%)
   - Ensures no information lost at boundaries
   - Configurable chunk size based on model context

3. **Semantic Similarity Chunking** (Advanced)
   - Group related paragraphs using embeddings
   - Maintain topical coherence within chunks
   - Better for narrative documents

**B. Core Functions**

```python
def chunk_document(
    text: str,
    max_tokens: int,
    strategy: str = "section",
    overlap_tokens: int = 200
) -> list[dict]:
    """
    Split document into manageable chunks.
    
    Args:
        text: Full document text
        max_tokens: Maximum tokens per chunk (model context - buffer)
        strategy: "section|sliding|semantic"
        overlap_tokens: Overlap between chunks (prevents info loss)
    
    Returns:
        [
            {
                "chunk_id": 1,
                "text": "chunk content...",
                "tokens": 45000,
                "metadata": {
                    "start_char": 0,
                    "end_char": 180000,
                    "sections": ["Part 1", "Division 1"],
                    "page_range": "1-120"
                }
            },
            ...
        ]
    """
```

**C. Chunk Index Generator**
```python
def create_chunk_index(chunks: list[dict]) -> dict:
    """
    Create searchable index for chunks.
    
    Returns:
        {
            "total_chunks": 3,
            "total_tokens": 288195,
            "avg_tokens_per_chunk": 96065,
            "chunks": [
                {
                    "id": 1,
                    "summary": "Parts 1-2: Budget Overview and Tax Measures",
                    "key_sections": ["Part 1", "Division 1-5"],
                    "page_range": "1-210",
                    "keywords": ["taxation", "GST", "carbon tax"]
                },
                ...
            ]
        }
    """
```

#### Implementation Notes:
- For legislative documents, detect section patterns (Part, Division, Section)
- Generate mini-summaries for each chunk (100 words max)
- Save chunk metadata to JSON for Q&A reference
- Add visual chunk map in GUI

---

## Phase 3: Enhanced Q&A System

### 3.1 Multi-Chunk Q&A Engine
**Priority:** P0 - Critical  
**Estimated Effort:** 3-4 days  
**File:** `enhanced_document_qa.py`

#### Requirements:

**A. Query Routing**

```python
def route_query(
    question: str,
    chunks: list[dict],
    method: str = "all"
) -> list[int]:
    """
    Determine which chunks to query.
    
    Methods:
        - "all": Query all chunks (comprehensive, slower)
        - "keyword": Match keywords to chunk summaries (fast)
        - "semantic": Use embeddings to find relevant chunks (accurate)
    
    Returns:
        [chunk_id_1, chunk_id_3, chunk_id_5]  # Relevant chunks
    """
```

**B. Multi-Chunk Query Strategies**

1. **Strategy: Query All + Synthesize** (Comprehensive)
   - Query each chunk independently
   - Collect all answers
   - Use LLM to synthesize final answer
   - Best for: "How many times is X mentioned?"

2. **Strategy: Query Relevant Only** (Efficient)
   - Use semantic search to find top 2-3 relevant chunks
   - Query only those chunks
   - Best for: "What does Section 12 say about...?"

3. **Strategy: Map-Reduce** (Scalable)
   - Query all chunks in parallel
   - Extract key points from each
   - Reduce to final comprehensive answer
   - Best for: "Summarize all discretionary powers"

**C. Answer Synthesis**

```python
def synthesize_answers(
    question: str,
    chunk_answers: list[dict],
    model: str = "llama3.1:8b"
) -> dict:
    """
    Combine answers from multiple chunks.
    
    Returns:
        {
            "question": str,
            "answer": str,  # Synthesized final answer
            "sources": [
                {
                    "chunk_id": 1,
                    "partial_answer": "...",
                    "confidence": 0.85,
                    "sections": ["Part 2, Division 3"]
                }
            ],
            "coverage": "3/3 chunks queried",
            "confidence": 0.9
        }
    """
```

**D. Context-Aware Prompting**

```python
MULTI_CHUNK_PROMPT = """You are answering a question about a large document split into {total_chunks} chunks.

Document: {document_name}
This is chunk {chunk_id}/{total_chunks} covering {metadata}.

Previous chunk summaries:
{chunk_1_summary}
{chunk_2_summary}

Current chunk content:
{chunk_text}

Question: {question}

Instructions:
1. Answer ONLY based on THIS chunk
2. If the answer isn't in this chunk, say "Not found in this section"
3. If you find relevant information, cite the section/page number
4. Be specific and factual

Answer:"""
```

#### Implementation Notes:
- Add progress bar for multi-chunk queries (GUI)
- Cache chunk embeddings for semantic search
- Provide chunk source attribution in answers
- Add "search all chunks" toggle in GUI

---

## Phase 4: GUI Integration

### 4.1 Enhanced Q&A Interface
**Priority:** P1 - High  
**Estimated Effort:** 2 days  
**File:** `gui/sparrow_gui.py`

#### Requirements:

**A. Document Analysis Panel** (New Section)
```
┌─ Document Size Analysis ────────────────────────────┐
│ File: bill_c15_english_only.txt                     │
│ Size: 1.15 MB (1,152,779 chars)                    │
│ Estimated Tokens: 288,195 (tiktoken method)        │
│                                                      │
│ Recommended Model: llama3.1:70b                     │
│ Strategy: Chunked (3 chunks, 128K each)            │
│                                                      │
│ [📊 View Chunk Map] [🔍 Test Token Count]          │
└──────────────────────────────────────────────────────┘
```

**B. Enhanced Q&A Controls**
```
┌─ Document Q&A ───────────────────────────────────────┐
│ Model: [llama3.1:70b ▼]                              │
│                                                       │
│ Query Strategy:                                       │
│   ○ Smart (auto-detect relevant chunks)               │
│   ● Comprehensive (query all chunks)                  │
│   ○ Quick (query first chunk only)                    │
│                                                       │
│ Question: ───────────────────────────────────────────│
│ │ What discretionary powers are granted in Part 2?  ││
│ └────────────────────────────────────────────────────┘│
│                                                       │
│ [🔍 Ask Question]  [📋 View Chunks]  [💾 Save]       │
│                                                       │
│ Answer: ──────────────────────────────────────────── │
│ │ Based on analysis of Part 2 (Chunks 1-2):        ││
│ │                                                   ││
│ │ 1. Minister may exempt entities (Section 12.3)   ││
│ │ 2. Broad "any federal law" scope (Section 14.1)  ││
│ │ 3. Self-judgment clause "in minister's opinion"  ││
│ │                                                   ││
│ │ Sources: Chunk 1 (Pages 1-210), Chunk 2 (211-420)││
│ │ Confidence: 0.92                                  ││
│ └────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────┘
```

**C. Chunk Visualization**
```
┌─ Document Chunk Map ─────────────────────────────────┐
│                                                       │
│ Chunk 1 (96K tokens)  ████████████░░░░░░░            │
│ ├─ Part 1: Budget Overview                           │
│ ├─ Part 2: Tax Measures                              │
│ └─ Pages: 1-210                                       │
│                                                       │
│ Chunk 2 (96K tokens)  ░░░░░░░████████████░░░░        │
│ ├─ Part 3: Social Programs                           │
│ ├─ Part 4: Infrastructure                            │
│ └─ Pages: 211-420                                     │
│                                                       │
│ Chunk 3 (96K tokens)  ░░░░░░░░░░░░░░████████████     │
│ ├─ Part 5: Regulations                               │
│ ├─ Appendices & Schedules                            │
│ └─ Pages: 421-632                                     │
│                                                       │
│ [✓] Chunk 1  [✓] Chunk 2  [ ] Chunk 3               │
│ (Checkboxes indicate which chunks to query)          │
└───────────────────────────────────────────────────────┘
```

#### Implementation Notes:
- Auto-calculate tokens on document load
- Show model recommendation in status bar
- Add chunk selection interface (manual override)
- Display query progress: "Querying chunk 2/3..."
- Save chunk metadata to output folder

---

## Phase 5: Advanced Features

### 5.1 Semantic Search with Embeddings
**Priority:** P2 - Medium  
**Estimated Effort:** 3-4 days  
**File:** `semantic_search.py`

#### Requirements:

**A. Chunk Embedding Generation**
```python
def generate_chunk_embeddings(
    chunks: list[dict],
    model: str = "all-MiniLM-L6-v2"
) -> dict:
    """
    Create vector embeddings for each chunk.
    
    Uses sentence-transformers for fast, accurate embeddings.
    Enables semantic similarity search for query routing.
    
    Returns:
        {
            "embeddings": np.ndarray,  # Shape: (n_chunks, 384)
            "model": "all-MiniLM-L6-v2",
            "dimension": 384
        }
    """
```

**B. Similarity Search**
```python
def find_relevant_chunks(
    query: str,
    chunk_embeddings: dict,
    chunks: list[dict],
    top_k: int = 3
) -> list[int]:
    """
    Find most relevant chunks for query.
    
    Returns:
        [chunk_id_3, chunk_id_1, chunk_id_7]  # Sorted by relevance
    """
```

**C. Hybrid Search** (Keywords + Semantic)
- Combine keyword matching (fast, precise)
- With semantic similarity (catches related concepts)
- Best of both worlds

#### Dependencies:
- `sentence-transformers` library
- `faiss` for fast vector search (optional, for large docs)

---

### 5.2 Query History & Learning
**Priority:** P3 - Low  
**Estimated Effort:** 1-2 days  

#### Requirements:

**A. Save Query History**
```json
{
    "document": "bill_c15_english_only.txt",
    "queries": [
        {
            "timestamp": "2025-12-07T10:54:22",
            "question": "What discretionary powers exist?",
            "strategy": "comprehensive",
            "chunks_queried": [1, 2, 3],
            "answer": "...",
            "confidence": 0.92,
            "user_rating": 5
        }
    ]
}
```

**B. Suggested Questions**
- Analyze document to suggest relevant questions
- "Based on this document, you might ask:"
  - "What are the discretionary powers?"
  - "What oversight mechanisms exist?"
  - "What are the exemption clauses?"

**C. Popular Queries Dashboard**
- Show most common questions across all users
- Enable knowledge sharing

---

## Testing Strategy

### Test Documents:

| Document | Size | Tokens | Strategy | Expected Result |
|----------|------|--------|----------|-----------------|
| Short article | 5 pages | 2K | Single | Fits in context |
| Medium report | 50 pages | 20K | Single | Fits in most models |
| Bill C-15 | 632 pages | 288K | Chunked (3) | Requires chunking |
| Combined budget docs | 2000 pages | 800K | Chunked (7+) | Extreme case |

### Test Scenarios:

1. **Token Estimation Accuracy**
   - Compare tiktoken vs actual Ollama tokenization
   - Verify <5% error margin

2. **Chunk Boundary Integrity**
   - Ensure no information lost at chunk boundaries
   - Verify overlap captures split sentences

3. **Query Routing Accuracy**
   - Test semantic search finds correct chunks
   - Measure precision/recall

4. **Answer Synthesis Quality**
   - Compare single-chunk vs multi-chunk answers
   - Verify comprehensive coverage

5. **Performance Benchmarks**
   - Time to chunk 1M character document
   - Query latency (all chunks vs selective)

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- ✅ Create `token_calculator.py`
- ✅ Add model context database
- ✅ Build CLI token analysis tool
- ✅ Test on Bill C-15

### Phase 2: Chunking (Week 2)
- ✅ Create `semantic_chunker.py`
- ✅ Implement section-based chunking
- ✅ Add sliding window strategy
- ✅ Generate chunk metadata/index

### Phase 3: Enhanced Q&A (Week 3)
- ✅ Create `enhanced_document_qa.py`
- ✅ Implement multi-chunk querying
- ✅ Build answer synthesis
- ✅ Add query routing logic

### Phase 4: GUI Integration (Week 4)
- ✅ Add document analysis panel
- ✅ Update Q&A interface with strategies
- ✅ Create chunk visualization
- ✅ Add progress indicators

### Phase 5: Advanced Features (Week 5-6)
- ⬜ Add semantic search with embeddings
- ⬜ Implement query history
- ⬜ Build suggested questions
- ⬜ Performance optimization

---

## Success Metrics

### Coverage:
- ✅ 100% of document accessible via Q&A (vs current partial coverage)
- ✅ Users can query any section, regardless of document size

### Accuracy:
- ✅ >90% answer accuracy on multi-chunk queries
- ✅ <5% token estimation error

### Usability:
- ✅ Model recommendation shown within 2 seconds
- ✅ Chunk map visualized clearly
- ✅ Query results cite specific sections/pages

### Performance:
- ✅ Chunking completes in <10 seconds for 1M chars
- ✅ Semantic search finds relevant chunks in <1 second
- ✅ Multi-chunk query completes in <30 seconds (3 chunks)

---

## Dependencies

### New Python Packages:
```bash
pip install tiktoken           # Token counting (OpenAI-compatible)
pip install sentence-transformers  # Embeddings for semantic search
pip install faiss-cpu          # Fast vector search (optional)
```

### Ollama Models (Recommended):
```bash
ollama pull llama3.1:8b        # Good balance (128K context)
ollama pull llama3.1:70b       # Best for large docs (128K context)
ollama pull qwen2.5:72b        # Largest context (131K)
```

---

## Integration Points

### Files to Modify:
1. `gui/sparrow_gui.py` - Add document analysis panel, enhanced Q&A interface
2. `document_qa.py` - Upgrade to use chunking system
3. `narrative_qa.py` - Update for chunk-aware narrative queries
4. `sparrow_grader_v8.py` - Add token analysis to CLI

### Files to Create:
1. `token_calculator.py` - Token counting and model recommendation
2. `semantic_chunker.py` - Intelligent document chunking
3. `enhanced_document_qa.py` - Multi-chunk Q&A engine
4. `semantic_search.py` - Embedding-based chunk search (Phase 5)

---

## Documentation Requirements

### User Documentation:
- "How to Choose the Right Model for Your Document"
- "Understanding Document Chunks"
- "Query Strategies Explained"

### Technical Documentation:
- Update `TECHNICAL_ARCHITECTURE_REPORT.md` with v8.6 Q&A system
- Create `QA_SYSTEM_ARCHITECTURE.md` with chunking details
- Add token calculation guide

---

## Future Enhancements (v8.7+)

1. **Cross-Document Q&A** - Query multiple documents simultaneously
2. **Temporal Q&A** - Compare document versions ("What changed in Budget 2024 vs 2025?")
3. **Citation Extraction** - Auto-extract and verify citations during Q&A
4. **Interactive Drill-Down** - Click answer to see source chunk in context
5. **Export Q&A Report** - Generate PDF with all questions/answers
6. **Multi-Language Q&A** - Ask in English, get answers from French sections
7. **Voice Q&A** - Audio input/output for accessibility

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Token estimation inaccurate | Low | Medium | Use tiktoken + test against actual Ollama counts |
| Chunking loses context | Medium | High | Implement overlap, test on known questions |
| Multi-chunk synthesis poor | Medium | High | Use stronger synthesis model, add confidence scores |
| Semantic search slow | Low | Medium | Use faiss, cache embeddings, optimize indexing |
| User confusion with chunks | Medium | Medium | Add clear visualization, auto-select strategy |

---

## Conclusion

This enhancement transforms Sparrow SPOT's Q&A from single-context to comprehensive document coverage. Users analyzing 600+ page bills will get accurate answers across the entire document, with intelligent model selection and transparent chunk attribution.

**Key Benefits:**
- ✅ Handle documents of ANY size (no context limits)
- ✅ Intelligent model recommendation (save compute)
- ✅ Comprehensive coverage (query entire document)
- ✅ Source attribution (cite specific sections)
- ✅ User-friendly (auto-chunking, clear visualization)

**Implementation Priority:** HIGH  
**Target Completion:** 4-6 weeks  
**Version:** 8.6.0

---

*TODO created by Sparrow SPOT Development Team - December 7, 2025*

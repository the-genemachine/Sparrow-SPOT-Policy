# Token Metrics System Design Document
## Sparrow SPOT Scale™ v8.6.1

**Document Version:** 1.0  
**Date:** December 8, 2025  
**Status:** Design Specification for Review  

---

## Executive Summary

This document outlines a comprehensive token metrics system for Sparrow SPOT Scale™. Users will be able to see:

1. **Document Token Count** - How many tokens the input document uses
2. **Model Capacity** - Maximum tokens each Ollama model can process
3. **Utilization %** - How much of the model's capacity the document consumes
4. **Tokens Consumed** - Actual tokens used during analysis
5. **Cost Estimation** - (Optional) Cost per analysis if using API-based models

**Problem Solved:** Currently users have no visibility into whether their document will fit in the model's context window, or how efficiently the analysis used available tokens.

**User Impact:** Users can make informed decisions about document size, model selection, and understand analysis scope.

---

## Core Metrics Definition

### 1. Document Tokens
**Definition:** Total number of tokens in the input document

**Calculation Point:** On document upload/ingestion  
**Method:** Use tokenizer to count tokens in full text  
**Display:** Show to user before analysis starts  
**Storage:** In analysis results as `token_metrics.document_tokens`

**Example:**
```
Bill-C9.txt: 9,826 characters → 2,156 tokens
```

### 2. Model Capacity
**Definition:** Maximum tokens a specific Ollama model can process in one request

**Examples by Model:**
- llama2 (7B): 4,096 token context window
- llama2 (13B): 4,096 token context window
- mistral (7B): 8,192 token context window
- neural-chat: 8,192 token context window
- orca-mini: 2,048 token context window

**Calculation Point:** Static, loaded from model_capabilities.json  
**Display:** Show when user selects model  
**Storage:** In analysis results as `token_metrics.model_capacity`

### 3. Utilization Percentage
**Definition:** Document tokens ÷ Model capacity × 100

**Formula:** 
```
Utilization % = (Document Tokens / Model Capacity) × 100
```

**Safety Thresholds:**
- 0-50%: Safe ✅ (plenty of room for analysis)
- 51-75%: Caution ⚠️ (getting tight, consider smaller document)
- 76-90%: Warning ⚠️⚠️ (risky, may fail or be slow)
- 91-100%: Danger ❌ (will fail, document too large)
- 100%+: Blocked ❌ (cannot process with this model)

**Display:** Color-coded gauge chart  
**Storage:** In analysis results as `token_metrics.utilization_percent`

### 4. Tokens Consumed in Analysis
**Definition:** Actual tokens used during the analysis process

**Breakdown:**
- Input tokens: Document tokens sent to model
- Processing tokens: Intermediate analysis steps
- Output tokens: Response/analysis generated
- Total: Sum of all

**Calculation Point:** During analysis (if API-based) or estimate post-analysis  
**Display:** Show in analysis summary  
**Storage:** In analysis results as `token_metrics.analysis_breakdown`

**Example:**
```
{
  "input_tokens": 2156,
  "processing_tokens": 450,
  "output_tokens": 890,
  "total_consumed": 3496,
  "tokens_available": 4096
}
```

### 5. Cost Estimation (Optional)
**Definition:** Estimated cost for this analysis (if using API-based models)

**Applicable To:**
- OpenAI models (GPT-4, GPT-3.5, etc)
- Anthropic models (Claude)
- Other API-based models

**Not Applicable To:**
- Ollama models (self-hosted, no per-token cost)

**Calculation:**
```
Cost = (Input Tokens × Input Price) + (Output Tokens × Output Price)
```

**Example (GPT-4):**
```
Input: 2,156 tokens × $0.00003/token = $0.06
Output: 890 tokens × $0.00006/token = $0.05
Total: $0.11
```

---

## System Architecture

### Component 1: Token Counter Module

**File:** `token_counter.py` (NEW, ~300 lines)

**Responsibilities:**
- Count tokens in text using appropriate tokenizer
- Query model capacities from database
- Calculate utilization percentages
- Estimate tokens consumed

**Main Classes:**

```python
class TokenCounter:
    """
    Main token counting interface
    """
    
    def __init__(self, tokenizer_backend="auto"):
        """
        Initialize with specified tokenizer
        Options: "auto", "tiktoken", "transformers", "ollama"
        """
        pass
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        pass
    
    def get_model_capacity(self, model_name: str) -> int:
        """Get max tokens for a model"""
        pass
    
    def calculate_utilization(self, 
                            document_tokens: int, 
                            model_name: str) -> float:
        """Return utilization percentage (0-100+)"""
        pass
    
    def estimate_tokens_consumed(self,
                                input_tokens: int,
                                output_tokens: int,
                                model_name: str) -> Dict:
        """Estimate/calculate tokens used in analysis"""
        pass
    
    def estimate_cost(self,
                     input_tokens: int,
                     output_tokens: int,
                     model_provider: str) -> float:
        """Estimate cost for API-based models"""
        pass
```

**Tokenizer Strategy:**

```
Auto-detect tokenizer based on model:
├─ Ollama models → Use ollama-specific tokenizer
├─ OpenAI models → Use tiktoken
├─ Anthropic models → Use claude tokenizer
└─ Default → Use transformers tokenizer as fallback
```

### Component 2: Model Capabilities Database

**File:** `model_capabilities.json` (NEW, ~200 lines)

**Structure:**

```json
{
  "models": {
    "llama2:7b": {
      "provider": "ollama",
      "context_window": 4096,
      "input_price_per_k": 0,
      "output_price_per_k": 0,
      "description": "Meta's Llama 2 7B",
      "typical_utilization": "45%",
      "performance": "balanced"
    },
    "mistral:latest": {
      "provider": "ollama",
      "context_window": 8192,
      "input_price_per_k": 0,
      "output_price_per_k": 0,
      "description": "Mistral 7B v0.1",
      "typical_utilization": "40%",
      "performance": "fast"
    },
    "gpt-4": {
      "provider": "openai",
      "context_window": 8192,
      "input_price_per_k": 0.03,
      "output_price_per_k": 0.06,
      "description": "OpenAI GPT-4",
      "typical_utilization": "60%",
      "performance": "best"
    },
    "claude-2": {
      "provider": "anthropic",
      "context_window": 100000,
      "input_price_per_k": 0.008,
      "output_price_per_k": 0.024,
      "description": "Anthropic Claude 2",
      "typical_utilization": "25%",
      "performance": "best"
    }
  }
}
```

### Component 3: Display Locations

#### 3.1 Pre-Upload Estimation

**Location:** GUI file upload screen

**Display:**
```
📄 Select document to analyze

When file selected:
┌─────────────────────────────┐
│ Document: Bill-C9.txt       │
│ Size: 45 KB                 │
│ Estimated Tokens: 2,156     │
│                             │
│ Selected Model: llama2:7b   │
│ Model Capacity: 4,096       │
│ Utilization: 52.7%  ⚠️      │
│                             │
│ Status: ✅ Can process      │
│                             │
│ [Continue] [Select Different Model]
└─────────────────────────────┘
```

#### 3.2 GUI Dashboard

**Location:** New tab in Gradio interface: "Analysis Metrics"

**Display:**
```
═══════════════════════════════════════════════════════════════
                    TOKEN METRICS DASHBOARD
═══════════════════════════════════════════════════════════════

Document Analysis
┌───────────────────────────────────────────────────────────┐
│ Document Tokens: 2,156 / 4,096                            │
│ ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░ 52.7%         │
│                                                           │
│ Status: ⚠️ Caution - Consider smaller document           │
└───────────────────────────────────────────────────────────┘

Token Usage Breakdown
┌───────────────────────────────────────────────────────────┐
│ Input Tokens:      2,156  (64%)                           │
│ Processing:          450  (13%)                           │
│ Output Generated:    890  (26%)                           │
│ ─────────────────────────────────────────────────────────│
│ Total Consumed:    3,496  of 4,096 available (85%)       │
└───────────────────────────────────────────────────────────┘

Model Information
┌───────────────────────────────────────────────────────────┐
│ Model: llama2:7b                                          │
│ Context Window: 4,096 tokens                             │
│ Provider: Ollama (self-hosted)                           │
│ Cost: $0.00 (local processing)                           │
└───────────────────────────────────────────────────────────┘

Efficiency Rating: Good 82/100
```

#### 3.3 Investigation Viewer (index.html)

**Location:** New panel in investigation_index_generator.py output

**Display:**
```html
<div class="metrics-panel">
  <h3>📊 Token Metrics</h3>
  
  <div class="metric-item">
    <label>Document Tokens:</label>
    <span class="value">2,156</span>
    <span class="context">(45 KB input)</span>
  </div>
  
  <div class="metric-item">
    <label>Model Capacity:</label>
    <span class="value">4,096</span>
    <span class="context">llama2:7b</span>
  </div>
  
  <div class="metric-item">
    <label>Utilization:</label>
    <progress value="52.7" max="100"></progress>
    <span class="value">52.7%</span>
    <span class="status caution">⚠️ Caution</span>
  </div>
  
  <div class="metric-item">
    <label>Efficiency Rating:</label>
    <span class="value">82/100 - Good</span>
  </div>
</div>
```

#### 3.4 Narrative Reports

**Location:** Included in published markdown reports

**Display:**
```markdown
## Analysis Scope Metrics

This analysis was performed under the following technical constraints:

**Token Utilization:**
- Document size: 2,156 tokens
- Model capacity: 4,096 tokens (llama2:7b)
- Utilization rate: 52.7% ⚠️
- Status: Caution - Document approaching model's comfortable range

**Analysis Efficiency:**
- Input tokens consumed: 2,156
- Processing overhead: 450 tokens
- Analysis output generated: 890 tokens
- Total tokens used: 3,496 of 4,096 available (85%)
- Efficiency rating: Good (82/100)

**Model Information:**
- Model: llama2:7b (Meta Llama 2 7 Billion)
- Provider: Ollama (self-hosted)
- Processing cost: $0.00 (local)
- Average processing time: 45 seconds

**Interpretation:**
This document was processed efficiently with good utilization of available model capacity. 
The 52.7% utilization rate indicates there is adequate room for the model to perform 
comprehensive analysis without being constrained by context window limits.
```

#### 3.5 Certificate/Summary Documents

**Location:** In HTML certificate and summary outputs

**Display:**
```html
<div class="analysis-metadata">
  <h4>Analysis Scope</h4>
  <table>
    <tr>
      <td>Document Tokens</td>
      <td>2,156</td>
    </tr>
    <tr>
      <td>Model Used</td>
      <td>llama2:7b</td>
    </tr>
    <tr>
      <td>Model Capacity</td>
      <td>4,096 tokens</td>
    </tr>
    <tr>
      <td>Utilization Rate</td>
      <td><span class="caution">52.7%</span></td>
    </tr>
    <tr>
      <td>Analysis Efficiency</td>
      <td>Good (82/100)</td>
    </tr>
  </table>
</div>
```

---

## Integration Points

### 1. Document Ingestion (sparrow_grader_v8.py)

```python
# Around line 200 - When document is loaded
from token_counter import TokenCounter

token_counter = TokenCounter()

# Count input tokens
input_tokens = token_counter.count_tokens(full_text)
logging.info(f"Input document: {input_tokens} tokens")

# Store in analysis results
analysis_results = {
    "token_metrics": {
        "document_tokens": input_tokens,
        "document_size_bytes": len(full_text.encode('utf-8')),
        "estimated_characters": len(full_text)
    }
}
```

### 2. Model Selection (sparrow_grader_v8.py)

```python
# Around line 250 - When model is selected
model_capacity = token_counter.get_model_capacity(selected_model)
utilization = token_counter.calculate_utilization(input_tokens, selected_model)

# Validate document fits
if utilization > 100:
    raise ValueError(f"Document too large for {selected_model}. "
                    f"Utilization: {utilization}%. "
                    f"Use a larger model or smaller document.")

if utilization > 75:
    logging.warning(f"High utilization: {utilization}%. Analysis may be slow.")

analysis_results["token_metrics"].update({
    "model_capacity": model_capacity,
    "selected_model": selected_model,
    "utilization_percent": utilization,
    "utilization_status": "safe" if utilization < 50 
                         else "caution" if utilization < 75
                         else "warning"
})
```

### 3. Analysis Execution (sparrow_grader_v8.py)

```python
# Around line 3000 - During/after analysis
# Track tokens consumed (if API-based)
if uses_api_model:
    analysis_results["token_metrics"]["tokens_consumed"] = {
        "input": input_tokens,
        "output": output_token_count,
        "processing_overhead": estimated_processing_tokens,
        "total": input_tokens + output_token_count + estimated_processing_tokens,
        "available": model_capacity
    }
    
    # Calculate cost if applicable
    cost = token_counter.estimate_cost(
        input_tokens, 
        output_token_count,
        model_provider
    )
    analysis_results["token_metrics"]["estimated_cost"] = cost
```

### 4. Output Generation

**JSON Output (Bill-C9-00.json):**
```json
{
  "token_metrics": {
    "document_tokens": 2156,
    "document_size_bytes": 45123,
    "model_used": "llama2:7b",
    "model_capacity": 4096,
    "utilization_percent": 52.7,
    "utilization_status": "caution",
    "tokens_consumed": {
      "input": 2156,
      "output": 890,
      "processing_overhead": 450,
      "total": 3496,
      "available": 4096
    },
    "efficiency_rating": 82,
    "efficiency_description": "Good",
    "estimated_cost": 0.0,
    "cost_breakdown": {
      "input_cost": 0.0,
      "output_cost": 0.0,
      "currency": "USD"
    }
  }
}
```

---

## Tokenizer Selection Strategy

### Current State
The app likely uses various models without consistent token counting.

### Proposed Approach

```python
class TokenizerManager:
    """
    Manages tokenizer selection and caching
    """
    
    def get_tokenizer(self, model_name: str):
        """
        Auto-detect and return appropriate tokenizer
        
        Logic:
        1. If Ollama model → Use ollama tokenizer library
        2. If OpenAI model → Use tiktoken
        3. If Anthropic model → Use anthropic tokenizer
        4. If transformers available → Use transformers
        5. Else → Use character-based estimation (rough)
        """
        pass
    
    # Cache tokenizers to avoid repeated loading
    _tokenizer_cache = {}
```

### Dependencies to Add

```txt
# In requirements.txt

# Token counting
tiktoken>=0.5.0              # OpenAI token counting
transformers>=4.30.0         # HuggingFace tokenizers

# Ollama support (if needed)
ollama>=0.0.1               # For ollama-specific token counting

# Visualization (optional)
plotly>=5.17.0              # For token metrics charts
```

---

## Safety and Validation

### Document Size Limits

```python
DOCUMENT_LIMITS = {
    "ollama": {
        "llama2:7b": {"max_tokens": 4096, "safe_tokens": 2048},
        "mistral:latest": {"max_tokens": 8192, "safe_tokens": 6144},
    },
    "openai": {
        "gpt-3.5-turbo": {"max_tokens": 4096, "safe_tokens": 3072},
        "gpt-4": {"max_tokens": 8192, "safe_tokens": 6144},
    }
}

# Validation
if utilization > 100:
    raise DocumentTooLargeError(
        f"Document is {utilization}% of model capacity. "
        f"Cannot process with {model_name}."
    )

if utilization > 90:
    logging.warning(
        f"Document is {utilization}% of model capacity. "
        f"Analysis may fail or be slow."
    )

if utilization > 75:
    logging.warning(
        f"Document is {utilization}% of model capacity. "
        f"Consider using a larger model or smaller document."
    )
```

---

## Edge Cases & Error Handling

### 1. Different Tokenizers Produce Different Counts
**Problem:** tiktoken counts differently than transformers

**Solution:**
- Use official model tokenizer when possible
- Document which tokenizer was used in metadata
- Allow 10% variance tolerance

### 2. Special Tokens vs Content
**Problem:** [CLS], [SEP], [PAD] tokens inflate count

**Solution:**
- Count only content tokens for user display
- Include special tokens in technical metrics
- Separate display: "2,156 content tokens + 42 special"

### 3. Multilingual Documents
**Problem:** Tokenizer may not handle all languages equally

**Solution:**
- Detect language and warn if unusual
- Use language-specific tokenizers if available
- Document language in analysis metadata

### 4. Very Large Documents
**Problem:** Document larger than any available model

**Solution:**
- Detect upfront
- Recommend chunking document
- Provide guidance on splitting text

### 5. Token Counting Performance
**Problem:** Counting millions of tokens could slow analysis

**Solution:**
- Cache tokenizers after first load
- Count tokens in parallel for large documents
- Use estimation for very large texts

---

## User-Facing Documentation

### For Users: "Understanding Token Metrics"

**What are tokens?**
Tokens are small chunks of text. Models break documents into tokens to process them.
- 1 token ≈ 4 characters or 0.75 words
- A 1,000-word document ≈ 1,300 tokens

**Why does this matter?**
Each model has a maximum number of tokens it can handle at once (context window).
If your document is too large for the model's context window, the analysis will fail.

**Reading the metrics:**
- **Document Tokens:** How many tokens your input document has
- **Model Capacity:** Max tokens the selected model can handle
- **Utilization %:** How much of the model's capacity your document uses
- **Status Color:** 
  - 🟢 Green (0-50%): Safe, plenty of room
  - 🟡 Yellow (51-75%): Caution, getting tight
  - 🔴 Red (76-100%): Warning, may fail
  - ⚫ Black (100%+): Blocked, document too large

**If your document is too large:**
1. Try a larger model (e.g., 13B instead of 7B)
2. Split your document into smaller parts
3. Remove less relevant sections
4. Use document summarization first

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- ✅ Create token_counter.py module
- ✅ Build model_capabilities.json database
- ✅ Add tokenizer dependencies
- ✅ Integrate into sparrow_grader_v8.py

### Phase 2: Display (Week 2)
- ✅ Add to GUI dashboard
- ✅ Add to index.html viewer
- ✅ Include in JSON outputs
- ✅ Pre-upload estimation

### Phase 3: Reports (Week 3)
- ✅ Narrative report sections
- ✅ Certificate metadata
- ✅ User documentation

### Phase 4: Polish (Week 4)
- ✅ Edge case handling
- ✅ Performance optimization
- ✅ Testing and validation
- ✅ Admin analytics (optional)

---

## Success Criteria

**Users should be able to:**
- ✅ See document token count before uploading
- ✅ Know if document fits in selected model
- ✅ Understand why analysis failed (if too large)
- ✅ Make informed model/document size decisions
- ✅ See efficiency rating after analysis
- ✅ Compare token usage across analyses

**System should:**
- ✅ Validate document size before analysis
- ✅ Provide clear warnings for high utilization
- ✅ Block processing if document exceeds model capacity
- ✅ Count tokens consistently across all displays
- ✅ Not slow down analysis process
- ✅ Handle edge cases gracefully

---

## Optional Future Enhancements

1. **Token History Dashboard**
   - Track tokens over time
   - Identify trends in document sizes
   - Analyze efficiency improvements

2. **Cost Dashboard** (if using API models)
   - Track cost per analysis
   - Budget tracking
   - Cost optimization recommendations

3. **Document Chunking Tool**
   - Auto-split large documents
   - Process multiple chunks in parallel
   - Reassemble results

4. **Model Benchmarking**
   - Speed tests for different models
   - Quality comparisons
   - Cost-benefit analysis per model

5. **Admin Analytics**
   - Total tokens consumed per day/week/month
   - Average tokens per document type
   - Model utilization rates
   - Recommendations for infrastructure optimization

---

## Conclusion

This token metrics system provides transparency into the analysis process and helps users make informed decisions. By showing:
- What fits before processing
- How efficiently the system works
- Why something failed (if applicable)

Users gain confidence in the system and can optimize their workflows accordingly.

The implementation is modular and can be rolled out in phases without disrupting existing functionality.

---

**Document Status:** Ready for review and implementation

**Next Steps:** 
1. Review this design document
2. Approve implementation approach
3. Begin Phase 1: Foundation
4. Schedule token metrics feature for specific sprint/release

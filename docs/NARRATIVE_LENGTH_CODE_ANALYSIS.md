# Code Analysis: Narrative Length Issue (450 words vs. 3500 expected)

## Problem Summary
When user selects "comprehensive" narrative length (3500+ words), the system generates only ~450 words with a meta-note explaining what should have been generated.

---

## Code Flow Analysis

### 1. **User Selection → Backend (sparrow_grader_v8.py, line 2379)**
```python
narrative_length = args.narrative_length  # ✅ Correctly captures 'comprehensive'
narrative_outputs = grader.narrative_pipeline.generate_complete_narrative(
    report, 
    tone=narrative_tone,
    length=narrative_length,        # ✅ Passed to pipeline
    ollama_model=ollama_model
)
```
**Status:** ✅ Working correctly - length parameter is passed.

---

### 2. **Pipeline Entry Point (narrative_integration.py, line 98-102)**
```python
def generate_complete_narrative(self, analysis: Dict, tone: str = 'journalistic', 
                                 length: str = 'standard', ollama_model: str = None):
```
**Status:** ✅ Function accepts length parameter

---

### 3. **Tone Adaptation Step (narrative_integration.py, line 139)**
```python
narrative_text = self.tone_adaptor.adapt(narrative_components, tone, length=length)
```
**Status:** ✅ Length passed to tone_adaptor

---

### 4. **Tone Adapter Processing (tone_adaptor.py, line 62-93)**

The adapter defines:
```python
length_targets = {
    'concise': 500,
    'standard': 1000,
    'detailed': 2000,
    'comprehensive': 3500
}
target_words = length_targets.get(length, 1000)  # ✅ Gets 3500 for comprehensive
```

Then routes based on tone (critical, academic, journalistic, etc.):
```python
if tone == 'journalistic':
    return self._adapt_journalistic(..., target_words)  # Passes 3500
elif tone == 'critical':
    return self._adapt_critical(..., target_words)      # Passes 3500
# etc.
```

**Key Point:** The tone adaptor ONLY generates base narrative of ~450-500 words. It doesn't expand to target length.

**Status:** ⚠️ **Limitation found here** - tone adaptor generates small narrative regardless of target_words value.

---

### 5. **Expansion Logic (narrative_integration.py, line 142-145)**

After tone adaptation, the code checks:
```python
if length in ['detailed', 'comprehensive'] and ollama_model:
    print(f"   📝 Expanding narrative with {ollama_model}...")
    narrative_text, analysis, length, ollama_model
)
```

**This is where expansion to 3500 words SHOULD happen.**

**Status:** ⚠️ **Critical issue found** - There's a syntax error here!

---

## Issues Found

### **Issue #1: Incomplete Expansion Call (CRITICAL)**
**Location:** `narrative_integration.py`, line 145

**Current Code:**
```python
if length in ['detailed', 'comprehensive'] and ollama_model:
    print(f"   📝 Expanding narrative with {ollama_model}...")
    narrative_text, analysis, length, ollama_model
)
```

**Problem:** 
- The line `narrative_text, analysis, length, ollama_model` doesn't do anything
- Missing function call to `_expand_narrative_with_ollama()`
- The function exists (line 497) but is never called!
- Missing assignment of returned expanded text

**Expected:**
```python
if length in ['detailed', 'comprehensive'] and ollama_model:
    print(f"   📝 Expanding narrative with {ollama_model}...")
    narrative_text = self._expand_narrative_with_ollama(
        narrative_text, analysis, length, ollama_model
    )
```

**Impact:** The expansion function exists but is never invoked, so narrative stays at 450 words.

---

### **Issue #2: Silent Failure Path**

When expansion doesn't run, the code continues with the small narrative and then adds a meta-note (lines 151-153 area) acknowledging the gap:

```
(Note: This expanded narrative is approximately 450 words. To reach the 
desired length of approximately 3500 words...)
```

This is a fallback message that shouldn't appear if expansion was working.

**Impact:** User sees acknowledgment of the failure instead of actual expansion.

---

### **Issue #3: tone_adaptor Only Generates Base Narrative**

**Location:** `tone_adaptor.py`, lines 139-157, 224-245, 318-319

The adaptor has checks like:
```python
if target_words >= 2000:  # detailed or comprehensive
    narrative.append("Additional section")
    
if target_words >= 3500:  # comprehensive
    narrative.append("Comprehensive section")
```

But these only add small incremental sections (~50-100 words each), not full expansion to 3500 words.

**Impact:** The tone adaptor generates a base narrative of ~450 words, then the expansion function is supposed to take it to 3500. But since expansion isn't called, it stops at 450.

---

## Root Cause

**The `_expand_narrative_with_ollama()` function is defined but never called due to a syntax error in the calling code.**

The function is complete and functional:
- Takes narrative_text, analysis, length, and ollama_model
- Constructs appropriate Ollama prompt for expansion
- Handles timeouts (120 second timeout for generation)
- Strips meta-commentary from response
- Returns expanded text

But it's unreachable because the calling statement at line 145 is incomplete.

---

## Suggested Fixes

### **Fix #1: Complete the Function Call (PRIORITY: CRITICAL)**
**File:** `narrative_integration.py`, line 142-145

**Current (Broken):**
```python
if length in ['detailed', 'comprehensive'] and ollama_model:
    print(f"   📝 Expanding narrative with {ollama_model}...")
    narrative_text, analysis, length, ollama_model
)
```

**Suggested (Working):**
```python
if length in ['detailed', 'comprehensive'] and ollama_model:
    print(f"   📝 Expanding narrative with {ollama_model}...")
    narrative_text = self._expand_narrative_with_ollama(
        narrative_text, analysis, length, ollama_model
    )
```

**Why:** This actually calls the expansion function and captures the expanded text.

---

### **Fix #2: Add Error Handling for Ollama Connection**
**File:** `narrative_integration.py`, line 142

The code assumes Ollama is running. If it's not, expansion silently fails and returns the base narrative.

**Suggested Addition:**
```python
if length in ['detailed', 'comprehensive'] and ollama_model:
    print(f"   📝 Expanding narrative with {ollama_model}...")
    try:
        narrative_text = self._expand_narrative_with_ollama(
            narrative_text, analysis, length, ollama_model
        )
    except Exception as e:
        print(f"   ⚠️  Ollama expansion failed ({str(e)}), using base narrative")
        print(f"   💡 Ensure Ollama is running: ollama serve")
```

**Why:** Users will know why expansion didn't happen.

---

### **Fix #3: Improve Meta-Note Messaging**
**Location:** Unknown (search for "approximately 450 words" in codebase)

The meta-note should only appear if expansion was explicitly skipped due to Ollama being unavailable, not as a fallback.

**Suggested Change:**
Instead of always including the note, only include it in error cases:
```python
if expansion_attempted_but_failed:
    narrative_text += "\n\n(Note: Narrative expansion was not completed...)"
```

---

### **Fix #4: Add Debugging Output**
**File:** `narrative_integration.py`, line 142

Add logging to verify the path is being taken:
```python
print(f"   Length requirement: {length}")
print(f"   Ollama available: {ollama_model is not None}")
if length in ['detailed', 'comprehensive'] and ollama_model:
    print(f"   ✓ Expansion conditions met, expanding narrative...")
else:
    print(f"   ℹ️  Expansion conditions not met (length={length}, ollama={ollama_model is not None})")
```

**Why:** Helps diagnose why expansion isn't happening.

---

## Additional Observations

### **Ollama Timeout Configuration**
The expansion function uses 120-second timeout (line 608):
```python
timeout=120  # 2 minute timeout for longer generation
```

For comprehensive narratives requiring 3500 words with slower models, this might be tight. Consider:
- Increasing to 180 seconds for comprehensive length
- Making it configurable per length/model

---

### **Token Budget**
The expansion prompt sets:
```python
"num_predict": target_words * 2,  # Allow generous token count
```

For comprehensive (3500 words), this requests ~7000 tokens. This is reasonable but:
- Faster models (granite, mistral) might produce fewer tokens
- Slower models (llama2) might be more verbose
- No error handling if actual output is significantly under target

**Suggestion:** Add fallback logic if first expansion generates < 80% of target, retry with additional context.

---

## Testing Recommendations

1. **Test with comprehensive length selected:**
   - Verify `narrative_text = self._expand_narrative_with_ollama(...)` line is actually executed
   - Check Ollama server logs for request/response
   - Verify returned text is > 2000 words

2. **Test Ollama availability:**
   - Run without Ollama server
   - Verify error message displays
   - Confirm fallback to base narrative works

3. **Test different lengths:**
   - concise (should skip expansion, ~500 words) ✓
   - standard (should skip expansion, ~1000 words) ✓
   - detailed (should expand to ~2000 words) - NEEDS FIX
   - comprehensive (should expand to ~3500 words) - NEEDS FIX

4. **Test output verification:**
   - Ensure meta-note about "approximately 450 words" doesn't appear after expansion
   - Check word count matches expected range ±10%

---

## Summary

| Issue | Location | Severity | Status |
|-------|----------|----------|--------|
| Missing function call | `narrative_integration.py:145` | CRITICAL | Unverified |
| No Ollama error handling | `narrative_integration.py:142` | HIGH | Unverified |
| Meta-note always present | Unknown | MEDIUM | Unverified |
| Insufficient debugging | Multiple | MEDIUM | Unverified |
| Tight timeout for slow models | `narrative_integration.py:608` | LOW | Unverified |

**Primary Fix Required:** Line 145 in `narrative_integration.py` - add function call assignment.

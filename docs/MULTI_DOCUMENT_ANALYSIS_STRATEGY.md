# Multi-Document Analysis Strategy for Sparrow SPOT Policy Investigations

**Date:** December 12, 2025  
**Issue:** Cross-Document Legal Analysis Requirements  
**Status:** Proposed Solutions

---

## Problem Statement

### Current Limitation
Sparrow SPOT Scale™ is designed as a **single-document analyzer**, but policy investigations often require **cross-document reasoning** to:
- Compare implementing legislation against source declarations
- Identify gaps between international commitments and domestic law
- Analyze how vague language in one document affects obligations in another
- Track compliance mechanisms across multiple legal instruments

### Real-World Example: Bill C-15 & UNDRIP Investigation

**Investigation Goal:**  
Determine whether Bill C-15's implementation language creates exploitable gaps when implementing UNDRIP Article 28's land redress provisions.

**Required Analysis:**
1. Extract UNDRIP Article 28's specific requirements (restitution, compensation, consent)
2. Extract Bill C-15's implementation mechanisms (Section 5, Section 6)
3. **Compare** to identify gaps, vague language, or missing enforcement
4. Assess whether ministerial discretion could delay/avoid obligations

**Current System Limitation:**
- Combined document approach loses document identity
- Cannot distinguish "what UNDRIP requires" vs "what Bill C-15 implements"
- Model treats combined text as single narrative, missing structural comparison

---

## Solution Architecture

### Option 1: Structured Template Approach ⭐ **IMMEDIATE SOLUTION**

**Concept:** Create pre-structured analysis documents that explicitly separate source documents and frame comparison questions.

**Implementation:**

```markdown
# Analysis Template Structure

## PART 1: SOURCE DOCUMENT (UNDRIP)
[Extract relevant articles with full text]

## PART 2: IMPLEMENTING DOCUMENT (BILL C-15)
[Extract relevant sections with full text]

## PART 3: COMPARISON FRAMEWORK
[Explicit comparison questions for model]

## PART 4: ANALYSIS REQUEST
[Targeted query comparing both parts]
```

**Advantages:**
✅ Works with existing Sparrow SPOT infrastructure  
✅ No code changes required  
✅ Maintains document separation through structure  
✅ Can be deployed immediately

**Disadvantages:**
⚠️ Manual template creation for each investigation  
⚠️ Relies on model understanding structural cues  
⚠️ Limited automation

**Use Case:** Immediate analysis needs, one-off investigations

---

### Option 2: Sequential Analysis Pipeline 🔄 **SHORT-TERM AUTOMATION**

**Concept:** Chain multiple Sparrow SPOT analyses, feeding outputs as context to subsequent queries.

**Workflow:**

```bash
# Stage 1: Extract UNDRIP requirements
sparrow_grader_v8.py undrip.txt \
  --document-qa "What specific obligations does Article 28 establish?"
  
# Stage 2: Extract Bill C-15 mechanisms  
sparrow_grader_v8.py bill_c15.txt \
  --document-qa "What implementation mechanisms does Section 5-6 establish?"

# Stage 3: Combine results and analyze
cat stage1_output.md stage2_output.md > combined_context.txt
sparrow_grader_v8.py combined_context.txt \
  --document-qa "Based on above comparison, what gaps exist?"
```

**Script Example:**

```bash
#!/bin/bash
# multi_doc_pipeline.sh

DOC1=$1      # Primary document (e.g., UNDRIP)
DOC2=$2      # Secondary document (e.g., Bill C-15)
QUERY=$3     # Analysis question
OUTPUT_DIR=$4

# Stage 1: Analyze primary document
python sparrow_grader_v8.py "$DOC1" \
  -o "$OUTPUT_DIR/stage1" \
  --enable-chunking \
  --document-qa "Extract all provisions relevant to: $QUERY"

# Stage 2: Analyze secondary document
python sparrow_grader_v8.py "$DOC2" \
  -o "$OUTPUT_DIR/stage2" \
  --enable-chunking \
  --document-qa "Extract all provisions relevant to: $QUERY"

# Stage 3: Create comparison context
cat << EOF > "$OUTPUT_DIR/comparison_context.txt"
PRIMARY DOCUMENT FINDINGS:
$(cat "$OUTPUT_DIR/stage1/qa/analysis_qa_analysis.md")

SECONDARY DOCUMENT FINDINGS:
$(cat "$OUTPUT_DIR/stage2/qa/analysis_qa_analysis.md")

COMPARISON REQUEST:
$QUERY
EOF

# Stage 4: Comparative analysis
python sparrow_grader_v8.py "$OUTPUT_DIR/comparison_context.txt" \
  -o "$OUTPUT_DIR/final_analysis" \
  --enable-chunking \
  --document-qa "Compare the two documents above and identify gaps, inconsistencies, or vague language relevant to: $QUERY"
```

**Advantages:**
✅ Automated workflow  
✅ Preserves document identity through stages  
✅ Can be scripted for reproducibility  
✅ Works with existing codebase

**Disadvantages:**
⚠️ Multiple passes increase processing time  
⚠️ Context concatenation may exceed token limits  
⚠️ Intermediate outputs need manual review

**Use Case:** Recurring investigation patterns, batch analysis

---

### Option 3: Multi-Document Reference System 🔗 **MEDIUM-TERM ENHANCEMENT**

**Concept:** Extend Sparrow SPOT with `--reference-documents` feature allowing cross-referencing during analysis.

**Proposed CLI Interface:**

```bash
python sparrow_grader_v8.py undrip.txt \
  --reference-documents bill_c15.txt afn_brief.pdf \
  --document-qa "Does Bill C-15's Section 5 adequately implement Article 28?" \
  --cross-reference-mode enabled
```

**Technical Implementation:**

```python
# In sparrow_grader_v8.py

parser.add_argument('--reference-documents', 
                   nargs='+',
                   help='Additional documents for cross-referencing')

parser.add_argument('--cross-reference-mode',
                   action='store_true',
                   help='Enable multi-document reasoning')

# In enhanced_document_qa.py

class MultiDocumentQAEngine:
    def __init__(self, primary_doc, reference_docs):
        self.primary_engine = DocumentQAEngine(primary_doc)
        self.reference_engines = [
            DocumentQAEngine(ref) for ref in reference_docs
        ]
    
    def query_with_references(self, question):
        # Query primary document
        primary_result = self.primary_engine.query(question)
        
        # Query all reference documents
        reference_results = []
        for ref_engine in self.reference_engines:
            ref_result = ref_engine.query(question)
            reference_results.append(ref_result)
        
        # Synthesize cross-document answer
        return self._synthesize_multi_document(
            question,
            primary_result,
            reference_results
        )
    
    def _synthesize_multi_document(self, question, primary, references):
        """
        Combine insights from multiple documents into coherent answer.
        Maintains document attribution and identifies gaps/conflicts.
        """
        synthesis_prompt = f"""
        Question: {question}
        
        PRIMARY DOCUMENT findings:
        {primary.answer}
        
        REFERENCE DOCUMENT findings:
        {[ref.answer for ref in references]}
        
        Synthesize a comprehensive answer that:
        1. Identifies what primary document establishes
        2. Shows how reference documents relate/implement
        3. Highlights gaps, conflicts, or ambiguities
        4. Maintains clear attribution to each document
        """
        # Use Ollama to synthesize
        return ollama_synthesize(synthesis_prompt)
```

**Advantages:**
✅ Native multi-document support  
✅ Maintains document attribution automatically  
✅ Single command invocation  
✅ Reusable for future investigations

**Disadvantages:**
⚠️ Requires significant code changes  
⚠️ Complex synthesis logic needed  
⚠️ Testing multi-document interactions  
⚠️ Potential token limit issues with many references

**Use Case:** Long-term system capability, frequent cross-document analysis

---

### Option 4: Structured Comparison Mode 📊 **RECOMMENDED LONG-TERM**

**Concept:** Add dedicated comparison analysis mode with specialized output format.

**Proposed CLI Interface:**

```bash
python sparrow_grader_v8.py undrip.txt \
  --compare-with bill_c15.txt \
  --comparison-type implementation \
  --focus-sections "Article 28:Section 5,Section 6" \
  --output-format comparison_report
```

**Comparison Types:**

1. **Implementation Analysis**
   - Does Document B adequately implement Document A's requirements?
   - Identifies missing enforcement, vague language, timeline gaps

2. **Consistency Check**
   - Are Document A and B consistent with each other?
   - Flags contradictions, conflicting obligations

3. **Gap Analysis**
   - What's in Document A but missing in Document B?
   - What discretion does Document B introduce?

**Output Format:**

```markdown
# Implementation Analysis Report
## Source: UNDRIP Article 28
## Implementation: Bill C-15 Sections 5-6

### Requirements from Source Document

| Requirement | Strength | Source |
|-------------|----------|--------|
| Right to restitution | Mandatory | Article 28(1) |
| Land-for-land preferred | Strong preference | Article 28(2) |
| Free, prior, informed consent | Required | Article 28(1) |
| Just, fair, equitable compensation | Mandatory | Article 28(1) |

### Implementation Mechanisms in Implementing Document

| Mechanism | Language Strength | Implementation |
|-----------|-------------------|----------------|
| "All measures necessary" | Vague | Section 5 |
| "Ensure consistency" | Weak (not "implement") | Section 5 |
| "In consultation" | Limited (not "consent") | Section 5 |
| Action plan to "achieve objectives" | Aspirational | Section 6 |

### Gap Analysis

#### ⚠️ CRITICAL GAPS IDENTIFIED

1. **No Direct Enforcement Mechanism**
   - UNDRIP: Mandatory right to redress
   - Bill C-15: "Must take measures" but no enforcement if fails
   - **Risk:** No consequences for non-implementation

2. **Semantic Weakening: "Consistency" vs "Implementation"**
   - UNDRIP: Direct rights
   - Bill C-15: Laws must be "consistent with" (not "implement")
   - **Risk:** Can claim consistency while avoiding actual implementation

3. **Consent Downgraded to Consultation**
   - UNDRIP: "Free, prior, informed consent"
   - Bill C-15: "In consultation and cooperation"
   - **Risk:** Government can consult but not require consent

4. **Timeline Delays Built In**
   - UNDRIP: Immediate rights
   - Bill C-15: 2 years to PREPARE action plan (not implement)
   - **Risk:** Indefinite delay of actual land redress

5. **Ministerial Discretion Without Boundaries**
   - Bill C-15: Minister determines "measures necessary"
   - No definition of what constitutes adequate implementation
   - **Risk:** Arbitrary interpretation favoring government interests

### Vague Language Inventory

| Phrase | Location | Concern |
|--------|----------|---------|
| "All measures necessary" | Section 5 | Undefined scope |
| "Ensure consistency" | Section 5 | Not "implement directly" |
| "In consultation" | Section 5, 6 | Not "with consent" |
| "Achieve objectives" | Section 6 | Aspirational, not mandatory |
| "As soon as practicable" | Section 6(4) | No deadline |
| "If the Minister is satisfied" | (hypothetical) | Subjective judgment |

### Recommendations

1. ✓ Use Template Analysis for immediate investigations
2. ✓ Implement Sequential Pipeline for recurring patterns
3. ✓ Develop Comparison Mode for long-term capability
4. ✓ Create Gap Analysis framework for legislative reviews
```

**Technical Implementation:**

```python
# New module: document_comparison.py

class DocumentComparison:
    def __init__(self, source_doc, implementing_doc):
        self.source = DocumentQAEngine(source_doc)
        self.implementing = DocumentQAEngine(implementing_doc)
    
    def analyze_implementation_gaps(self, source_section, impl_sections):
        """
        Compare source requirements against implementation mechanisms.
        Returns structured gap analysis.
        """
        # Extract source requirements
        source_reqs = self.source.query(
            f"List all mandatory requirements in {source_section}"
        )
        
        # Extract implementation mechanisms
        impl_mechs = self.implementing.query(
            f"List all implementation mechanisms in {impl_sections}"
        )
        
        # Identify gaps
        gaps = self._identify_gaps(source_reqs, impl_mechs)
        
        # Analyze vague language
        vague_terms = self._extract_vague_language(impl_mechs)
        
        return ComparisonReport(
            source_requirements=source_reqs,
            implementation_mechanisms=impl_mechs,
            gaps=gaps,
            vague_language=vague_terms,
            risk_assessment=self._assess_risks(gaps, vague_terms)
        )
```

**Advantages:**
✅ Purpose-built for comparative legal analysis  
✅ Structured output format ideal for reports  
✅ Automated gap identification  
✅ Tracks vague/permissive language systematically  
✅ Reusable framework for any document comparison

**Disadvantages:**
⚠️ Significant development effort  
⚠️ Requires sophisticated synthesis logic  
⚠️ Need domain expertise to identify "gaps" accurately  
⚠️ May require iterative refinement

**Use Case:** Professional policy analysis, legislative review, recurring investigations

---

## Implementation Roadmap

### Phase 1: Immediate (This Week) ✅

**Goal:** Enable Bill C-15/UNDRIP investigation to proceed

**Actions:**
1. Create structured analysis templates for each investigation query
2. Document template format for reuse
3. Run initial analyses using template approach
4. Validate output quality

**Deliverables:**
- [ ] Template: Article 28 Implementation Gap Analysis
- [ ] Template: Ministerial Discretion Analysis
- [ ] Template: FPIC vs Consultation Analysis
- [ ] Template: Enforcement Mechanism Analysis
- [ ] Documentation: Template Usage Guide

**Estimated Time:** 1-2 days

---

### Phase 2: Short-Term (Next 2 Weeks) 🔄

**Goal:** Automate sequential analysis pipeline

**Actions:**
1. Create `multi_doc_pipeline.sh` script
2. Add configuration file support for query batching
3. Implement result aggregation utilities
4. Test with full investigation query set (20 queries)

**Deliverables:**
- [ ] Bash script: `multi_doc_pipeline.sh`
- [ ] Config format: `investigation_config.yaml`
- [ ] Utility: `aggregate_results.py`
- [ ] Documentation: Pipeline Usage Guide
- [ ] Test results: All 20 queries from investigation

**Estimated Time:** 1 week

---

### Phase 3: Medium-Term (Next Month) 🔗

**Goal:** Add native multi-document support to Sparrow SPOT

**Actions:**
1. Design `--reference-documents` CLI interface
2. Implement `MultiDocumentQAEngine` class
3. Add cross-document synthesis logic
4. Create attribution tracking system
5. Update narrative generation for multi-doc context
6. Write comprehensive tests

**Deliverables:**
- [ ] Feature: `--reference-documents` argument
- [ ] Module: `enhanced_document_qa.py` multi-doc support
- [ ] Tests: Multi-document query scenarios
- [ ] Documentation: Multi-Document Analysis Guide
- [ ] Examples: Bill C-15/UNDRIP use cases

**Estimated Time:** 2-3 weeks

---

### Phase 4: Long-Term (Next Quarter) 📊

**Goal:** Production-ready comparison analysis system

**Actions:**
1. Implement structured comparison mode
2. Create specialized output formats (comparison reports)
3. Add gap detection algorithms
4. Implement vague language detection
5. Create risk assessment framework
6. Build GUI interface for comparison mode
7. Performance optimization for large documents

**Deliverables:**
- [ ] Feature: `--compare-with` comparison mode
- [ ] Module: `document_comparison.py`
- [ ] Report formats: HTML, Markdown, JSON
- [ ] GUI: Comparison mode interface
- [ ] Documentation: Comparison Analysis Manual
- [ ] Case studies: Legislative review examples

**Estimated Time:** 4-6 weeks

---

## Recommended Approach for Current Investigation

### Immediate Action Plan

**1. Create Analysis Template (Today)**

```bash
# Create template structure
cat > /home/gene/Sparrow-SPOT-Policy/Investigations/Bill-C-15-UNDRIP/templates/article28_gap_analysis.txt << 'EOF'
# [Full structured template content]
EOF
```

**2. Run First Analysis (Today)**

```bash
# Test with Article 28 query
python sparrow_grader_v8.py \
  templates/article28_gap_analysis.txt \
  -o Bill-C15-GapAnalysis-01/analysis \
  --document-title "Article 28 Implementation Gap Analysis" \
  --enable-chunking \
  --ollama-model qwen2.5:7b \
  --document-qa "Based on comparing UNDRIP Article 28 requirements with Bill C-15 implementation mechanisms, what gaps exist in enforcement, timeline, and consent requirements?"
```

**3. Iterate Templates (This Week)**

Create templates for each of the 20 investigation queries:
- Ministerial discretion analysis
- FPIC vs consultation comparison
- Timeline and accountability gaps
- Provincial jurisdiction conflicts
- Enforcement mechanism analysis

**4. Document Process (This Week)**

Create usage guide for future investigations requiring multi-document analysis.

---

## Success Metrics

### Phase 1 Success Criteria
- ✅ Templates generate useful comparative analysis
- ✅ Model correctly identifies document-specific provisions
- ✅ Gap identification is accurate and actionable
- ✅ All 20 investigation queries answered satisfactorily

### Phase 2 Success Criteria
- ✅ Pipeline reduces manual work by 70%
- ✅ Results are reproducible across runs
- ✅ Aggregated reports suitable for publication

### Phase 3 Success Criteria
- ✅ Multi-document queries execute in single command
- ✅ Attribution tracking is accurate
- ✅ Performance acceptable for 2-3 reference documents

### Phase 4 Success Criteria
- ✅ Comparison mode used by external policy analysts
- ✅ Gap detection accuracy >85%
- ✅ System handles complex multi-document scenarios
- ✅ GUI enables non-technical users

---

## Risk Assessment

### Technical Risks

**1. Token Limit Constraints**
- **Risk:** Concatenating multiple documents exceeds model context window
- **Mitigation:** Implement smart chunking that preserves cross-references
- **Status:** Monitor in Phase 2

**2. Synthesis Quality**
- **Risk:** Model struggles to maintain attribution across documents
- **Mitigation:** Explicit prompting, structured output formats
- **Status:** Test in Phase 1 templates

**3. Performance Degradation**
- **Risk:** Multiple document queries slow system significantly
- **Mitigation:** Parallel processing, caching, smart routing
- **Status:** Address in Phase 4

### Operational Risks

**1. Template Maintenance Burden**
- **Risk:** Phase 1 approach requires manual template creation
- **Mitigation:** Document patterns, automate in Phase 2+
- **Status:** Acceptable for immediate needs

**2. Complex Query Formulation**
- **Risk:** Users struggle to formulate effective multi-doc queries
- **Mitigation:** Provide examples, query templates, GUI assistance
- **Status:** Address in Phases 3-4

---

## Conclusion

The Bill C-15/UNDRIP investigation revealed a fundamental limitation in Sparrow SPOT's single-document design. This document proposes a phased approach:

1. **Immediate:** Structured templates enable current investigation
2. **Short-term:** Automation reduces manual overhead
3. **Medium-term:** Native multi-document support enhances capability
4. **Long-term:** Purpose-built comparison mode serves professional analysis

**Recommendation:** Proceed with Phase 1 immediately to unblock current investigation, then evaluate Phase 2+ based on recurring multi-document analysis needs.

---

## References

- Current Investigation: `/Investigations/Bill-C-15-UNDRIP/`
- Query Set: `Queries & Answers on UNDRIP, AFN, and Potential Land Implications.md`
- Sparrow SPOT Core: `sparrow_grader_v8.py`
- Q&A Engine: `enhanced_document_qa.py`
- Troubleshooting Doc: `docs/TROUBLESHOOTING_Q&A_NARRATIVE_GENERATION.md`

---

**Next Steps:**
1. Review this strategy document
2. Approve Phase 1 approach
3. Create first analysis template
4. Run initial Bill C-15/UNDRIP comparative analysis
5. Iterate based on results

**Questions for Decision:**
- [ ] Proceed with Phase 1 structured template approach?
- [ ] Prioritize Phase 2 automation or skip to Phase 3?
- [ ] What comparison output format is most useful for investigation?
- [ ] Should GUI support be prioritized earlier?

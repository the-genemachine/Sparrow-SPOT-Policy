# Transparency & Accountability Remediation TODO List
## Sparrow SPOT v8.6.1 - Address Critique Gaps

**Created:** December 10, 2025  
**Priority:** CRITICAL  
**Status:** READY FOR IMPLEMENTATION  

---

## Phase 1: Template & Immediate Reporting (Current Week)

### TODO 1.1: Update Narrative Template - Evidence Section
**Status:** NOT STARTED  
**Effort:** 2 hours  
**Files to modify:**
- `/home/gene/Sparrow-SPOT-Policy/narrative_engine.py` (find narrative template generation)
- `/home/gene/Sparrow-SPOT-Policy/narrative_integration.py` (narrative pipeline)

**Acceptance Criteria:**
- [ ] Narrative template includes "Evidence Appendix" section
- [ ] Each criterion score includes minimum 2 citations
- [ ] Evidence shown as: `[CRITERION: Score/100] Section X: "quoted text" (instances: N)`
- [ ] Test on Bill-C15-01: Generate narrative and verify evidence section exists
- [ ] Evidence ties scores to actual policy language

**Implementation Notes:**
- Add new section `_generate_evidence_appendix()` to narrative engine
- For each criterion score, query source document for matching phrases
- Track section numbers, quote excerpts, instance counts
- Format as evidence tier: 🟢 STRONG, 🟡 MODERATE, 🔴 WEAK

---

### TODO 1.2: Update Narrative Template - Trust Score Methodology  
**Status:** NOT STARTED  
**Effort:** 2 hours  
**Files to modify:**
- `/home/gene/Sparrow-SPOT-Policy/narrative_engine.py`
- `/home/gene/Sparrow-SPOT-Policy/trust_score_calculator.py` (if exists)

**Acceptance Criteria:**
- [ ] Narrative includes "Trust Score Methodology" section
- [ ] Shows formula: `Trust = (FT × 0.25 + ER × 0.25 + PA × 0.20 + AT × 0.30 + SB × 0.10)`
- [ ] Shows calculation step-by-step: `(53.8 × 0.25) = 13.45`, etc.
- [ ] Shows weighting rationale (why each weight?)
- [ ] Shows final calculation: `13.45 + 12.75 + 15.50 + 19.50 + 7.29 = 68.49 (rounded: 52.4)`
- [ ] Shows interpretation guide: score 0-39=CRITICAL, 40-59=LOW, 60-79=MODERATE, 80-100=HIGH
- [ ] Test: Generate for Bill-C15-01, manually verify calculation matches

**Implementation Notes:**
- Create `trust_score_documentation()` function
- Document weighting factors with policy rationale
- Show detailed calculation breakdown
- Include interpretation guide in template

---

### TODO 1.3: Update Narrative Template - Risk Tier Escalation
**Status:** NOT STARTED  
**Effort:** 3 hours  
**Files to modify:**
- `/home/gene/Sparrow-SPOT-Policy/sparrow_grader_v8.py` (risk tier calculation)
- `/home/gene/Sparrow-SPOT-Policy/narrative_engine.py` (risk explanation)

**Acceptance Criteria:**
- [ ] Risk tier calculation includes escalation rules:
  - Base tier from composite score
  - Escalate 1 tier if ANY criterion < 50
  - Escalate 2 tiers if ER < 50 (viability threat)
  - Escalate 1 tier if 3+ criteria < 65 (systemic issue)
- [ ] For Bill-C15-01: FT=53.8 escalates LOW tier to MODERATE; ER=51 escalates MEDIUM to HIGH; ER<50 should escalate to CRITICAL
- [ ] Narrative includes "Risk Tier Justification" explaining which rules triggered
- [ ] Example: "Risk tier escalated from MEDIUM to CRITICAL because Economic Rigor (51/100) falls below 50, indicating viability concerns"
- [ ] Test: Verify escalation logic with sample scores

**Implementation Notes:**
- Rewrite `calculate_risk_tier()` function in sparrow_grader_v8.py
- Implement explicit escalation rules with comments
- Track which rules triggered for explanation
- Return both tier and escalation explanation
- Update narrative template to include explanation

---

### TODO 1.4: Update Narrative Template - Document Verification
**Status:** NOT STARTED  
**Effort:** 1.5 hours  
**Files to modify:**
- `/home/gene/Sparrow-SPOT-Policy/narrative_engine.py`
- `/home/gene/Sparrow-SPOT-Policy/sparrow_grader_v8.py` (document metadata)

**Acceptance Criteria:**
- [ ] Narrative starts with "Document Verification & Scope" section
- [ ] Shows document filename, size, character count, format
- [ ] Lists detected major sections/divisions
- [ ] States this is Bill C-15 specific analysis, NOT template
- [ ] For Bill-C15-01: Lists "Part 5: High-Speed Rail", "Consumer Banking Act", etc.
- [ ] Includes MD5 hash for document verification
- [ ] Test: Generate for Bill-C15-01, verify document details are specific

**Implementation Notes:**
- Extract document metadata during initial load
- Detect structure (divisions, parts, sections)
- Calculate MD5 hash for verification
- Include in narrative metadata section
- Reference in introduction

---

### TODO 1.5: Update Narrative Template - Analysis Limitations
**Status:** NOT STARTED  
**Effort:** 1 hour  
**Files to modify:**
- `/home/gene/Sparrow-SPOT-Policy/narrative_engine.py`

**Acceptance Criteria:**
- [ ] Narrative includes "Analysis Limitations & Disclaimer" section
- [ ] Lists 5+ framework limitations (captures 6 criteria, not all factors; assessor-dependent, etc.)
- [ ] Explicitly states: "AI involvement (X%) means some portions are machine-generated"
- [ ] Recommends: "Independent expert review is recommended"
- [ ] Lists external sources for verification
- [ ] Tone is neutral, not promotional
- [ ] Test: Review for any marketing language or tool promotion

**Implementation Notes:**
- Create standardized limitations section
- Keep tone neutral and objective
- Emphasis on tool being ONE INPUT, not final word
- Include independent verification recommendations

---

### TODO 1.6: Update Narrative Template - Independent Verification
**Status:** NOT STARTED  
**Effort:** 1 hour  
**Files to modify:**
- `/home/gene/Sparrow-SPOT-Policy/narrative_engine.py`

**Acceptance Criteria:**
- [ ] Narrative includes "How to Verify This Analysis" section
- [ ] Links to official source documents (Parliament, Finance Canada)
- [ ] Explains how to verify scores using policy text
- [ ] Recommends third-party AI detection tools
- [ ] Recommends expert review process
- [ ] Provides contact/feedback mechanism
- [ ] Test: All links work, guidance is clear

**Implementation Notes:**
- Create verification methodology section
- Include verified URLs for official sources
- Step-by-step verification instructions
- Encourage external validation

---

### TODO 1.7: Regenerate Bill-C15-01 Narrative with All Updates
**Status:** NOT STARTED  
**Effort:** 1 hour  
**Files affected:**
- `/home/gene/Sparrow-SPOT-Policy/Investigations/Bill-C-15/Bill-C15-01/narrative/Bill-C15-01_publish.md`

**Acceptance Criteria:**
- [ ] Run sparrow_grader_v8.py with Bill-C15-01 source document
- [ ] Verify all 6 new sections are present:
  1. Document Verification & Scope
  2. Evidence Appendix
  3. Trust Score Methodology
  4. Risk Tier Justification
  5. AI Contribution Transparency
  6. Analysis Limitations & Disclaimer
  7. Independent Verification guidance
- [ ] Verify all scores have citations
- [ ] Verify Trust Score calculation shown
- [ ] Verify risk tier escalation explained
- [ ] Verify no generic "Economic Revitalization Strategy" language (should say Bill C-15)
- [ ] Verify analysis limitations section present
- [ ] Manual check: Does it address all 6 critique points?

**Implementation Notes:**
- Re-run analysis with updated templates
- Verify output contains all sections
- Cross-reference against critique to ensure all points addressed

---

## Phase 2: Code Implementation (Next 2 weeks)

### TODO 2.1: Implement Evidence Citation Module
**Status:** NOT STARTED  
**Effort:** 4 hours  
**Files to modify/create:**
- Create: `/home/gene/Sparrow-SPOT-Policy/evidence_citation_module.py`
- Modify: `/home/gene/Sparrow-SPOT-Policy/sparrow_grader_v8.py`

**Requirements:**
- [ ] Create `EvidenceCitation` class with fields:
  - criterion (string)
  - section_number (string)
  - quote_text (string)
  - instance_count (int)
  - evidence_tier (STRONG/MODERATE/WEAK)
- [ ] Implement `extract_evidence()` function:
  - Takes score, criterion, source document
  - Searches for relevant policy language
  - Returns list of evidence citations
  - Assigns evidence tier based on relevance
- [ ] Integrate into scoring pipeline
- [ ] Test with Bill C-15 sample sections

**Acceptance Criteria:**
- [ ] Evidence module finds 2+ citations per criterion
- [ ] Citations are directly from source document
- [ ] Evidence tiers assigned logically
- [ ] Can be called during narrative generation
- [ ] Tested with Bill-C15-01 scores

---

### TODO 2.2: Implement Trust Score Calculation Module
**Status:** NOT STARTED  
**Effort:** 2 hours  
**Files to modify/create:**
- Modify: `/home/gene/Sparrow-SPOT-Policy/trust_score_calculator.py` (or create if doesn't exist)

**Requirements:**
- [ ] Function `calculate_trust_score(criteria_dict)`:
  - Input: {FT: 53.8, ER: 51.0, PA: 77.5, SB: 72.9, PC: 89.3, AT: 65.0}
  - Calculate with weights: FT×0.25, ER×0.25, PA×0.20, AT×0.30, SB×0.10
  - Return: (raw_score, rounded_score, interpretation)
- [ ] Function `document_calculation()`:
  - Returns formatted string showing step-by-step calculation
  - Includes weighting rationale
- [ ] Function `interpret_trust_score(score)`:
  - Returns interpretation: "CRITICAL (0-39)", "LOW (40-59)", "MODERATE (60-79)", "HIGH (80-100)"
  - Includes explanation of what score means for stakeholders

**Acceptance Criteria:**
- [ ] For Bill-C15-01 criteria, calculates to 52.4 (or documented alternative)
- [ ] Calculation documentation shows all steps
- [ ] Weighting rationale is documented
- [ ] Interpretation is clear and actionable
- [ ] Unit tests pass with sample data

---

### TODO 2.3: Implement Risk Tier Escalation Logic
**Status:** NOT STARTED  
**Effort:** 3 hours  
**Files to modify:**
- `/home/gene/Sparrow-SPOT-Policy/sparrow_grader_v8.py`

**Requirements:**
- [ ] Rewrite `calculate_risk_tier()` function:
  ```python
  def calculate_risk_tier(composite_score, criteria_dict):
      # Step 1: Base tier from composite
      base_tier = get_base_tier(composite_score)
      escalations = []
      
      # Step 2: Check critical criteria
      if criteria_dict['FT'] < 50:
          escalations.append(('FT_critical', 1, 'Fiscal Transparency below 50'))
      if criteria_dict['ER'] < 50:
          escalations.append(('ER_critical', 2, 'Economic Rigor below 50 - viability threat'))
      if criteria_dict['PC'] < 60:
          escalations.append(('PC_below_60', 1, 'Policy Consequentiality below 60'))
      
      # Step 3: Check consistency
      below_65 = sum(1 for score in criteria_dict.values() if score < 65)
      if below_65 >= 3:
          escalations.append(('consistency', 1, 'Systemic issues - 3+ criteria below 65'))
      
      # Step 4: Apply escalations
      final_tier = escalate_tier(base_tier, escalations)
      
      return final_tier, escalations
  ```
- [ ] Document escalation rules in code comments
- [ ] Return tuple: (tier, escalation_list) for explanation in narrative
- [ ] Test with Bill-C15-01: Should escalate to CRITICAL due to ER=51

**Acceptance Criteria:**
- [ ] Bill-C15-01 escalates from MEDIUM (67.4 composite) to CRITICAL (ER<50)
- [ ] Escalation explanation shows which rules triggered
- [ ] Unit tests cover all escalation scenarios
- [ ] Code is well-commented with rule justifications

---

### TODO 2.4: Implement Document Verification Module
**Status:** NOT STARTED  
**Effort:** 2 hours  
**Files to modify/create:**
- Create: `/home/gene/Sparrow-SPOT-Policy/document_verification_module.py`
- Modify: `/home/gene/Sparrow-SPOT-Policy/sparrow_grader_v8.py`

**Requirements:**
- [ ] Function `extract_document_metadata(doc_text, filename)`:
  - Calculate file size, character count
  - Calculate MD5 hash
  - Detect major divisions/parts/sections
  - Return metadata dict
- [ ] Function `detect_document_structure(doc_text)`:
  - Identify all major divisions
  - Return list of: {division_number, division_name, section_count}
  - For Bill C-15: Should find "Part 5", "High-Speed Rail Network Act", etc.
- [ ] Function `format_document_verification_section()`:
  - Returns formatted markdown section for narrative

**Acceptance Criteria:**
- [ ] Bill-C15-01 analysis shows document is Bill C-15, not generic template
- [ ] Shows detected divisions specific to Bill C-15
- [ ] MD5 hash can be used for verification
- [ ] Section detection accurate

---

### TODO 2.5: Implement AI Contribution Tracking at Component Level
**Status:** NOT STARTED  
**Effort:** 4 hours  
**Files to modify:**
- `/home/gene/Sparrow-SPOT-Policy/narrative_integration.py`
- `/home/gene/Sparrow-SPOT-Policy/narrative_engine.py`
- Create: `/home/gene/Sparrow-SPOT-Policy/ai_contribution_tracker_detailed.py`

**Requirements:**
- [ ] Modify generation to track:
  - Component name (e.g., "Scoring Rationale")
  - Generation method (100% AI, hybrid, 100% human)
  - Model used (if AI)
  - Word count
  - Human reviewer name/date
  - Edit notes
- [ ] Store as JSON with component-level granularity
- [ ] Create function to format as detailed breakdown for narrative
- [ ] Calculate aggregate AI% from component contributions

**Acceptance Criteria:**
- [ ] Each major section tracked separately
- [ ] Generation method clearly labeled
- [ ] Human reviewers identified
- [ ] Total AI% calculated from components
- [ ] Can be included in narrative transparency section

---

## Phase 3: Testing & Validation (Weeks 3-4)

### TODO 3.1: Unit Test Evidence Citation Module
**Status:** NOT STARTED  
**Effort:** 2 hours  
**File:** `/home/gene/Sparrow-SPOT-Policy/tests/test_evidence_citation.py`

**Acceptance Criteria:**
- [ ] Test finds citations for each criterion
- [ ] Test verifies citations are from source document
- [ ] Test checks evidence tier assignment logic
- [ ] Test with Bill C-15 excerpt passes
- [ ] Minimum 85% passing tests

---

### TODO 3.2: Unit Test Trust Score Calculation
**Status:** NOT STARTED  
**Effort:** 1 hour  
**File:** `/home/gene/Sparrow-SPOT-Policy/tests/test_trust_score.py`

**Acceptance Criteria:**
- [ ] Test calculates known sample correctly
- [ ] Test for Bill-C15-01 scores returns correct value
- [ ] Test interprets scores correctly
- [ ] Test documents calculation steps
- [ ] 100% passing tests

---

### TODO 3.3: Unit Test Risk Tier Escalation
**Status:** NOT STARTED  
**Effort:** 2 hours  
**File:** `/home/gene/Sparrow-SPOT-Policy/tests/test_risk_escalation.py`

**Acceptance Criteria:**
- [ ] Test base tiers assigned correctly
- [ ] Test escalations triggered correctly
- [ ] Test Bill-C15-01 escalates to CRITICAL
- [ ] Test multiple escalation scenarios
- [ ] 100% passing tests

---

### TODO 3.4: Integration Test - Full Narrative Generation
**Status:** NOT STARTED  
**Effort:** 3 hours  
**File:** `/home/gene/Sparrow-SPOT-Policy/tests/test_full_narrative_generation.py`

**Acceptance Criteria:**
- [ ] Generate full narrative with all new sections
- [ ] Verify all 7 sections present:
  1. Document Verification
  2. Evidence Appendix
  3. Trust Score Methodology
  4. Risk Tier Justification
  5. AI Contribution Breakdown
  6. Analysis Limitations
  7. Independent Verification
- [ ] Verify no promotional language
- [ ] Verify evidence citations present
- [ ] Verify calculations correct
- [ ] Manual review by policy analyst

---

### TODO 3.5: Validate Against Original Critique
**Status:** NOT STARTED  
**Effort:** 2 hours

**Process:**
1. Generate updated Bill-C15-01 narrative with all changes
2. Re-read original critique (Examination of the Sparrow SPOT Narrative Analysis Report.md)
3. Check each of 6 critique points:
   - ✅ Specificity & evidence ties - Do citations provide evidence?
   - ✅ Trust score undefined - Is methodology documented?
   - ✅ Risk tier inconsistent - Is escalation explained?
   - ✅ AI attribution opaque - Is breakdown clear?
   - ✅ Document mismatch - Is it specific to Bill C-15?
   - ✅ Promotional undertones - Is tone neutral?
4. Document response to each critique point
5. Create verification checklist

**Acceptance Criteria:**
- [ ] All 6 critique points explicitly addressed
- [ ] New narrative is demonstrably different/improved
- [ ] Evidence of improvements documented
- [ ] Ready for external review

---

### TODO 3.6: External Review & Feedback
**Status:** NOT STARTED  
**Effort:** Depends on reviewer availability

**Process:**
1. Share updated narrative with:
   - Independent policy analyst (for content)
   - Academic researcher (for methodology)
   - Privacy/transparency advocate (for disclosure)
2. Collect feedback on:
   - Clarity of evidence citations
   - Trust score documentation
   - Risk tier justification
   - AI/human attribution
   - Document specificity
   - Analysis limitations
3. Iterate based on feedback
4. Document all feedback and responses

**Acceptance Criteria:**
- [ ] External reviewers confirm improvement
- [ ] All major concerns addressed
- [ ] Feedback incorporated or documented with rationale
- [ ] Ready for publication

---

## Phase 4: Rollout & Documentation (Month 2+)

### TODO 4.1: Update All Existing Bill C-15 Analyses
**Status:** NOT STARTED  
**Effort:** 4 hours per analysis

**Affected files:**
- Bill-C15-00 analysis
- Bill-C15-01 analysis
- Any other Bill C-15 variants

**Process:**
1. Re-run sparrow_grader with updated templates
2. Regenerate all output files
3. Update publications
4. Archive old versions

**Acceptance Criteria:**
- [ ] All existing analyses updated
- [ ] Old versions archived for reference
- [ ] Publication sites updated

---

### TODO 4.2: Create Methodology Documentation
**Status:** NOT STARTED  
**Effort:** 4 hours

**Create document:** `/home/gene/Sparrow-SPOT-Policy/docs/METHODOLOGY_TRANSPARENCY.md`

**Content:**
- Evidence citation methodology
- Trust score calculation with weighting rationale
- Risk tier escalation rules
- AI detection and contribution tracking
- Human review process
- Verification and reproducibility standards

**Acceptance Criteria:**
- [ ] Complete methodology documented
- [ ] Available for external peer review
- [ ] Published on public site

---

### TODO 4.3: Create Analyst Training Guide
**Status:** NOT STARTED  
**Effort:** 3 hours

**Create document:** `/home/gene/Sparrow-SPOT-Policy/docs/ANALYST_TRANSPARENCY_GUIDE.md`

**Content:**
- How to interpret evidence tiers
- How to document human contributions
- How to maintain citations
- How to explain risk escalations
- Quality assurance checklist

**Acceptance Criteria:**
- [ ] Clear guidance for analysts
- [ ] Training materials ready
- [ ] All analysts trained and signed off

---

### TODO 4.4: Publish Methodology for Peer Review
**Status:** NOT STARTED  
**Effort:** 2 hours

**Process:**
1. Prepare methodology document for publication
2. Submit to relevant policy analysis forums
3. Request peer feedback
4. Incorporate feedback (or document rationale for rejection)

**Acceptance Criteria:**
- [ ] Methodology publicly available
- [ ] Open to external critique
- [ ] Feedback mechanism in place

---

## 📊 Progress Tracking

### Phase 1 (Current Week): Template & Immediate Reporting
- [ ] 1.1 Evidence section added
- [ ] 1.2 Trust score methodology added
- [ ] 1.3 Risk tier justification added
- [ ] 1.4 Document verification added
- [ ] 1.5 Analysis limitations added
- [ ] 1.6 Verification guidance added
- [ ] 1.7 Bill-C15-01 regenerated with all sections

**Phase 1 Progress: 0/7 complete**

### Phase 2 (Weeks 3-4): Code Implementation
- [ ] 2.1 Evidence citation module
- [ ] 2.2 Trust score calculation module
- [ ] 2.3 Risk tier escalation logic
- [ ] 2.4 Document verification module
- [ ] 2.5 AI contribution tracking (detailed)

**Phase 2 Progress: 0/5 complete**

### Phase 3 (Weeks 5-6): Testing & Validation
- [ ] 3.1 Evidence citation tests
- [ ] 3.2 Trust score tests
- [ ] 3.3 Risk tier escalation tests
- [ ] 3.4 Integration tests
- [ ] 3.5 Critique validation
- [ ] 3.6 External review

**Phase 3 Progress: 0/6 complete**

### Phase 4 (Month 2+): Rollout
- [ ] 4.1 Update existing analyses
- [ ] 4.2 Methodology documentation
- [ ] 4.3 Analyst training
- [ ] 4.4 Peer review publication

**Phase 4 Progress: 0/4 complete**

---

## 🎯 Success Metrics

### By End of Phase 1:
- All 7 template sections added to narrative generation
- Bill-C15-01 narrative includes all transparency sections
- External reviewer confirms improvement against critique

### By End of Phase 2:
- All 5 code modules implemented and integrated
- Unit tests at 85%+ pass rate
- Integration tests successful

### By End of Phase 3:
- Full narrative generation with all sections tested
- All 6 critique points explicitly addressed
- External reviewers confirm substantial improvement

### By End of Phase 4:
- Methodology available for peer review
- Analysts trained on new processes
- Public confidence in Sparrow SPOT transparency established

---

## 🚀 Start Action

**First task:** TODO 1.1 - Update narrative template with evidence section

**Expected completion:** By end of today

**Next step:** Re-generate Bill-C15-01 narrative and verify against critique points

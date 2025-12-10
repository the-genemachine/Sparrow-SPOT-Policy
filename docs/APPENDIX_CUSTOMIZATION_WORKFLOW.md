# Appendix Customization Workflow

**Purpose:** Guide for filling in actual Bill C-15 data into appendix templates  
**Effort:** 4-6 hours (1 developer)  
**Result:** Production-ready appendices for Bill-C15-01 analysis  

---

## Pre-Work Checklist

Before starting customization:

```
[ ] Access to Bill-C15-01.json (analysis metadata)
[ ] Access to Bill-C15-01_deep_analysis.md (findings)
[ ] Access to Bill-C15-01_publish.md (current narrative)
[ ] Bill C-15 official text (Parliament.ca)
[ ] Actual scores and evidence from analysis
[ ] Human review records (if available)
[ ] AI detection results (if available)
```

**Files needed:**
- `/Investigations/Bill-C-15/Bill-C15-01/core/Bill-C15-01.json`
- `/Investigations/Bill-C-15/Bill-C15-01/core/Bill-C15-01.txt` (summary)
- `/Investigations/Bill-C-15/Bill-C15-01/reports/Bill-C15-01_deep_analysis.md`
- `/Investigations/Bill-C-15/Bill-C15-01/narrative/Bill-C15-01_publish.md`

---

## Step 1: Customize APPENDIX A (Evidence Citations)

**File:** `/appendices/evidence/EVIDENCE_APPENDIX_TEMPLATE.md`  
**Effort:** 90 minutes  
**Task:** Replace template placeholders with actual Bill C-15 evidence

### 1.1: Add Document Specifications

**Find in template:** Document specifications section (top)

**Replace these placeholders:**
```markdown
BEFORE:
- **Total Word Count:** 196,742 words
- **Total Sections:** [X] major sections across [Y] divisions

AFTER:
- **Total Word Count:** 196,742 words (from Bill-C15-01.json)
- **Total Sections:** [Extract from bill text]
- **Major Divisions:** [List from bill text]
```

**Source:** Check Bill-C15-01.json for document metadata

### 1.2: Fill in Criterion 1 Evidence (Fiscal Transparency - 53.8)

**From:** Bill-C15-01.json and deep_analysis.md

**Find evidence for:**
- Explicit financial disclosures
- Cost-benefit analysis gaps
- Discretionary funding allocation

**For each evidence piece, add:**
```markdown
#### Evidence Section Title
**Evidence Tier:** 🟢 STRONG (Multiple direct citations)

**Section References:**
- **[Bill Section], Section [#]:** "[Actual quote from Bill C-15]"
  - Instances Found: [Number]
  - Impact: [Analysis of impact]
```

**Sources to check:**
- Bill-C15-01_deep_analysis.md for analysis findings
- Bill C-15 official text for exact quotes

### 1.3: Repeat for Remaining Criteria

**Repeat steps 1.1-1.2 for:**
- Criterion 2: Economic Rigor (51.0/100)
- Criterion 3: Policy Consequentiality (89.3/100)
- Criterion 4: Stakeholder Balance (72.9/100)
- Criterion 5: Accessibility & Transparency (65.0/100)

**Where to find evidence:**
- Deep analysis report shows findings for each criterion
- Bill C-15 text provides specific sections to cite

### 1.4: Update Summary Section

**Replace:**
```
## Summary by Evidence Strength

### STRONG Evidence (🟢)
- [List actual strong evidence found]

### MODERATE Evidence (🟡)
- [List actual moderate evidence found]

### WEAK Evidence (🔴)
- [List actual weak evidence found]
```

**Count from your customization above**

---

## Step 2: Customize APPENDIX B (Methodology)

**File:** `/appendices/methodology/METHODOLOGY_APPENDIX_TEMPLATE.md`  
**Effort:** 60 minutes  
**Task:** Update with actual scores and weighting used

### 2.1: Update Criterion Scores

**Find:** Section "2. Six Evaluation Criteria"

**Replace placeholders:**
```markdown
**Bill C-15-01 Score: 53.8/100** ← This actual score for FT
**Bill C-15-01 Score: 51.0/100** ← This actual score for ER
**Bill C-15-01 Score: 89.3/100** ← This actual score for PC
**Bill C-15-01 Score: 72.9/100** ← This actual score for SB
**Bill C-15-01 Score: 65.0/100** ← This actual score for AT
```

**Source:** Bill-C15-01.json

### 2.2: Update Trust Score Calculation

**Find:** Section "4. Trust Score Calculation"

**Update formula with actual weighting:**
```markdown
Bill C-15-01 Calculation

TRUST SCORE = (FT × W_FT) + (ER × W_ER) + (PA × W_PA) + (AT × W_AT) + (SB × W_SB)
            = (53.8 × [?]) + (51.0 × [?]) + (77.5 × [?]) + (65.0 × [?]) + (72.9 × [?])
            = [Calculate actual result]
```

**Where to find:** 
- Weighting should be in Bill-C15-01.json or previous analysis docs
- Or determine from narrative if it states trust score methodology

### 2.3: Update Risk Tier Example

**Find:** Section "5. Risk Tier Assignment"

**Update Bill C-15-01 example:**
```markdown
Step 1: Composite Score = 67.4/100 → BASE TIER = MEDIUM

Step 2: Escalation Checks
  FT (53.8) < 50? [YES/NO]
  ER (51.0) < 50? [YES/NO]
  Criteria < 65: [List which ones]

FINAL RISK TIER: [CRITICAL/HIGH/MEDIUM/LOW]
Reason: [Actual escalation reasoning]
```

**Source:** Verify from analysis data

### 2.4: Add Confidence Intervals

**Find:** Section "Confidence Intervals"

**Update with actual confidence assessments:**
```markdown
**Bill C-15-01 Confidence:**
- FT: 53.8 ± [?] (HIGH/MODERATE/LOW)
- ER: 51.0 ± [?]
- PC: 89.3 ± [?]
- SB: 72.9 ± [?]
- AT: 65.0 ± [?]
```

---

## Step 3: Customize APPENDIX C (Component Disclosure)

**File:** `/appendices/disclosure/COMPONENT_DISCLOSURE_TEMPLATE.md`  
**Effort:** 90 minutes  
**Task:** Document actual AI vs. human involvement in Bill-C15-01 analysis

### 3.1: Update Generation Breakdown

**Find:** Section "Component Generation Breakdown"

**For each narrative section, replace:**
```markdown
### Narrative Section [N]: [Title]

| Aspect | Value |
|--------|-------|
| **Primary Generation Method** | [100% Human / X% Human, Y% AI / 100% AI] |
| **AI Involvement** | [None / Initial draft / Expansion / etc.] |
| **Author** | [Names of actual authors] |
| **Human Review** | [Who reviewed, role] |
| **Confidence Level** | [HIGH/MODERATE/LOW] |

**Generation Process:**
[Actual process used]
```

**Sources:**
- Project logs showing AI tool usage
- Analyst names from Bill-C15-01 project records
- Human review records if available

### 3.2: Update Overall Statistics

**Find:** Section "Summary Statistics"

**Replace table with actual percentages:**
```markdown
| Component | Human % | AI % | Confidence |
|-----------|---------|------|-----------|
| [Section name] | [?]% | [?]% | [?] |
| TOTAL NARRATIVE | [?]% | [?]% | [?] |
```

**Calculation:** 
- Count actual human vs AI usage from component breakdown
- Confidence based on: How certain are we of these percentages?

### 3.3: Add AI Model Details

**Find:** Section "AI Model Details"

**If AI was used, document:**
```markdown
**Models Used:**
- [Model name] (e.g., Ollama mistral:7b)
  - Used for: [Specific sections]
  - Parameters: [temperature, num_predict, etc.]
  - Instances: [How many times used]
```

**Source:** Check project logs or tool configuration

### 3.4: Add Human Review Audit Trail

**Find:** Section "Human Review Audit Trail"

**Replace with actual:**
```markdown
### Reviewers & Hours

| Role | Hours | Focus |
|------|-------|-------|
| [Actual role] | [Hours] | [What they reviewed] |

### Review Notes Summary

[Actual review findings]
```

---

## Step 4: Customize APPENDIX D (Bill Findings)

**File:** `/appendices/findings/BILL_FINDINGS_TEMPLATE.md`  
**Effort:** 120 minutes  
**Task:** Add actual Bill C-15-specific findings

### 4.1: Update Document Specifications

**Find:** Section "Bill C-15 Document Specifications"

**Add actual:**
```markdown
### Division 1: [Actual Division Title]
- Sections: [X-Y]
- Policy focus: [Actual description]
- Word count: [Actual count]
```

**Source:** Bill-C15-01.json and bill text

### 4.2: Add Major Findings

**Find:** Section "Provision-Level Analysis"

**For each major finding discovered in analysis:**

**Example structure:**
```markdown
### MAJOR FINDING #[N]: [Title]

**Scope:** [What this covers]

**Key Discovery:**
[One-sentence core finding]

#### Analysis of [Sub-topic]

**Evidence Tier:** [STRONG/MODERATE/WEAK]

**Section References:**
[Specific Bill sections supporting finding]

**Impact Assessment:**
[How this affects policy viability]

**Remediation Needs:**
[What should be fixed]
```

**Sources:**
- Bill-C15-01_deep_analysis.md
- Bill-C15-01_publish.md narrative findings
- Deep analysis report findings

### 4.3: Update Stakeholder Impact Matrix

**Find:** Section "Stakeholder Impact Matrix"

**Fill in actual stakeholders:**
```markdown
| Stakeholder | Provision(s) Affected | Impact Type | Magnitude |
|---|---|---|---|
| [Actual group] | [Which provisions] | [Positive/Negative/Mixed] | [MAJOR/MODERATE/MINOR] |
```

**Sources:**
- Deep analysis stakeholder assessment
- Bill C-15 analysis for affected groups

---

## Step 5: Customize APPENDIX E (Verification)

**File:** `/appendices/verification/VERIFICATION_GUIDE_TEMPLATE.md`  
**Effort:** 30 minutes  
**Task:** Add analysis-specific resources and contacts

### 5.1: Update Resources Section

**Find:** Section "Resources for Verification"

**Add actual:**
```markdown
**Bill C-15 Sources:**
- Official Bill: [Actual Parliament.ca URL]
- Debate Records: [Actual Hansard link]
- Committee Analysis: [If available]

**Think Tanks:**
- [Actual organization name]: [URL and contact]

**Government Analysis:**
- Finance Canada: [Actual analysis if published]
```

### 5.2: Update Contact Information

**Find:** Section "Contact & Feedback"

**Replace with actual:**
```markdown
**For verification questions:**
- Name: [Analyst name]
- Email: [Email address]
- Role: [Title]
- Expertise: [Relevant background]
```

---

## Step 6: Update INDEX.md

**File:** `/appendices/INDEX.md`  
**Effort:** 15 minutes  
**Task:** Verify all cross-references work

### 6.1: Check all file paths
```
[ ] evidence/EVIDENCE_APPENDIX_TEMPLATE.md exists
[ ] methodology/METHODOLOGY_APPENDIX_TEMPLATE.md exists  
[ ] disclosure/COMPONENT_DISCLOSURE_TEMPLATE.md exists
[ ] findings/BILL_FINDINGS_TEMPLATE.md exists
[ ] verification/VERIFICATION_GUIDE_TEMPLATE.md exists
```

### 6.2: Verify cross-references
```
[ ] Appendix A references Methodology B correctly
[ ] Appendix B references Evidence A correctly
[ ] Appendix D references Findings correctly
[ ] Appendix E references all others correctly
```

---

## Step 7: Create Main Narrative Link Document

**New file:** `/APPENDICES_NARRATIVE_INTEGRATION.md`

**Purpose:** Show how to integrate appendix references into main narrative

**Content example:**
```markdown
# How to Link Main Narrative to Appendices

## In Criterion Section

### BEFORE (current)
```
Fiscal Transparency: 53.8/100
This score reflects...
```

### AFTER (with appendix links)
```
## Fiscal Transparency: 53.8/100

This score reflects the degree to which Bill C-15's financial mechanisms 
are clearly disclosed and accounted for.

**See:**
- Appendix A (Evidence Citations) for specific Bill C-15 sections supporting this score
- Appendix B (Methodology) for how this score was calculated
- Appendix D (Bill Findings) for major fiscal transparency issues identified

**Score calculation:**
[FT score components from Appendix B]

**Key evidence:**
- [Top 3 evidence points from Appendix A]

**Major concerns:**
- [Top 2 findings from Appendix D]
```

---

## Quality Checklist

Before considering customization complete:

```
APPENDIX A (Evidence):
[ ] All 5 criteria have evidence citations
[ ] Each citation includes specific Bill section
[ ] Evidence strength tiers assigned (STRONG/MODERATE/WEAK)
[ ] Evidence count matches summary section
[ ] No [PLACEHOLDER] text remaining

APPENDIX B (Methodology):
[ ] All actual scores filled in (FT=53.8, ER=51.0, etc.)
[ ] Trust Score formula filled with actual weighting
[ ] Risk Tier example worked through for Bill C-15-01
[ ] Confidence intervals assigned to each score
[ ] No [?] placeholders remaining

APPENDIX C (Disclosure):
[ ] AI/human percentages filled for each section
[ ] Total AI/human percentages calculated correctly
[ ] Human reviewers and hours documented
[ ] AI models and parameters documented
[ ] No [?] or [TBD] remaining

APPENDIX D (Findings):
[ ] Document specifications filled (word count, divisions)
[ ] 4-6 major findings documented
[ ] Each finding has Evidence Tier, sections, impact
[ ] Stakeholder impact matrix complete
[ ] Recommendation section filled with Bill-specific recs

APPENDIX E (Verification):
[ ] Bill C-15 specific resources added
[ ] Contact information filled
[ ] All step examples walkthrough Bill C-15-01
[ ] Resources section links valid

INDEX.md:
[ ] All cross-references checked
[ ] No broken links
[ ] Navigation working
```

---

## Estimated Timeline

```
Task                              | Duration | Cumulative
----------------------------------+----------+----------
1. APPENDIX A (Evidence)          | 90 min   | 90 min (1.5 hrs)
2. APPENDIX B (Methodology)       | 60 min   | 150 min (2.5 hrs)
3. APPENDIX C (Disclosure)        | 90 min   | 240 min (4 hrs)
4. APPENDIX D (Findings)          | 120 min  | 360 min (6 hrs)
5. APPENDIX E (Verification)      | 30 min   | 390 min (6.5 hrs)
6. INDEX.md validation            | 15 min   | 405 min (6.75 hrs)
7. Quality checklist & fixes      | 30 min   | 435 min (7.25 hrs)
----------------------------------+----------+----------
TOTAL                             |          | ~7 hours
```

**Reality:** Likely 5-6 hours (assumes data is accessible and organized)

---

## Tips for Success

### TIP #1: Use "Find & Replace"
Many placeholders are repeated. Use editor find/replace:
- Find: `[?]` Replace with: actual value
- Find: `{PLACEHOLDER}` Replace with: actual data

### TIP #2: Cross-Reference While Working
As you fill in Appendix A (Evidence), note:
- Which findings are STRONG vs WEAK
- Which require methodology explanation
- Which need Bill-specific examples

This informs Appendices B, D, E.

### TIP #3: Save Frequently
These are large files. Save after each appendix completed.

### TIP #4: Validate as You Go
After each appendix, do 5-minute validation:
- Check for [PLACEHOLDER] text
- Verify numbers match between appendices
- Make sure cross-references work

### TIP #5: Have Data Sources Ready
Before starting, organize:
- Bill-C15-01.json open in one window
- Bill-C15-01_deep_analysis.md in another
- Bill-C15-01_publish.md in third window
- Bill C-15 text available for lookup

---

## After Customization: Next Steps

Once appendices are customized:

1. **Validate** - Run through quality checklist
2. **Review** - Have someone else review for accuracy
3. **Integrate** - Add appendix links to main narrative
4. **Test** - Verify all cross-references work
5. **Publish** - Release complete analysis package
6. **Distribute** - Share with original critique authors

---

## Help & Troubleshooting

**Q: Where do I find the actual scores?**  
A: Check Bill-C15-01.json for analysis metadata, or Bill-C15-01.txt for summary

**Q: What if I don't have human review records?**  
A: Document "Review process not formally documented" - still valuable for transparency

**Q: Should I add all this detail?**  
A: Yes - this is the point: full transparency enables verification

**Q: Can I automate this?**  
A: Yes! After first manual version, create Python script to auto-populate from Bill-C15-01.json

**Q: Who should do this work?**  
A: Original analyst (best) or developer familiar with Bill-C15-01 analysis

# Analysis: Policy Documents vs. Legislative Documents

Based on The Sparrow's examination of the Bill C-15-05 evaluation system and the underlying document being analyzed, here are the key distinctions:

## Fundamental Differences

### **Legislative Documents** (Primary Sources)
Legislative documents like Bill C-15 are **authoritative legal texts** that:

1. **Create binding law** - They establish legal requirements, obligations, and frameworks that have force of law once enacted
2. **Follow strict formatting conventions** - Numbered sections, subsections, defined terms, enactment clauses
3. **Require no citations** - They ARE the primary source of authority; they don't cite other sources because they establish the authoritative position themselves
4. **Use prescriptive language** - "shall," "must," "may not" - creating legal obligations
5. **Go through formal legislative processes** - Readings, committee review, votes, royal assent
6. **Have legal standing** - Courts interpret and enforce them; they're codified in statute books

### **Policy Documents** (Secondary/Analytical Sources)
Policy documents are **analytical or advisory texts** that:

1. **Recommend or propose** - They suggest courses of action but don't create binding obligations
2. **Require evidence and citations** - Must cite research, data, expert opinions to support recommendations
3. **Use persuasive language** - "should," "recommends," "suggests" - building arguments for positions
4. **Inform decision-making** - Guide choices but don't mandate them
5. **Include analysis and rationale** - Explain why certain approaches are preferred based on evidence
6. **May contain** - Executive summaries, literature reviews, data visualizations, stakeholder input

## Why This Matters for the Evaluation System

The Sparrow identified a critical flaw in the Bill C-15-05 system: **it applies research paper standards to legislation**.

### The Problem as Currently Implemented:

```
Citation Quality Assessment:
Quality Score: 0.0/100
Quality Level: Very Poor
Summary: No citations found. Document lacks source attribution.
```

This assessment is **incorrect for legislation** because:
- Bill C-15 is the **authoritative source itself**
- It doesn't need to cite other sources—it establishes the legal framework
- Zero citations is the **expected and appropriate** state for primary legislation

### The Sparrow's Recommended Fix:

```python
def assess_citation_quality(doc_type, citation_count, url_count):
    citation_expectations = {
        'legislation': {
            'expected_min': 0,
            'expected_max': 0,
            'interpretation': 'Primary legislative sources do not require citations'
        },
        'policy_brief': {
            'expected_min': 5,
            'expected_max': 20,
            'interpretation': 'Policy briefs should cite supporting evidence'
        }
    }
    
    if doc_type == 'legislation':
        if citation_count == 0:
            return {
                'score': 100.0,  # Perfect for legislation
                'level': 'Appropriate',
                'summary': 'Primary legislation - citations not expected or required'
            }
```

## Practical Implications

### Example 1: Infrastructure Spending Authorization

**Legislative Document** (Bill):
> "The Minister may make payments out of the Consolidated Revenue Fund for infrastructure projects up to $100 million."

- No citation needed—this creates the legal authority
- Language is prescriptive ("may make payments")
- Creates actionable legal framework

**Policy Document** (Policy Brief):
> "The government should invest $100 million in infrastructure. Research by Smith et al. (2024) shows infrastructure spending yields 1.5x economic multiplier effects. The Parliamentary Budget Office estimates this would create 2,000 jobs."

- Requires citations to justify the recommendation
- Language is suggestive ("should invest")
- Must build evidence-based case

### Example 2: Environmental Standards

**Legislative Document**:
> "Section 12(1): No person shall emit more than 50 parts per million of sulfur dioxide. Section 12(2): Violations are subject to fines up to $500,000."

- Self-contained legal requirement
- Enforceable by courts
- No need to cite scientific studies justifying the 50 ppm threshold

**Policy Document**:
> "We recommend setting sulfur dioxide limits at 50 ppm based on WHO air quality guidelines (2021), Health Canada risk assessments (Johnson, 2023), and cost-benefit analysis showing net benefits of $2.3 billion (Treasury Board, 2024)."

- Must cite scientific basis
- Must demonstrate evidence-informed decision-making
- Builds credibility through external sources

## Summary

The core distinction: **Legislative documents CREATE authority; policy documents PERSUADE using existing authority and evidence.**

The Sparrow's analysis reveals that the evaluation system was penalizing Bill C-15 for not having citations—treating it like a policy brief or research paper when it's actually primary legislation. This is analogous to criticizing a dictionary for not citing sources for word definitions: **the dictionary IS the authoritative source for definitions**, just as legislation IS the authoritative source for legal requirements.

The recommended fix (Priority 5 in The Sparrow's roadmap) would implement document-type recognition to apply appropriate evaluation criteria based on whether the document is legislative, policy-oriented, or research-based.
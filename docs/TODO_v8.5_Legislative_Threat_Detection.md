# TODO: Sparrow SPOT v8.5 - Legislative Threat Detection Suite

**Priority:** CRITICAL  
**Target Version:** 8.5.0  
**Created:** 2025-12-06  
**Status:** PLANNING

---

## Executive Summary

Based on analysis of Bill C-15 commentary, citizens and watchdog groups need tools to detect:
- Hidden provisions buried in large documents
- Broad discretionary powers with weak oversight
- "Transparency theater" - oversight language with escape clauses
- Exemption stacking that creates accountability black holes
- Temporal anomalies (short tests, long exemptions)

This TODO outlines the **Legislative Threat Detection Suite** for Sparrow SPOT v8.5.

---

## Phase 1: Core Detection Modules

### 1.1 Discretionary Power Analyzer (DPA)
**Priority:** P0 - Critical  
**Estimated Effort:** 3-4 days  
**File:** `discretionary_power_analyzer.py`

#### Detection Targets:

| Pattern Type | Examples | Risk Level |
|--------------|----------|------------|
| **Permissive Language** | "may", "may by order", "at the minister's discretion" | MEDIUM |
| **Self-Judgment Clauses** | "in the minister's opinion", "if the minister is satisfied", "considers appropriate" | HIGH |
| **Undefined Timelines** | "as soon as feasible", "within a reasonable time", "promptly" | MEDIUM |
| **Broad Scope** | "any entity", "any provision", "any federal law", "for any purpose" | CRITICAL |
| **Exclusion Powers** | "may exclude", "may exempt", "may waive" | HIGH |

#### Output:
```python
{
    "discretionary_power_score": 0-100,
    "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
    "findings": [
        {
            "pattern": "self_judgment",
            "text": "in the minister's opinion",
            "location": {"section": "12.3", "page": 412},
            "context": "surrounding text...",
            "risk_assessment": "Minister is sole arbiter with no appeal mechanism"
        }
    ],
    "power_concentration_index": 0-100,
    "recommendations": []
}
```

#### Implementation Tasks:
- [ ] Create regex patterns for discretionary language
- [ ] Build context analyzer to assess severity
- [ ] Implement "may" vs "shall" counter
- [ ] Add self-exemption detection (when decision-maker benefits)
- [ ] Create power concentration scoring algorithm
- [ ] Unit tests with Bill C-15 excerpts

---

### 1.2 Buried Provision Scanner (BPS)
**Priority:** P0 - Critical  
**Estimated Effort:** 2-3 days  
**File:** `buried_provision_scanner.py`

#### Detection Logic:
1. **Position Analysis** - Flag high-impact clauses in document depths
   - Calculate "burial depth" = section position / total sections
   - Higher risk if impactful provision is in bottom 25% of document

2. **Significance Mismatch** - Compare section importance vs prominence
   - Measure keyword density (power, exempt, waive, exclude)
   - Compare to preamble/executive summary mentions
   - Flag if significant content not mentioned in summary

3. **Page Count Threshold** - Documents over 200 pages get automatic deep scan

#### Output:
```python
{
    "buried_provisions": [
        {
            "section": "Division 15, Part 4",
            "page": 412,
            "burial_depth": 0.85,  # 85% deep in document
            "significance_score": 92,
            "mentioned_in_summary": False,
            "mentioned_in_preamble": False,
            "key_powers_granted": ["exemption authority", "disclosure waiver"],
            "alert_level": "CRITICAL"
        }
    ],
    "document_structure_score": 0-100,
    "transparency_of_organization": "LOW|MEDIUM|HIGH"
}
```

#### Implementation Tasks:
- [ ] Build document structure parser (sections, divisions, parts)
- [ ] Create significance scoring based on power-granting language
- [ ] Implement preamble/summary cross-reference
- [ ] Add page-depth risk calculator
- [ ] Create "omnibus bill" detector (multi-topic legislation)
- [ ] Unit tests with known buried provisions

---

### 1.3 Accountability Gap Detector (AGD)
**Priority:** P0 - Critical  
**Estimated Effort:** 3-4 days  
**File:** `accountability_gap_detector.py`

#### Analysis Framework:

**Powers Granted (numerator):**
- Exemption authorities
- Discretionary decisions
- Information withholding rights
- Extension capabilities
- Waiver powers

**Oversight Mechanisms (denominator):**
- Reporting requirements (with teeth?)
- Parliamentary review mandates
- Judicial review access
- Public disclosure obligations
- Sunset clauses
- Appeal mechanisms

**Accountability Ratio = Oversight Strength / Powers Granted**

#### Escape Clause Detection:
| Clause Type | Pattern | Risk |
|-------------|---------|------|
| **Conditional Transparency** | "subject to subsections..." | HIGH |
| **Self-Exception** | "may exclude information that in the minister's opinion..." | CRITICAL |
| **Optional Reporting** | "is not required to prepare a report if..." | HIGH |
| **Undefined Review** | "referred to committee" (no action required) | MEDIUM |
| **Toothless Oversight** | Annual report with no enforcement | MEDIUM |

#### Output:
```python
{
    "accountability_ratio": 0.0-1.0,  # <0.5 = concerning
    "powers_granted": [
        {"power": "exempt any entity from any law", "scope": "BROAD", "duration": "6 years"}
    ],
    "oversight_mechanisms": [
        {"mechanism": "annual report", "enforcement": "NONE", "effectiveness": "LOW"}
    ],
    "escape_clauses": [
        {"text": "may exclude information...", "type": "self_exception", "risk": "CRITICAL"}
    ],
    "sunset_clause_present": False,
    "judicial_review_available": False,
    "appeal_mechanism": "NONE",
    "overall_risk": "CRITICAL"
}
```

#### Implementation Tasks:
- [ ] Build power-granting language classifier
- [ ] Create oversight mechanism detector
- [ ] Implement escape clause pattern matching
- [ ] Calculate accountability ratio
- [ ] Add sunset clause detector
- [ ] Check for appeal/review mechanisms
- [ ] Unit tests with transparency theater examples

---

### 1.4 Transparency Theater Detector (TTD)
**Priority:** P1 - High  
**Estimated Effort:** 2 days  
**File:** `transparency_theater_detector.py`

#### Detection Pattern:
Identify sections with transparency-signaling titles that contain undermining clauses.

**Title Signals:**
- "Transparency and..."
- "Oversight"
- "Accountability"
- "Public disclosure"
- "Reporting requirements"

**Undermining Patterns:**
- "subject to subsections..."
- "the minister may exclude..."
- "is not required to..."
- "for reasons of confidentiality..."
- "in the minister's opinion would be inappropriate..."
- "no timeline defined"

#### Output:
```python
{
    "transparency_theater_score": 0-100,  # Higher = more theatrical
    "findings": [
        {
            "section_title": "Transparency and Parliamentary Oversight",
            "promises": ["make publicly accessible", "description of decision-making"],
            "undermining_clauses": [
                "may exclude information that in the minister's opinion...",
                "as soon as feasible (no timeline)"
            ],
            "net_transparency": "NEGATIVE",
            "theater_rating": "HIGH"
        }
    ]
}
```

#### Implementation Tasks:
- [ ] Build transparency title pattern matcher
- [ ] Create undermining clause detector
- [ ] Implement promise vs exception analyzer
- [ ] Calculate net transparency score
- [ ] Unit tests with Bill C-15 Section 13

---

### 1.5 Exemption Cascade Analyzer (ECA)
**Priority:** P1 - High  
**Estimated Effort:** 3 days  
**File:** `exemption_cascade_analyzer.py`

#### Analysis Framework:

Map which laws can be exempted and identify dangerous combinations:

**Dangerous Combinations:**
1. Lobbying Act + Conflict of Interest Act = Secret influence + hidden conflicts
2. Access to Information + Procurement Rules = Hidden contracts
3. Competition Act + Treasury Board Rules = Monopoly + sole-source
4. Environmental Acts + Tax Reporting = Pollute + hide finances

#### Cross-Reference Database:
```python
FEDERAL_ACTS = {
    "lobbying_act": {"risk_if_exempt": "secret lobbying", "severity": "HIGH"},
    "conflict_of_interest_act": {"risk_if_exempt": "hidden conflicts", "severity": "CRITICAL"},
    "access_to_information_act": {"risk_if_exempt": "document hiding", "severity": "CRITICAL"},
    "canada_elections_act": {"risk_if_exempt": "election interference", "severity": "CRITICAL"},
    "competition_act": {"risk_if_exempt": "monopoly formation", "severity": "HIGH"},
    "environmental_protection_act": {"risk_if_exempt": "environmental harm", "severity": "HIGH"},
    # ... full list
}

DANGEROUS_COMBINATIONS = [
    (["lobbying_act", "conflict_of_interest_act"], "CRITICAL", "Secret influence with hidden conflicts"),
    (["access_to_information_act", "treasury_board_rules"], "CRITICAL", "Hidden procurement"),
    # ... 
]
```

#### Output:
```python
{
    "exemptable_acts": ["lobbying_act", "conflict_of_interest_act", ...],
    "excluded_acts": ["criminal_code"],
    "dangerous_combinations_possible": [
        {
            "combination": ["lobbying_act", "conflict_of_interest_act"],
            "risk": "CRITICAL",
            "scenario": "Entity lobbies secretly while minister has undisclosed conflict"
        }
    ],
    "cascade_risk_score": 0-100,
    "worst_case_scenario": "Full description of layered exemption abuse..."
}
```

#### Implementation Tasks:
- [ ] Build federal acts database with risk profiles
- [ ] Create dangerous combination matrix
- [ ] Implement exemption scope parser
- [ ] Generate worst-case scenario narratives
- [ ] Add visual cascade diagram (mermaid)
- [ ] Unit tests with Bill C-15 exemption scope

---

### 1.6 Temporal Anomaly Detector (TAD)
**Priority:** P2 - Medium  
**Estimated Effort:** 1-2 days  
**File:** `temporal_anomaly_detector.py`

#### Detection Targets:

| Anomaly Type | Pattern | Example |
|--------------|---------|---------|
| **Duration Mismatch** | Short purpose, long validity | "test for 5 minutes, exempt for 3 years" |
| **Extension Creep** | Initial + extensions = excessive | "3 years + 3 years = 6 years total" |
| **No Shortening Mechanism** | Validity continues regardless | "continues until end of period even if testing completed" |
| **Undefined Timelines** | "as soon as feasible" with no deadline | No enforcement possible |
| **Missing Sunset** | Powers without expiration | Permanent authority grants |

#### Output:
```python
{
    "temporal_anomalies": [
        {
            "type": "duration_mismatch",
            "stated_purpose": "testing",
            "validity_period": "3 years",
            "mismatch_severity": "HIGH",
            "quote": "even if the testing... is completed before the end of that period"
        }
    ],
    "sunset_clause_present": False,
    "maximum_duration": "6 years",
    "shortening_mechanism": False,
    "temporal_risk_score": 0-100
}
```

#### Implementation Tasks:
- [ ] Build duration extraction regex
- [ ] Create purpose-to-duration reasonableness checker
- [ ] Implement extension clause detector
- [ ] Add sunset clause presence check
- [ ] Unit tests with Bill C-15 temporal provisions

---

## Phase 2: Cross-Document Verification

### 2.1 Disclosure Integrity Checker (DIC)
**Priority:** P1 - High  
**Estimated Effort:** 4-5 days  
**File:** `disclosure_integrity_checker.py`

#### Multi-Document Comparison:
Compare legislative text against:
1. Budget document
2. Press releases
3. Ministerial speeches
4. Committee testimony
5. Government backgrounders

#### Detection:
- Provisions in bill but NOT in budget summary
- Powers granted but NOT discussed in speeches
- Sections added after initial publication
- Scope expansion between readings

#### Output:
```python
{
    "undisclosed_provisions": [
        {
            "provision": "Ministerial exemption power",
            "bill_section": "Division 15",
            "mentioned_in_budget": False,
            "mentioned_in_press": False,
            "mentioned_in_speeches": False,
            "disclosure_gap": "COMPLETE"
        }
    ],
    "disclosure_completeness_score": 0-100,
    "hidden_significance_index": 0-100
}
```

#### Implementation Tasks:
- [ ] Build document ingestion for multiple formats
- [ ] Create provision extraction and normalization
- [ ] Implement cross-document matching algorithm
- [ ] Add speech/press release parsers
- [ ] Calculate disclosure completeness score
- [ ] Unit tests with Bill C-15 vs budget document

---

## Phase 3: Integration & Reporting

### 3.1 Legislative Threat Report Generator
**Priority:** P1 - High  
**Estimated Effort:** 2 days  
**File:** `legislative_threat_report.py`

#### Consolidated Report Sections:
1. **Executive Summary** - Overall threat assessment
2. **Power Concentration Analysis** - DPA results
3. **Buried Provisions Alert** - BPS findings
4. **Accountability Analysis** - AGD ratio and gaps
5. **Transparency Theater Flags** - TTD findings
6. **Exemption Risk Map** - ECA cascade analysis
7. **Temporal Concerns** - TAD anomalies
8. **Cross-Document Verification** - DIC results (if available)
9. **Worst-Case Scenario** - Narrative of potential abuse
10. **Recommendations** - Amendments needed

#### Output Formats:
- JSON (machine-readable)
- Markdown (human-readable)
- HTML Certificate with threat visualization
- PDF Executive Brief

---

### 3.2 GUI Integration
**Priority:** P2 - Medium  
**Estimated Effort:** 1 day

#### New Tab: "Legislative Threat Analysis"
- [ ] Checkbox: "Run Legislative Threat Detection"
- [ ] Options for which modules to run
- [ ] Threat level visualization (gauge/meter)
- [ ] Drill-down to specific findings

#### Certificate Enhancement:
- [ ] Add "Legislative Threat Score" to certificate
- [ ] Visual indicator for buried provisions
- [ ] Accountability gap warning banner

---

### 3.3 CLI Integration
**Priority:** P2 - Medium  
**Estimated Effort:** 0.5 days

```bash
python sparrow_grader_v8.py document.pdf \
    --legislative-threat-analysis \
    --threat-modules all \
    --compare-against budget.pdf speech.txt \
    --output-threat-report
```

---

## Phase 4: Testing & Validation

### 4.1 Test Cases
**Priority:** P0 - Critical  
**Estimated Effort:** 2 days

#### Primary Test Document:
- Bill C-15 (Budget Implementation Act 2025) - Division 15

#### Additional Test Documents:
- [ ] Bill C-5 (Building Canada Act) - Known exemption provisions
- [ ] Emergencies Act - Historical power grab reference
- [ ] Various omnibus bills with known buried provisions

#### Validation Criteria:
- [ ] Correctly identifies Division 15 exemption powers
- [ ] Flags "in the minister's opinion" clauses
- [ ] Detects transparency theater in Section 13
- [ ] Calculates appropriate accountability ratio
- [ ] Identifies dangerous exemption combinations

---

## Implementation Timeline

| Phase | Module | Priority | Days | Target Date |
|-------|--------|----------|------|-------------|
| 1.1 | Discretionary Power Analyzer | P0 | 3-4 | Week 1 |
| 1.2 | Buried Provision Scanner | P0 | 2-3 | Week 1 |
| 1.3 | Accountability Gap Detector | P0 | 3-4 | Week 2 |
| 1.4 | Transparency Theater Detector | P1 | 2 | Week 2 |
| 1.5 | Exemption Cascade Analyzer | P1 | 3 | Week 3 |
| 1.6 | Temporal Anomaly Detector | P2 | 1-2 | Week 3 |
| 2.1 | Disclosure Integrity Checker | P1 | 4-5 | Week 4 |
| 3.1 | Threat Report Generator | P1 | 2 | Week 4 |
| 3.2 | GUI Integration | P2 | 1 | Week 5 |
| 3.3 | CLI Integration | P2 | 0.5 | Week 5 |
| 4.1 | Testing & Validation | P0 | 2 | Week 5 |

**Total Estimated Effort:** 24-30 days  
**Target Completion:** v8.5.0

---

## Success Metrics

1. **Detection Rate:** >90% of known buried provisions identified
2. **False Positive Rate:** <15% of flagged items are non-issues
3. **Performance:** Full legislative analysis in <5 minutes for 600-page document
4. **User Adoption:** Threat analysis used in >50% of policy document analyses

---

## Dependencies

- Existing: `sparrow_grader_v8.py`, `ai_detection_engine.py`, `deep_analyzer.py`
- New: Federal Acts database (research required)
- Optional: Access to government press releases API

---

## Risk Factors

1. **Scope Creep:** Each module could expand significantly
2. **False Positives:** Legal language is complex; context matters
3. **Performance:** Large documents may slow analysis
4. **Maintenance:** Laws change; patterns need updating

---

## Notes

This suite is inspired by the Bill C-15 commentary analysis, specifically the framework:

> "We don't look at legislation in terms of only the good that is intended to accomplish... assuming that you have a corrupt government in power, what could be the worst possible thing that they could do with that legislation?"

Sparrow SPOT should operationalize this watchdog mentality.

---

*Document created: 2025-12-06*  
*Author: Sparrow Development Team*

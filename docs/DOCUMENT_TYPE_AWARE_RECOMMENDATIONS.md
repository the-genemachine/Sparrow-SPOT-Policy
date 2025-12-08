# Document-Type-Aware Remediation Recommendations
## Sparrow SPOT Scale™ v8.6.1

**Document Version:** 1.0  
**Date:** December 8, 2025  
**Status:** Design Specification  

---

## Executive Summary

This document extends the remediation recommendation system to be fully context-aware of document type. The same issue (e.g., "Low Economic Rigor") generates completely different recommendations based on whether the document is:

- **Legislation** (bills, acts, regulations)
- **Policy Report** (white papers, position papers, analysis)
- **News/Journalism** (articles, opinion pieces, investigative reports)
- **Academic** (research papers, case studies, scholarly articles)
- **Business** (proposals, business cases, strategic documents)

**Key Principle:** A metric that's CRITICAL for legislation might be OPTIONAL for a news article. Recommendations must reflect this reality.

---

## Document Type Classification

### 1. Legislation
**Characteristics:**
- Formal policy language
- Legal implications
- Budget impact
- Implementation timeline
- Regulatory requirements
- Stakeholder compliance obligations

**Metric Priorities:**
- CRITICAL: Fiscal Transparency, Economic Rigor, Policy Consequentiality
- HIGH: Stakeholder Balance, Analytical Transparency
- MEDIUM: Public Accessibility

**Context:**
- Citizens must understand laws affecting them
- Economic impact must be rigorous (affects markets)
- Costs and funding must be crystal clear
- Unintended consequences could be severe
- Must address stakeholder concerns

---

### 2. Policy Report
**Characteristics:**
- Research-based analysis
- Multiple perspectives explored
- Evidence-driven recommendations
- Often peer-reviewed or expert-vetted
- Intended for decision-makers

**Metric Priorities:**
- CRITICAL: Analytical Transparency, Stakeholder Balance
- HIGH: Economic Rigor, Fiscal Transparency
- MEDIUM: Public Accessibility, Policy Consequentiality

**Context:**
- Decision-makers need to trust methodology
- Multiple viewpoints strengthen credibility
- Evidence must be clear and verifiable
- May be technical (not always public-facing)
- Recommendations based on analysis

---

### 3. News/Journalism
**Characteristics:**
- Time-sensitive information
- Broad public audience
- Varied perspectives standard
- Public interest focus
- Fact-checking essential

**Metric Priorities:**
- CRITICAL: Public Accessibility, Stakeholder Balance
- HIGH: Analytical Transparency
- MEDIUM: Policy Consequentiality, Fiscal Transparency
- LOW: Economic Rigor (unless economics-focused article)

**Context:**
- Average reader, not specialist
- Complex jargon must be explained
- Multiple sources essential
- Balanced coverage expected
- Can be opinion but must be labeled

---

### 4. Academic
**Characteristics:**
- Peer-reviewed or peer-reviewable
- Rigorous methodology
- Contribution to knowledge
- Technical audience
- Citable source material

**Metric Priorities:**
- CRITICAL: Analytical Transparency
- HIGH: Economic Rigor (if applicable), Stakeholder Balance
- MEDIUM: Fiscal Transparency (if policy-focused)
- LOW: Public Accessibility (academic audience expected)

**Context:**
- Methodology is paramount
- Limitations must be acknowledged
- Sources must be citable
- Peer review is validation

---

### 5. Business
**Characteristics:**
- Decision-oriented
- Cost-benefit focused
- Implementation-focused
- Stakeholder impact (employees, customers, partners)
- ROI emphasis

**Metric Priorities:**
- CRITICAL: Policy Consequentiality, Fiscal Transparency
- HIGH: Economic Rigor, Analytical Transparency
- MEDIUM: Public Accessibility, Stakeholder Balance

**Context:**
- ROI must be clear
- Implementation must be realistic
- Costs must be accurate
- Stakeholder impact (employee morale, customer reaction)
- Feasibility essential

---

## Document-Type-Aware Recommendation Framework

### Issue: Low Economic Rigor (Score: 3/100)

#### For LEGISLATION
```json
{
  "issue": "Economic Rigor",
  "score": 3,
  "document_type": "legislation",
  "severity": "CRITICAL",
  "reasoning": "Bills directly impact economic systems and create compliance costs for businesses. Without rigorous economic analysis, the bill is vulnerable to challenge and may have unintended negative consequences.",
  
  "tier_1_quick_wins": [
    {
      "name": "Add Economic Impact Overview",
      "description": "Write 1-2 page summary of expected economic effects based on available evidence",
      "for_legislation_context": "Show you've thought through economic impacts, even if detailed analysis pending",
      "steps": [
        "Review existing studies on similar policies",
        "Identify expected effects on GDP, employment, business costs",
        "Write narrative summary with caveats",
        "Add to policy document as Section 3"
      ],
      "time_hours": 8,
      "cost": 0,
      "score_impact": 8,
      "tools": ["Google Scholar", "Government statistics databases"]
    },
    {
      "name": "Quantify Implementation Costs for Business Compliance",
      "description": "Calculate and document all new compliance costs imposed on regulated entities",
      "for_legislation_context": "Legislation must be transparent about costs it imposes on others",
      "steps": [
        "List all new requirements for businesses/organizations",
        "Estimate one-time implementation costs per type of entity",
        "Estimate ongoing compliance/reporting costs",
        "Create table showing cost impacts by sector"
      ],
      "time_hours": 12,
      "cost": 0,
      "score_impact": 10,
      "tools": ["Excel", "Industry cost databases"]
    }
  ],
  
  "tier_2_medium_fixes": [
    {
      "name": "Commission Economic Impact Analysis from Economist",
      "description": "Hire professional economist to model economic impacts",
      "for_legislation_context": "Government bills are expected to have economic analysis. This is industry standard.",
      "required_analysis": [
        "Gross Domestic Product (GDP) impact",
        "Employment impacts (jobs created/lost)",
        "Business cost analysis (especially small business)",
        "Sector-by-sector impacts",
        "Consumer impacts (price changes, access)",
        "Sensitivity analysis (what-if scenarios)"
      ],
      "expert_needed": "Economist with policy modeling experience",
      "cost_range": {"min": 8000, "max": 15000},
      "timeline_weeks": 4-6,
      "deliverables": [
        "Economic impact model",
        "Sensitivity analysis with scenarios",
        "Executive summary for policymakers",
        "Detailed technical report"
      ],
      "score_impact": 62,
      "when_to_do": "Before any public consultation or tabling",
      "why_for_legislation": "Parliament and public expect evidence-based economic analysis for bills"
    },
    {
      "name": "Develop Cost-Benefit Analysis Specific to Government Fiscal Impact",
      "description": "Analyze what this costs government vs. what it saves/generates",
      "for_legislation_context": "Parliament scrutinizes government expenditure. Clear fiscal impact is essential.",
      "analysis_includes": [
        "New government spending required (operating, capital)",
        "New government revenue generated (if any)",
        "Year-by-year fiscal projections (5-10 years)",
        "Cost per target population/outcome",
        "Funding mechanism (where money comes from)",
        "Comparison to alternative approaches"
      ],
      "cost_range": {"min": 3000, "max": 8000},
      "timeline_weeks": 2-3,
      "score_impact": 15,
      "critical_for_legislation": true
    }
  ],
  
  "tier_3_major_initiatives": [
    {
      "name": "Comprehensive Economic Analysis and Modeling",
      "description": "Full economic impact study with multiple scenarios",
      "for_legislation_context": "Major bills should have comprehensive economic analysis published with the legislation",
      "scope": [
        "Macroeconomic modeling",
        "Sector-specific impacts",
        "Regional impacts",
        "10-year fiscal projections",
        "Employment impact modeling",
        "Innovation and competitiveness impacts",
        "Environmental economic costs/benefits",
        "Health/social benefits (if applicable)"
      ],
      "timeline_weeks": 12-16,
      "cost_range": {"min": 25000, "max": 50000},
      "score_impact": 80,
      "expected_outcome": "Policy becomes defensible on economic grounds, publication-ready analysis"
    }
  ],
  
  "alternative_if_budget_limited": "Commission quick analysis from academic economist ($2K-$4K, 2 weeks) as interim solution",
  
  "red_flag": "Without economic analysis, this bill is vulnerable to opposition critique and may not withstand parliamentary scrutiny"
}
```

#### For POLICY REPORT
```json
{
  "issue": "Economic Rigor",
  "score": 3,
  "document_type": "policy_report",
  "severity": "HIGH",
  "reasoning": "Policy reports are evidence-based documents. Readers expect economic claims to be backed by analysis or cited research.",
  
  "tier_1_quick_wins": [
    {
      "name": "Cite Existing Economic Research",
      "description": "Find published studies supporting economic claims and cite them properly",
      "for_report_context": "Reports don't need original analysis, but must cite evidence for claims",
      "steps": [
        "Identify all economic claims in report",
        "Search for peer-reviewed research supporting each claim",
        "Add citations to footnotes/bibliography",
        "Add note explaining research basis"
      ],
      "time_hours": 4,
      "cost": 0,
      "score_impact": 12,
      "tools": ["Google Scholar", "Library database access"]
    },
    {
      "name": "Add Economic Evidence Section",
      "description": "Create section summarizing economic research findings",
      "for_report_context": "Demonstrates you've reviewed evidence, improves credibility",
      "steps": [
        "Create 'Economic Evidence' section",
        "Summarize 3-5 key studies",
        "Show how findings support recommendations",
        "Acknowledge limitations of research"
      ],
      "time_hours": 6,
      "cost": 0,
      "score_impact": 10
    }
  ],
  
  "tier_2_medium_fixes": [
    {
      "name": "Peer Review by Economist",
      "description": "Have economist review claims and verify economic reasoning",
      "for_report_context": "Expert review boosts credibility of policy recommendations",
      "scope": [
        "Verify economic claims are accurate",
        "Check citations are appropriate",
        "Suggest improvements or missing analysis",
        "Provide written peer review commentary",
        "Optional: Allow cited in report as validation"
      ],
      "expert_needed": "Economist (any specialization acceptable)",
      "cost_range": {"min": 2000, "max": 5000},
      "timeline_weeks": 2-3,
      "score_impact": 25,
      "bonus": "Peer review can be cited as credibility validation"
    },
    {
      "name": "Add Economic Data Visualizations",
      "description": "Create charts/graphs showing economic data supporting claims",
      "for_report_context": "Reports are meant to communicate. Visuals make economic data accessible",
      "examples": [
        "Cost trend chart",
        "Benefit distribution pie chart",
        "Scenario comparison bar chart",
        "Timeline showing economic progression"
      ],
      "cost_range": {"min": 1000, "max": 3000},
      "timeline_weeks": 1,
      "score_impact": 8
    }
  ],
  
  "tier_3_major_initiatives": [
    {
      "name": "Commission Original Economic Analysis",
      "description": "Hire economist to analyze your specific policy question",
      "for_report_context": "Only if report is high-profile or makes novel economic claims",
      "cost_range": {"min": 8000, "max": 15000},
      "timeline_weeks": 6-8,
      "score_impact": 45,
      "when_justified": "If report claims are economically novel or will influence major decisions"
    }
  ],
  
  "note": "Reports can achieve high scores by properly citing existing research. Original analysis only needed for novel claims."
}
```

#### For NEWS/JOURNALISM
```json
{
  "issue": "Economic Rigor",
  "score": 3,
  "document_type": "news",
  "severity": "MEDIUM",
  "reasoning": "News articles should cite economic experts and data, but don't require original economic analysis. Balance and context matter more than depth of analysis.",
  
  "tier_1_quick_wins": [
    {
      "name": "Quote Economic Expert",
      "description": "Add quotes from economist or policy expert providing economic context",
      "for_news_context": "Journalism standard: expert commentary adds credibility and analysis",
      "steps": [
        "Identify 1-2 economists with relevant expertise",
        "Request quote about economic implications",
        "Integrate quote into article narrative",
        "Identify expert with credentials"
      ],
      "time_hours": 2,
      "cost": 0,
      "score_impact": 15,
      "sourcing": "University economists often willing to comment on policy"
    },
    {
      "name": "Add Economic Context/Comparison",
      "description": "Explain what policy costs/saves compared to current baseline",
      "for_news_context": "Helps readers understand scope and significance",
      "examples": [
        "'Would cost $2M/year, equivalent to 50 school teacher salaries'",
        "'Saves 5% of current program spending'",
        "'Impacts 10% of workforce'"
      ],
      "time_hours": 1,
      "cost": 0,
      "score_impact": 8
    },
    {
      "name": "Link to Original Economic Data/Studies",
      "description": "Cite government statistics or published studies supporting claims",
      "for_news_context": "Readers can verify claims, improves trust",
      "steps": [
        "Find official data sources",
        "Include links in article",
        "Briefly explain what data shows"
      ],
      "time_hours": 2,
      "cost": 0,
      "score_impact": 10
    }
  ],
  
  "tier_2_medium_fixes": [
    {
      "name": "Request Official Economic Impact Statement",
      "description": "Ask government agency for official economic analysis",
      "for_news_context": "Agencies often publish economic analysis; request for FOIA if needed",
      "steps": [
        "Contact relevant government department",
        "Request economic analysis if published",
        "If not published, note in article ('requested but not available')",
        "Use in updated article"
      ],
      "time_hours": 4,
      "cost": 0,
      "score_impact": 12,
      "note": "Sometimes requires FOIA request (1-2 weeks)"
    },
    {
      "name": "Interview Multiple Economists on Economic Impact",
      "description": "Get perspectives from economists with different viewpoints",
      "for_news_context": "Balance is essential in journalism. Different experts = different perspectives",
      "examples": [
        "Industry economist (sees costs/burdens)",
        "University economist (academic perspective)",
        "Think tank economist (ideological perspective)"
      ],
      "cost_range": {"min": 0, "max": 500},
      "timeline_hours": 4-6,
      "score_impact": 20,
      "why_important": "Shows you've explored multiple economic perspectives"
    }
  ],
  
  "tier_3_major_initiatives": [
    {
      "name": "Investigative Deep Dive into Economic Impact",
      "description": "Multi-part investigative series analyzing economic consequences",
      "for_news_context": "Only for major stories with significant economic implications",
      "cost_range": {"min": 3000, "max": 10000},
      "timeline_weeks": 4-8,
      "score_impact": 35,
      "when_justified": "Breaking news about major economic policy changes"
    }
  ],
  
  "key_principle": "News doesn't need rigorous economic modeling. It needs quotes from experts, official data, and multiple perspectives. Focus on accessibility over depth."
}
```

#### For ACADEMIC
```json
{
  "issue": "Economic Rigor",
  "score": 3,
  "document_type": "academic",
  "severity": "CRITICAL",
  "reasoning": "Academic papers must demonstrate rigorous methodology. Economic claims require quantitative analysis, statistical testing, and clear methodology documentation.",
  
  "tier_1_quick_wins": [
    {
      "name": "Document Economic Methodology Section",
      "description": "Write clear methodology section explaining how economic analysis was conducted",
      "for_academic_context": "Peer reviewers need to understand and potentially replicate your analysis",
      "required_elements": [
        "Data sources and definitions",
        "Variables and their measurement",
        "Statistical methods used",
        "Assumptions made",
        "Limitations acknowledged"
      ],
      "time_hours": 8,
      "cost": 0,
      "score_impact": 15,
      "critical": "Cannot publish without clear methodology"
    },
    {
      "name": "Add Economic Literature Review",
      "description": "Comprehensive review of existing economic research on topic",
      "for_academic_context": "Shows you understand existing scholarship and where your contribution fits",
      "steps": [
        "Search economic literature comprehensively",
        "Organize findings by theme",
        "Position your work relative to existing research",
        "Identify gaps your work addresses"
      ],
      "time_hours": 16,
      "cost": 0,
      "score_impact": 20
    }
  ],
  
  "tier_2_medium_fixes": [
    {
      "name": "Peer Review by Economist Specialist",
      "description": "Have economist review methodology and economic soundness",
      "for_academic_context": "Peer review is requirement for publication. Get feedback before submitting.",
      "expert_needed": "PhD Economist in your field",
      "scope": [
        "Methodology review",
        "Data analysis verification",
        "Statistical testing appropriateness",
        "Interpretation of results",
        "Limitations assessment"
      ],
      "cost_range": {"min": 2000, "max": 5000},
      "timeline_weeks": 3-4,
      "score_impact": 30,
      "deliverable": "Peer review report with recommendations"
    },
    {
      "name": "Add Statistical Robustness Checks",
      "description": "Verify results hold under different assumptions and specifications",
      "for_academic_context": "Shows you've tested your findings rigorously",
      "examples": [
        "Alternative variable definitions",
        "Different statistical methods",
        "Sensitivity analysis",
        "Subsample analysis"
      ],
      "cost_range": {"min": 1000, "max": 3000},
      "timeline_weeks": 2-3,
      "score_impact": 25
    }
  ],
  
  "tier_3_major_initiatives": [
    {
      "name": "Major Methodological Revision and Re-analysis",
      "description": "Redesign study with more rigorous methodology and larger dataset",
      "for_academic_context": "If current methodology is fundamentally flawed",
      "timeline_weeks": 12-20,
      "cost_range": {"min": 10000, "max": 30000},
      "score_impact": 75,
      "when_needed": "If initial analysis has major methodological problems"
    }
  ],
  
  "publication_pathway": "These fixes enable publication in peer-reviewed journal. Essential before submission."
}
```

#### For BUSINESS
```json
{
  "issue": "Economic Rigor",
  "score": 3,
  "document_type": "business",
  "severity": "HIGH",
  "reasoning": "Business documents must clearly show return on investment, cost-benefit analysis, and financial viability. Stakeholders (investors, executives, board) need to understand economic case.",
  
  "tier_1_quick_wins": [
    {
      "name": "Add ROI Calculation and Payback Period",
      "description": "Calculate and clearly display return on investment and payback timeline",
      "for_business_context": "Decision-makers must see clear financial benefit to approve projects",
      "steps": [
        "Calculate total investment required",
        "Calculate annual benefits/savings",
        "Compute ROI percentage",
        "Calculate payback period (months/years)",
        "Create summary table or chart"
      ],
      "time_hours": 4,
      "cost": 0,
      "score_impact": 20,
      "example": "'$100K investment, $30K annual savings, 3.3-year payback, 28% ROI'"
    },
    {
      "name": "Quantify All Costs (Hidden and Obvious)",
      "description": "Create comprehensive cost breakdown including often-hidden costs",
      "for_business_context": "Incomplete cost analysis leads to failed projects. Stakeholders need to see total true cost",
      "cost_categories": [
        "Direct implementation costs",
        "Staff training and change management",
        "System integration and compatibility",
        "Ongoing support and maintenance",
        "Risk contingency (typically 10-20%)"
      ],
      "time_hours": 6,
      "cost": 0,
      "score_impact": 15
    }
  ],
  
  "tier_2_medium_fixes": [
    {
      "name": "Three-Scenario Financial Analysis",
      "description": "Model costs and benefits under optimistic, realistic, and pessimistic scenarios",
      "for_business_context": "Shows you've considered risk and uncertainty",
      "scenarios": [
        "Best case: Everything goes perfectly, achieve all benefits on timeline",
        "Realistic case: Some delays, some benefits achieved as expected",
        "Worst case: Major delays, fewer benefits, higher costs"
      ],
      "output": [
        "Side-by-side comparison",
        "Risk assessment for each scenario",
        "Decision framework (proceed despite worst case?)",
        "Mitigation strategies"
      ],
      "cost_range": {"min": 1000, "max": 3000},
      "timeline_hours": 8-12,
      "score_impact": 25,
      "decision_value": "Shows leadership you've thought through risks"
    },
    {
      "name": "Financial Benchmarking Against Industry Standards",
      "description": "Compare your project costs and ROI to similar industry projects",
      "for_business_context": "Investors want to know: Is this deal competitive?",
      "analysis": [
        "Research similar projects in your industry",
        "Compare cost per unit/metric",
        "Compare ROI percentages",
        "Identify where you're better/worse than average",
        "Explain why any differences exist"
      ],
      "cost_range": {"min": 2000, "max": 5000},
      "timeline_weeks": 2,
      "score_impact": 15,
      "credibility_boost": "Shows proposal is grounded in industry reality"
    }
  ],
  
  "tier_3_major_initiatives": [
    {
      "name": "Third-Party Financial Validation",
      "description": "Have external auditor or consultant validate financial assumptions",
      "for_business_context": "Large proposals ($1M+) often get independent validation",
      "validation_scope": [
        "Cost assumptions review",
        "Benefit projections assessment",
        "ROI calculation verification",
        "Risk analysis review",
        "Written validation report"
      ],
      "expert_needed": "Accounting firm or financial consultant",
      "cost_range": {"min": 5000, "max": 15000},
      "timeline_weeks": 3-4,
      "score_impact": 35,
      "decision_impact": "Often required to get board approval for major projects"
    }
  ],
  
  "key_metrics": "For business: Focus on ROI, payback period, cost per unit, and competitive positioning. Numbers drive decisions."
}
```

---

## Recommendation Engine Logic Flow

```
1. IDENTIFY ISSUE
   └─ What metric is low? (e.g., Economic Rigor)

2. DETECT DOCUMENT TYPE
   └─ What kind of document is this?
      (Legislation, Policy Report, News, Academic, Business)

3. ASSESS CRITICALITY FOR THIS DOCUMENT TYPE
   └─ For this document type, is this metric:
      CRITICAL? HIGH? MEDIUM? LOW? OPTIONAL?

4. FILTER RECOMMENDATIONS BY TYPE
   └─ Show only recommendations appropriate for this document type
      Remove inapplicable tiers/recommendations

5. RANK BY EFFORT vs. IMPACT
   └─ Prioritize quick wins
      Then medium fixes with high ROI
      Only suggest major initiatives if justified

6. PROVIDE TYPE-SPECIFIC CONTEXT
   └─ Explain why this matters for THIS document type
      Cite standards/expectations for this document type
      Provide type-relevant resources

7. ESTIMATE IMPACT
   └─ Calculate score improvement if recommendation implemented
      Adjusted for document type expectations
```

---

## Document Type Metric Relevance Matrix

```
                    Legislation  Policy   News  Academic  Business
Fiscal Trans.       CRITICAL     HIGH     MED   LOW       CRITICAL
Economic Rigor      CRITICAL     CRITICAL MED   CRITICAL  HIGH
Stakeholder Bal.    HIGH         CRITICAL CRIT  HIGH      MEDIUM
Public Accessib.    HIGH         MEDIUM   CRIT  LOW       MEDIUM
Policy Conseq.      CRITICAL     HIGH     MEDIUM HIGH      CRITICAL
Analytical Trans.   HIGH         CRITICAL MED   CRITICAL  MEDIUM

CRITICAL: Must fix to be credible in this document type
HIGH: Important, expect it, worth fixing
MEDIUM: Nice to have, helpful but not essential
LOW: Not really expected for this document type
OPTIONAL: Irrelevant to this document type
```

---

## Example Recommendation Set Generation

### Scenario: Economic Rigor Issue in a Bill (Legislation)

**Input:**
```
{
  "document_type": "legislation",
  "issue": "economic_rigor",
  "current_score": 3,
  "available_budget": 15000,
  "timeline_weeks": 8
}
```

**Generated Output:**
```
REMEDIATION RECOMMENDATIONS FOR BILL C-9
Document Type: LEGISLATION
Issue: Economic Rigor (Score: 3/100)

Criticality for Legislation: CRITICAL
Reasoning: Bills directly impact economic systems. Parliament and stakeholders expect 
rigorous economic analysis. Without this, bill is vulnerable to opposition critique.

────────────────────────────────────────────────────────────────────────────

TIER 1: QUICK WINS (Do These First - 0-2 weeks)
Recommended: YES - Will show good faith effort while you work on deeper analysis

□ Quick Win 1: Add Economic Impact Overview
  Time: 8 hours | Cost: $0 | Score impact: +8 points
  Why for bills: Demonstrates you've considered economic effects
  
□ Quick Win 2: Quantify Implementation Costs for Business Compliance
  Time: 12 hours | Cost: $0 | Score impact: +10 points
  Why for bills: Bills often impose new costs on businesses - must be transparent about these

Combined Quick Wins: 20 hours, $0, +18 point improvement
New projected score: 21/100

────────────────────────────────────────────────────────────────────────────

TIER 2: MEDIUM PRIORITY FIXES (Recommended - 2-8 weeks)
Recommended: YES - These are industry standard for bills

□ Medium Fix 1: Commission Economic Impact Analysis
  Time: 4-6 weeks | Cost: $8K-$15K | Score impact: +62 points
  Why for bills: Industry standard. Parliament and public expect this.
  Expert: Economist with policy modeling experience
  Timeline: Fits within your 8-week window
  
□ Medium Fix 2: Develop Government Fiscal Impact Analysis
  Time: 2-3 weeks | Cost: $3K-$8K | Score impact: +15 points
  Why for bills: Parliament scrutinizes government spending. Cost-benefit clear needed.
  
Combined Medium Fixes: 6-9 weeks, $11K-$23K, +77 point improvement
PROBLEM: Exceeds budget slightly, but core analysis ($8K) achievable

────────────────────────────────────────────────────────────────────────────

TIER 3: MAJOR INITIATIVES (Not recommended given timeline)
Recommended: NO - Would exceed budget and timeline
Only consider if: You can delay tabling bill by 4+ months

────────────────────────────────────────────────────────────────────────────

RECOMMENDED ROADMAP FOR YOUR SITUATION:

Week 1-2: Execute both Quick Wins
  Cost: $0 | New score: 21/100
  
Week 2-8: Commission Economic Impact Analysis
  Cost: $8K (within budget) | New score: 83/100
  Note: Medium Fix 2 (fiscal analysis) can be done in parallel at reduced scope
  
RESULT: Score improves from 3 → 83/100 in 8 weeks, $8K budget
Document becomes defensible on economic grounds
Ready for parliamentary review

────────────────────────────────────────────────────────────────────────────

SPECIFIC RESOURCES FOR LEGISLATION:

Economists who do policy modeling:
- RBC Economics (Toronto)
- Deloitte Economics & Policy
- University economists (often more affordable)

Cost-Benefit Analysis Resources:
- Treasury Board Cost-Benefit Analysis Guidelines
- Canadian CBA template
- Examples: Recent government bills with CBA attached

Next Steps:
1. Do quick wins immediately (0 cost, 20 hours)
2. Contact 2-3 economists for RFP and quotes
3. Begin parallel fiscal impact analysis
4. Target completion by Week 8
```

### Same Issue in a News Article

**Input:**
```
{
  "document_type": "news",
  "issue": "economic_rigor",
  "current_score": 3,
  "available_budget": 500,
  "timeline_days": 2
}
```

**Generated Output:**
```
REMEDIATION RECOMMENDATIONS FOR NEWS ARTICLE
Document Type: JOURNALISM
Issue: Economic Rigor (Score: 3/100)

Criticality for Journalism: MEDIUM
Reasoning: News articles should cite economic experts and data, but don't require original
analysis. Balance and accessibility matter more than analytical depth.

────────────────────────────────────────────────────────────────────────────

TIER 1: QUICK WINS (Strongly Recommended - Can do TODAY)

□ Quick Win 1: Add Quote from Economic Expert
  Time: 2-4 hours | Cost: $0 | Score impact: +15 points
  Why for news: Journalism standard. Expert commentary adds credibility.
  How: Call university economist, ask for 2-minute quote on economic implications
  
□ Quick Win 2: Add Economic Context
  Time: 1 hour | Cost: $0 | Score impact: +8 points
  Why for news: Helps readers understand scope and significance
  Examples: "Would cost $2M/year, equivalent to 50 teachers' salaries"
  
□ Quick Win 3: Link to Source Data
  Time: 1-2 hours | Cost: $0 | Score impact: +10 points
  Why for news: Readers can verify, improves trust
  
TOTAL QUICK WINS: 4-7 hours, $0, +33 point improvement
New score: 36/100

────────────────────────────────────────────────────────────────────────────

TIER 2: MEDIUM FIXES (Optional - If timeline allows)

□ Medium Fix 1: Interview Multiple Economists
  Time: 4-6 hours | Cost: $0-$500 | Score impact: +20 points
  Why for news: Balance is essential. Multiple perspectives show you did reporting.
  
New score if implemented: 56/100

────────────────────────────────────────────────────────────────────────────

TIER 3: Major Initiatives (NOT RECOMMENDED)
Skip this - Not appropriate for daily/weekly news timeline

────────────────────────────────────────────────────────────────────────────

RECOMMENDED FOR YOUR SITUATION:

Timeline: You have 2 days
Budget: $500
Best approach: Do ALL quick wins (7 hours, $0)

Expected result: Score 36/100 - MAJOR improvement
Timeline: Can complete by end of day tomorrow

If you have time: Add second economist quote for balance
Result: Score 56/100 - Very respectable for news article

THIS IS THE STANDARD JOURNALISM APPROACH - Don't expect or need deep economic analysis.
Expert quotes + context + source data = solid journalism
```

---

## Implementation Specification

### Database Structure Enhancement

```python
recommendation = {
    "id": "rec_001",
    "issue_key": "economic_rigor_missing_modeling",
    "metric": "ER",
    
    # Document type specificity
    "applicability_by_type": {
        "legislation": {
            "applies": True,
            "severity": "CRITICAL",
            "context": "Bills directly impact economic systems...",
            "tier_1_recommendations": ["list of tier 1 keys"],
            "tier_2_recommendations": ["list of tier 2 keys"],
            "tier_3_recommendations": ["list of tier 3 keys"],
            "resources_specific_to_type": {
                "examples": ["list of bills with economic analysis"],
                "standards": ["Parliamentary standards for economic analysis"],
                "templates": ["Government RFP templates"]
            }
        },
        "policy_report": {
            "applies": True,
            "severity": "HIGH",
            "context": "Policy reports are evidence-based...",
            # ... etc
        },
        "news": {
            "applies": True,
            "severity": "MEDIUM",
            "context": "News articles should cite experts...",
            # ... etc
        },
        "academic": {
            "applies": True,
            "severity": "CRITICAL",
            "context": "Academic papers require methodology...",
            # ... etc
        },
        "business": {
            "applies": True,
            "severity": "HIGH",
            "context": "Business documents need ROI clarity...",
            # ... etc
        }
    },
    
    # Tier 1 recommendations (varies by document type)
    "tier_1_recommendations": {
        "legislation": [
            {
                "name": "Add Economic Impact Overview",
                "steps": [...],
                "time": 8,
                "cost": 0,
                "impact": 8,
                "why_for_this_type": "Show you've considered economic effects"
            }
        ],
        "policy_report": [
            {
                "name": "Cite Existing Economic Research",
                "steps": [...],
                "why_for_this_type": "Reports don't need original analysis, cite research"
            }
        ],
        "news": [
            {
                "name": "Quote Economic Expert",
                "steps": [...],
                "why_for_this_type": "Journalism standard for credibility"
            }
        ]
        # ... etc for other types
    },
    
    # Tier 2 and Tier 3 similarly documented by document type
    
    "document_type_ranking": {
        # Importance of this fix across document types
        "legislation": 1,      # Most critical
        "academic": 2,
        "policy_report": 3,
        "business": 4,
        "news": 5             # Least critical
    }
}
```

### Engine Logic Pseudocode

```python
def generate_recommendations(analysis_results, document_type):
    """
    Generate document-type-aware recommendations
    """
    recommendations = []
    
    for issue in analysis_results.issues:
        # Get all recommendations for this issue
        all_recs = get_recommendation_templates(issue.key)
        
        # Filter for this document type
        for recommendation in all_recs:
            applicability = recommendation.applicability_by_type[document_type]
            
            if not applicability.applies:
                continue  # Skip - not relevant for this document type
            
            # Adapt recommendation for document type
            adapted_rec = {
                "issue": issue.key,
                "severity": applicability.severity,
                "context": applicability.context,
                "tier_1": filter_for_type(applicability.tier_1_recommendations),
                "tier_2": filter_for_type(applicability.tier_2_recommendations),
                "tier_3": filter_for_type(applicability.tier_3_recommendations),
                "resources": applicability.resources_specific_to_type
            }
            
            recommendations.append(adapted_rec)
    
    # Prioritize by severity for this document type
    recommendations = sort_by_severity(recommendations, document_type)
    
    return recommendations
```

---

## Benefits of Document-Type Awareness

1. **Relevance** - Only show recommendations that matter for this document type
2. **Efficiency** - Don't ask journalist to do economic modeling or academic to worry about public accessibility
3. **Accuracy** - Severity and criticality adjusted for context
4. **Resource Appropriateness** - Expert types and costs match document type needs
5. **Credibility** - Recommendations reflect actual standards for each document type
6. **User Satisfaction** - Users see recommendations that actually apply to their situation

---

## Conclusion

This document-type-aware approach transforms recommendations from generic to contextual. The same issue (e.g., low economic rigor) generates completely different guidance based on:

- What's actually needed for this document type
- What standards apply in this domain
- What's achievable within realistic constraints
- What will actually make a difference

**Result:** Users get actionable, relevant guidance instead of inappropriate suggestions.

---

**Document Status:** Ready for implementation

**Next Steps:** Integrate document type detection into recommendation engine and implement type-specific recommendation database

# Document-Type-Aware Remediation System - Implementation Architecture
## Sparrow SPOT Scale™ v8.6.1

**Document Version:** 1.0  
**Date:** December 8, 2025  
**Status:** Technical Implementation Guide  

---

## Executive Summary

The document-type-aware recommendation system is implemented through a **layered approach**:

1. **Detection Layer** - Identify document type from analysis
2. **Recommendation Database** - Store all recommendations organized by document type
3. **Filtering Layer** - Select only recommendations applicable to detected type
4. **Adaptation Layer** - Customize recommendations for specific type
5. **Output Layer** - Format and present recommendations

**Key Insight:** The complexity is hidden behind simple interfaces. Users see contextual recommendations automatically.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   Analysis Pipeline                             │
│  (sparrow_grader_v8.py produces analysis_results)              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  1. DOCUMENT TYPE DETECTION│
        │  • Extract from metadata   │
        │  • Detect from content     │
        │  • Use user input          │
        └────────────────┬───────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │  2. ISSUE IDENTIFICATION               │
        │  • Scores < thresholds                 │
        │  • Flags from analysis                 │
        │  • Contradictions detected             │
        └────────────────┬───────────────────────┘
                         │
                         ▼
        ┌───────────────────────────────────────────┐
        │  3. RECOMMENDATION DATABASE LOOKUP        │
        │  recommendations_db.json                 │
        │  Structure: {issue} → {document_type}    │
        │           → {tier_1, tier_2, tier_3}    │
        └────────────────┬────────────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────────────┐
        │  4. FILTERING & ADAPTATION               │
        │  • Filter for document type             │
        │  • Include type-specific context        │
        │  • Adjust severity/priority             │
        │  • Calculate score impact               │
        └────────────────┬─────────────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────────────┐
        │  5. PRIORITIZATION                       │
        │  • Sort by effort/impact ratio          │
        │  • Group by tier                         │
        │  • Build remediation roadmap             │
        └────────────────┬─────────────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────────────┐
        │  6. OUTPUT GENERATION                    │
        │  • Narrative format                      │
        │  • JSON for dashboard                    │
        │  • HTML interactive viewer               │
        │  • Markdown for reports                  │
        └──────────────────────────────────────────┘
```

---

## Component 1: Document Type Detection

### Location: New module `document_type_detector.py`

```python
"""
document_type_detector.py
Detects document type from analysis results and metadata
"""

import json
from typing import Optional, Dict
from enum import Enum

class DocumentType(Enum):
    """Enumeration of supported document types"""
    LEGISLATION = "legislation"
    POLICY_REPORT = "policy_report"
    NEWS = "news"
    ACADEMIC = "academic"
    BUSINESS = "business"
    UNKNOWN = "unknown"

class DocumentTypeDetector:
    """
    Detects document type using multiple signals
    """
    
    def __init__(self):
        """Initialize detector with patterns and keywords"""
        self.patterns = {
            DocumentType.LEGISLATION: {
                "keywords": ["bill", "act", "statute", "regulation", "parliament", 
                           "congress", "legislative", "law", "enact", "clause"],
                "patterns": [
                    r"^(Bill|Act|Regulation)\s+(C-|S-|H\.R\.|S\.)",
                    r"(Part|Section|Clause)\s+\d+",
                    r"(Royal Assent|Parliament|Legislature)"
                ]
            },
            DocumentType.POLICY_REPORT: {
                "keywords": ["white paper", "position paper", "report", "policy brief",
                           "analysis", "recommendations", "findings", "evidence"],
                "patterns": [
                    r"^(White Paper|Policy Brief|Report)",
                    r"Executive Summary",
                    r"Research Methodology"
                ]
            },
            DocumentType.NEWS: {
                "keywords": ["article", "breaking", "story", "investigation", 
                           "interview", "comment", "opinion", "news"],
                "patterns": [
                    r"^(Breaking|News|Analysis|Opinion):",
                    r"By\s+\w+\s+\w+",  # Byline pattern
                    r"(Share|Comment|Read More)"
                ]
            },
            DocumentType.ACADEMIC: {
                "keywords": ["abstract", "methodology", "literature review", "peer-review",
                           "hypothesis", "statistical", "research", "journal", "study"],
                "patterns": [
                    r"^(Abstract|Introduction|Literature Review)",
                    r"(p\s*<|statistical significance)",
                    r"(References|Bibliography)$"
                ]
            },
            DocumentType.BUSINESS: {
                "keywords": ["roi", "investment", "business case", "proposal",
                           "budget", "forecast", "executive summary", "stakeholder"],
                "patterns": [
                    r"^(Executive Summary|Business Case|Proposal)",
                    r"(\$|Cost|Budget|Investment|ROI)",
                    r"(Recommendation|Decision Required)"
                ]
            }
        }
    
    def detect(self, 
               analysis_results: Dict,
               user_specified_type: Optional[str] = None,
               document_name: str = "",
               document_text: str = "") -> DocumentType:
        """
        Detect document type using multiple signals
        
        Priority order:
        1. User-specified type (if provided)
        2. Metadata in analysis_results
        3. Document name pattern matching
        4. Text content analysis
        5. Default to UNKNOWN
        """
        
        # Signal 1: User-specified type (highest priority)
        if user_specified_type:
            try:
                return DocumentType(user_specified_type.lower())
            except ValueError:
                pass
        
        # Signal 2: Metadata in analysis results
        if "document_metadata" in analysis_results:
            if "document_type" in analysis_results["document_metadata"]:
                doc_type = analysis_results["document_metadata"]["document_type"]
                try:
                    return DocumentType(doc_type.lower())
                except ValueError:
                    pass
        
        # Signal 3: Document name pattern matching
        detected = self._detect_from_name(document_name)
        if detected != DocumentType.UNKNOWN:
            return detected
        
        # Signal 4: Text content analysis
        detected = self._detect_from_content(document_text)
        if detected != DocumentType.UNKNOWN:
            return detected
        
        # Default
        return DocumentType.UNKNOWN
    
    def _detect_from_name(self, document_name: str) -> DocumentType:
        """Detect type from filename/title"""
        name_lower = document_name.lower()
        
        for doc_type, patterns_dict in self.patterns.items():
            keywords = patterns_dict["keywords"]
            if any(keyword in name_lower for keyword in keywords):
                return doc_type
        
        return DocumentType.UNKNOWN
    
    def _detect_from_content(self, text: str, sample_size: int = 1000) -> DocumentType:
        """
        Detect type from document content
        Analyze first sample_size characters for efficiency
        """
        import re
        
        text_sample = text[:sample_size].lower()
        scores = {}
        
        for doc_type, patterns_dict in self.patterns.items():
            score = 0
            
            # Check keywords
            keywords = patterns_dict["keywords"]
            keyword_matches = sum(1 for kw in keywords if kw in text_sample)
            score += keyword_matches * 2
            
            # Check patterns
            patterns = patterns_dict["patterns"]
            for pattern in patterns:
                if re.search(pattern, text_sample, re.IGNORECASE):
                    score += 5
            
            scores[doc_type] = score
        
        # Return type with highest score (if any matches found)
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return DocumentType.UNKNOWN
    
    def confidence_score(self, doc_type: DocumentType, 
                        document_name: str, 
                        document_text: str) -> float:
        """
        Return confidence score 0-1 for the detected type
        Helps decide if we should ask user to confirm
        """
        confidence = 0.0
        checks = 0
        
        # Name analysis
        name_lower = document_name.lower()
        name_keywords = self.patterns[doc_type]["keywords"]
        if any(kw in name_lower for kw in name_keywords):
            confidence += 0.3
        checks += 1
        
        # Content analysis (sample)
        text_sample = document_text[:500].lower()
        content_keywords = self.patterns[doc_type]["keywords"]
        matches = sum(1 for kw in content_keywords if kw in text_sample)
        confidence += min(0.4, matches * 0.1)
        checks += 1
        
        # Return average confidence
        return confidence / checks if checks > 0 else 0.0


# Usage in sparrow_grader_v8.py
detector = DocumentTypeDetector()
doc_type = detector.detect(
    analysis_results=report_data,
    user_specified_type=user_provided_type,
    document_name=document_name,
    document_text=full_text
)
confidence = detector.confidence_score(doc_type, document_name, full_text)

if confidence < 0.5:
    # Ask user to confirm/override
    logging.warning(f"Low confidence on document type: {doc_type.value} ({confidence:.1%})")
```

---

## Component 2: Recommendation Database

### Location: New file `recommendations_database.json`

```json
{
  "recommendations": {
    "economic_rigor_missing_analysis": {
      "metric": "ER",
      "issue_name": "Low Economic Rigor",
      "issue_description": "Document lacks quantitative economic analysis",
      
      "applicability": {
        "legislation": {
          "applies": true,
          "severity": "CRITICAL",
          "context": "Bills directly impact economic systems. Parliament and stakeholders expect rigorous economic analysis.",
          "metric_rationale": "Economic rigor is essential for legislation - wrong assumptions lead to policy failure",
          "standard": "Government standard for bills: Economic impact analysis mandatory",
          "tier_1_applicable": true,
          "tier_2_applicable": true,
          "tier_3_applicable": true
        },
        "policy_report": {
          "applies": true,
          "severity": "HIGH",
          "context": "Policy reports are evidence-based. Economic claims must be backed by research or analysis.",
          "metric_rationale": "Decision-makers need to trust the economic reasoning",
          "standard": "Academic/policy standard: Claims must be cited or original analysis provided",
          "tier_1_applicable": true,
          "tier_2_applicable": true,
          "tier_3_applicable": false
        },
        "news": {
          "applies": true,
          "severity": "MEDIUM",
          "context": "News doesn't need original economic modeling, but should cite experts and data",
          "metric_rationale": "Readers benefit from expert context, but depth varies by story",
          "standard": "Journalism standard: Expert quotes, data citations, multiple perspectives",
          "tier_1_applicable": true,
          "tier_2_applicable": true,
          "tier_3_applicable": false
        },
        "academic": {
          "applies": true,
          "severity": "CRITICAL",
          "context": "Academic papers must demonstrate rigorous methodology. Economic claims require quantitative analysis.",
          "metric_rationale": "Peer reviewers expect rigorous methodology documentation",
          "standard": "Academic standard: Methodology documented, statistical testing, peer reviewable",
          "tier_1_applicable": true,
          "tier_2_applicable": true,
          "tier_3_applicable": true
        },
        "business": {
          "applies": true,
          "severity": "HIGH",
          "context": "Business documents need ROI clarity. Decision-makers must see financial case.",
          "metric_rationale": "Investors/executives need to understand return on investment",
          "standard": "Business standard: ROI calculation, cost-benefit analysis, risk assessment",
          "tier_1_applicable": true,
          "tier_2_applicable": true,
          "tier_3_applicable": false
        }
      },
      
      "tier_1": {
        "legislation": [
          {
            "id": "leg_er_t1_001",
            "name": "Add Economic Impact Overview",
            "description": "Write 1-2 page summary of expected economic effects based on available evidence",
            "steps": [
              "Review existing studies on similar policies",
              "Identify expected effects on GDP, employment, business costs",
              "Write narrative summary with caveats",
              "Add to policy document as Section 3"
            ],
            "time_estimate": {"value": 8, "unit": "hours"},
            "cost_estimate": {"min": 0, "max": 0, "currency": "CAD"},
            "score_impact": 8,
            "tools_needed": ["Google Scholar", "Government statistics databases"],
            "expertise_required": "Domain knowledge (no external hire)",
            "why_for_this_type": "Show Parliament you've considered economic impacts, even if detailed analysis pending",
            "effort_category": "internal"
          },
          {
            "id": "leg_er_t1_002",
            "name": "Quantify Implementation Costs for Business Compliance",
            "description": "Calculate and document all new compliance costs imposed on regulated entities",
            "steps": [
              "List all new requirements for businesses/organizations",
              "Estimate one-time implementation costs per type of entity",
              "Estimate ongoing compliance/reporting costs",
              "Create table showing cost impacts by sector"
            ],
            "time_estimate": {"value": 12, "unit": "hours"},
            "cost_estimate": {"min": 0, "max": 0, "currency": "CAD"},
            "score_impact": 10,
            "tools_needed": ["Excel", "Industry cost databases"],
            "expertise_required": "None",
            "why_for_this_type": "Bills impose compliance costs on others - must be transparent about these",
            "effort_category": "internal"
          }
        ],
        "policy_report": [
          {
            "id": "rep_er_t1_001",
            "name": "Cite Existing Economic Research",
            "description": "Find published studies supporting economic claims and cite them",
            "steps": [
              "Identify all economic claims in report",
              "Search for peer-reviewed research supporting each claim",
              "Add citations to footnotes/bibliography",
              "Add note explaining research basis"
            ],
            "time_estimate": {"value": 4, "unit": "hours"},
            "cost_estimate": {"min": 0, "max": 0, "currency": "CAD"},
            "score_impact": 12,
            "tools_needed": ["Google Scholar", "University library access"],
            "expertise_required": "Literature review skills",
            "why_for_this_type": "Reports don't need original analysis, but must cite evidence for claims",
            "effort_category": "internal"
          }
        ],
        "news": [
          {
            "id": "news_er_t1_001",
            "name": "Quote Economic Expert",
            "description": "Add quotes from economist or policy expert providing economic context",
            "steps": [
              "Identify 1-2 economists with relevant expertise",
              "Request quote about economic implications",
              "Integrate quote into article narrative",
              "Identify expert with credentials"
            ],
            "time_estimate": {"value": 2, "unit": "hours"},
            "cost_estimate": {"min": 0, "max": 0, "currency": "CAD"},
            "score_impact": 15,
            "tools_needed": ["Phone", "Email"],
            "expertise_required": "Journalism/source identification",
            "why_for_this_type": "Journalism standard: expert commentary adds credibility and analysis",
            "effort_category": "external_contact"
          }
        ],
        "academic": [
          {
            "id": "acad_er_t1_001",
            "name": "Document Economic Methodology Section",
            "description": "Write clear methodology section explaining how economic analysis was conducted",
            "steps": [
              "List data sources and definitions",
              "Document variables and their measurement",
              "Explain statistical methods used",
              "State all assumptions made",
              "Acknowledge limitations"
            ],
            "time_estimate": {"value": 8, "unit": "hours"},
            "cost_estimate": {"min": 0, "max": 0, "currency": "CAD"},
            "score_impact": 15,
            "tools_needed": ["Word processor", "Statistical software docs"],
            "expertise_required": "Research methodology knowledge",
            "why_for_this_type": "Peer reviewers need to understand and potentially replicate your analysis",
            "effort_category": "internal",
            "critical": true
          }
        ],
        "business": [
          {
            "id": "bus_er_t1_001",
            "name": "Add ROI Calculation and Payback Period",
            "description": "Calculate and display return on investment and payback timeline",
            "steps": [
              "Calculate total investment required",
              "Calculate annual benefits/savings",
              "Compute ROI percentage",
              "Calculate payback period",
              "Create summary table or chart"
            ],
            "time_estimate": {"value": 4, "unit": "hours"},
            "cost_estimate": {"min": 0, "max": 0, "currency": "CAD"},
            "score_impact": 20,
            "tools_needed": ["Excel", "Calculator"],
            "expertise_required": "Basic financial analysis",
            "why_for_this_type": "Decision-makers must see clear financial benefit to approve projects",
            "effort_category": "internal"
          }
        ]
      },
      
      "tier_2": {
        "legislation": [
          {
            "id": "leg_er_t2_001",
            "name": "Commission Economic Impact Analysis from Economist",
            "description": "Hire professional economist to model economic impacts",
            "scope": [
              "Gross Domestic Product (GDP) impact",
              "Employment impacts (jobs created/lost)",
              "Business cost analysis (especially small business)",
              "Sector-by-sector impacts",
              "Consumer impacts (price changes, access)",
              "Sensitivity analysis (what-if scenarios)"
            ],
            "expert_needed": {
              "type": "economist",
              "specialization": "Policy economics, economic modeling",
              "credentials": "PhD Economics preferred, policy experience required"
            },
            "cost_estimate": {"min": 8000, "max": 15000, "currency": "CAD"},
            "time_estimate": {"value": 4, "unit": "weeks"},
            "score_impact": 62,
            "deliverables": [
              "Economic impact model/spreadsheet",
              "Sensitivity analysis with scenarios",
              "Executive summary for policymakers",
              "Detailed technical report"
            ],
            "where_to_source": [
              "RBC Economics",
              "Deloitte Economics & Policy",
              "University economists (often more affordable)",
              "Economic consulting firms"
            ],
            "why_for_this_type": "Government and Parliament expect evidence-based economic analysis for bills",
            "effort_category": "external_hire",
            "critical_for_type": true,
            "when_to_do": "Before public consultation or parliamentary tabling"
          }
        ],
        "policy_report": [
          {
            "id": "rep_er_t2_001",
            "name": "Peer Review by Economist",
            "description": "Have economist review claims and verify economic reasoning",
            "scope": [
              "Verify economic claims are accurate",
              "Check citations are appropriate",
              "Suggest improvements or missing analysis",
              "Provide written peer review commentary",
              "Optional: Allow citation in report as validation"
            ],
            "expert_needed": {
              "type": "economist",
              "specialization": "Any relevant specialization",
              "credentials": "PhD Economics preferred"
            },
            "cost_estimate": {"min": 2000, "max": 5000, "currency": "CAD"},
            "time_estimate": {"value": 2, "unit": "weeks"},
            "score_impact": 25,
            "deliverables": [
              "Written peer review report",
              "Suggested improvements",
              "Credibility validation"
            ],
            "why_for_this_type": "Expert review boosts credibility of policy recommendations",
            "effort_category": "external_hire",
            "bonus": "Peer review can be cited as credibility validation"
          }
        ],
        "news": [
          {
            "id": "news_er_t2_001",
            "name": "Interview Multiple Economists on Economic Impact",
            "description": "Get perspectives from economists with different viewpoints",
            "scope": [
              "Industry economist (sees costs/burdens)",
              "University economist (academic perspective)",
              "Think tank economist (ideological perspective)"
            ],
            "cost_estimate": {"min": 0, "max": 500, "currency": "CAD"},
            "time_estimate": {"value": 4, "unit": "hours"},
            "score_impact": 20,
            "deliverables": [
              "Multiple quotes from different perspectives",
              "Balanced coverage of economic viewpoints",
              "Cited expert credentials"
            ],
            "why_for_this_type": "Shows you've explored multiple economic perspectives (journalism standard)",
            "effort_category": "external_contact"
          }
        ],
        "academic": [
          {
            "id": "acad_er_t2_001",
            "name": "Peer Review by Economist Specialist",
            "description": "Have economist review methodology and economic soundness",
            "scope": [
              "Methodology review",
              "Data analysis verification",
              "Statistical testing appropriateness",
              "Interpretation of results",
              "Limitations assessment"
            ],
            "expert_needed": {
              "type": "economist",
              "specialization": "Your field of study",
              "credentials": "PhD Economics required"
            },
            "cost_estimate": {"min": 2000, "max": 5000, "currency": "CAD"},
            "time_estimate": {"value": 3, "unit": "weeks"},
            "score_impact": 30,
            "deliverables": [
              "Peer review report with recommendations",
              "Methodology validation",
              "Improvement suggestions"
            ],
            "why_for_this_type": "Peer review is requirement for academic publication - get feedback before submitting",
            "effort_category": "external_hire",
            "critical_for_type": true
          }
        ],
        "business": [
          {
            "id": "bus_er_t2_001",
            "name": "Three-Scenario Financial Analysis",
            "description": "Model costs and benefits under optimistic, realistic, and pessimistic scenarios",
            "scope": [
              "Best case scenario with assumptions",
              "Realistic case scenario with assumptions",
              "Worst case scenario with assumptions",
              "Risk assessment for each scenario",
              "Decision framework",
              "Mitigation strategies"
            ],
            "cost_estimate": {"min": 1000, "max": 3000, "currency": "CAD"},
            "time_estimate": {"value": 1, "unit": "weeks"},
            "score_impact": 25,
            "deliverables": [
              "Scenario comparison spreadsheet",
              "Risk assessment matrix",
              "Decision framework document",
              "Mitigation plan"
            ],
            "why_for_this_type": "Shows leadership you've thought through risks and uncertainty",
            "effort_category": "internal_or_consultant"
          }
        ]
      },
      
      "tier_3": {
        "legislation": [
          {
            "id": "leg_er_t3_001",
            "name": "Comprehensive Economic Analysis and Modeling",
            "description": "Full economic impact study with multiple scenarios",
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
            "cost_estimate": {"min": 25000, "max": 50000, "currency": "CAD"},
            "time_estimate": {"value": 12, "unit": "weeks"},
            "score_impact": 80,
            "expected_outcome": "Policy becomes defensible on economic grounds, publication-ready analysis",
            "effort_category": "external_hire_major"
          }
        ],
        "academic": [
          {
            "id": "acad_er_t3_001",
            "name": "Major Methodological Revision and Re-analysis",
            "description": "Redesign study with more rigorous methodology and larger dataset",
            "scope": [
              "Study redesign",
              "Larger or more representative sample",
              "More rigorous statistical methods",
              "Longer study period",
              "Multiple analysis approaches"
            ],
            "cost_estimate": {"min": 10000, "max": 30000, "currency": "CAD"},
            "time_estimate": {"value": 12, "unit": "weeks"},
            "score_impact": 75,
            "when_needed": "If initial analysis has major methodological problems",
            "effort_category": "external_hire_major"
          }
        ]
      }
    }
    
    // More issues follow same structure...
    // "stakeholder_balance_missing_perspectives": {...},
    // "fiscal_transparency_hidden_costs": {...},
    // etc.
  }
}
```

---

## Component 3: Recommendation Filtering Engine

### Location: New module `recommendation_filter.py`

```python
"""
recommendation_filter.py
Filters and adapts recommendations based on document type
"""

from typing import List, Dict, Optional
from document_type_detector import DocumentType
import json

class RecommendationFilter:
    """
    Filters recommendations from database based on document type
    """
    
    def __init__(self, recommendations_db_path: str):
        """Load recommendations database"""
        with open(recommendations_db_path, 'r') as f:
            self.db = json.load(f)
    
    def get_recommendations_for_type(self,
                                     issue_key: str,
                                     doc_type: DocumentType) -> Dict:
        """
        Get all applicable recommendations for an issue in a specific document type
        
        Returns filtered and adapted recommendations object
        """
        
        if issue_key not in self.db["recommendations"]:
            return None
        
        issue = self.db["recommendations"][issue_key]
        
        # Check if this issue applies to this document type
        type_name = doc_type.value
        if type_name not in issue["applicability"]:
            return None
        
        applicability = issue["applicability"][type_name]
        if not applicability["applies"]:
            return None
        
        # Build filtered recommendation set
        filtered_rec = {
            "issue_key": issue_key,
            "metric": issue["metric"],
            "issue_name": issue["issue_name"],
            "document_type": type_name,
            "severity": applicability["severity"],
            "context": applicability["context"],
            "metric_rationale": applicability["metric_rationale"],
            "standard": applicability["standard"],
            "tiers": {}
        }
        
        # Include applicable tiers
        for tier in [1, 2, 3]:
            tier_key = f"tier_{tier}"
            
            if tier_key not in issue:
                continue
            
            if not applicability.get(f"tier_{tier}_applicable", False):
                continue
            
            # Get type-specific recommendations for this tier
            if type_name in issue[tier_key]:
                filtered_rec["tiers"][tier] = {
                    "recommendations": issue[tier_key][type_name],
                    "count": len(issue[tier_key][type_name])
                }
        
        return filtered_rec
    
    def get_all_issues_for_type(self,
                                issues: List[str],
                                doc_type: DocumentType,
                                scores: Dict) -> List[Dict]:
        """
        Get all relevant recommendations for all detected issues
        """
        
        recommendations = []
        
        for issue_key in issues:
            rec = self.get_recommendations_for_type(issue_key, doc_type)
            if rec:
                # Add current score to context
                if rec["metric"] in scores:
                    rec["current_score"] = scores[rec["metric"]]
                
                recommendations.append(rec)
        
        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(
            key=lambda r: severity_order.get(r["severity"], 999)
        )
        
        return recommendations
    
    def calculate_roadmap(self,
                         recommendations: List[Dict],
                         budget_limit: Optional[float] = None,
                         timeline_weeks: Optional[int] = None) -> Dict:
        """
        Build phased remediation roadmap
        
        Considers:
        - Budget constraints
        - Timeline constraints
        - Effort vs. impact trade-offs
        - Tier priorities
        """
        
        roadmap = {
            "current_state": {},
            "phases": [],
            "summary": {}
        }
        
        # Analyze constraints
        can_do_tier_1 = True  # Always doable
        can_do_tier_2 = (budget_limit is None or budget_limit >= 2000) and \
                        (timeline_weeks is None or timeline_weeks >= 2)
        can_do_tier_3 = (budget_limit is None or budget_limit >= 15000) and \
                        (timeline_weeks is None or timeline_weeks >= 8)
        
        # Build phases
        all_recs = []
        
        # Gather all recommendations by tier
        tier_1_recs = []
        tier_2_recs = []
        tier_3_recs = []
        
        for rec_set in recommendations:
            for tier, tier_data in rec_set.get("tiers", {}).items():
                for individual_rec in tier_data["recommendations"]:
                    if tier == 1:
                        tier_1_recs.append((rec_set, individual_rec))
                    elif tier == 2:
                        tier_2_recs.append((rec_set, individual_rec))
                    elif tier == 3:
                        tier_3_recs.append((rec_set, individual_rec))
        
        # Phase 1: Quick Wins
        phase_1 = {
            "name": "Quick Wins",
            "tier": 1,
            "duration_weeks": 2,
            "total_cost": 0,
            "recommendations": [r[1] for r in tier_1_recs],
            "expected_score_improvement": sum(r[1].get("score_impact", 0) for r in tier_1_recs),
            "recommended": True
        }
        roadmap["phases"].append(phase_1)
        
        # Phase 2: Medium Fixes (if possible)
        if can_do_tier_2:
            phase_2 = {
                "name": "Medium Priority Fixes",
                "tier": 2,
                "duration_weeks": 6,
                "total_cost_min": sum(r[1].get("cost_estimate", {}).get("min", 0) 
                                     for r in tier_2_recs),
                "total_cost_max": sum(r[1].get("cost_estimate", {}).get("max", 0) 
                                     for r in tier_2_recs),
                "recommendations": [r[1] for r in tier_2_recs],
                "expected_score_improvement": sum(r[1].get("score_impact", 0) 
                                                 for r in tier_2_recs),
                "recommended": True
            }
            roadmap["phases"].append(phase_2)
        
        # Phase 3: Major Initiatives (if possible)
        if can_do_tier_3:
            phase_3 = {
                "name": "Major Initiatives",
                "tier": 3,
                "duration_weeks": 12,
                "total_cost_min": sum(r[1].get("cost_estimate", {}).get("min", 0) 
                                     for r in tier_3_recs),
                "total_cost_max": sum(r[1].get("cost_estimate", {}).get("max", 0) 
                                     for r in tier_3_recs),
                "recommendations": [r[1] for r in tier_3_recs],
                "expected_score_improvement": sum(r[1].get("score_impact", 0) 
                                                 for r in tier_3_recs),
                "recommended": False  # Only if justified
            }
            roadmap["phases"].append(phase_3)
        
        return roadmap


# Usage in sparrow_grader_v8.py
from recommendation_filter import RecommendationFilter

filter_engine = RecommendationFilter("./recommendations_database.json")

# Get all recommendations for detected issues
recommendations = filter_engine.get_all_issues_for_type(
    issues=detected_issue_keys,
    doc_type=detected_document_type,
    scores=report_data["scores"]
)

# Build roadmap considering constraints
roadmap = filter_engine.calculate_roadmap(
    recommendations=recommendations,
    budget_limit=client_budget,
    timeline_weeks=client_timeline
)
```

---

## Component 4: Output Generation

### Location: Modified `narrative_engine.py`

```python
"""
Modified narrative_engine.py to include remediation recommendations
"""

def generate_narrative_with_recommendations(analysis_results, doc_type):
    """
    Generate narrative that includes remediation recommendations
    """
    
    # Existing narrative generation...
    narrative = generate_base_narrative(analysis_results)
    
    # NEW: Add remediation section
    if REMEDIATION_ENGINE_AVAILABLE:
        from recommendation_filter import RecommendationFilter
        
        detector = DocumentTypeDetector()
        filter_engine = RecommendationFilter("./recommendations_database.json")
        
        # Get recommendations for this document type
        recommendations = filter_engine.get_all_issues_for_type(
            issues=analysis_results["detected_issues"],
            doc_type=doc_type,
            scores=analysis_results["scores"]
        )
        
        # Build roadmap
        roadmap = filter_engine.calculate_roadmap(recommendations)
        
        # Format as narrative section
        remediation_section = format_recommendations_as_narrative(
            recommendations=recommendations,
            roadmap=roadmap,
            doc_type=doc_type
        )
        
        # Append to narrative
        narrative += "\n\n" + remediation_section
    
    return narrative


def format_recommendations_as_narrative(recommendations, roadmap, doc_type):
    """
    Convert structured recommendations to narrative prose
    """
    
    output = "## Remediation Recommendations\n\n"
    
    # Add context about what these recommendations are based on
    output += f"### For {doc_type.value.replace('_', ' ').title()} Documents\n\n"
    
    # Add each recommendation in narrative form
    for rec_set in recommendations:
        output += f"### {rec_set['issue_name']}\n\n"
        output += f"**Severity for this document type:** {rec_set['severity']}\n"
        output += f"**Why this matters:** {rec_set['context']}\n\n"
        
        # Tier 1 recommendations
        if 1 in rec_set.get("tiers", {}):
            output += "#### Quick Wins (Do These First)\n\n"
            for rec in rec_set["tiers"][1]["recommendations"]:
                output += format_single_recommendation(rec, doc_type)
        
        # Tier 2 recommendations
        if 2 in rec_set.get("tiers", {}):
            output += "#### Medium Priority Fixes\n\n"
            for rec in rec_set["tiers"][2]["recommendations"]:
                output += format_single_recommendation(rec, doc_type)
        
        # Tier 3 recommendations
        if 3 in rec_set.get("tiers", {}):
            output += "#### Major Initiatives\n\n"
            for rec in rec_set["tiers"][3]["recommendations"]:
                output += format_single_recommendation(rec, doc_type)
    
    # Add roadmap
    output += format_roadmap_as_narrative(roadmap)
    
    return output


def format_single_recommendation(rec, doc_type):
    """Format individual recommendation as prose"""
    
    output = f"**{rec['name']}**\n"
    output += f"{rec['description']}\n\n"
    
    output += f"- Time: {rec['time_estimate']['value']} {rec['time_estimate']['unit']}\n"
    output += f"- Cost: ${rec['cost_estimate']['min']:,}-${rec['cost_estimate']['max']:,}\n"
    output += f"- Score Impact: +{rec['score_impact']} points\n"
    output += f"- Effort Level: {rec['effort_category']}\n"
    output += f"- **Why for {doc_type}:** {rec['why_for_this_type']}\n\n"
    
    return output


def format_roadmap_as_narrative(roadmap):
    """Format remediation roadmap as prose"""
    
    output = "## Implementation Roadmap\n\n"
    
    for phase in roadmap["phases"]:
        output += f"### Phase {phase['tier']}: {phase['name']}\n\n"
        output += f"Duration: {phase.get('duration_weeks', 'TBD')} weeks\n"
        output += f"Cost: ${phase.get('total_cost_min', 0):,}-${phase.get('total_cost_max', 0):,}\n"
        output += f"Expected Score Improvement: +{phase['expected_score_improvement']} points\n"
        output += f"Recommended: {'Yes' if phase['recommended'] else 'No'}\n\n"
    
    return output
```

---

## Component 5: Integration into Pipeline

### Modified `sparrow_grader_v8.py`

```python
# Around line 40 - Add imports
try:
    from document_type_detector import DocumentTypeDetector
    from recommendation_filter import RecommendationFilter
    REMEDIATION_ENGINE_AVAILABLE = True
except ImportError:
    REMEDIATION_ENGINE_AVAILABLE = False
    logging.warning("Remediation engine not available")

# Around line 3400 - After analysis complete, generate recommendations
if REMEDIATION_ENGINE_AVAILABLE:
    try:
        # Detect document type
        detector = DocumentTypeDetector()
        document_type = detector.detect(
            analysis_results=report_data,
            document_name=document_name,
            document_text=full_text
        )
        
        confidence = detector.confidence_score(
            document_type, 
            document_name, 
            full_text
        )
        
        if confidence < 0.5:
            logging.warning(
                f"Low confidence document type detection: "
                f"{document_type.value} ({confidence:.1%})"
            )
        
        # Generate type-aware recommendations
        filter_engine = RecommendationFilter("./recommendations_database.json")
        recommendations = filter_engine.get_all_issues_for_type(
            issues=report_data.get("detected_issue_keys", []),
            doc_type=document_type,
            scores=report_data.get("scores", {})
        )
        
        # Build remediation roadmap
        roadmap = filter_engine.calculate_roadmap(recommendations)
        
        # Add to report data
        report_data["document_type"] = document_type.value
        report_data["type_confidence"] = confidence
        report_data["remediation_recommendations"] = recommendations
        report_data["remediation_roadmap"] = roadmap
        
        logging.info(
            f"Generated {len(recommendations)} recommendation sets "
            f"for {document_type.value}"
        )
        
    except Exception as e:
        logging.error(f"Remediation recommendation generation failed: {e}")
        # Continue without recommendations
```

---

## File Structure Summary

```
Sparrow-SPOT-Policy/
├── document_type_detector.py          (NEW - 200 lines)
├── recommendation_filter.py           (NEW - 250 lines)
├── recommendations_database.json      (NEW - 5000+ lines)
├── narrative_engine.py                (MODIFIED - Add recommendation formatting)
├── sparrow_grader_v8.py               (MODIFIED - Integrate detection/filtering)
├── investigation_index_generator.py   (MODIFIED - Add recommendations tab)
└── docs/
    ├── REMEDIATION_RECOMMENDATION_SYSTEM.md
    ├── DOCUMENT_TYPE_AWARE_RECOMMENDATIONS.md
    └── DOCUMENT_TYPE_AWARE_IMPLEMENTATION.md (this file)
```

---

## Data Flow Example

```
USER UPLOADS BILL-C9

                    ↓
        
    sparrow_grader_v8.py runs analysis
    ├─ Scores: ER=3, FT=3, SB=56, PA=75, PC=42, AT=20
    └─ Issues: ["economic_rigor_missing_analysis", "fiscal_transparency_hidden_costs"]
    
                    ↓
        
    DocumentTypeDetector.detect()
    ├─ Name contains "Bill", "C-", "parliament" → Probable LEGISLATION
    ├─ Text contains "clause", "enact", "regulation" → Confirms LEGISLATION
    ├─ Confidence: 0.85 (High)
    └─ Result: DocumentType.LEGISLATION
    
                    ↓
        
    RecommendationFilter.get_all_issues_for_type()
    ├─ Issue: economic_rigor_missing_analysis
    │  └─ Get recommendations for LEGISLATION
    │     ├─ Severity: CRITICAL (not MEDIUM like for news)
    │     ├─ Tier 1: Add Economic Impact Overview, Quantify Compliance Costs
    │     ├─ Tier 2: Commission economist, develop CBA
    │     └─ Tier 3: Comprehensive economic analysis
    │
    └─ Issue: fiscal_transparency_hidden_costs
       └─ Get recommendations for LEGISLATION
          ├─ Severity: CRITICAL
          ├─ Tier 1: Add cost breakdown table
          ├─ Tier 2: Commission fiscal impact analysis
          └─ Tier 3: Independent financial audit
    
                    ↓
        
    RecommendationFilter.calculate_roadmap()
    ├─ Constraints: Budget $15K, Timeline 8 weeks
    ├─ Phase 1 (Week 1-2): Quick wins, $0, +18 pts
    ├─ Phase 2 (Week 2-8): Commission economist, $8K, +62 pts
    └─ Result: 31.7 → 83.0 in 8 weeks with $8K
    
                    ↓
        
    narrative_engine.generate_narrative_with_recommendations()
    ├─ Base narrative + 
    └─ Recommendations section organized by issue/tier/type
    
                    ↓
        
    Output files:
    ├─ Bill-C9-00.json (includes recommendations)
    ├─ Bill-C9-00_narrative.txt (includes recommendations)
    ├─ Bill-C9-00_publish.md (includes recommendations)
    └─ index.html (new "Recommendations" tab with interactive UI)
```

---

## Complexity Management

The system manages complexity through **abstraction layers**:

| Complexity | Hidden By | User Experience |
|-----------|-----------|-----------------|
| Document type detection algorithms | DocumentTypeDetector class | Automatic, invisible |
| 5000+ line JSON database | RecommendationFilter class | Simple queries |
| Filtering logic (5 types × 3 tiers) | get_all_issues_for_type() | Single function call |
| Roadmap building logic | calculate_roadmap() | Single function call |
| Integration points | sparrow_grader_v8.py | Standard imports |
| Output formatting | narrative_engine.py | Existing workflow |

---

## Error Handling

```python
# All components include graceful fallbacks

try:
    doc_type = detector.detect(...)
    if confidence < 0.5:
        logging.warning("Low confidence, using default")
        doc_type = DocumentType.UNKNOWN
except Exception as e:
    logging.error(f"Detection failed: {e}")
    doc_type = DocumentType.UNKNOWN
    # Continue without type-specific recommendations

try:
    recommendations = filter_engine.get_all_issues_for_type(...)
except Exception as e:
    logging.error(f"Recommendation generation failed: {e}")
    recommendations = []
    # Continue without recommendations (graceful degradation)

# Analysis and narrative generation ALWAYS completes
# Recommendations are OPTIONAL enhancement
```

---

## Testing Strategy

```
test_document_type_detector.py
├─ Test legislation detection (bills, acts, regulations)
├─ Test policy report detection
├─ Test news article detection
├─ Test academic paper detection
└─ Test business document detection

test_recommendation_filter.py
├─ Test filtering for each document type
├─ Test recommendation retrieval
├─ Test roadmap building with constraints
└─ Test score impact calculations

test_end_to_end_recommendations.py
├─ Run analysis on Bill C-9
├─ Detect document type
├─ Generate recommendations
├─ Verify recommendation structure
└─ Verify output formats
```

---

## Summary

The document-type-aware system manages complexity through:

1. **Modular architecture** - Each component has single responsibility
2. **Database-driven** - All recommendations in structured JSON
3. **Simple interfaces** - Complex logic hidden behind clean APIs
4. **Graceful degradation** - Works without recommendations if needed
5. **Abstraction layers** - User never sees complexity

**Result:** Despite handling 5 document types × 6 metrics × 3 tiers = 90 combinations, the system is maintainable, testable, and extensible.

---

**Status:** Ready for implementation

**Next Steps:**
1. Create recommendations_database.json with all issue/type combinations
2. Implement document_type_detector.py
3. Implement recommendation_filter.py
4. Integrate into sparrow_grader_v8.py
5. Test end-to-end

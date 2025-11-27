"""
NIST AI Risk Management Framework Integration for SPOT-Policy™ v7.0

Classifies evaluation tasks by risk tier and activates appropriate controls.
Implements NIST AI RMF 1.0: Govern, Map, Measure, Manage functions

Pillar 2 Component: Risk Classification & Control Activation

Author: SPOT-Policy™ v7.0 Ethical Framework
Date: November 13, 2025
"""

from typing import Dict, List, Tuple
from enum import Enum
from datetime import datetime


class RiskTier(Enum):
    """NIST Risk Tiers for AI System Classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NISTRiskMapper:
    """
    Maps policy evaluation tasks to risk tiers and activates controls.
    Based on NIST AI RMF 1.0 (Govern, Map, Measure, Manage)
    """
    
    def __init__(self):
        self.version = "1.0"
        self.framework = "NIST AI RMF 1.0"
        self.functions = ["Govern", "Map", "Measure", "Manage"]
    
    def classify(self, document_characteristics: Dict) -> Dict:
        """
        Classify evaluation task by risk tier.
        
        Input:
        {
            "task": "policy_scoring",
            "document_type": "budget" | "regulation" | "memo" | ...,
            "scope": "national" | "departmental" | "local",
            "decision_criticality": "strategic" | "operational" | "informational",
            "affected_population": int,  # Estimated number of people affected
            "budget_impact": float,  # Estimated budget impact in millions
            "timeline": "immediate" | "medium_term" | "long_term"
        }
        
        Output:
        {
            "risk_tier": "low" | "medium" | "high",
            "risk_score": 0-100,
            "required_controls": [...],
            "nist_functions_activated": [...],
            "explanation": str,
            "timestamp": ISO8601
        }
        """
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(document_characteristics)
        
        # Classify into tier
        risk_tier = self._classify_tier(risk_score)
        
        # Activate controls based on tier
        required_controls = self._activate_controls(risk_tier)
        nist_functions = self._activate_nist_functions(risk_tier)
        
        explanation = self._generate_explanation(risk_tier, risk_score, document_characteristics)
        
        return {
            "risk_tier": risk_tier.value,
            "risk_score": round(risk_score, 1),
            "required_controls": required_controls,
            "nist_functions_activated": nist_functions,
            "explanation": explanation,
            "framework": self.framework,
            "version": self.version,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _calculate_risk_score(self, characteristics: Dict) -> float:
        """
        Calculate composite risk score (0-100).
        
        Factors:
        - Document type (budget/regulation high-risk)
        - Scope (national high-risk, local low-risk)
        - Decision criticality (strategic high-risk)
        - Affected population (larger = higher risk)
        - Budget impact (larger = higher risk)
        - Timeline (immediate = higher risk)
        """
        
        score = 0.0
        
        # Document type score (0-25)
        document_type = characteristics.get("document_type", "").lower()
        if document_type in ["budget", "financial_policy", "regulation", "legislation"]:
            score += 25
        elif document_type in ["strategy", "framework", "plan"]:
            score += 20
        elif document_type in ["memo", "brief", "analysis"]:
            score += 10
        else:
            score += 5
        
        # Scope score (0-25)
        scope = characteristics.get("scope", "").lower()
        if scope == "national":
            score += 25
        elif scope == "regional":
            score += 15
        elif scope == "departmental":
            score += 10
        elif scope == "local":
            score += 5
        
        # Decision criticality score (0-20)
        criticality = characteristics.get("decision_criticality", "").lower()
        if criticality == "strategic":
            score += 20
        elif criticality == "operational":
            score += 10
        elif criticality == "informational":
            score += 5
        
        # Affected population score (0-15)
        population = characteristics.get("affected_population", 0)
        if population > 1000000:
            score += 15
        elif population > 100000:
            score += 12
        elif population > 10000:
            score += 8
        elif population > 1000:
            score += 4
        
        # Budget impact score (0-10)
        budget_impact = characteristics.get("budget_impact", 0)
        if budget_impact > 1000:  # > $1B
            score += 10
        elif budget_impact > 100:  # > $100M
            score += 8
        elif budget_impact > 10:  # > $10M
            score += 5
        elif budget_impact > 0:
            score += 2
        
        # Timeline score (0-5)
        timeline = characteristics.get("timeline", "").lower()
        if timeline == "immediate":
            score += 5
        elif timeline == "medium_term":
            score += 3
        elif timeline == "long_term":
            score += 1
        
        return min(score, 100.0)
    
    def _classify_tier(self, risk_score: float) -> RiskTier:
        """
        Classify risk score into tier.
        - 0-30: LOW
        - 31-65: MEDIUM
        - 66-100: HIGH
        """
        if risk_score <= 30:
            return RiskTier.LOW
        elif risk_score <= 65:
            return RiskTier.MEDIUM
        else:
            return RiskTier.HIGH
    
    def _activate_controls(self, risk_tier: RiskTier) -> List[str]:
        """
        Activate controls based on risk tier.
        Controls enforce governance requirements.
        """
        
        if risk_tier == RiskTier.LOW:
            return [
                "basic_logging",
                "version_control",
                "optional_explainability"
            ]
        
        elif risk_tier == RiskTier.MEDIUM:
            return [
                "comprehensive_logging",
                "bias_audit_basic",
                "explainability_lime",
                "error_tracking",
                "performance_monitoring",
                "stakeholder_notification"
            ]
        
        else:  # HIGH
            return [
                "comprehensive_logging",
                "bias_audit_comprehensive",
                "explainability_shap_mandatory",
                "error_tracking_detailed",
                "performance_monitoring_intensive",
                "stakeholder_notification_mandatory",
                "human_review_mandatory",
                "audit_trail_detailed",
                "trust_score_calculation",
                "adversarial_testing",
                "impact_assessment",
                "remediation_planning"
            ]
    
    def _activate_nist_functions(self, risk_tier: RiskTier) -> List[Dict]:
        """
        Activate NIST AI RMF functions based on risk tier.
        
        NIST AI RMF 1.0 Functions:
        1. Govern - Establish organizational policies
        2. Map - Understand AI system context & risks
        3. Measure - Assess AI system performance
        4. Manage - Mitigate identified risks
        """
        
        if risk_tier == RiskTier.LOW:
            return [
                {
                    "name": "Govern",
                    "status": "activated",
                    "actions": [
                        "Document AI use case"
                    ]
                },
                {
                    "name": "Map",
                    "status": "activated",
                    "actions": [
                        "Identify input/output characteristics"
                    ]
                }
            ]
        
        elif risk_tier == RiskTier.MEDIUM:
            return [
                {
                    "name": "Govern",
                    "status": "activated",
                    "actions": [
                        "Document AI use case",
                        "Define AI governance roles",
                        "Establish escalation procedures"
                    ]
                },
                {
                    "name": "Map",
                    "status": "activated",
                    "actions": [
                        "Identify input/output characteristics",
                        "Map risk categories",
                        "Document AI system assumptions"
                    ]
                },
                {
                    "name": "Measure",
                    "status": "activated",
                    "actions": [
                        "Measure performance metrics",
                        "Assess bias levels",
                        "Calculate fairness ratios"
                    ]
                }
            ]
        
        else:  # HIGH
            return [
                {
                    "name": "Govern",
                    "status": "activated",
                    "actions": [
                        "Document AI use case",
                        "Define AI governance roles",
                        "Establish escalation procedures",
                        "Develop impact mitigation strategy",
                        "Plan stakeholder engagement"
                    ]
                },
                {
                    "name": "Map",
                    "status": "activated",
                    "actions": [
                        "Identify input/output characteristics",
                        "Map risk categories comprehensively",
                        "Document AI system assumptions",
                        "Assess external dependencies",
                        "Evaluate regulatory context"
                    ]
                },
                {
                    "name": "Measure",
                    "status": "activated",
                    "actions": [
                        "Measure performance metrics comprehensively",
                        "Assess bias levels (DIR, EOD, SPD)",
                        "Calculate fairness ratios",
                        "Perform adversarial testing",
                        "Generate explainability metrics",
                        "Monitor for drift"
                    ]
                },
                {
                    "name": "Manage",
                    "status": "activated",
                    "actions": [
                        "Develop risk mitigation plans",
                        "Implement control measures",
                        "Plan for human oversight",
                        "Establish incident response",
                        "Schedule regular audits",
                        "Document all decisions"
                    ]
                }
            ]
    
    def _generate_explanation(self, risk_tier: RiskTier, risk_score: float, 
                             characteristics: Dict) -> str:
        """Generate human-readable explanation of classification."""
        
        explanation = f"Risk Classification: {risk_tier.value.upper()} (Score: {risk_score}/100)\n\n"
        
        # Add risk drivers
        explanation += "Risk Drivers:\n"
        
        doc_type = characteristics.get("document_type", "Unknown")
        explanation += f"• Document Type: {doc_type}\n"
        
        scope = characteristics.get("scope", "Unknown")
        explanation += f"• Scope: {scope}\n"
        
        criticality = characteristics.get("decision_criticality", "Unknown")
        explanation += f"• Decision Criticality: {criticality}\n"
        
        affected = characteristics.get("affected_population", 0)
        if affected > 0:
            explanation += f"• Estimated Affected Population: {affected:,}\n"
        
        budget = characteristics.get("budget_impact", 0)
        if budget > 0:
            explanation += f"• Budget Impact: ${budget}M\n"
        
        # Add interpretation
        if risk_tier == RiskTier.LOW:
            explanation += "\nInterpretation:\n"
            explanation += "This evaluation task has LOW impact. Standard AI governance applies.\n"
            explanation += "Basic logging and version control are required.\n"
            explanation += "Explainability is optional.\n"
        
        elif risk_tier == RiskTier.MEDIUM:
            explanation += "\nInterpretation:\n"
            explanation += "This evaluation task has MEDIUM impact. Enhanced AI governance applies.\n"
            explanation += "Bias auditing, basic explainability, and stakeholder notification required.\n"
            explanation += "Human review is recommended for final decisions.\n"
        
        else:  # HIGH
            explanation += "\nInterpretation:\n"
            explanation += "This evaluation task has HIGH impact. COMPREHENSIVE AI governance applies.\n"
            explanation += "NIST AI RMF 1.0 fully activated: Govern, Map, Measure, Manage.\n"
            explanation += "Mandatory: Bias audit, SHAP explainability, human review, audit trail.\n"
            explanation += "This analysis MUST be reviewed by a human expert before use.\n"
        
        explanation += "\nRecommendation:\n"
        if risk_tier == RiskTier.LOW:
            explanation += "✓ Proceed with standard analysis process."
        elif risk_tier == RiskTier.MEDIUM:
            explanation += "⚠ Proceed with analysis. Plan for human review of results."
        else:  # HIGH
            explanation += "⚠ Proceed with analysis AND mandatory human expert review."
        
        return explanation


class ControlActivationManager:
    """
    Manages activation and execution of controls based on risk tier.
    """
    
    def __init__(self, risk_tier: str):
        self.risk_tier = risk_tier
        self.controls = self._get_controls_for_tier(risk_tier)
    
    def _get_controls_for_tier(self, tier: str) -> Dict[str, bool]:
        """Return activated controls for this risk tier."""
        mapper = NISTRiskMapper()
        characteristics = {
            "task": "policy_scoring",
            "document_type": "budget",
            "scope": "national" if tier == "high" else "departmental" if tier == "medium" else "local",
            "decision_criticality": "strategic" if tier == "high" else "operational" if tier == "medium" else "informational"
        }
        
        result = mapper.classify(characteristics)
        
        # Convert to dict of control: active
        controls = {}
        for control in result["required_controls"]:
            controls[control] = True
        
        return controls
    
    def is_control_active(self, control_name: str) -> bool:
        """Check if a specific control is active."""
        return self.controls.get(control_name, False)
    
    def require_explainability(self) -> bool:
        """Is explainability required?"""
        return self.is_control_active("explainability_shap_mandatory") or \
               self.is_control_active("explainability_lime")
    
    def require_bias_audit(self) -> bool:
        """Is bias audit required?"""
        return self.is_control_active("bias_audit_comprehensive") or \
               self.is_control_active("bias_audit_basic")
    
    def require_human_review(self) -> bool:
        """Is human review mandatory?"""
        return self.is_control_active("human_review_mandatory")
    
    def require_audit_trail(self) -> bool:
        """Is detailed audit trail required?"""
        return self.is_control_active("audit_trail_detailed") or \
               self.is_control_active("comprehensive_logging")


# Example usage
if __name__ == "__main__":
    import json
    
    mapper = NISTRiskMapper()
    
    # Test: National budget analysis (HIGH RISK)
    print("=== NATIONAL BUDGET ANALYSIS (HIGH RISK) ===")
    high_risk_characteristics = {
        "task": "policy_scoring",
        "document_type": "budget",
        "scope": "national",
        "decision_criticality": "strategic",
        "affected_population": 38000000,  # Canada
        "budget_impact": 400,  # $400B
        "timeline": "immediate"
    }
    
    result = mapper.classify(high_risk_characteristics)
    print(json.dumps(result, indent=2))
    
    # Test: Departmental memo (LOW RISK)
    print("\n=== DEPARTMENTAL MEMO (LOW RISK) ===")
    low_risk_characteristics = {
        "task": "policy_scoring",
        "document_type": "memo",
        "scope": "departmental",
        "decision_criticality": "informational",
        "affected_population": 500,
        "budget_impact": 0.5,
        "timeline": "long_term"
    }
    
    result = mapper.classify(low_risk_characteristics)
    print(json.dumps(result, indent=2))

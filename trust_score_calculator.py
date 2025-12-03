"""
Trust Score Calculator for SPOT-Policy™ v7.0

Composite trust metric combining explainability, fairness, robustness, and compliance.
Produces 0-100 trustworthiness score for policy evaluation results.

Pillar 2-3 Component: Trustworthiness Assessment

Author: SPOT-Policy™ v7.0 Ethical Framework
Date: November 13, 2025
"""

from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class TrustLevel(Enum):
    """Trustworthiness levels"""
    CRITICAL = "critical"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TrustScoreCalculator:
    """
    Calculates composite Trust Score (0-100).
    
    Trust Score = 0.30 × Explainability + 0.30 × Fairness + 0.20 × Robustness + 0.20 × Compliance
    
    Each component: 0-100 scale
    Result: 0-100 with interpretation and recommendations
    """
    
    def __init__(self):
        self.version = "1.0"
        self.weights = {
            "explainability": 0.30,
            "fairness": 0.30,
            "robustness": 0.20,
            "compliance": 0.20
        }
    
    def calculate(self, 
                 ai_detection_result: Optional[Dict] = None,
                 bias_audit_result: Optional[Dict] = None,
                 risk_tier: Optional[str] = None,
                 nist_functions: Optional[list] = None) -> Dict:
        """
        Calculate composite Trust Score from component metrics.
        
        Inputs:
        - ai_detection_result: from AIDetectionEngine.analyze_document()
        - bias_audit_result: from BiasAuditor.audit_scores()
        - risk_tier: from NISTRiskMapper.classify()
        - nist_functions: activated NIST functions
        
        Output:
        {
            "trust_score": 0-100,
            "trust_level": "critical" | "low" | "medium" | "high" | "very_high",
            "component_scores": {
                "explainability": 0-100,
                "fairness": 0-100,
                "robustness": 0-100,
                "compliance": 0-100
            },
            "interpretation": str,
            "recommendations": [...],
            "timestamp": ISO8601,
            "version": "1.0"
        }
        """
        
        # Calculate component scores
        explainability_score = self._calculate_explainability(ai_detection_result)
        fairness_score = self._calculate_fairness(bias_audit_result)
        robustness_score = self._calculate_robustness(ai_detection_result, bias_audit_result)
        compliance_score = self._calculate_compliance(risk_tier, nist_functions)
        
        # Composite calculation
        trust_score = (
            self.weights["explainability"] * explainability_score +
            self.weights["fairness"] * fairness_score +
            self.weights["robustness"] * robustness_score +
            self.weights["compliance"] * compliance_score
        )
        
        trust_score = round(trust_score, 1)
        trust_level = self._determine_trust_level(trust_score)
        
        # Generate interpretation and recommendations
        interpretation = self._generate_interpretation(trust_score, trust_level, {
            "explainability": explainability_score,
            "fairness": fairness_score,
            "robustness": robustness_score,
            "compliance": compliance_score
        })
        
        recommendations = self._generate_recommendations(trust_score, trust_level, {
            "explainability": explainability_score,
            "fairness": fairness_score,
            "robustness": robustness_score,
            "compliance": compliance_score
        })
        
        return {
            "trust_score": trust_score,
            "trust_level": trust_level.value,
            "component_scores": {
                "explainability": round(explainability_score, 1),
                "fairness": round(fairness_score, 1),
                "robustness": round(robustness_score, 1),
                "compliance": round(compliance_score, 1)
            },
            "weights": self.weights,
            "interpretation": interpretation,
            "recommendations": recommendations,
            "risk_tier": risk_tier,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": self.version
        }
    
    def _calculate_explainability(self, ai_detection: Optional[Dict]) -> float:
        """
        Calculate explainability component (0-100).
        
        Based on AI detection transparency:
        - If AI detected: Lower explainability (unclear how policy was formed)
        - If Human/Mixed: Higher explainability
        - Confidence level matters
        """
        
        if ai_detection is None:
            return 50.0  # Neutral if unknown
        
        ai_score = ai_detection.get("ai_detection_score", 0.5)
        confidence = ai_detection.get("confidence", 0.5)
        
        # If high confidence that input is human-written: high explainability
        if ai_score < 0.3 and confidence > 0.7:
            return 90.0
        
        # If moderate AI influence: medium explainability
        elif 0.3 <= ai_score < 0.7:
            return 60.0 + (1 - confidence) * 10
        
        # If high AI influence with high confidence: low explainability
        elif ai_score >= 0.7 and confidence > 0.7:
            return 30.0
        
        # If AI-generated but low confidence: medium risk
        else:
            return 50.0
    
    def _calculate_fairness(self, bias_audit: Optional[Dict]) -> float:
        """
        Calculate fairness component (0-100).
        
        Based on bias audit overall fairness score.
        Direct mapping: 0-100
        """
        
        if bias_audit is None:
            return 50.0  # Neutral if unknown
        
        overall_score = bias_audit.get("overall_fairness_score", 50.0)
        
        return overall_score
    
    def _calculate_robustness(self, ai_detection: Optional[Dict], 
                             bias_audit: Optional[Dict]) -> float:
        """
        Calculate robustness component (0-100).
        
        Based on:
        - Consistency of AI detection (confidence level)
        - Absence of demographic bias
        - Stability across groups
        """
        
        score = 50.0  # Start neutral
        
        # Factor 1: AI detection consistency (if available)
        if ai_detection is not None:
            confidence = ai_detection.get("confidence", 0.5)
            score += confidence * 20  # Up to +20 points
        
        # Factor 2: Demographic stability (if available)
        if bias_audit is not None:
            bias_detected = bias_audit.get("bias_detected", False)
            if not bias_detected:
                score += 30  # High robustness if no bias
            else:
                # Reduce based on severity
                warnings = bias_audit.get("warnings_present", False)
                if warnings:
                    score += 10
        
        return min(score, 100.0)
    
    def _calculate_compliance(self, risk_tier: Optional[str], 
                             nist_functions: Optional[list]) -> float:
        """
        Calculate compliance component (0-100).
        
        Based on:
        - Risk tier (higher risk = more compliance burden)
        - NIST AI RMF functions activated
        """
        
        if risk_tier is None:
            return 50.0  # Neutral if unknown
        
        # Base score by risk tier
        if risk_tier == "low":
            score = 80.0  # Low risk = easier compliance
        elif risk_tier == "medium":
            score = 60.0  # Medium risk = moderate compliance
        else:  # high
            score = 40.0  # High risk = strict compliance requirements
        
        # Bonus if NIST functions are activated
        if nist_functions is not None and len(nist_functions) > 0:
            # Each activated function = +5 points (max 4 functions = +20)
            nist_bonus = min(len(nist_functions) * 5, 20)
            score += nist_bonus
        
        return min(score, 100.0)
    
    def _determine_trust_level(self, score: float) -> TrustLevel:
        """Determine trust level from score."""
        if score < 20:
            return TrustLevel.CRITICAL
        elif score < 40:
            return TrustLevel.LOW
        elif score < 60:
            return TrustLevel.MEDIUM
        elif score < 80:
            return TrustLevel.HIGH
        else:
            return TrustLevel.VERY_HIGH
    
    def _generate_interpretation(self, score: float, level: TrustLevel, 
                                components: Dict) -> str:
        """Generate human-readable interpretation."""
        
        interpretation = f"Trust Score: {score}/100 ({level.value.upper()})\n\n"
        
        # Component breakdown
        interpretation += "Component Breakdown:\n"
        interpretation += f"  • Explainability:   {components['explainability']:5.1f}/100\n"
        interpretation += f"  • Fairness:         {components['fairness']:5.1f}/100\n"
        interpretation += f"  • Robustness:       {components['robustness']:5.1f}/100\n"
        interpretation += f"  • Compliance:       {components['compliance']:5.1f}/100\n"
        
        interpretation += "\nTrustworthy Use Assessment:\n"
        
        if level == TrustLevel.CRITICAL:
            interpretation += "🔴 CRITICAL: This analysis has LOW trustworthiness.\n"
            interpretation += "   DO NOT use for policy decisions without extensive review.\n"
        
        elif level == TrustLevel.LOW:
            interpretation += "⚠️  LOW: This analysis has LIMITED trustworthiness.\n"
            interpretation += "   Use only with significant human expert oversight.\n"
        
        elif level == TrustLevel.MEDIUM:
            interpretation += "🟡 MEDIUM: This analysis has MODERATE trustworthiness.\n"
            interpretation += "   Suitable with human review and validation.\n"
        
        elif level == TrustLevel.HIGH:
            interpretation += "🟢 HIGH: This analysis is reasonably trustworthy.\n"
            interpretation += "   Suitable for decision support with standard review.\n"
        
        else:  # VERY_HIGH
            interpretation += "✅ VERY HIGH: This analysis is highly trustworthy.\n"
            interpretation += "   Suitable for primary use in policy decisions.\n"
        
        # Identify weakest component
        weakest = min(components, key=components.get)
        weakest_value = components[weakest]
        
        if weakest_value < 50:
            interpretation += f"\nWeakest Component: {weakest.capitalize()} ({weakest_value:.1f}/100)\n"
            interpretation += f"→ Consider improving {weakest} before final decisions.\n"
        
        return interpretation
    
    def _generate_recommendations(self, score: float, level: TrustLevel,
                                 components: Dict) -> list:
        """Generate actionable recommendations."""
        
        recommendations = []
        
        # Overall level recommendations
        if level == TrustLevel.CRITICAL:
            recommendations.append("🔴 CRITICAL: Escalate to executive/legal review immediately.")
            recommendations.append("   Review all fairness and explainability metrics.")
            recommendations.append("   Conduct impact assessment before any implementation.")
        
        elif level == TrustLevel.LOW:
            recommendations.append("⚠️  Require comprehensive professional review.")
            recommendations.append("   Investigate low-scoring components.")
            recommendations.append("   Document all assumptions and limitations.")
        
        elif level == TrustLevel.MEDIUM:
            recommendations.append("🟡 Proceed with caution. Standard review required.")
            recommendations.append("   Strengthen weakest components if possible.")
            recommendations.append("   Monitor for bias and drift during implementation.")
        
        elif level == TrustLevel.HIGH:
            recommendations.append("🟢 Suitable for decision support.")
            recommendations.append("   Continue standard governance and monitoring.")
            recommendations.append("   Regular trust score recalculation recommended.")
        
        else:  # VERY_HIGH
            recommendations.append("✅ Highly trustworthy for policy support.")
            recommendations.append("   Maintain current governance practices.")
            recommendations.append("   Schedule periodic reassessment.")
        
        # Component-specific recommendations
        if components["explainability"] < 50:
            recommendations.append("→ [EXPLAINABILITY] Review AI detection results and improve transparency.")
        
        if components["fairness"] < 50:
            recommendations.append("→ [FAIRNESS] Address bias concerns identified in audit.")
        
        if components["robustness"] < 50:
            recommendations.append("→ [ROBUSTNESS] Increase confidence through additional validation.")
        
        if components["compliance"] < 50:
            recommendations.append("→ [COMPLIANCE] Ensure NIST AI RMF controls are activated.")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    import json
    
    calculator = TrustScoreCalculator()
    
    # Test Case 1: High-trust scenario
    print("=== TEST CASE 1: HIGH-TRUST SCENARIO ===")
    ai_detection_good = {
        "ai_detection_score": 0.15,  # Low AI influence
        "confidence": 0.95,
        "detected": False
    }
    
    bias_audit_good = {
        "overall_fairness_score": 95.0,  # Excellent fairness
        "bias_detected": False
    }
    
    result_good = calculator.calculate(
        ai_detection_result=ai_detection_good,
        bias_audit_result=bias_audit_good,
        risk_tier="medium",
        nist_functions=["Govern", "Map", "Measure"]
    )
    
    print(json.dumps(result_good, indent=2))
    
    # Test Case 2: Low-trust scenario
    print("\n\n=== TEST CASE 2: LOW-TRUST SCENARIO ===")
    ai_detection_poor = {
        "ai_detection_score": 0.85,  # High AI influence
        "confidence": 0.92,
        "detected": True
    }
    
    bias_audit_poor = {
        "overall_fairness_score": 35.0,  # Poor fairness
        "bias_detected": True,
        "warnings_present": True
    }
    
    result_poor = calculator.calculate(
        ai_detection_result=ai_detection_poor,
        bias_audit_result=bias_audit_poor,
        risk_tier="high",
        nist_functions=["Govern"]
    )
    
    print(json.dumps(result_poor, indent=2))
    print(f"\n{result_poor['interpretation']}")

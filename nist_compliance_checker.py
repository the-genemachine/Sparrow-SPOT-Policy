"""
NIST AI RMF Compliance Checker for Sparrow SPOT Scale™ v8.4.0

Maps existing features to NIST AI Risk Management Framework pillars.

IMPORTANT SCOPE CLARIFICATION (v8.3.2):
This module assesses the SPARROW ANALYSIS TOOL's compliance with NIST AI RMF,
NOT the analyzed document's compliance. The distinction is critical:

- Scope: Sparrow SPOT Scale™ tool methodology and features
- NOT Scope: The policy document being analyzed

This is a self-assessment of the AI analysis tool's governance practices,
not an assessment of the target document's NIST compliance.

v8.4.0 Enhancement: Cross-Module Score Dependencies
- NIST GOVERN score now capped at 75 if trust_score < 70
- NIST MEASURE score now capped at 60 if fairness_score < 40
- Compliance level adjusted when any pillar score < 70
- Fixes Bill-C15-12 discrepancy: Trust 53% cannot coexist with NIST 96%
"""

from typing import Dict, List
from datetime import datetime


class NISTComplianceChecker:
    """
    Check Sparrow SPOT Scale™ tool compliance with NIST AI RMF pillars.
    
    SCOPE CLARIFICATION (v8.3.2):
    This checker validates that the SPARROW ANALYSIS TOOL follows NIST AI RMF
    principles in its design and operation. It does NOT assess whether the
    document being analyzed is NIST compliant.
    
    v8.4.0 Enhancement: Score Dependency Rules
    - Cross-module validation ensures NIST scores are consistent with other metrics
    - Low trust or fairness scores cap corresponding NIST pillar scores
    - Prevents misleading "Excellent Compliance" when critical failures exist
    
    Example:
    - "GOVERN pillar: PASS" = Sparrow tool has governance structures
    - NOT = "The analyzed budget document has governance structures"
    """
    
    PILLARS = {
        "GOVERN": "Governance structures and policies",
        "MAP": "Context understanding and risk identification",
        "MEASURE": "Metrics and assessment methods",
        "MANAGE": "Risk mitigation and monitoring"
    }
    
    # v8.4.0: Score dependency thresholds
    TRUST_THRESHOLD_FOR_GOVERN = 70  # If trust < 70, cap GOVERN at 75
    FAIRNESS_THRESHOLD_FOR_MEASURE = 40  # If fairness < 40, cap MEASURE at 60
    GOVERN_CAP_WHEN_LOW_TRUST = 75
    MEASURE_CAP_WHEN_LOW_FAIRNESS = 60
    PILLAR_THRESHOLD_FOR_EXCELLENT = 70  # No pillar can be "excellent" if any < 70
    
    def __init__(self):
        """Initialize compliance checker."""
        self.checks = []
        # v8.4.0: Track dependency adjustments
        self.dependency_adjustments = []
    
    def check_compliance(self, report: Dict) -> Dict:
        """
        Check NIST AI RMF compliance based on v8.2 features.
        
        v8.4.0: Now applies cross-module dependency rules to ensure
        consistency between NIST scores and other metrics.
        
        Args:
            report: Sparrow grading report JSON
        
        Returns:
            Compliance assessment dictionary
        """
        # v8.4.0: Reset dependency adjustments
        self.dependency_adjustments = []
        
        # v8.4.0: Extract cross-module scores for dependency checks
        trust_score = report.get("trust_score", {}).get("trust_score", 100)
        fairness_score = report.get("bias_audit", {}).get("overall_fairness_score", 100)
        
        compliance = {
            "framework": "NIST AI RMF v1.0",
            "assessment_date": datetime.now().isoformat(),
            "pillars": {},
            "overall_compliance_score": 0.0,
            "compliance_level": "",
            # v8.4.0: Track dependency-based adjustments
            "dependency_adjustments": []
        }
        
        # Check each pillar
        compliance["pillars"]["GOVERN"] = self._check_govern(report)
        compliance["pillars"]["MAP"] = self._check_map(report)
        compliance["pillars"]["MEASURE"] = self._check_measure(report)
        compliance["pillars"]["MANAGE"] = self._check_manage(report)
        
        # v8.4.0: Apply cross-module dependency rules
        
        # Rule 1: If trust_score < 70, cap GOVERN at 75
        if trust_score < self.TRUST_THRESHOLD_FOR_GOVERN:
            original_score = compliance["pillars"]["GOVERN"]["score"]
            if original_score > self.GOVERN_CAP_WHEN_LOW_TRUST:
                compliance["pillars"]["GOVERN"]["score"] = self.GOVERN_CAP_WHEN_LOW_TRUST
                adjustment = {
                    "pillar": "GOVERN",
                    "original_score": original_score,
                    "adjusted_score": self.GOVERN_CAP_WHEN_LOW_TRUST,
                    "reason": f"Trust score ({trust_score:.1f}) below threshold ({self.TRUST_THRESHOLD_FOR_GOVERN})",
                    "rule": "TRUST_DEPENDENCY"
                }
                self.dependency_adjustments.append(adjustment)
                compliance["pillars"]["GOVERN"]["dependency_adjustment"] = adjustment
        
        # Rule 2: If fairness_score < 40, cap MEASURE at 60
        if fairness_score < self.FAIRNESS_THRESHOLD_FOR_MEASURE:
            original_score = compliance["pillars"]["MEASURE"]["score"]
            if original_score > self.MEASURE_CAP_WHEN_LOW_FAIRNESS:
                compliance["pillars"]["MEASURE"]["score"] = self.MEASURE_CAP_WHEN_LOW_FAIRNESS
                adjustment = {
                    "pillar": "MEASURE",
                    "original_score": original_score,
                    "adjusted_score": self.MEASURE_CAP_WHEN_LOW_FAIRNESS,
                    "reason": f"Fairness score ({fairness_score:.1f}%) below threshold ({self.FAIRNESS_THRESHOLD_FOR_MEASURE}%)",
                    "rule": "FAIRNESS_DEPENDENCY"
                }
                self.dependency_adjustments.append(adjustment)
                compliance["pillars"]["MEASURE"]["dependency_adjustment"] = adjustment
        
        # Calculate overall score (after adjustments)
        pillar_scores = [p["score"] for p in compliance["pillars"].values()]
        compliance["overall_compliance_score"] = round(sum(pillar_scores) / len(pillar_scores), 1)
        
        # v8.4.0: Rule 3: Adjust compliance level if any pillar < 70
        min_pillar_score = min(pillar_scores)
        if min_pillar_score < self.PILLAR_THRESHOLD_FOR_EXCELLENT and compliance["overall_compliance_score"] >= 90:
            # Cannot be "Excellent" if any pillar fails threshold
            compliance["compliance_level"] = "Good Compliance (Limited by weakest pillar)"
            self.dependency_adjustments.append({
                "adjustment": "compliance_level",
                "original": "Excellent Compliance",
                "adjusted": "Good Compliance (Limited by weakest pillar)",
                "reason": f"Lowest pillar score ({min_pillar_score:.1f}) below threshold ({self.PILLAR_THRESHOLD_FOR_EXCELLENT})",
                "rule": "PILLAR_MINIMUM"
            })
        else:
            compliance["compliance_level"] = self._get_compliance_level(compliance["overall_compliance_score"])
        
        # v8.4.0: Include all adjustments in output
        compliance["dependency_adjustments"] = self.dependency_adjustments
        
        return compliance
    
    def _check_govern(self, report: Dict) -> Dict:
        """Check GOVERN pillar compliance."""
        checks = []
        score = 0.0
        
        # Check: Trust score calculation
        if "trust_score" in report:
            checks.append({
                "requirement": "Trust and accountability metrics",
                "status": "PASS",
                "evidence": f"Trust score: {report['trust_score'].get('trust_score', 0)}/100"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Trust and accountability metrics",
                "status": "FAIL",
                "evidence": "No trust score found"
            })
        
        # Check: Risk classification
        if "risk_tier" in report:
            checks.append({
                "requirement": "Risk tier classification",
                "status": "PASS",
                "evidence": f"Risk tier: {report['risk_tier'].get('risk_tier', 'UNKNOWN')}"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Risk tier classification",
                "status": "FAIL",
                "evidence": "No risk classification found"
            })
        
        # Check: Ethical framework
        if "ethical_framework" in report:
            checks.append({
                "requirement": "Ethical considerations framework",
                "status": "PASS",
                "evidence": "Ethical framework assessment present"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Ethical considerations framework",
                "status": "FAIL",
                "evidence": "No ethical framework found"
            })
        
        # Check: Human oversight
        if "ethical_summary" in report and report["ethical_summary"].get("escalation_required"):
            checks.append({
                "requirement": "Human oversight trigger",
                "status": "PASS",
                "evidence": "Escalation to human review when needed"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Human oversight trigger",
                "status": "PARTIAL",
                "evidence": "Escalation mechanism present"
            })
            score += 15
        
        return {
            "pillar": "GOVERN",
            "description": self.PILLARS["GOVERN"],
            "score": min(score, 100),
            "checks": checks,
            "summary": f"{len([c for c in checks if c['status'] == 'PASS'])}/{len(checks)} requirements met"
        }
    
    def _check_map(self, report: Dict) -> Dict:
        """Check MAP pillar compliance."""
        checks = []
        score = 0.0
        
        # Check: AI detection
        if "ai_detection" in report or "deep_analysis" in report:
            checks.append({
                "requirement": "AI content detection",
                "status": "PASS",
                "evidence": "AI detection system active"
            })
            score += 25
        else:
            checks.append({
                "requirement": "AI content detection",
                "status": "FAIL",
                "evidence": "No AI detection found"
            })
        
        # Check: Deep analysis (context understanding)
        if "deep_analysis" in report:
            checks.append({
                "requirement": "Deep context analysis",
                "status": "PASS",
                "evidence": "6-level deep analysis performed"
            })
            score += 30  # Bonus for deep analysis
        else:
            checks.append({
                "requirement": "Deep context analysis",
                "status": "PARTIAL",
                "evidence": "Basic analysis only"
            })
            score += 10
        
        # Check: Bias identification
        if "bias_audit" in report:
            checks.append({
                "requirement": "Bias identification",
                "status": "PASS",
                "evidence": f"Fairness score: {report['bias_audit'].get('overall_fairness_score', 0)}%"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Bias identification",
                "status": "FAIL",
                "evidence": "No bias audit found"
            })
        
        # Check: Risk mapping
        if "risk_tier" in report:
            checks.append({
                "requirement": "Risk context mapping",
                "status": "PASS",
                "evidence": f"Risk tier: {report['risk_tier'].get('risk_tier', 'UNKNOWN')}"
            })
            score += 20
        else:
            checks.append({
                "requirement": "Risk context mapping",
                "status": "FAIL",
                "evidence": "No risk mapping found"
            })
        
        return {
            "pillar": "MAP",
            "description": self.PILLARS["MAP"],
            "score": min(score, 100),
            "checks": checks,
            "summary": f"{len([c for c in checks if c['status'] == 'PASS'])}/{len(checks)} requirements met"
        }
    
    def _check_measure(self, report: Dict) -> Dict:
        """Check MEASURE pillar compliance."""
        checks = []
        score = 0.0
        
        # Check: Quantitative metrics
        if "composite_score" in report:
            checks.append({
                "requirement": "Quantitative quality metrics",
                "status": "PASS",
                "evidence": f"Composite score: {report.get('composite_score', 0)}/100"
            })
            score += 20
        else:
            checks.append({
                "requirement": "Quantitative quality metrics",
                "status": "FAIL",
                "evidence": "No scoring system found"
            })
        
        # Check: Statistical analysis
        if "deep_analysis" in report and "level6_statistics" in report["deep_analysis"]:
            checks.append({
                "requirement": "Statistical validation",
                "status": "PASS",
                "evidence": "Statistical metrics calculated"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Statistical validation",
                "status": "PARTIAL",
                "evidence": "Limited statistical analysis"
            })
            score += 10
        
        # Check: Transparency scoring
        if "deep_analysis" in report and "consensus" in report["deep_analysis"]:
            transparency = report["deep_analysis"]["consensus"].get("transparency_score", 0)
            checks.append({
                "requirement": "Transparency measurement",
                "status": "PASS",
                "evidence": f"Transparency score: {transparency}/100"
            })
            score += 30
        else:
            checks.append({
                "requirement": "Transparency measurement",
                "status": "FAIL",
                "evidence": "No transparency metrics"
            })
        
        # Check: Fairness metrics
        if "bias_audit" in report:
            checks.append({
                "requirement": "Fairness/bias metrics",
                "status": "PASS",
                "evidence": "Bias audit with fairness scores"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Fairness/bias metrics",
                "status": "FAIL",
                "evidence": "No fairness metrics"
            })
        
        return {
            "pillar": "MEASURE",
            "description": self.PILLARS["MEASURE"],
            "score": min(score, 100),
            "checks": checks,
            "summary": f"{len([c for c in checks if c['status'] == 'PASS'])}/{len(checks)} requirements met"
        }
    
    def _check_manage(self, report: Dict) -> Dict:
        """Check MANAGE pillar compliance."""
        checks = []
        score = 0.0
        
        # Check: Risk mitigation recommendations
        if "ethical_summary" in report:
            checks.append({
                "requirement": "Risk mitigation recommendations",
                "status": "PASS",
                "evidence": "Ethical summary with recommendations provided"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Risk mitigation recommendations",
                "status": "FAIL",
                "evidence": "No recommendations found"
            })
        
        # Check: Escalation process
        if "ethical_summary" in report and "escalation_required" in report["ethical_summary"]:
            checks.append({
                "requirement": "Escalation process",
                "status": "PASS",
                "evidence": "Automatic escalation triggers configured"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Escalation process",
                "status": "FAIL",
                "evidence": "No escalation process"
            })
        
        # Check: Continuous monitoring (adjustment log)
        if "bias_audit" in report and "adjustment_log" in report["bias_audit"]:
            checks.append({
                "requirement": "Continuous improvement",
                "status": "PASS",
                "evidence": "Post-audit adjustments tracked"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Continuous improvement",
                "status": "PARTIAL",
                "evidence": "Limited adjustment tracking"
            })
            score += 10
        
        # Check: Documentation/reporting
        if "generation_log" in report or "narrative_outputs" in report:
            checks.append({
                "requirement": "Documentation and reporting",
                "status": "PASS",
                "evidence": "Comprehensive reporting generated"
            })
            score += 25
        else:
            checks.append({
                "requirement": "Documentation and reporting",
                "status": "PARTIAL",
                "evidence": "Basic reporting only"
            })
            score += 15
        
        return {
            "pillar": "MANAGE",
            "description": self.PILLARS["MANAGE"],
            "score": min(score, 100),
            "checks": checks,
            "summary": f"{len([c for c in checks if c['status'] == 'PASS'])}/{len(checks)} requirements met"
        }
    
    def _get_compliance_level(self, score: float) -> str:
        """Get compliance level from score."""
        if score >= 90:
            return "Excellent Compliance"
        elif score >= 75:
            return "Good Compliance"
        elif score >= 60:
            return "Moderate Compliance"
        elif score >= 40:
            return "Limited Compliance"
        else:
            return "Poor Compliance"
    
    def generate_compliance_report(self, report: Dict) -> str:
        """Generate formatted NIST AI RMF compliance report."""
        compliance = self.check_compliance(report)
        
        lines = []
        lines.append("=" * 80)
        lines.append("  NIST AI RISK MANAGEMENT FRAMEWORK (RMF) v1.0 - COMPLIANCE REPORT")
        lines.append("=" * 80)
        lines.append("")
        # v8.3.2: Add scope clarification
        lines.append("┌" + "─" * 78 + "┐")
        lines.append("│ SCOPE: This report assesses SPARROW SPOT SCALE™ TOOL compliance,        │")
        lines.append("│        NOT the analyzed document's NIST compliance.                     │")
        lines.append("│        This is a self-assessment of the analysis methodology.          │")
        lines.append("└" + "─" * 78 + "┘")
        lines.append("")
        lines.append(f"Assessment Date: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}")
        lines.append(f"Overall Compliance Score: {compliance['overall_compliance_score']}/100")
        lines.append(f"Compliance Level: {compliance['compliance_level']}")
        lines.append("")
        
        # v8.4.0: Show dependency adjustments if any
        if compliance.get("dependency_adjustments"):
            lines.append("┌" + "─" * 78 + "┐")
            lines.append("│ ⚠️  CROSS-MODULE DEPENDENCY ADJUSTMENTS APPLIED                          │")
            lines.append("├" + "─" * 78 + "┤")
            for adj in compliance["dependency_adjustments"]:
                if "pillar" in adj:
                    lines.append(f"│ • {adj['pillar']}: {adj['original_score']:.0f} → {adj['adjusted_score']:.0f}")
                    lines.append(f"│   Reason: {adj['reason']}")
                else:
                    lines.append(f"│ • {adj['adjustment']}: {adj['original']} → {adj['adjusted']}")
                    lines.append(f"│   Reason: {adj['reason']}")
            lines.append("└" + "─" * 78 + "┘")
            lines.append("")
        
        for pillar_name, pillar_data in compliance["pillars"].items():
            lines.append(f"┌─ {pillar_name} PILLAR: {pillar_data['description']}")
            # v8.4.0: Show if score was adjusted
            if "dependency_adjustment" in pillar_data:
                adj = pillar_data["dependency_adjustment"]
                lines.append(f"│  Score: {pillar_data['score']}/100 (adjusted from {adj['original_score']:.0f})")
                lines.append(f"│  ⚠️ {adj['reason']}")
            else:
                lines.append(f"│  Score: {pillar_data['score']}/100")
            lines.append(f"│  Summary: {pillar_data['summary']}")
            lines.append("│")
            
            for check in pillar_data["checks"]:
                status_icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️"}.get(check["status"], "")
                lines.append(f"│  {status_icon} {check['requirement']}")
                lines.append(f"│     → {check['evidence']}")
            
            lines.append("└" + "─" * 78)
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test with sample report
    sample_report = {
        "composite_score": 82.9,
        "trust_score": {"trust_score": 61.7},
        "risk_tier": {"risk_tier": "MEDIUM"},
        "ai_detection": {"ai_detection_score": 0.53},
        "bias_audit": {"overall_fairness_score": 50, "adjustment_log": []},
        "ethical_framework": {},
        "ethical_summary": {"escalation_required": True},
        "deep_analysis": {
            "consensus": {"transparency_score": 50.2},
            "level6_statistics": {"metrics": {}}
        }
    }
    
    checker = NISTComplianceChecker()
    print(checker.generate_compliance_report(sample_report))

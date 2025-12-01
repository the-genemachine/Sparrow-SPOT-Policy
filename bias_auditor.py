"""
Bias Auditor for SPOT-Policy™ v7.0

Audits policy evaluation scores for fairness across demographic groups.
Implements fairness metrics: DIR (Disparate Impact Ratio), EOD (Equalized Odds Difference), SPD (Statistical Parity Difference)

Pillar 2 Component: Fairness Analysis & Bias Detection

Author: SPOT-Policy™ v7.0 Ethical Framework
Date: November 13, 2025
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from statistics import mean, stdev
import json
from datetime import datetime


@dataclass
class DemographicGroup:
    """Represents a demographic group within the evaluation."""
    name: str
    description: str
    sample_size: int
    average_score: float
    score_std_dev: float
    score_min: float
    score_max: float
    scores: List[float]


@dataclass
class FairnessMetric:
    """Represents a calculated fairness metric."""
    metric_name: str
    reference_group: str
    comparison_group: str
    value: float
    threshold: float
    status: str  # "pass" | "warning" | "fail"
    interpretation: str


class BiasAuditor:
    """
    Audits policy evaluation scores for fairness.
    Identifies bias across demographic groups.
    """
    
    def __init__(self):
        self.version = "1.0"
        self.framework = "Fairness & Bias Detection"
        self.metrics_available = ["DIR", "EOD", "SPD", "PPV", "FNR"]
    
    def audit_scores(self, scores_by_group: Dict[str, List[float]], 
                    reference_group: Optional[str] = None) -> Dict:
        """
        Audit evaluation scores across demographic groups.
        
        Input:
        {
            "Indigenous": [65, 70, 72, ...],
            "Visible_Minority": [75, 78, 80, ...],
            "Women": [68, 72, 74, ...],
            "Persons_with_Disabilities": [55, 60, 65, ...]
        }
        
        Output:
        {
            "audit_timestamp": ISO8601,
            "demographic_groups": [...],
            "fairness_metrics": [...],
            "bias_detected": bool,
            "overall_fairness_score": 0-100,
            "recommendations": [...],
            "audit_summary": str
        }
        """
        
        # Build demographic groups
        demographic_groups = []
        for group_name, scores in scores_by_group.items():
            if len(scores) > 0:
                group = DemographicGroup(
                    name=group_name,
                    description=f"Group: {group_name}",
                    sample_size=len(scores),
                    average_score=mean(scores),
                    score_std_dev=stdev(scores) if len(scores) > 1 else 0,
                    score_min=min(scores),
                    score_max=max(scores),
                    scores=scores
                )
                demographic_groups.append(group)
        
        # Use first group as reference if not specified
        if reference_group is None and len(demographic_groups) > 0:
            reference_group = demographic_groups[0].name
        
        # Calculate fairness metrics
        fairness_metrics = []
        
        # DIR (Disparate Impact Ratio)
        dir_metrics = self._calculate_dir(demographic_groups, reference_group)
        fairness_metrics.extend(dir_metrics)
        
        # EOD (Equalized Odds Difference)
        eod_metrics = self._calculate_eod(demographic_groups, reference_group)
        fairness_metrics.extend(eod_metrics)
        
        # SPD (Statistical Parity Difference)
        spd_metrics = self._calculate_spd(demographic_groups, reference_group)
        fairness_metrics.extend(spd_metrics)
        
        # Detect bias
        bias_detected = any(m.status == "fail" for m in fairness_metrics)
        warnings = any(m.status == "warning" for m in fairness_metrics)
        
        # v8.3.2 Fix: warnings_present should be True when ANY issue is detected
        # (both "warning" and "fail" statuses should trigger warnings_present)
        warnings_present = warnings or bias_detected
        
        # Calculate overall fairness score
        overall_score = self._calculate_overall_fairness_score(fairness_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(fairness_metrics, bias_detected)
        
        # Generate summary
        summary = self._generate_audit_summary(demographic_groups, fairness_metrics, bias_detected)
        
        return {
            "audit_timestamp": datetime.utcnow().isoformat() + "Z",
            "framework": self.framework,
            "version": self.version,
            "demographic_groups": [self._group_to_dict(g) for g in demographic_groups],
            "fairness_metrics": [self._metric_to_dict(m) for m in fairness_metrics],
            "bias_detected": bias_detected,
            "warnings_present": warnings_present,  # v8.3.2: Fixed - True when any issue detected
            "overall_fairness_score": round(overall_score, 1),
            "reference_group": reference_group,
            "recommendations": recommendations,
            "audit_summary": summary
        }
    
    def _calculate_dir(self, groups: List[DemographicGroup], 
                      reference_group: Optional[str]) -> List[FairnessMetric]:
        """
        Calculate Disparate Impact Ratio (DIR).
        
        DIR = Selection Rate (Minority) / Selection Rate (Majority)
        Threshold: >= 0.8 is considered acceptable (80% Rule)
        
        Selection Rate = avg_score >= threshold / group_size
        """
        
        metrics = []
        
        if len(groups) < 2:
            return metrics
        
        # Find reference group (typically highest average)
        if reference_group is None:
            ref = max(groups, key=lambda g: g.average_score)
        else:
            ref = next((g for g in groups if g.name == reference_group), None)
            if ref is None:
                ref = groups[0]
        
        threshold = 70  # Use 70 as passing score threshold
        
        ref_selected = sum(1 for s in ref.scores if s >= threshold) / len(ref.scores)
        
        for group in groups:
            if group.name != ref.name:
                group_selected = sum(1 for s in group.scores if s >= threshold) / len(group.scores)
                
                if ref_selected > 0:
                    dir_value = group_selected / ref_selected
                else:
                    dir_value = 0.0
                
                # Determine status
                if dir_value >= 0.8:
                    status = "pass"
                    interpretation = f"Acceptable disparate impact (DIR: {dir_value:.2f})"
                elif dir_value >= 0.7:
                    status = "warning"
                    interpretation = f"Borderline disparate impact (DIR: {dir_value:.2f}). Monitor closely."
                else:
                    status = "fail"
                    interpretation = f"Significant disparate impact (DIR: {dir_value:.2f}). Investigate bias."
                
                metric = FairnessMetric(
                    metric_name="Disparate Impact Ratio (DIR)",
                    reference_group=ref.name,
                    comparison_group=group.name,
                    value=round(dir_value, 3),
                    threshold=0.8,
                    status=status,
                    interpretation=interpretation
                )
                metrics.append(metric)
        
        return metrics
    
    def _calculate_eod(self, groups: List[DemographicGroup], 
                      reference_group: Optional[str]) -> List[FairnessMetric]:
        """
        Calculate Equalized Odds Difference (EOD).
        
        EOD = |FPR_group1 - FPR_group2| (False Positive Rate difference)
        Threshold: <= 0.1 is considered acceptable
        
        FPR = false_positives / (false_positives + true_negatives)
        For scores: FPR = scores < 50 / all scores < 70
        """
        
        metrics = []
        
        if len(groups) < 2:
            return metrics
        
        # Find reference group
        if reference_group is None:
            ref = max(groups, key=lambda g: g.average_score)
        else:
            ref = next((g for g in groups if g.name == reference_group), None)
            if ref is None:
                ref = groups[0]
        
        # Calculate FPR for reference group
        ref_low_scores = sum(1 for s in ref.scores if s < 50)
        ref_fpr = ref_low_scores / len(ref.scores) if len(ref.scores) > 0 else 0.0
        
        for group in groups:
            if group.name != ref.name:
                group_low_scores = sum(1 for s in group.scores if s < 50)
                group_fpr = group_low_scores / len(group.scores) if len(group.scores) > 0 else 0.0
                
                eod_value = abs(ref_fpr - group_fpr)
                
                # Determine status
                if eod_value <= 0.1:
                    status = "pass"
                    interpretation = f"Equalized odds maintained (EOD: {eod_value:.3f})"
                elif eod_value <= 0.15:
                    status = "warning"
                    interpretation = f"Borderline equalized odds (EOD: {eod_value:.3f}). Review scoring."
                else:
                    status = "fail"
                    interpretation = f"Unequal odds detected (EOD: {eod_value:.3f}). Investigate."
                
                metric = FairnessMetric(
                    metric_name="Equalized Odds Difference (EOD)",
                    reference_group=ref.name,
                    comparison_group=group.name,
                    value=round(eod_value, 3),
                    threshold=0.1,
                    status=status,
                    interpretation=interpretation
                )
                metrics.append(metric)
        
        return metrics
    
    def _calculate_spd(self, groups: List[DemographicGroup], 
                      reference_group: Optional[str]) -> List[FairnessMetric]:
        """
        Calculate Statistical Parity Difference (SPD).
        
        SPD = |Selection_Rate_group1 - Selection_Rate_group2|
        Threshold: <= 0.1 is considered acceptable
        
        Selection Rate = count(score >= 70) / group_size
        """
        
        metrics = []
        
        if len(groups) < 2:
            return metrics
        
        # Find reference group
        if reference_group is None:
            ref = max(groups, key=lambda g: g.average_score)
        else:
            ref = next((g for g in groups if g.name == reference_group), None)
            if ref is None:
                ref = groups[0]
        
        threshold = 70
        ref_selection_rate = sum(1 for s in ref.scores if s >= threshold) / len(ref.scores)
        
        for group in groups:
            if group.name != ref.name:
                group_selection_rate = sum(1 for s in group.scores if s >= threshold) / len(group.scores)
                
                spd_value = abs(ref_selection_rate - group_selection_rate)
                
                # Determine status
                if spd_value <= 0.1:
                    status = "pass"
                    interpretation = f"Statistical parity maintained (SPD: {spd_value:.3f})"
                elif spd_value <= 0.15:
                    status = "warning"
                    interpretation = f"Borderline statistical parity (SPD: {spd_value:.3f}). Monitor."
                else:
                    status = "fail"
                    interpretation = f"Statistical parity not maintained (SPD: {spd_value:.3f}). Review."
                
                metric = FairnessMetric(
                    metric_name="Statistical Parity Difference (SPD)",
                    reference_group=ref.name,
                    comparison_group=group.name,
                    value=round(spd_value, 3),
                    threshold=0.1,
                    status=status,
                    interpretation=interpretation
                )
                metrics.append(metric)
        
        return metrics
    
    def _calculate_overall_fairness_score(self, metrics: List[FairnessMetric]) -> float:
        """
        Calculate overall fairness score (0-100).
        Based on metric status distribution.
        """
        
        if len(metrics) == 0:
            return 100.0
        
        passes = sum(1 for m in metrics if m.status == "pass")
        warnings = sum(1 for m in metrics if m.status == "warning")
        fails = sum(1 for m in metrics if m.status == "fail")
        
        # Scoring: pass=100, warning=70, fail=0, average
        scores = [100] * passes + [70] * warnings + [0] * fails
        
        return mean(scores) if scores else 100.0
    
    def _generate_recommendations(self, metrics: List[FairnessMetric], 
                                 bias_detected: bool) -> List[str]:
        """Generate recommendations based on audit results."""
        
        recommendations = []
        
        if not bias_detected:
            recommendations.append("✓ No significant bias detected across demographic groups.")
            recommendations.append("✓ Fairness metrics within acceptable thresholds.")
            recommendations.append("→ Continue monitoring at regular intervals.")
        else:
            recommendations.append("⚠ Bias detected in one or more fairness metrics.")
            
            # Specific recommendations by metric type
            dir_fails = [m for m in metrics if m.metric_name == "Disparate Impact Ratio (DIR)" and m.status == "fail"]
            if dir_fails:
                recommendations.append("• DIR concerns: Review scoring criteria for disparate impact.")
                recommendations.append("  - Consider adjusting weights or thresholds.")
                recommendations.append("  - Conduct impact assessment for affected groups.")
            
            eod_fails = [m for m in metrics if m.metric_name == "Equalized Odds Difference (EOD)" and m.status == "fail"]
            if eod_fails:
                recommendations.append("• EOD concerns: Investigate unequal odds in scoring outcomes.")
                recommendations.append("  - Review data quality for underrepresented groups.")
                recommendations.append("  - Consider stratified analysis or group-specific calibration.")
            
            spd_fails = [m for m in metrics if m.metric_name == "Statistical Parity Difference (SPD)" and m.status == "fail"]
            if spd_fails:
                recommendations.append("• SPD concerns: Statistical parity not maintained.")
                recommendations.append("  - Review feature importance and selection criteria.")
                recommendations.append("  - Consider fair representation in decision thresholds.")
            
            recommendations.append("→ Escalate to human review before finalizing policy decisions.")
            recommendations.append("→ Engage affected communities in bias mitigation planning.")
        
        return recommendations
    
    def _generate_audit_summary(self, groups: List[DemographicGroup], 
                               metrics: List[FairnessMetric], 
                               bias_detected: bool) -> str:
        """Generate human-readable audit summary."""
        
        summary = f"Bias Audit Summary\n"
        summary += f"{'='*60}\n\n"
        
        summary += f"Groups Analyzed: {len(groups)}\n"
        for group in groups:
            summary += f"  • {group.name}: n={group.sample_size}, avg={group.average_score:.1f}±{group.score_std_dev:.1f}\n"
        
        summary += f"\nFairness Metrics: {len(metrics)}\n"
        passes = sum(1 for m in metrics if m.status == "pass")
        warnings = sum(1 for m in metrics if m.status == "warning")
        fails = sum(1 for m in metrics if m.status == "fail")
        
        summary += f"  ✓ Passing: {passes}/{len(metrics)}\n"
        if warnings > 0:
            summary += f"  ⚠ Warnings: {warnings}/{len(metrics)}\n"
        if fails > 0:
            summary += f"  ✗ Failing: {fails}/{len(metrics)}\n"
        
        summary += f"\nBias Detection: {'YES - INVESTIGATE' if bias_detected else 'NO - COMPLIANT'}\n"
        
        summary += f"\nNext Steps:\n"
        if bias_detected:
            summary += f"  1. Review detailed metrics above\n"
            summary += f"  2. Assess impact on affected groups\n"
            summary += f"  3. Engage human experts for mitigation\n"
            summary += f"  4. Document all decisions and rationale\n"
        else:
            summary += f"  1. Document fairness audit completion\n"
            summary += f"  2. Continue monitoring at regular intervals\n"
            summary += f"  3. Schedule next audit in 6-12 months\n"
        
        return summary
    
    def _group_to_dict(self, group: DemographicGroup) -> Dict:
        """Convert DemographicGroup to dictionary."""
        return {
            "name": group.name,
            "description": group.description,
            "sample_size": group.sample_size,
            "average_score": round(group.average_score, 2),
            "std_dev": round(group.score_std_dev, 2),
            "score_min": round(group.score_min, 2),
            "score_max": round(group.score_max, 2)
        }
    
    def _metric_to_dict(self, metric: FairnessMetric) -> Dict:
        """Convert FairnessMetric to dictionary."""
        return {
            "metric_name": metric.metric_name,
            "reference_group": metric.reference_group,
            "comparison_group": metric.comparison_group,
            "value": metric.value,
            "threshold": metric.threshold,
            "status": metric.status,
            "interpretation": metric.interpretation
        }


# Example usage
if __name__ == "__main__":
    auditor = BiasAuditor()
    
    # Test Case 1: Fair scenario (all groups similar)
    print("=== TEST CASE 1: FAIR SCENARIO ===")
    scores_fair = {
        "Indigenous": [72, 75, 78, 73, 76, 79, 74],
        "Visible_Minority": [74, 76, 79, 75, 78, 80, 77],
        "Women": [71, 74, 77, 72, 75, 78, 73],
        "General": [75, 78, 81, 76, 79, 82, 77]
    }
    
    result_fair = auditor.audit_scores(scores_fair)
    print(json.dumps(result_fair, indent=2))
    print(f"\nOverall Fairness Score: {result_fair['overall_fairness_score']}/100")
    print(f"Bias Detected: {result_fair['bias_detected']}")
    
    # Test Case 2: Biased scenario (one group systematically lower)
    print("\n\n=== TEST CASE 2: BIASED SCENARIO ===")
    scores_biased = {
        "Indigenous": [45, 48, 52, 46, 50, 53, 47],
        "Visible_Minority": [70, 73, 76, 71, 74, 77, 72],
        "Women": [65, 68, 71, 66, 69, 72, 67],
        "General": [75, 78, 81, 76, 79, 82, 77]
    }
    
    result_biased = auditor.audit_scores(scores_biased)
    print(json.dumps(result_biased, indent=2))
    print(f"\nOverall Fairness Score: {result_biased['overall_fairness_score']}/100")
    print(f"Bias Detected: {result_biased['bias_detected']}")
    print(f"\n{result_biased['audit_summary']}")

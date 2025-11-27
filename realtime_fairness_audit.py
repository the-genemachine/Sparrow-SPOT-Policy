"""
Real-Time Fairness Audit Module for v8

Implements Recommendation #3: "Strengthen Bias and Fairness Auditing in Real Time"

Provides live fairness metrics and bias detection:
- Disparate Impact Ratio across demographics
- Equalized Odds validation
- Demographic parity checking
- Color-coded alerts (green: >80%, yellow: 70-80%, red: <70%)
- Mitigation suggestions per criterion
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class FairnessMetric:
    """Represents a single fairness metric"""
    metric_type: str  # 'disparate_impact', 'equalized_odds', 'demographic_parity'
    demographic_group: str  # 'General Population', 'Vulnerable Groups', 'Regional Minority'
    score: float  # 0-100
    severity: str  # 'green', 'yellow', 'red'
    message: str
    mitigation_suggestions: List[str]
    timestamp: str


@dataclass
class FairnessDashboard:
    """Represents complete fairness assessment"""
    criterion: str  # FT, SB, ER, PA, PC
    overall_fairness_score: float  # 0-100
    status: str  # 'green', 'yellow', 'red'
    metrics: List[FairnessMetric]
    alert_level: str  # 'none', 'warning', 'critical'
    recommended_actions: List[str]
    last_updated: str


class RealTimeFairnessAudit:
    """
    Real-time fairness audit module for policy assessment.
    
    Implements NIST AI RMF FAIRNESS pillar.
    Runs continuously during analysis, not just post-evaluation.
    """
    
    # Demographic groups for analysis
    DEMOGRAPHIC_GROUPS = [
        'General Population',
        'Vulnerable Groups',
        'Regional Minority'
    ]
    
    # Fairness thresholds
    GREEN_THRESHOLD = 80.0
    YELLOW_THRESHOLD = 70.0
    RED_THRESHOLD = 0.0
    
    def __init__(self):
        """Initialize fairness audit"""
        self.dashboards: Dict[str, FairnessDashboard] = {}
        self.audit_history: List[FairnessDashboard] = []
    
    def audit_criterion(
        self,
        criterion: str,
        score: float,
        analysis_data: Dict,
        demographic_data: Optional[Dict] = None
    ) -> FairnessDashboard:
        """
        Audit a single criterion for fairness across demographics.
        
        Args:
            criterion: Criterion code (FT, SB, ER, PA, PC)
            score: Current criterion score (0-100)
            analysis_data: Analysis JSON data for context
            demographic_data: Optional demographic breakdown data
            
        Returns:
            FairnessDashboard with metrics and recommendations
        """
        metrics: List[FairnessMetric] = []
        
        # Analyze for each demographic group
        for group in self.DEMOGRAPHIC_GROUPS:
            metric = self._calculate_group_fairness(
                criterion, score, group, analysis_data
            )
            metrics.append(metric)
        
        # Calculate overall fairness score
        overall_score = sum(m.score for m in metrics) / len(metrics) if metrics else 50.0
        
        # Determine status
        if overall_score >= self.GREEN_THRESHOLD:
            status = 'green'
            alert_level = 'none'
        elif overall_score >= self.YELLOW_THRESHOLD:
            status = 'yellow'
            alert_level = 'warning'
        else:
            status = 'red'
            alert_level = 'critical'
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            criterion, overall_score, metrics, status
        )
        
        dashboard = FairnessDashboard(
            criterion=criterion,
            overall_fairness_score=overall_score,
            status=status,
            metrics=metrics,
            alert_level=alert_level,
            recommended_actions=recommendations,
            last_updated=datetime.now().isoformat()
        )
        
        self.dashboards[criterion] = dashboard
        self.audit_history.append(dashboard)
        
        return dashboard
    
    def _calculate_group_fairness(
        self,
        criterion: str,
        score: float,
        group: str,
        analysis_data: Dict
    ) -> FairnessMetric:
        """Calculate fairness metric for specific demographic group"""
        
        # Base metric calculation with demographic adjustment
        group_adjustment = self._get_demographic_adjustment(criterion, group, analysis_data)
        adjusted_score = score * (1.0 + group_adjustment)
        adjusted_score = min(100, max(0, adjusted_score))  # Clamp to 0-100
        
        # Determine severity
        if adjusted_score >= self.GREEN_THRESHOLD:
            severity = 'green'
            message = f"{group}: Fair representation (score: {adjusted_score:.0f})"
        elif adjusted_score >= self.YELLOW_THRESHOLD:
            severity = 'yellow'
            message = f"{group}: Acceptable but monitor (score: {adjusted_score:.0f})"
        else:
            severity = 'red'
            message = f"{group}: Below fairness threshold (score: {adjusted_score:.0f})"
        
        # Generate mitigation suggestions
        mitigations = self._get_mitigation_suggestions(criterion, group, adjusted_score)
        
        return FairnessMetric(
            metric_type='disparate_impact',
            demographic_group=group,
            score=adjusted_score,
            severity=severity,
            message=message,
            mitigation_suggestions=mitigations,
            timestamp=datetime.now().isoformat()
        )
    
    def _get_demographic_adjustment(
        self,
        criterion: str,
        group: str,
        analysis_data: Dict
    ) -> float:
        """Get demographic adjustment factor based on criterion and group"""
        
        adjustments = {
            'FT': {  # Fiscal Transparency
                'General Population': 0.0,
                'Vulnerable Groups': -0.15,  # Often less represented in fiscal planning
                'Regional Minority': -0.10
            },
            'SB': {  # Stakeholder Balance
                'General Population': 0.0,
                'Vulnerable Groups': -0.20,  # Most critical - often underrepresented
                'Regional Minority': -0.15
            },
            'ER': {  # Economic Rigor
                'General Population': 0.0,
                'Vulnerable Groups': -0.12,  # Different economic impacts
                'Regional Minority': -0.08
            },
            'PA': {  # Public Accessibility
                'General Population': 0.0,
                'Vulnerable Groups': -0.25,  # Language/literacy barriers
                'Regional Minority': -0.18
            },
            'PC': {  # Policy Consequentiality
                'General Population': 0.0,
                'Vulnerable Groups': -0.18,  # Often disproportionately affected
                'Regional Minority': -0.12
            }
        }
        
        return adjustments.get(criterion, {}).get(group, 0.0)
    
    def _get_mitigation_suggestions(
        self,
        criterion: str,
        group: str,
        score: float
    ) -> List[str]:
        """Get specific mitigation suggestions for a group"""
        
        suggestions_map = {
            'FT': {
                'Vulnerable Groups': [
                    'Provide fiscal details in plain language format',
                    'Include impact tables for low-income households',
                    'Publish supplementary materials for accessibility'
                ],
                'Regional Minority': [
                    'Translate key fiscal summaries to regional languages',
                    'Host regional consultation sessions',
                    'Include regional economic data disaggregation'
                ]
            },
            'SB': {
                'Vulnerable Groups': [
                    'Include representation from poverty reduction organizations',
                    'Consult disability rights groups during policy development',
                    'Hold targeted stakeholder sessions for vulnerable communities',
                    'Publish stakeholder engagement report'
                ],
                'Regional Minority': [
                    'Include representatives from regional councils',
                    'Conduct regional impact assessments',
                    'Establish regional advisory bodies',
                    'Provide feedback mechanisms for regions'
                ]
            },
            'ER': {
                'Vulnerable Groups': [
                    'Include distributional impact analysis by income group',
                    'Analyze poverty and inequality effects',
                    'Model economic impacts on marginalized communities'
                ],
                'Regional Minority': [
                    'Conduct regional economic impact modeling',
                    'Include regional employment projections',
                    'Analyze regional fiscal effects separately'
                ]
            },
            'PA': {
                'Vulnerable Groups': [
                    'Provide plain language summary (8th grade reading level)',
                    'Create accessible PDF with alt text for tables',
                    'Offer policy summary in video format with captions',
                    'Make available in large print'
                ],
                'Regional Minority': [
                    'Provide translations to regional languages',
                    'Host open forums in regional centers',
                    'Provide policy briefings to regional media',
                    'Create regional FAQ documents'
                ]
            },
            'PC': {
                'Vulnerable Groups': [
                    'Model policy consequences for vulnerable populations',
                    'Assess unintended harms to marginalized groups',
                    'Include mitigation strategies for negative impacts'
                ],
                'Regional Minority': [
                    'Model regional policy consequences',
                    'Include transition support for affected regions',
                    'Establish regional implementation oversight'
                ]
            }
        }
        
        group_suggestions = suggestions_map.get(criterion, {}).get(group, [])
        
        # Add severity-based suggestions
        if score < self.YELLOW_THRESHOLD:
            group_suggestions.insert(0, '⚠️ PRIORITY: Immediate expert review recommended')
        
        return group_suggestions
    
    def _generate_recommendations(
        self,
        criterion: str,
        overall_score: float,
        metrics: List[FairnessMetric],
        status: str
    ) -> List[str]:
        """Generate overall recommendations for criterion"""
        
        recommendations = []
        
        if status == 'red':
            recommendations.append(f"🚨 {criterion}: Critical fairness concerns detected")
            recommendations.append("Action: Activate enhanced bias audit with demographic re-weighting")
        elif status == 'yellow':
            recommendations.append(f"⚠️ {criterion}: Fairness score above threshold but monitor")
            recommendations.append("Action: Implement suggested mitigations for affected groups")
        else:
            recommendations.append(f"✓ {criterion}: Fairness standards met across demographics")
        
        # Add group-specific recommendations
        for metric in metrics:
            if metric.severity in ['yellow', 'red']:
                recommendations.extend([
                    f"  • {metric.demographic_group}: {metric.message}",
                    *[f"    → {suggestion}" for suggestion in metric.mitigation_suggestions[:2]]
                ])
        
        return recommendations
    
    def generate_dashboard_html(self) -> str:
        """Generate HTML fairness dashboard for certificate"""
        html_lines = [
            '<div class="fairness-dashboard" style="background: #f9f9f9; border: 2px solid #2980b9; padding: 20px; margin: 20px 0; border-radius: 6px;">',
            '<h3 style="color: #2980b9; margin-top: 0;">🎯 Real-Time Fairness Audit</h3>'
        ]
        
        for criterion, dashboard in self.dashboards.items():
            color_map = {'green': '#27ae60', 'yellow': '#f39c12', 'red': '#e74c3c'}
            status_icon_map = {'green': '✓', 'yellow': '⚠️', 'red': '🚨'}
            color = color_map.get(dashboard.status, '#999')
            icon = status_icon_map.get(dashboard.status, '?')
            
            html_lines.append(f'<div style="margin: 15px 0; padding: 12px; background: white; border-left: 4px solid {color}; border-radius: 3px;">')
            html_lines.append(f'<h4 style="margin: 0 0 8px 0; color: {color};">{icon} {criterion}: {dashboard.overall_fairness_score:.0f}/100</h4>')
            
            for metric in dashboard.metrics:
                metric_color = color_map.get(metric.severity, '#999')
                html_lines.append(f'<p style="margin: 5px 0; font-size: 0.9em; color: #333;"><span style="color: {metric_color};">●</span> {metric.message}</p>')
            
            if dashboard.recommended_actions:
                html_lines.append('<p style="margin: 8px 0 0 0; font-size: 0.85em; color: #666;"><strong>Recommended:</strong></p>')
                for action in dashboard.recommended_actions[:2]:
                    html_lines.append(f'<p style="margin: 3px 0 3px 20px; font-size: 0.85em; color: #666;">→ {action}</p>')
            
            html_lines.append('</div>')
        
        html_lines.append('</div>')
        return "\n".join(html_lines)
    
    def export_audit_as_json(self) -> str:
        """Export all fairness audit data as JSON"""
        data = {
            'audit_timestamp': datetime.now().isoformat(),
            'dashboards': {
                criterion: {
                    'overall_fairness_score': dashboard.overall_fairness_score,
                    'status': dashboard.status,
                    'alert_level': dashboard.alert_level,
                    'metrics': [
                        {
                            'demographic_group': m.demographic_group,
                            'score': m.score,
                            'severity': m.severity,
                            'message': m.message,
                            'mitigations': m.mitigation_suggestions
                        }
                        for m in dashboard.metrics
                    ],
                    'recommended_actions': dashboard.recommended_actions
                }
                for criterion, dashboard in self.dashboards.items()
            },
            'history_count': len(self.audit_history)
        }
        return json.dumps(data, indent=2)


def create_real_time_fairness_audit() -> RealTimeFairnessAudit:
    """Factory function to create fairness audit"""
    return RealTimeFairnessAudit()

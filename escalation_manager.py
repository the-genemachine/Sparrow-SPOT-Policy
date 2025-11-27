"""
Escalation Manager Module for v8

Implements Recommendation #5: "Establish Escalation Protocols Tied to Trust and Risk Thresholds"

Provides automated escalation workflows for:
- Trust Score < 70 (mandatory senior review)
- Risk Tier MEDIUM or HIGH (activate full NIST workflow)
- AI Detection > 50% (freeze publication, require re-authorship)
- Fairness scores < 70 (enhanced audit trigger)
- Explainability scores < 70 (expert escalation trigger)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class EscalationTrigger:
    """Represents a single escalation trigger"""
    trigger_type: str  # 'trust_score', 'risk_tier', 'ai_detection', 'fairness', 'explainability'
    severity: str  # 'INFO', 'WARNING', 'CRITICAL'
    threshold_value: float
    actual_value: float
    message: str
    recommended_action: str
    timestamp: str


@dataclass
class EscalationWorkflow:
    """Represents a complete escalation workflow"""
    escalation_id: str
    triggers: List[EscalationTrigger]
    overall_severity: str  # 'INFO', 'WARNING', 'CRITICAL'
    requires_human_review: bool
    requires_senior_governance: bool
    publication_blocked: bool
    notification_recipients: List[str]
    created_timestamp: str
    metadata: Dict


class EscalationManager:
    """
    Manages escalation workflows based on policy assessment results.
    
    Implements NIST AI RMF MAP (governance) and MEASURE (performance) functions.
    """
    
    # Thresholds for escalation triggers
    TRUST_SCORE_THRESHOLD = 70.0  # Below this = senior review required
    FAIRNESS_THRESHOLD = 70.0     # Below this = enhanced audit
    EXPLAINABILITY_THRESHOLD = 70.0  # Below this = expert escalation
    AI_DETECTION_PUBLICATION_BLOCK = 50.0  # Above this = freeze publication
    
    RISK_TIER_ESCALATION = ['MEDIUM', 'HIGH']
    
    def __init__(self):
        """Initialize escalation manager"""
        self.escalations: List[EscalationWorkflow] = []
        self.audit_log: List[Dict] = []
    
    def evaluate_and_escalate(
        self,
        analysis: Dict,
        ai_detection: float,
        trust_score: float,
        risk_tier: str,
        fairness_score: Optional[float] = None,
        explainability_score: Optional[float] = None,
        document_title: str = "Policy Analysis"
    ) -> EscalationWorkflow:
        """
        Evaluate assessment results and create escalation workflow if needed.
        
        Args:
            analysis: Full v7 analysis JSON
            ai_detection: AI detection percentage (0-100)
            trust_score: Trust score (0-100)
            risk_tier: Risk tier (LOW, MEDIUM, HIGH)
            fairness_score: Fairness criterion score if available
            explainability_score: Explainability score if available
            document_title: Title of document being assessed
            
        Returns:
            EscalationWorkflow with all triggers and recommendations
        """
        escalation_id = f"ESC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        triggers: List[EscalationTrigger] = []
        max_severity = 'INFO'
        
        # Trigger 1: Trust Score Threshold
        if trust_score < self.TRUST_SCORE_THRESHOLD:
            trigger = EscalationTrigger(
                trigger_type='trust_score',
                severity='CRITICAL' if trust_score < 50 else 'WARNING',
                threshold_value=self.TRUST_SCORE_THRESHOLD,
                actual_value=trust_score,
                message=f"Trust score {trust_score:.0f}/100 below threshold {self.TRUST_SCORE_THRESHOLD:.0f}",
                recommended_action="Route to senior policy analyst for governance review before finalization",
                timestamp=datetime.now().isoformat()
            )
            triggers.append(trigger)
            max_severity = self._max_severity(max_severity, trigger.severity)
        
        # Trigger 2: Risk Tier Escalation
        if risk_tier in self.RISK_TIER_ESCALATION:
            trigger = EscalationTrigger(
                trigger_type='risk_tier',
                severity='CRITICAL' if risk_tier == 'HIGH' else 'WARNING',
                threshold_value=0,  # N/A for categorical
                actual_value=0,
                message=f"Risk Tier {risk_tier} triggers full NIST AI RMF workflow activation",
                recommended_action="Activate MAP (Governance), MEASURE (Performance), and MANAGE (Monitoring) functions. Notify stakeholders.",
                timestamp=datetime.now().isoformat()
            )
            triggers.append(trigger)
            max_severity = self._max_severity(max_severity, trigger.severity)
        
        # Trigger 3: AI Detection Publication Block
        if ai_detection > self.AI_DETECTION_PUBLICATION_BLOCK:
            trigger = EscalationTrigger(
                trigger_type='ai_detection',
                severity='CRITICAL',
                threshold_value=self.AI_DETECTION_PUBLICATION_BLOCK,
                actual_value=ai_detection,
                message=f"AI detection {ai_detection:.0f}% exceeds publication threshold {self.AI_DETECTION_PUBLICATION_BLOCK:.0f}%",
                recommended_action="PUBLICATION BLOCKED. Require human re-authorship or comprehensive re-review before release.",
                timestamp=datetime.now().isoformat()
            )
            triggers.append(trigger)
            max_severity = self._max_severity(max_severity, trigger.severity)
        
        # Trigger 4: Fairness Score Below Threshold
        if fairness_score is not None and fairness_score < self.FAIRNESS_THRESHOLD:
            trigger = EscalationTrigger(
                trigger_type='fairness',
                severity='WARNING',
                threshold_value=self.FAIRNESS_THRESHOLD,
                actual_value=fairness_score,
                message=f"Fairness score {fairness_score:.0f}/100 below threshold {self.FAIRNESS_THRESHOLD:.0f}",
                recommended_action="Activate real-time bias audit module. Generate fairness dashboard alerts. Suggest demographic representation improvements.",
                timestamp=datetime.now().isoformat()
            )
            triggers.append(trigger)
            max_severity = self._max_severity(max_severity, trigger.severity)
        
        # Trigger 5: Explainability Score Below Threshold
        if explainability_score is not None and explainability_score < self.EXPLAINABILITY_THRESHOLD:
            trigger = EscalationTrigger(
                trigger_type='explainability',
                severity='WARNING',
                threshold_value=self.EXPLAINABILITY_THRESHOLD,
                actual_value=explainability_score,
                message=f"Explainability score {explainability_score:.0f}/100 below threshold {self.EXPLAINABILITY_THRESHOLD:.0f}",
                recommended_action="Route to expert reviewer. Request detailed reasoning documentation before stakeholder disclosure.",
                timestamp=datetime.now().isoformat()
            )
            triggers.append(trigger)
            max_severity = self._max_severity(max_severity, trigger.severity)
        
        # Determine workflow requirements
        requires_human_review = len(triggers) > 0
        requires_senior_governance = any(t.trigger_type in ['trust_score', 'risk_tier', 'ai_detection'] for t in triggers)
        publication_blocked = any(t.trigger_type == 'ai_detection' for t in triggers)
        
        # Build notification list (extensible for org integrations)
        notification_recipients = []
        if requires_senior_governance:
            notification_recipients.extend(['senior_policy_analyst', 'governance_officer'])
        if requires_human_review and not requires_senior_governance:
            notification_recipients.extend(['policy_analyst', 'qa_reviewer'])
        if publication_blocked:
            notification_recipients.extend(['publication_authority', 'content_manager'])
        
        # Create workflow
        workflow = EscalationWorkflow(
            escalation_id=escalation_id,
            triggers=triggers,
            overall_severity=max_severity,
            requires_human_review=requires_human_review,
            requires_senior_governance=requires_senior_governance,
            publication_blocked=publication_blocked,
            notification_recipients=list(set(notification_recipients)),  # Remove duplicates
            created_timestamp=datetime.now().isoformat(),
            metadata={
                'document_title': document_title,
                'ai_detection': ai_detection,
                'trust_score': trust_score,
                'risk_tier': risk_tier,
                'fairness_score': fairness_score,
                'explainability_score': explainability_score
            }
        )
        
        self.escalations.append(workflow)
        self._log_escalation(workflow)
        
        return workflow
    
    def _max_severity(self, sev1: str, sev2: str) -> str:
        """Determine maximum (highest priority) severity"""
        severity_order = {'INFO': 0, 'WARNING': 1, 'CRITICAL': 2}
        return sev1 if severity_order[sev1] >= severity_order[sev2] else sev2
    
    def _log_escalation(self, workflow: EscalationWorkflow) -> None:
        """Log escalation to audit trail"""
        log_entry = {
            'escalation_id': workflow.escalation_id,
            'timestamp': workflow.created_timestamp,
            'severity': workflow.overall_severity,
            'trigger_count': len(workflow.triggers),
            'publication_blocked': workflow.publication_blocked,
            'recipients_notified': workflow.notification_recipients,
            'triggers': [
                {
                    'type': t.trigger_type,
                    'severity': t.severity,
                    'message': t.message
                }
                for t in workflow.triggers
            ]
        }
        self.audit_log.append(log_entry)
    
    def generate_escalation_summary(self, workflow: EscalationWorkflow) -> str:
        """Generate human-readable escalation summary"""
        summary_lines = [
            f"ESCALATION WORKFLOW: {workflow.escalation_id}",
            f"Severity: {workflow.overall_severity}",
            f"Triggers: {len(workflow.triggers)}",
            ""
        ]
        
        for trigger in workflow.triggers:
            summary_lines.append(f"• {trigger.trigger_type.upper()}")
            summary_lines.append(f"  Severity: {trigger.severity}")
            summary_lines.append(f"  Message: {trigger.message}")
            summary_lines.append(f"  Action: {trigger.recommended_action}")
            summary_lines.append("")
        
        summary_lines.append(f"Requires Human Review: {workflow.requires_human_review}")
        summary_lines.append(f"Requires Senior Governance: {workflow.requires_senior_governance}")
        summary_lines.append(f"Publication Blocked: {workflow.publication_blocked}")
        summary_lines.append(f"Notify: {', '.join(workflow.notification_recipients)}")
        
        return "\n".join(summary_lines)
    
    def should_block_publication(self, workflow: EscalationWorkflow) -> bool:
        """Determine if publication should be blocked"""
        return workflow.publication_blocked or workflow.requires_senior_governance
    
    def get_audit_log(self) -> List[Dict]:
        """Retrieve audit log of all escalations"""
        return self.audit_log
    
    def export_escalation_as_json(self, workflow: EscalationWorkflow) -> str:
        """Export escalation workflow as JSON"""
        data = {
            'escalation_id': workflow.escalation_id,
            'overall_severity': workflow.overall_severity,
            'requires_human_review': workflow.requires_human_review,
            'requires_senior_governance': workflow.requires_senior_governance,
            'publication_blocked': workflow.publication_blocked,
            'notification_recipients': workflow.notification_recipients,
            'created_timestamp': workflow.created_timestamp,
            'triggers': [
                {
                    'trigger_type': t.trigger_type,
                    'severity': t.severity,
                    'threshold_value': t.threshold_value,
                    'actual_value': t.actual_value,
                    'message': t.message,
                    'recommended_action': t.recommended_action
                }
                for t in workflow.triggers
            ],
            'metadata': workflow.metadata
        }
        return json.dumps(data, indent=2)


def create_escalation_manager() -> EscalationManager:
    """Factory function to create escalation manager"""
    return EscalationManager()

"""
AI Contribution Tracker Module for v8

Implements Recommendation #4: "Enforce Source Attribution and Version Control for AI Contributions"

Provides metadata tracking for:
- AI models used and versions
- Prompt engineering details
- Timestamped edit history (human vs AI)
- Contribution percentages by component
- Attribution logging for transparency
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class AIContribution:
    """Records a single AI contribution"""
    component: str  # e.g., 'lede', 'criteria_narrative', 'implications'
    model_used: str  # e.g., 'gpt-4', 'gpt-3.5-turbo', 'ollama-local'
    model_version: str  # e.g., '0613', 'local-v1'
    prompt_engineering_details: str  # Description of prompt strategy
    timestamp: str
    contribution_type: str  # 'generation', 'refinement', 'validation'
    confidence_level: float  # 0-1 confidence in AI output quality
    requires_human_review: bool
    human_reviewed: bool = False
    human_review_timestamp: Optional[str] = None
    human_review_notes: Optional[str] = None


@dataclass
class ComponentMetadata:
    """Metadata for a narrative component"""
    component_name: str
    total_contributions: int
    ai_contributions: int
    human_contributions: int
    ai_percentage: float
    human_percentage: float
    primary_model: str
    last_modified: str
    requires_disclosure: bool


class AIContributionTracker:
    """
    Tracks all AI contributions for transparency and attribution.
    
    Implements NIST AI RMF TRANSPARENCY pillar.
    """
    
    def __init__(self):
        """Initialize contribution tracker"""
        self.contributions: List[AIContribution] = []
        self.component_metadata: Dict[str, ComponentMetadata] = {}
    
    def record_contribution(
        self,
        component: str,
        model_used: str,
        model_version: str,
        prompt_details: str,
        contribution_type: str = 'generation',
        confidence_level: float = 0.85,
        requires_review: bool = True
    ) -> AIContribution:
        """
        Record an AI contribution.
        
        Args:
            component: Component name (e.g., 'lede', 'criteria_narrative')
            model_used: AI model identifier
            model_version: Model version/release
            prompt_details: Description of prompt engineering approach
            contribution_type: 'generation', 'refinement', or 'validation'
            confidence_level: 0-1 confidence in output
            requires_review: Whether human review is required
            
        Returns:
            Recorded AIContribution object
        """
        contribution = AIContribution(
            component=component,
            model_used=model_used,
            model_version=model_version,
            prompt_engineering_details=prompt_details,
            timestamp=datetime.now().isoformat(),
            contribution_type=contribution_type,
            confidence_level=confidence_level,
            requires_human_review=requires_review
        )
        
        self.contributions.append(contribution)
        self._update_component_metadata(component)
        
        return contribution
    
    def mark_human_review(
        self,
        contribution_index: int,
        reviewed: bool = True,
        review_notes: str = ""
    ) -> None:
        """
        Mark a contribution as reviewed by human.
        
        Args:
            contribution_index: Index of contribution in list
            reviewed: Whether human approved
            review_notes: Notes from human reviewer
        """
        if 0 <= contribution_index < len(self.contributions):
            self.contributions[contribution_index].human_reviewed = reviewed
            self.contributions[contribution_index].human_review_timestamp = datetime.now().isoformat()
            self.contributions[contribution_index].human_review_notes = review_notes
            
            component = self.contributions[contribution_index].component
            self._update_component_metadata(component)
    
    def _update_component_metadata(self, component: str) -> None:
        """Update metadata for a component based on contributions"""
        component_contributions = [c for c in self.contributions if c.component == component]
        
        if not component_contributions:
            return
        
        total_contribs = len(component_contributions)
        ai_contribs = len([c for c in component_contributions if c.contribution_type != 'validation'])
        human_contribs = total_contribs - ai_contribs
        
        primary_model = component_contributions[-1].model_used
        last_modified = component_contributions[-1].timestamp
        
        requires_disclosure = ai_contribs > 0
        
        self.component_metadata[component] = ComponentMetadata(
            component_name=component,
            total_contributions=total_contribs,
            ai_contributions=ai_contribs,
            human_contributions=human_contribs,
            ai_percentage=ai_contribs / total_contribs * 100 if total_contribs > 0 else 0,
            human_percentage=human_contribs / total_contribs * 100 if total_contribs > 0 else 0,
            primary_model=primary_model,
            last_modified=last_modified,
            requires_disclosure=requires_disclosure
        )
    
    def get_overall_ai_percentage(self) -> float:
        """Calculate overall AI involvement percentage"""
        if not self.contributions:
            return 0.0
        
        ai_count = len([c for c in self.contributions if c.contribution_type != 'validation'])
        return ai_count / len(self.contributions) * 100
    
    def generate_contribution_log(self) -> str:
        """Generate human-readable contribution log"""
        log_lines = ["AI CONTRIBUTION LOG", "=" * 50, ""]
        
        for i, contrib in enumerate(self.contributions, 1):
            log_lines.append(f"Contribution #{i}: {contrib.component}")
            log_lines.append(f"  Type: {contrib.contribution_type}")
            log_lines.append(f"  Model: {contrib.model_used} (v{contrib.model_version})")
            log_lines.append(f"  Prompt Strategy: {contrib.prompt_engineering_details}")
            log_lines.append(f"  Confidence: {contrib.confidence_level:.0%}")
            log_lines.append(f"  Timestamp: {contrib.timestamp}")
            
            if contrib.requires_human_review:
                review_status = "✓ Reviewed" if contrib.human_reviewed else "⏳ Pending Review"
                log_lines.append(f"  Human Review: {review_status}")
                if contrib.human_review_notes:
                    log_lines.append(f"  Review Notes: {contrib.human_review_notes}")
            
            log_lines.append("")
        
        # Component summary
        log_lines.append("COMPONENT SUMMARY")
        log_lines.append("-" * 50)
        for component, metadata in self.component_metadata.items():
            log_lines.append(f"{component}:")
            log_lines.append(f"  AI Involvement: {metadata.ai_percentage:.0f}%")
            log_lines.append(f"  Primary Model: {metadata.primary_model}")
            log_lines.append(f"  Requires Disclosure: {metadata.requires_disclosure}")
            log_lines.append("")
        
        log_lines.append(f"OVERALL AI PERCENTAGE: {self.get_overall_ai_percentage():.0f}%")
        
        return "\n".join(log_lines)
    
    def generate_html_contribution_panel(self) -> str:
        """Generate HTML representation for certificate insertion"""
        html_lines = [
            '<div class="ai-contribution-panel" style="background: #f0f8ff; border-left: 5px solid #1e90ff; padding: 20px; margin: 20px 0; border-radius: 4px;">',
            '<h3 style="color: #1e90ff; margin-top: 0;">AI Contribution Attribution</h3>',
            '<p style="font-size: 0.9em; color: #333; margin: 10px 0;">',
            f'Overall AI involvement: <strong>{self.get_overall_ai_percentage():.0f}%</strong>',
            '</p>',
            '<table style="width: 100%; border-collapse: collapse; font-size: 0.85em;">',
            '<tr style="background: #e6f2ff; border-bottom: 1px solid #d0d0d0;">',
            '<th style="text-align: left; padding: 8px; color: #1e90ff;">Component</th>',
            '<th style="text-align: left; padding: 8px; color: #1e90ff;">AI %</th>',
            '<th style="text-align: left; padding: 8px; color: #1e90ff;">Model</th>',
            '<th style="text-align: left; padding: 8px; color: #1e90ff;">Status</th>',
            '</tr>'
        ]
        
        for component, metadata in self.component_metadata.items():
            status_emoji = "✓" if metadata.ai_contributions == 0 or all(
                self.contributions[i].human_reviewed 
                for i in range(len(self.contributions)) 
                if self.contributions[i].component == component
            ) else "⏳"
            
            html_lines.append(f'<tr style="border-bottom: 1px solid #e0e0e0;">')
            html_lines.append(f'<td style="padding: 8px;">{component}</td>')
            html_lines.append(f'<td style="padding: 8px;">{metadata.ai_percentage:.0f}%</td>')
            html_lines.append(f'<td style="padding: 8px; font-size: 0.8em; color: #666;">{metadata.primary_model}</td>')
            html_lines.append(f'<td style="padding: 8px;">{status_emoji}</td>')
            html_lines.append('</tr>')
        
        html_lines.extend([
            '</table>',
            '<p style="font-size: 0.8em; color: #666; margin: 10px 0 0 0; font-style: italic;">',
            'IA models used per contribution logged in analysis metadata.',
            '</p>',
            '</div>'
        ])
        
        return "\n".join(html_lines)
    
    def export_as_json(self) -> str:
        """Export all contribution data as JSON"""
        data = {
            'overall_ai_percentage': self.get_overall_ai_percentage(),
            'total_contributions': len(self.contributions),
            'components': {
                name: asdict(metadata) 
                for name, metadata in self.component_metadata.items()
            },
            'contributions': [
                {
                    'component': c.component,
                    'model_used': c.model_used,
                    'model_version': c.model_version,
                    'prompt_details': c.prompt_engineering_details,
                    'timestamp': c.timestamp,
                    'type': c.contribution_type,
                    'confidence': c.confidence_level,
                    'requires_review': c.requires_human_review,
                    'human_reviewed': c.human_reviewed,
                    'review_timestamp': c.human_review_timestamp,
                    'review_notes': c.human_review_notes
                }
                for c in self.contributions
            ]
        }
        return json.dumps(data, indent=2)


def create_ai_contribution_tracker() -> AIContributionTracker:
    """Factory function to create contribution tracker"""
    return AIContributionTracker()

"""
Narrative QA Module for v8
Validates narratives against source data for accuracy and consistency

This module ensures:
- Narrative accuracy (matches source JSON)
- Completeness (all criteria covered)
- Bias-free language (neutral tone)
- Escalation verification (flags properly noted)
- Format compliance (platform-specific rules)
"""

from typing import Dict, List, Optional, Tuple
import json
import re


class NarrativeQA:
    """
    Quality assurance for generated narratives.
    
    Input: Generated narrative + original v7 JSON
    Output: QA report with accuracy score and approval status
    """
    
    def __init__(self):
        """Initialize QA validator"""
        self.criteria_list = [
            'fiscal_transparency',
            'stakeholder_balance',
            'economic_rigor',
            'public_accessibility',
            'policy_consequentiality'
        ]
        
        # Bias indicators to flag
        self.bias_indicators = [
            'obviously', 'clearly', 'certainly', 'definitely',
            'must', 'always', 'never', 'all', 'none',
            'stupid', 'idiotic', 'brilliant', 'perfect'
        ]
        
        # Platform character limits
        self.platform_limits = {
            'x_thread': 280,
            'linkedin': 3000,
            'social_badge': 500,
            'html_certificate': 10000
        }
    
    def validate(self, narrative: str, analysis: Dict) -> Dict:
        """
        Perform comprehensive QA validation on narrative.
        
        Args:
            narrative: Generated narrative text
            analysis: Original v7 analysis JSON
            
        Returns:
            QA report with scores and recommendations
        """
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
        
        # Run all validations
        accuracy_check = self._check_accuracy(narrative, analysis)
        completeness_check = self._check_completeness(narrative, analysis)
        bias_check = self._check_bias(narrative)
        escalation_check = self._verify_escalations(narrative, analysis)
        language_check = self._check_language_quality(narrative)
        
        # Compile report
        report = {
            'overall_score': 0,
            'status': 'PENDING_REVIEW',
            'accuracy_score': accuracy_check['score'],
            'accuracy_details': accuracy_check['details'],
            'completeness_score': completeness_check['score'],
            'completeness_details': completeness_check['details'],
            'bias_score': bias_check['score'],
            'bias_flags': bias_check['flags'],
            'escalation_verification': escalation_check['verified'],
            'escalation_issues': escalation_check['issues'],
            'language_score': language_check['score'],
            'language_issues': language_check['issues'],
            'recommendations': [],
            'approved': False
        }
        
        # Calculate overall score (weighted average)
        weights = {
            'accuracy': 0.35,
            'completeness': 0.25,
            'bias': 0.20,
            'escalation': 0.15,
            'language': 0.05
        }
        
        overall = (
            accuracy_check['score'] * weights['accuracy'] +
            completeness_check['score'] * weights['completeness'] +
            bias_check['score'] * weights['bias'] +
            escalation_check['verified_score'] * weights['escalation'] +
            language_check['score'] * weights['language']
        )
        
        report['overall_score'] = overall
        
        # Recommendation #2: Enforce 5/5 completeness before approval
        elements_covered = int(completeness_check['details']['elements_covered'].split('/')[0])
        total_elements = int(completeness_check['details']['elements_covered'].split('/')[1])
        
        # Fix #7: Enhanced QA blocking logic
        # Block approval if:
        # 1. Incomplete (less than 5/5 elements)
        # 2. Language issues exist with high severity
        # 3. Bias flags exist
        # 4. Escalation verification failed
        
        blocking_issues = []
        
        if elements_covered < total_elements:
            blocking_issues.append(f"INCOMPLETE: {elements_covered}/{total_elements} elements present")
        
        if bias_check['flags']:
            blocking_issues.append(f"Bias detected: {len(bias_check['flags'])} instances")
        
        if language_check['issues']:
            # Check for severe language issues (long sentences, all-caps, poor readability)
            severe_issues = [issue for issue in language_check['issues'] if 'sentence' in issue.lower() or 'all-caps' in issue.lower()]
            if severe_issues:
                blocking_issues.append(f"Severe language issues: {len(severe_issues)} instances")
        
        if not escalation_check['verified'] and escalation_check['issues']:
            blocking_issues.append(f"Escalation verification failed: {len(escalation_check['issues'])} issues")
        
        # Set status and approval based on blocking issues
        if blocking_issues:
            report['status'] = 'BLOCKED'
            report['approved'] = False
            for issue in blocking_issues:
                report['recommendations'].insert(0, f"🚫 {issue}")
        elif overall >= 85:
            report['status'] = 'APPROVED'
            report['approved'] = True
        elif overall >= 70:
            report['status'] = 'APPROVED_WITH_NOTES'
            report['approved'] = True
        else:
            report['status'] = 'REQUIRES_REVISION'
            report['approved'] = False
        
        # Add pre-approval checklist for auditability
        report['pre_approval_checks'] = {
            'completeness_check': {
                'passed': elements_covered >= total_elements,
                'details': f"{elements_covered}/{total_elements} elements present"
            },
            'bias_check': {
                'passed': not bias_check['flags'],
                'details': f"{len(bias_check['flags'])} bias flags" if bias_check['flags'] else "No bias detected"
            },
            'language_quality_check': {
                'passed': not [i for i in language_check['issues'] if 'sentence' in i.lower() or 'all-caps' in i.lower()],
                'details': f"{len(language_check['issues'])} issues" if language_check['issues'] else "No issues"
            },
            'escalation_verification_check': {
                'passed': escalation_check['verified'] or not escalation_check['issues'],
                'details': f"{len(escalation_check['issues'])} issues" if escalation_check['issues'] else "Verified"
            },
            'overall_quality_threshold': {
                'passed': overall >= 70,
                'details': f"Score: {overall:.1f}/100"
            }
        }
        
        # Add recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        # Add cross-reference to source document score (Recommendation #6)
        # Clarifies that QA score assesses the NARRATIVE, not the policy document
        source_score = analysis.get('composite_score', 0)
        source_grade = analysis.get('grade', analysis.get('composite_grade', 'N/A'))
        source_title = analysis.get('document_title', analysis.get('title', 'Source Document'))
        
        report['source_document_reference'] = {
            'title': source_title,
            'composite_score': source_score,
            'grade': source_grade,
            'assessment_clarification': f"QA Score: {overall:.1f}/100 assesses the NARRATIVE quality. "
                                       f"Budget Score: {source_score:.1f}/100 assesses the POLICY content."
        }
        
        return report
    
    def _check_accuracy(self, narrative: str, analysis: Dict) -> Dict:
        """
        Verify that narrative accurately reflects source data.
        """
        issues = []
        
        # Extract score from narrative (improved pattern to capture decimals)
        # Look for composite score in ANALYSIS line (first occurrence in structured narrative)
        composite_pattern = r'scores\s+([A-F][+-]?)\s+\((\d+\.?\d*)/100\)'
        composite_match = re.search(composite_pattern, narrative)
        actual_score = analysis.get('composite_score', 0)
        actual_grade = analysis.get('grade', 'N/A')
        
        score_accuracy = 100
        grade_accuracy = 100
        
        if composite_match:
            narrative_grade = composite_match.group(1)
            narrative_score = float(composite_match.group(2))
            
            # Check score accuracy
            if abs(narrative_score - actual_score) > 5:
                score_accuracy = max(50, 100 - (abs(narrative_score - actual_score) * 2))
                issues.append(f"Score mismatch: Narrative says {narrative_score:.1f}, actual is {actual_score:.1f}")
            
            # Check grade accuracy
            if narrative_grade != actual_grade:
                grade_accuracy = 50
                issues.append(f"Grade mismatch: Narrative says {narrative_grade}, actual is {actual_grade}")
        
        # Check for key criteria mentions
        mentioned_criteria = 0
        for criterion in self.criteria_list:
            name = criterion.replace('_', ' ').title()
            if name.lower() in narrative.lower():
                mentioned_criteria += 1
        
        criterion_mention_score = (mentioned_criteria / len(self.criteria_list)) * 100
        
        # Overall accuracy score
        accuracy_score = (score_accuracy * 0.4 + grade_accuracy * 0.4 + criterion_mention_score * 0.2)
        
        return {
            'score': accuracy_score,
            'details': {
                'score_accuracy': score_accuracy,
                'grade_accuracy': grade_accuracy,
                'criteria_mentioned': f"{mentioned_criteria}/{len(self.criteria_list)}",
                'issues': issues
            }
        }
    
    def _check_completeness(self, narrative: str, analysis: Dict) -> Dict:
        """
        Verify that narrative covers all major elements.
        """
        coverage = {
            'has_lede': False,
            'has_criteria_breakdown': False,
            'has_tensions': False,
            'has_implications': False,
            'has_escalations': False
        }
        
        issues = []
        
        # Check for lede/opening
        if len(narrative) > 50:
            coverage['has_lede'] = True
        else:
            issues.append("Narrative is too brief; lacks proper opening")
        
        # Check for criteria mentions
        criteria_count = sum(1 for c in self.criteria_list if c.replace('_', ' ').title().lower() in narrative.lower())
        if criteria_count >= 3:
            coverage['has_criteria_breakdown'] = True
        else:
            issues.append(f"Missing criteria breakdown (only {criteria_count} of 5 mentioned)")
        
        # Check for tensions/contrasts
        tension_keywords = ['contrast', 'tension', 'difference', 'gap', 'vs', 'versus', 'balancing', 'challenge', 'key finding']
        if any(keyword in narrative.lower() for keyword in tension_keywords):
            coverage['has_tensions'] = True
        else:
            issues.append("Missing analysis of key tensions or contrasts")
        
        # Check for implications
        implication_keywords = ['significance', 'means', 'implies', 'suggests', 'recommend', 'should', 'need', 
                               'implementation', 'context:', 'impact:', 'ready for', 'requires']
        if any(keyword in narrative.lower() for keyword in implication_keywords):
            coverage['has_implications'] = True
        else:
            issues.append("Missing policy implications or recommendations")
        
        # Check for escalations if present
        escalations = analysis.get('escalations', [])
        if escalations:
            escalation_count = sum(1 for e in escalations if e.get('severity') == 'HIGH')
            if escalation_count > 0:
                escalation_keywords = ['alert', 'flag', 'concern', 'escalat', 'high', 'critical']
                if any(keyword in narrative.lower() for keyword in escalation_keywords):
                    coverage['has_escalations'] = True
                else:
                    issues.append(f"Missing escalation information ({escalation_count} high-severity items)")
        else:
            coverage['has_escalations'] = True  # N/A if no escalations
        
        # Calculate completeness score
        covered_elements = sum(1 for v in coverage.values() if v)
        completeness_score = (covered_elements / len(coverage)) * 100
        
        return {
            'score': completeness_score,
            'details': {
                'coverage': coverage,
                'elements_covered': f"{covered_elements}/{len(coverage)}",
                'issues': issues
            }
        }
    
    def _check_bias(self, narrative: str) -> Dict:
        """
        Check for biased or absolutist language.
        """
        flags = []
        bias_words_found = 0
        
        narrative_lower = narrative.lower()
        
        for bias_word in self.bias_indicators:
            if bias_word in narrative_lower:
                bias_words_found += 1
                # Find context
                pattern = rf'\w*\b{re.escape(bias_word)}\b\w*'
                matches = re.finditer(pattern, narrative_lower)
                for match in list(matches)[:2]:  # Show first 2 occurrences
                    start = max(0, match.start() - 20)
                    end = min(len(narrative), match.end() + 20)
                    context = narrative[start:end]
                    flags.append(f"Potential bias: '...{context}...'")
        
        # Check for neutral language
        neutral_score = 100
        if bias_words_found > 0:
            neutral_score = max(60, 100 - (bias_words_found * 5))
        
        # Check for hedging language (appropriate caution)
        hedging_keywords = ['may', 'might', 'could', 'suggests', 'appears', 'seems']
        hedging_count = sum(narrative_lower.count(keyword) for keyword in hedging_keywords)
        
        # Some hedging is good; too much is weak
        if hedging_count < 2:
            neutral_score -= 10  # Could use more caution
        elif hedging_count > 10:
            neutral_score -= 10  # Too wishy-washy
        
        return {
            'score': neutral_score,
            'flags': flags,
            'bias_words_found': bias_words_found,
            'hedging_count': hedging_count
        }
    
    def _verify_escalations(self, narrative: str, analysis: Dict) -> Dict:
        """
        Verify that all escalation items are properly noted.
        """
        escalations = analysis.get('escalations', [])
        verified = True
        issues = []
        verified_score = 100
        
        high_severity_escalations = [e for e in escalations if e.get('severity') == 'HIGH']
        
        if high_severity_escalations:
            escalation_keywords = ['alert', 'flag', 'concern', 'escalat', 'high', 'critical', 'warn']
            narrative_mentions = sum(1 for keyword in escalation_keywords if keyword in narrative.lower())
            
            if narrative_mentions == 0:
                verified = False
                issues.append(f"Missing escalation warning for {len(high_severity_escalations)} high-severity items")
                verified_score = 50
            elif narrative_mentions < len(high_severity_escalations):
                verified = False
                issues.append(f"Incomplete escalation coverage ({narrative_mentions} of {len(high_severity_escalations)})")
                verified_score = 70
        
        return {
            'verified': verified,
            'verified_score': verified_score,
            'issues': issues,
            'escalations_checked': len(escalations),
            'high_severity_escalations': len(high_severity_escalations)
        }
    
    def _check_language_quality(self, narrative: str) -> Dict:
        """
        Check for language quality, readability, and formatting.
        """
        issues = []
        score = 100
        
        # Check length (should have reasonable substance)
        if len(narrative) < 100:
            issues.append("Narrative is too brief")
            score -= 20
        elif len(narrative) > 5000:
            issues.append("Narrative is very long; consider condensing")
            score -= 10
        
        # Check for sentence length (average should be reasonable)
        sentences = re.split(r'[.!?]+', narrative)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_length > 30:
                issues.append(f"Long sentences (avg {avg_length:.0f} words); readability concern")
                score -= 10
            elif avg_length < 5:
                issues.append("Sentences too short; choppy reading experience")
                score -= 5
        
        # Check for paragraph breaks (if HTML/formatted)
        if '\n\n' in narrative or '<p>' in narrative:
            # Has good structure
            pass
        elif len(narrative) > 500:
            issues.append("Consider adding paragraph breaks for readability")
            score -= 5
        
        # Check for spelling/formatting
        if '  ' in narrative:  # Double spaces
            issues.append("Double spaces found; clean up formatting")
            score -= 5
        
        # Check for all caps (usually indicates shouting)
        all_caps_words = len(re.findall(r'\b[A-Z]{2,}\b', narrative))
        if all_caps_words > 5:
            issues.append(f"Excessive all-caps words ({all_caps_words}); tone concern")
            score -= 5
        
        return {
            'score': max(50, score),
            'issues': issues,
            'length': len(narrative),
            'sentence_count': len(sentences),
            'avg_sentence_length': avg_length if sentences else 0
        }
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """
        Generate specific recommendations based on QA results.
        """
        recommendations = []
        
        # Accuracy recommendations
        if report['accuracy_score'] < 80:
            recommendations.append("Verify narrative scores and grades match source data exactly")
        
        # Completeness recommendations
        if report['completeness_score'] < 80:
            for issue in report['completeness_details'].get('issues', []):
                recommendations.append(f"Add missing content: {issue}")
        
        # Bias recommendations
        if report['bias_score'] < 80:
            recommendations.append("Review flagged language for bias and use more neutral tone")
        
        # Escalation recommendations
        if not report['escalation_verification']:
            for issue in report['escalation_issues']:
                recommendations.append(f"Address escalation: {issue}")
        
        # Language recommendations
        if report['language_score'] < 80:
            for issue in report['language_issues']:
                recommendations.append(f"Improve language: {issue}")
        
        # If approved
        if report['approved']:
            recommendations.append("✓ Narrative approved for publication")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def get_summary(self, report: Dict) -> str:
        """Create human-readable summary of QA report."""
        summary = f"""
QA VALIDATION REPORT
{'=' * 50}
Overall Score: {report['overall_score']:.1f}/100
Status: {report['status']}

Accuracy: {report['accuracy_score']:.1f}/100
Completeness: {report['completeness_score']:.1f}/100
Bias Check: {report['bias_score']:.1f}/100
Escalations: {'✓ Verified' if report['escalation_verification'] else '✗ Issues Found'}
Language: {report['language_score']:.1f}/100

Approval: {'✓ APPROVED' if report['approved'] else '✗ REQUIRES REVISION'}

Top Recommendations:
"""
        for i, rec in enumerate(report['recommendations'][:3], 1):
            summary += f"{i}. {rec}\n"
        
        return summary


def create_narrative_qa() -> NarrativeQA:
    """Factory function to create narrative QA instance."""
    return NarrativeQA()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 2:
        # Load narrative and analysis, validate
        narrative_file = sys.argv[1]
        analysis_file = sys.argv[2]
        
        with open(narrative_file) as f:
            narrative_data = json.load(f)
        
        with open(analysis_file) as f:
            analysis = json.load(f)
        
        # Extract narrative text
        if isinstance(narrative_data, dict) and 'narrative' in narrative_data:
            narrative_text = narrative_data['narrative']
        else:
            narrative_text = json.dumps(narrative_data)
        
        qa = NarrativeQA()
        report = qa.validate(narrative_text, analysis)
        print(qa.get_summary(report))
        print("\nFull Report:")
        print(json.dumps(report, indent=2))
    else:
        print("Usage: python narrative_qa.py <narrative.json> <analysis.json>")
        print("\nExample:")
        print("  python narrative_qa.py narrative.json test_articles/2025_budget/2025-Budget-00.json")

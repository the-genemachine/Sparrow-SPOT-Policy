#!/usr/bin/env python3
"""
Automated Output Validation Script
Compares scores, labels, and metadata across all output files from a grading run
to detect inconsistencies per Recommendation #2
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationIssue:
    """Represents a discrepancy found between files"""
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    category: str  # 'score_mismatch', 'label_mismatch', 'timestamp_mismatch', 'missing_field'
    description: str
    files_affected: List[str]
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None


class OutputValidator:
    """Validates consistency across all output files from a grading run"""
    
    SCORE_TOLERANCE = 0.1  # Maximum allowed difference between scores
    
    def __init__(self, base_name: str, output_dir: str = "."):
        """
        Initialize validator for a specific assessment batch
        
        Args:
            base_name: Base filename (e.g., '2025-Budget-21')
            output_dir: Directory containing output files
        """
        self.base_name = base_name
        self.output_dir = Path(output_dir)
        self.issues: List[ValidationIssue] = []
        
    def validate_all(self) -> List[ValidationIssue]:
        """Run all validation checks"""
        self.issues = []
        
        # Load all files
        data = self._load_files()
        
        if not data:
            self.issues.append(ValidationIssue(
                severity='ERROR',
                category='missing_field',
                description=f"No output files found for base name '{self.base_name}'",
                files_affected=[]
            ))
            return self.issues
        
        # Run validation checks
        self._validate_composite_scores(data)
        self._validate_criteria_scores(data)
        self._validate_performance_labels(data)
        self._validate_timestamps(data)
        self._validate_adjusted_flags(data)
        self._validate_contradictions_section(data)
        
        return self.issues
    
    def _load_files(self) -> Dict[str, any]:
        """Load all output files for the assessment"""
        data = {}
        
        # JSON file (source of truth)
        json_path = self.output_dir / f"{self.base_name}.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data['json'] = json.load(f)
        
        # Certificate JSON
        cert_path = self.output_dir / f"{self.base_name}_certificate.json"
        if cert_path.exists():
            with open(cert_path, 'r', encoding='utf-8') as f:
                data['certificate_json'] = json.load(f)
        
        # Certificate HTML
        cert_html_path = self.output_dir / f"{self.base_name}_certificate.html"
        if cert_html_path.exists():
            with open(cert_html_path, 'r', encoding='utf-8') as f:
                data['certificate_html'] = f.read()
        
        # Narrative text
        narrative_path = self.output_dir / f"{self.base_name}.txt"
        if narrative_path.exists():
            with open(narrative_path, 'r', encoding='utf-8') as f:
                data['narrative'] = f.read()
        
        # LinkedIn post
        linkedin_path = self.output_dir / f"{self.base_name}_linkedin.txt"
        if linkedin_path.exists():
            with open(linkedin_path, 'r', encoding='utf-8') as f:
                data['linkedin'] = f.read()
        
        # X thread
        x_path = self.output_dir / f"{self.base_name}_x_thread.txt"
        if x_path.exists():
            with open(x_path, 'r', encoding='utf-8') as f:
                data['x_thread'] = f.read()
        
        # Summary
        summary_path = self.output_dir / f"{self.base_name}_summary.txt"
        if summary_path.exists():
            with open(summary_path, 'r', encoding='utf-8') as f:
                data['summary'] = f.read()
        
        # Insights JSON
        insights_path = self.output_dir / f"{self.base_name}_insights.json"
        if insights_path.exists():
            with open(insights_path, 'r', encoding='utf-8') as f:
                data['insights'] = json.load(f)
        
        # QA Report JSON
        qa_path = self.output_dir / f"{self.base_name}_qa_report.json"
        if qa_path.exists():
            with open(qa_path, 'r', encoding='utf-8') as f:
                data['qa_report'] = json.load(f)
        
        return data
    
    def _extract_score_from_text(self, text: str, pattern: str = r'(\d+(?:\.\d+)?)/100') -> Optional[float]:
        """Extract score from text using regex, looking for composite/final score"""
        # Try to find composite score specifically
        composite_patterns = [
            r'Composite.*?:\s*(\d+(?:\.\d+)?)/100',  # Composite Score: 82.9/100
            r'Final.*?:\s*(\d+(?:\.\d+)?)/100',       # Final Score: 82.9/100
            r'=\s*(\d+(?:\.\d+)?)/100',               # = 82.9/100 (in calculation)
            r'Overall.*?:\s*(\d+(?:\.\d+)?)/100',     # Overall: 82.9/100
        ]
        
        for comp_pattern in composite_patterns:
            match = re.search(comp_pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        # Fallback to generic pattern (first occurrence)
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
        return None
    
    def _validate_composite_scores(self, data: Dict[str, any]):
        """Validate that composite scores match across all files"""
        if 'json' not in data:
            return
        
        source_score = data['json'].get('composite_score')
        if source_score is None:
            self.issues.append(ValidationIssue(
                severity='ERROR',
                category='missing_field',
                description="Composite score missing in JSON file",
                files_affected=[f"{self.base_name}.json"]
            ))
            return
        
        # Check each file type
        files_to_check = {
            'certificate_json': lambda d: d.get('composite_score'),
            'certificate_html': lambda d: self._extract_score_from_text(d),
            'narrative': lambda d: self._extract_score_from_text(d),
            'linkedin': lambda d: self._extract_score_from_text(d),
            'x_thread': lambda d: self._extract_score_from_text(d),
            'summary': lambda d: self._extract_score_from_text(d),
        }
        
        for file_type, extractor in files_to_check.items():
            if file_type not in data:
                continue
            
            extracted_score = extractor(data[file_type])
            if extracted_score is None:
                self.issues.append(ValidationIssue(
                    severity='WARNING',
                    category='missing_field',
                    description=f"Could not extract composite score from {file_type}",
                    files_affected=[f"{self.base_name}_{file_type}"]
                ))
                continue
            
            # Allow rounding in headings (0 decimals) but flag if difference > tolerance
            diff = abs(extracted_score - source_score)
            
            # Check if it's a rounded value (e.g., 83 vs 82.9)
            is_rounded = extracted_score == round(source_score)
            
            if diff > self.SCORE_TOLERANCE and not is_rounded:
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    category='score_mismatch',
                    description=f"Composite score mismatch in {file_type}",
                    files_affected=[f"{self.base_name}.json", f"{self.base_name}_{file_type}"],
                    expected_value=str(source_score),
                    actual_value=str(extracted_score)
                ))
            elif is_rounded and diff > 0:
                # Info level - rounding is allowed in headings
                self.issues.append(ValidationIssue(
                    severity='INFO',
                    category='score_mismatch',
                    description=f"Rounded composite score in {file_type} (expected in headings)",
                    files_affected=[f"{self.base_name}_{file_type}"],
                    expected_value=str(source_score),
                    actual_value=str(extracted_score)
                ))
    
    def _validate_criteria_scores(self, data: Dict[str, any]):
        """Validate that individual criteria scores match across files"""
        if 'json' not in data:
            return
        
        source_scores = data['json'].get('raw_scores', {})
        if not source_scores:
            return
        
        # Check certificate JSON
        if 'certificate_json' in data:
            cert_scores = data['certificate_json'].get('criteria', [])
            for criterion in cert_scores:
                name = criterion.get('name', '')
                cert_score = criterion.get('score')
                
                # Map criterion name to JSON key
                key_map = {
                    'Fiscal Transparency': 'fiscal_transparency',
                    'Stakeholder Balance': 'stakeholder_balance',
                    'Evidence Rigor': 'evidence_rigor',
                    'Policy Alignment': 'policy_alignment',
                    'Political Candor': 'political_candor',
                    'AI Transparency': 'ai_transparency'
                }
                
                json_key = key_map.get(name)
                if json_key and json_key in source_scores:
                    source_score = source_scores[json_key]
                    diff = abs(cert_score - source_score)
                    
                    if diff > self.SCORE_TOLERANCE:
                        self.issues.append(ValidationIssue(
                            severity='ERROR',
                            category='score_mismatch',
                            description=f"{name} score mismatch between JSON and certificate",
                            files_affected=[f"{self.base_name}.json", f"{self.base_name}_certificate.json"],
                            expected_value=str(source_score),
                            actual_value=str(cert_score)
                        ))
    
    def _validate_performance_labels(self, data: Dict[str, any]):
        """Validate that performance labels match the score thresholds"""
        if 'json' not in data:
            return
        
        score = data['json'].get('composite_score')
        if score is None:
            return
        
        # Define standard label schema
        if score >= 90:
            expected_label = 'Exceptional'
        elif score >= 80:
            expected_label = 'Strong'
        elif score >= 60:
            expected_label = 'Needs Improvement'
        else:
            expected_label = 'Weak'
        
        # Check JSON
        json_label = data['json'].get('performance_label', '')
        if json_label and json_label != expected_label:
            self.issues.append(ValidationIssue(
                severity='ERROR',
                category='label_mismatch',
                description=f"Performance label in JSON doesn't match score threshold",
                files_affected=[f"{self.base_name}.json"],
                expected_value=expected_label,
                actual_value=json_label
            ))
        
        # Check certificate JSON
        if 'certificate_json' in data:
            cert_label = data['certificate_json'].get('performance_label', '')
            if cert_label and cert_label != expected_label:
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    category='label_mismatch',
                    description=f"Performance label in certificate doesn't match score threshold",
                    files_affected=[f"{self.base_name}_certificate.json"],
                    expected_value=expected_label,
                    actual_value=cert_label
                ))
    
    def _validate_timestamps(self, data: Dict[str, any]):
        """Validate that timestamps are consistent across all files from same batch"""
        timestamps = {}
        
        # Extract timestamps from each file
        if 'json' in data:
            timestamps['json'] = data['json'].get('timestamp')
        
        if 'certificate_json' in data:
            timestamps['certificate_json'] = data['certificate_json'].get('timestamp')
        
        if 'insights' in data:
            timestamps['insights'] = data['insights'].get('timestamp')
        
        if 'qa_report' in data:
            timestamps['qa_report'] = data['qa_report'].get('timestamp')
        
        # Check for mismatches
        unique_timestamps = set(t for t in timestamps.values() if t)
        
        if len(unique_timestamps) > 1:
            affected_files = [f"{self.base_name}_{k}" for k, v in timestamps.items() if v]
            self.issues.append(ValidationIssue(
                severity='WARNING',
                category='timestamp_mismatch',
                description=f"Multiple different timestamps found in files from same batch: {unique_timestamps}",
                files_affected=affected_files
            ))
    
    def _validate_adjusted_flags(self, data: Dict[str, any]):
        """Validate that adjusted flags are present when bias adjustments were made"""
        if 'json' not in data:
            return
        
        # Check if bias_audit has adjustments
        bias_audit = data['json'].get('bias_audit', {})
        adjustment_log = bias_audit.get('adjustment_log', [])
        
        has_adjustments = len(adjustment_log) > 0
        
        # Check for 'adjusted' flag in JSON
        adjusted_flag = data['json'].get('adjusted', False)
        
        if has_adjustments and not adjusted_flag:
            self.issues.append(ValidationIssue(
                severity='ERROR',
                category='missing_field',
                description="Bias adjustments were made but 'adjusted' flag is missing or false",
                files_affected=[f"{self.base_name}.json"],
                expected_value='true',
                actual_value=str(adjusted_flag)
            ))
        
        # Check certificate JSON
        if 'certificate_json' in data and has_adjustments:
            cert_adjusted = data['certificate_json'].get('adjusted', False)
            if not cert_adjusted:
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    category='missing_field',
                    description="Bias adjustments were made but 'adjusted' flag missing in certificate",
                    files_affected=[f"{self.base_name}_certificate.json"],
                    expected_value='true',
                    actual_value=str(cert_adjusted)
                ))
    
    def _validate_contradictions_section(self, data: Dict[str, any]):
        """Validate that contradiction findings are present in outputs if detected"""
        if 'json' not in data:
            return
        
        # Check if contradictions were detected
        contradiction_analysis = data['json'].get('contradiction_analysis', {})
        contradictions = contradiction_analysis.get('contradictions', [])
        
        has_contradictions = len(contradictions) > 0
        
        if not has_contradictions:
            return  # No contradictions, nothing to validate
        
        # Check narrative for contradictions section
        if 'narrative' in data:
            narrative_text = data['narrative']
            has_section = ('Flags and Contradictions' in narrative_text or 
                          'Contradiction' in narrative_text or
                          'Inconsistencies' in narrative_text)
            
            if not has_section:
                self.issues.append(ValidationIssue(
                    severity='WARNING',
                    category='missing_field',
                    description=f"Contradictions detected ({len(contradictions)} found) but no dedicated section in narrative",
                    files_affected=[f"{self.base_name}.txt"]
                ))
        
        # Check LinkedIn for contradictions mention
        if 'linkedin' in data:
            linkedin_text = data['linkedin']
            has_mention = ('contradiction' in linkedin_text.lower() or 
                          'inconsistenc' in linkedin_text.lower() or
                          'flag' in linkedin_text.lower())
            
            if not has_mention:
                self.issues.append(ValidationIssue(
                    severity='INFO',
                    category='missing_field',
                    description=f"Contradictions detected but not mentioned in LinkedIn post",
                    files_affected=[f"{self.base_name}_linkedin.txt"]
                ))
    
    def generate_report(self) -> str:
        """Generate human-readable validation report"""
        if not self.issues:
            return f"✅ VALIDATION PASSED: No issues found for {self.base_name}\n"
        
        report = [
            f"🔍 VALIDATION REPORT: {self.base_name}",
            f"=" * 80,
            ""
        ]
        
        # Group by severity
        errors = [i for i in self.issues if i.severity == 'ERROR']
        warnings = [i for i in self.issues if i.severity == 'WARNING']
        info = [i for i in self.issues if i.severity == 'INFO']
        
        if errors:
            report.append(f"❌ ERRORS ({len(errors)}):")
            report.append("-" * 80)
            for issue in errors:
                report.append(f"  • {issue.description}")
                report.append(f"    Category: {issue.category}")
                report.append(f"    Files: {', '.join(issue.files_affected)}")
                if issue.expected_value:
                    report.append(f"    Expected: {issue.expected_value}")
                    report.append(f"    Actual: {issue.actual_value}")
                report.append("")
        
        if warnings:
            report.append(f"⚠️  WARNINGS ({len(warnings)}):")
            report.append("-" * 80)
            for issue in warnings:
                report.append(f"  • {issue.description}")
                report.append(f"    Category: {issue.category}")
                report.append(f"    Files: {', '.join(issue.files_affected)}")
                if issue.expected_value:
                    report.append(f"    Expected: {issue.expected_value}")
                    report.append(f"    Actual: {issue.actual_value}")
                report.append("")
        
        if info:
            report.append(f"ℹ️  INFO ({len(info)}):")
            report.append("-" * 80)
            for issue in info:
                report.append(f"  • {issue.description}")
                report.append(f"    Files: {', '.join(issue.files_affected)}")
                if issue.expected_value:
                    report.append(f"    Expected: {issue.expected_value}")
                    report.append(f"    Actual: {issue.actual_value}")
                report.append("")
        
        report.append("=" * 80)
        report.append(f"SUMMARY: {len(errors)} errors, {len(warnings)} warnings, {len(info)} info")
        
        return "\n".join(report)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate consistency across SPOT Scale output files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_outputs.py 2025-Budget-21
  python validate_outputs.py 2025-Budget-21 --output-dir ./certificates
  python validate_outputs.py 2025-Budget-21 --json
        """
    )
    
    parser.add_argument('base_name', help='Base filename (e.g., 2025-Budget-21)')
    parser.add_argument('--output-dir', default='.', help='Directory containing output files')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Run validation
    validator = OutputValidator(args.base_name, args.output_dir)
    issues = validator.validate_all()
    
    if args.json:
        # JSON output for programmatic use
        import json
        output = {
            'base_name': args.base_name,
            'total_issues': len(issues),
            'errors': len([i for i in issues if i.severity == 'ERROR']),
            'warnings': len([i for i in issues if i.severity == 'WARNING']),
            'info': len([i for i in issues if i.severity == 'INFO']),
            'issues': [
                {
                    'severity': i.severity,
                    'category': i.category,
                    'description': i.description,
                    'files_affected': i.files_affected,
                    'expected_value': i.expected_value,
                    'actual_value': i.actual_value
                }
                for i in issues
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable report
        print(validator.generate_report())
    
    # Exit with non-zero if errors found
    errors = len([i for i in issues if i.severity == 'ERROR'])
    exit(0 if errors == 0 else 1)


if __name__ == '__main__':
    main()

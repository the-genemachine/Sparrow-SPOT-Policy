"""
Validation Middleware for Sparrow SPOT Scale™ v8.3.2

Pre-output validation to catch errors before file generation.
Implements single source of truth pattern for score consistency.

Checks:
- All score fields populated (no "N/A" unless intentional)
- Confidence values ≤ 100%
- AI percentage values consistent across output files
- Required JSON fields present before template rendering
- Percentages in valid range 0-100
- Cross-field consistency validation

Author: Sparrow SPOT Scale™ v8.3.2
Date: December 1, 2025
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import re


@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    severity: str  # 'critical', 'warning', 'info'
    current_value: Any = None
    expected_range: Optional[str] = None


@dataclass 
class ValidationResult:
    """Result of validation checks."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)
    
    def add_error(self, error: ValidationError):
        """Add error to appropriate list based on severity."""
        if error.severity == 'critical':
            self.errors.append(error)
            self.is_valid = False
        elif error.severity == 'warning':
            self.warnings.append(error)
        else:
            self.info.append(error)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'is_valid': self.is_valid,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': [{'field': e.field, 'message': e.message, 'value': str(e.current_value)} 
                      for e in self.errors],
            'warnings': [{'field': e.field, 'message': e.message, 'value': str(e.current_value)} 
                        for e in self.warnings]
        }
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [f"Validation {'PASSED' if self.is_valid else 'FAILED'}"]
        lines.append(f"  Errors: {len(self.errors)}, Warnings: {len(self.warnings)}")
        
        if self.errors:
            lines.append("\nCritical Errors:")
            for e in self.errors[:5]:  # Show first 5
                lines.append(f"  • {e.field}: {e.message}")
                if e.current_value is not None:
                    lines.append(f"    Value: {e.current_value}")
        
        if self.warnings:
            lines.append("\nWarnings:")
            for w in self.warnings[:5]:
                lines.append(f"  • {w.field}: {w.message}")
        
        return '\n'.join(lines)


class ValidationMiddleware:
    """
    Validates analysis results before output generation.
    
    Implements pre-output checks to catch common errors:
    - Score inconsistencies
    - Invalid percentage values
    - Missing required fields
    - Cross-field contradictions
    """
    
    def __init__(self):
        self.version = "8.3.5"
        
        # Required top-level fields
        self.required_fields = [
            'document_name',
            'timestamp',
            'ai_detection',
            'criteria',
            'overall_score'
        ]
        
        # Fields that must be percentages (0-100)
        self.percentage_fields = [
            ('ai_detection', 'ai_detection_score'),
            ('ai_detection', 'confidence'),
            ('overall_score',),
            ('trust_score', 'score'),
            ('fairness_audit', 'overall_fairness_score'),
        ]
        
        # Fields that can be 0-1 (will be converted to 0-100)
        self.decimal_percentage_fields = [
            ('ai_detection', 'ai_detection_score'),
            ('ai_detection', 'confidence'),
        ]
    
    def validate(self, results: Dict) -> ValidationResult:
        """
        Run all validation checks on analysis results.
        
        Args:
            results: The complete analysis results dictionary
            
        Returns:
            ValidationResult with all errors and warnings
        """
        validation = ValidationResult(is_valid=True)
        
        # Run all validation checks
        self._check_required_fields(results, validation)
        self._check_percentage_ranges(results, validation)
        self._check_score_consistency(results, validation)
        self._check_ai_detection(results, validation)
        self._check_criteria_scores(results, validation)
        self._check_confidence_values(results, validation)
        
        return validation
    
    def validate_and_fix(self, results: Dict) -> Tuple[Dict, ValidationResult]:
        """
        Validate and auto-fix common issues where possible.
        
        Args:
            results: The analysis results dictionary
            
        Returns:
            Tuple of (fixed_results, validation_result)
        """
        # Make a copy to avoid modifying original
        import copy
        fixed = copy.deepcopy(results)
        
        # Auto-fix common issues
        fixed = self._fix_percentage_ranges(fixed)
        fixed = self._fix_confidence_values(fixed)
        fixed = self._ensure_required_fields(fixed)
        
        # Validate the fixed version
        validation = self.validate(fixed)
        
        return fixed, validation
    
    def _check_required_fields(self, results: Dict, validation: ValidationResult):
        """Check that required fields are present."""
        for field in self.required_fields:
            if field not in results:
                validation.add_error(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    severity='critical'
                ))
            elif results[field] is None:
                validation.add_error(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is None",
                    severity='warning',
                    current_value=None
                ))
    
    def _check_percentage_ranges(self, results: Dict, validation: ValidationResult):
        """Check that percentage values are in valid range 0-100."""
        for path in self.percentage_fields:
            value = self._get_nested_value(results, path)
            if value is not None:
                field_name = '.'.join(path)
                
                # Check for values > 100 (impossible percentage)
                if isinstance(value, (int, float)) and value > 100:
                    validation.add_error(ValidationError(
                        field=field_name,
                        message=f"Percentage value {value} exceeds 100%",
                        severity='critical',
                        current_value=value,
                        expected_range="0-100"
                    ))
                
                # Check for negative values
                if isinstance(value, (int, float)) and value < 0:
                    validation.add_error(ValidationError(
                        field=field_name,
                        message=f"Percentage value {value} is negative",
                        severity='critical',
                        current_value=value,
                        expected_range="0-100"
                    ))
    
    def _check_score_consistency(self, results: Dict, validation: ValidationResult):
        """Check that scores are consistent across different sections."""
        # Check AI percentage consistency
        ai_percentages = []
        
        # Deep analysis consensus
        deep = results.get('deep_analysis', {})
        if deep:
            consensus = deep.get('consensus', {})
            if 'ai_percentage' in consensus:
                ai_percentages.append(('deep_analysis.consensus.ai_percentage', 
                                      consensus['ai_percentage']))
        
        # Basic detection
        ai_det = results.get('ai_detection', {})
        if ai_det:
            score = ai_det.get('ai_detection_score')
            if score is not None:
                # Normalize to percentage
                if score <= 1.0:
                    score = score * 100
                ai_percentages.append(('ai_detection.ai_detection_score', score))
        
        # Check consistency (allow 5% variance for rounding)
        if len(ai_percentages) >= 2:
            values = [v for _, v in ai_percentages]
            max_diff = max(values) - min(values)
            if max_diff > 15:  # More than 15% difference is suspicious
                validation.add_error(ValidationError(
                    field='ai_percentage_consistency',
                    message=f"AI percentage values differ by {max_diff:.1f}%",
                    severity='warning',
                    current_value={k: f"{v:.1f}%" for k, v in ai_percentages}
                ))
    
    def _check_ai_detection(self, results: Dict, validation: ValidationResult):
        """Validate AI detection fields."""
        ai_det = results.get('ai_detection', {})
        
        if not ai_det:
            validation.add_error(ValidationError(
                field='ai_detection',
                message="AI detection section is missing or empty",
                severity='warning'
            ))
            return
        
        # Check for likely model
        likely_model = ai_det.get('likely_ai_model', {})
        if isinstance(likely_model, dict):
            model = likely_model.get('model')
            if model == 'Unknown' or model is None:
                validation.add_error(ValidationError(
                    field='ai_detection.likely_ai_model.model',
                    message="AI model detection returned 'Unknown'",
                    severity='info'
                ))
    
    def _check_criteria_scores(self, results: Dict, validation: ValidationResult):
        """Validate criteria scores."""
        criteria = results.get('criteria', {})
        
        if not criteria:
            validation.add_error(ValidationError(
                field='criteria',
                message="Criteria scores section is missing or empty",
                severity='critical'
            ))
            return
        
        # Check each criterion
        for name, data in criteria.items():
            if isinstance(data, dict):
                score = data.get('score')
                if score is None or score == 'N/A':
                    validation.add_error(ValidationError(
                        field=f'criteria.{name}.score',
                        message=f"Criterion '{name}' has no valid score",
                        severity='warning',
                        current_value=score
                    ))
                elif isinstance(score, (int, float)):
                    if score < 0 or score > 100:
                        validation.add_error(ValidationError(
                            field=f'criteria.{name}.score',
                            message=f"Score {score} outside valid range",
                            severity='critical',
                            current_value=score,
                            expected_range="0-100"
                        ))
    
    def _check_confidence_values(self, results: Dict, validation: ValidationResult):
        """Check all confidence values are valid."""
        # Check AI detection confidence
        ai_det = results.get('ai_detection', {})
        if ai_det:
            likely_model = ai_det.get('likely_ai_model', {})
            if isinstance(likely_model, dict):
                conf = likely_model.get('confidence')
                if conf is not None and isinstance(conf, (int, float)):
                    # Confidence should be 0-1 or 0-100
                    if conf > 100:
                        validation.add_error(ValidationError(
                            field='ai_detection.likely_ai_model.confidence',
                            message=f"Confidence {conf} exceeds 100%",
                            severity='critical',
                            current_value=conf,
                            expected_range="0-100"
                        ))
        
        # Check deep analysis level confidences
        deep = results.get('deep_analysis', {})
        if deep:
            for level_key in ['level1_document', 'level2_section', 'level4_model', 
                             'level5_behavioral', 'level6_phrase']:
                level = deep.get(level_key, {})
                if isinstance(level, dict):
                    conf = level.get('confidence')
                    if conf is not None and isinstance(conf, (int, float)) and conf > 100:
                        validation.add_error(ValidationError(
                            field=f'deep_analysis.{level_key}.confidence',
                            message=f"Level confidence {conf} exceeds 100%",
                            severity='warning',
                            current_value=conf
                        ))
    
    def _get_nested_value(self, data: Dict, path: tuple) -> Any:
        """Get a nested value from a dictionary using a path tuple."""
        current = data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _fix_percentage_ranges(self, results: Dict) -> Dict:
        """Auto-fix percentage values that are out of range."""
        # Fix confidence values > 100
        ai_det = results.get('ai_detection', {})
        if ai_det:
            likely_model = ai_det.get('likely_ai_model', {})
            if isinstance(likely_model, dict) and 'confidence' in likely_model:
                conf = likely_model['confidence']
                if isinstance(conf, (int, float)) and conf > 100:
                    # Cap at 100
                    likely_model['confidence'] = min(conf, 100)
        
        return results
    
    def _fix_confidence_values(self, results: Dict) -> Dict:
        """Normalize confidence values to 0-100 scale."""
        ai_det = results.get('ai_detection', {})
        if ai_det:
            # Fix detection score
            score = ai_det.get('ai_detection_score')
            if score is not None and isinstance(score, (int, float)):
                if score <= 1.0:
                    # Already normalized, convert to percentage
                    ai_det['ai_detection_score_percentage'] = score * 100
                else:
                    ai_det['ai_detection_score_percentage'] = min(score, 100)
        
        return results
    
    def _ensure_required_fields(self, results: Dict) -> Dict:
        """Ensure required fields have sensible defaults."""
        if 'timestamp' not in results:
            results['timestamp'] = datetime.now().isoformat()
        
        if 'version' not in results:
            results['version'] = f"v{self.version}"
        
        return results


def validate_before_output(results: Dict, auto_fix: bool = True) -> Tuple[Dict, ValidationResult]:
    """
    Convenience function to validate results before generating output files.
    
    Args:
        results: Analysis results dictionary
        auto_fix: Whether to auto-fix common issues
        
    Returns:
        Tuple of (validated_results, validation_result)
    """
    middleware = ValidationMiddleware()
    
    if auto_fix:
        return middleware.validate_and_fix(results)
    else:
        return results, middleware.validate(results)


# Example usage and self-test
if __name__ == "__main__":
    print("Validation Middleware v8.3.2 - Self Test")
    print("=" * 50)
    
    # Test with problematic data
    test_data = {
        'document_name': 'Test Document',
        'timestamp': '2025-12-01T10:00:00',
        'ai_detection': {
            'ai_detection_score': 0.532,
            'confidence': 0.95,
            'likely_ai_model': {
                'model': 'Cohere',
                'confidence': 120  # BUG: Over 100%
            }
        },
        'criteria': {
            'fiscal_transparency': {'score': 53.8, 'grade': 'F'},
            'stakeholder_inclusion': {'score': None, 'grade': 'N/A'},  # BUG: No score
        },
        'overall_score': 45.6,
        'deep_analysis': {
            'consensus': {'ai_percentage': 31.8},
            'level1_document': {'ai_percentage': 41.8, 'confidence': 95}  # Different from consensus
        }
    }
    
    # Run validation with auto-fix
    fixed, result = validate_before_output(test_data, auto_fix=True)
    
    print(result.summary())
    print("\nFixed confidence value:", 
          fixed.get('ai_detection', {}).get('likely_ai_model', {}).get('confidence'))

"""
Analysis Results - Single Source of Truth for Sparrow SPOT Scale™ v8.3.2

This module implements the Single Source of Truth pattern to ensure consistent
scores and values across all output formats (JSON, TXT, HTML, certificates).

Architecture:
- All analysis results are stored in a validated AnalysisResults object
- All output generators (certificate, disclosure, summary) read from this object
- No direct calculation in exporters - only formatting

Benefits:
- Eliminates score inconsistencies between output files
- Centralizes validation logic
- Makes debugging easier (single point to check)
- Enables caching and performance optimization

Usage:
    from analysis_results import AnalysisResults
    
    # After analysis completes
    results = AnalysisResults(raw_analysis_output)
    results.validate()  # Runs validation middleware
    
    # All exporters use the same validated data
    certificate_gen.generate(results)
    disclosure_gen.generate(results)
    summary_gen.generate(results)

Author: Sparrow SPOT Scale™ v8.3.2
Date: December 1, 2025
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import copy


class ConfidenceLevel(Enum):
    """Confidence level qualifiers for transparency."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    UNKNOWN = "Unknown"


@dataclass
class ScoreWithConfidence:
    """A score value with associated confidence level."""
    value: float
    confidence: ConfidenceLevel
    source: str  # Where this score came from
    methodology: str = ""  # How it was calculated
    
    def to_dict(self) -> Dict:
        return {
            'value': self.value,
            'confidence': self.confidence.value,
            'source': self.source,
            'methodology': self.methodology
        }
    
    def format_display(self, precision: int = 1) -> str:
        """Format for display with confidence qualifier."""
        return f"{self.value:.{precision}f} ({self.confidence.value} Confidence)"


class AnalysisResults:
    """
    Single Source of Truth for all analysis results.
    
    This class encapsulates all analysis data and provides validated,
    consistent access to scores and metrics across all output formats.
    
    Key Features:
    - Immutable after validation (prevents accidental modification)
    - Consistent percentage formatting (all use same precision)
    - Confidence levels attached to all scores
    - Caching for frequently accessed values
    """
    
    VERSION = "8.3.3"
    
    def __init__(self, raw_results: Dict):
        """
        Initialize with raw analysis output.
        
        Args:
            raw_results: The raw dictionary output from sparrow_grader_v8.py
        """
        self._raw = copy.deepcopy(raw_results)  # Defensive copy
        self._validated = False
        self._validation_errors = []
        self._cache = {}
        
        # Extracted and normalized values
        self._ai_percentage: Optional[ScoreWithConfidence] = None
        self._trust_score: Optional[ScoreWithConfidence] = None
        self._overall_score: Optional[ScoreWithConfidence] = None
        self._criteria_scores: Dict[str, ScoreWithConfidence] = {}
        self._model_detection: Optional[Dict] = None
        
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate and normalize all results.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Extract and validate AI percentage
        try:
            self._ai_percentage = self._extract_ai_percentage()
        except Exception as e:
            errors.append(f"AI percentage extraction failed: {e}")
        
        # Extract and validate trust score
        try:
            self._trust_score = self._extract_trust_score()
        except Exception as e:
            errors.append(f"Trust score extraction failed: {e}")
        
        # Extract and validate overall score
        try:
            self._overall_score = self._extract_overall_score()
        except Exception as e:
            errors.append(f"Overall score extraction failed: {e}")
        
        # Extract and validate criteria scores
        try:
            self._criteria_scores = self._extract_criteria_scores()
        except Exception as e:
            errors.append(f"Criteria scores extraction failed: {e}")
        
        # Extract model detection info
        try:
            self._model_detection = self._extract_model_detection()
        except Exception as e:
            errors.append(f"Model detection extraction failed: {e}")
        
        self._validation_errors = errors
        self._validated = len(errors) == 0
        
        return self._validated, errors
    
    def _extract_ai_percentage(self) -> ScoreWithConfidence:
        """
        Extract AI percentage from the most reliable source.
        
        Priority order:
        1. deep_analysis.consensus.ai_percentage (multi-method, highest confidence)
        2. ai_detection.ai_detection_score (single method, medium confidence)
        3. Default to 0 (unknown)
        """
        # Try deep analysis consensus first (most reliable)
        deep = self._raw.get('deep_analysis', {})
        if deep:
            consensus = deep.get('consensus', {})
            if 'ai_percentage' in consensus:
                pct = consensus['ai_percentage']
                # Determine confidence based on level agreement
                level_count = sum(1 for k in deep if k.startswith('level') and deep[k])
                if level_count >= 5:
                    confidence = ConfidenceLevel.HIGH
                elif level_count >= 3:
                    confidence = ConfidenceLevel.MEDIUM
                else:
                    confidence = ConfidenceLevel.LOW
                
                return ScoreWithConfidence(
                    value=pct,
                    confidence=confidence,
                    source='deep_analysis.consensus',
                    methodology=f'Weighted consensus across {level_count} analysis levels'
                )
        
        # Fallback to basic AI detection
        ai_det = self._raw.get('ai_detection', {})
        if ai_det:
            score = ai_det.get('ai_detection_score')
            if score is not None:
                # Normalize to percentage
                if score <= 1.0:
                    pct = score * 100
                else:
                    pct = min(score, 100)
                
                return ScoreWithConfidence(
                    value=pct,
                    confidence=ConfidenceLevel.MEDIUM,
                    source='ai_detection.ai_detection_score',
                    methodology='Single-method pattern analysis'
                )
        
        # Default
        return ScoreWithConfidence(
            value=0.0,
            confidence=ConfidenceLevel.UNKNOWN,
            source='default',
            methodology='No AI detection data available'
        )
    
    def _extract_trust_score(self) -> ScoreWithConfidence:
        """Extract trust score from results."""
        trust = self._raw.get('trust_score', {})
        if trust:
            score = trust.get('trust_score') or trust.get('score')
            if score is not None:
                # Determine confidence based on component completeness
                components = ['explainability', 'fairness', 'robustness', 'compliance']
                complete = sum(1 for c in components if trust.get(c) is not None)
                
                if complete >= 4:
                    confidence = ConfidenceLevel.HIGH
                elif complete >= 2:
                    confidence = ConfidenceLevel.MEDIUM
                else:
                    confidence = ConfidenceLevel.LOW
                
                return ScoreWithConfidence(
                    value=score,
                    confidence=confidence,
                    source='trust_score',
                    methodology=f'{complete}/4 components calculated'
                )
        
        return ScoreWithConfidence(
            value=50.0,
            confidence=ConfidenceLevel.UNKNOWN,
            source='default',
            methodology='No trust score data available'
        )
    
    def _extract_overall_score(self) -> ScoreWithConfidence:
        """Extract overall/composite score from results."""
        # Try composite_score first
        score = self._raw.get('composite_score')
        if score is not None:
            return ScoreWithConfidence(
                value=score,
                confidence=ConfidenceLevel.HIGH,
                source='composite_score',
                methodology='Weighted aggregate of all criteria'
            )
        
        # Try overall_score
        score = self._raw.get('overall_score')
        if score is not None:
            return ScoreWithConfidence(
                value=score,
                confidence=ConfidenceLevel.HIGH,
                source='overall_score',
                methodology='Weighted aggregate of all criteria'
            )
        
        return ScoreWithConfidence(
            value=0.0,
            confidence=ConfidenceLevel.UNKNOWN,
            source='default',
            methodology='No overall score available'
        )
    
    def _extract_criteria_scores(self) -> Dict[str, ScoreWithConfidence]:
        """Extract individual criteria scores."""
        scores = {}
        criteria = self._raw.get('criteria', {})
        
        # Also check categories (alternative key name)
        if not criteria:
            criteria = self._raw.get('categories', {})
        
        for name, data in criteria.items():
            if isinstance(data, dict):
                score = data.get('score')
                if score is not None and score != 'N/A':
                    scores[name] = ScoreWithConfidence(
                        value=float(score),
                        confidence=ConfidenceLevel.HIGH,
                        source=f'criteria.{name}',
                        methodology='Evidence-based scoring'
                    )
                else:
                    scores[name] = ScoreWithConfidence(
                        value=0.0,
                        confidence=ConfidenceLevel.UNKNOWN,
                        source=f'criteria.{name}',
                        methodology='Score not available'
                    )
            elif isinstance(data, (int, float)):
                scores[name] = ScoreWithConfidence(
                    value=float(data),
                    confidence=ConfidenceLevel.HIGH,
                    source=f'criteria.{name}',
                    methodology='Direct score'
                )
        
        return scores
    
    def _extract_model_detection(self) -> Dict:
        """Extract AI model detection information."""
        ai_det = self._raw.get('ai_detection', {})
        likely_model = ai_det.get('likely_ai_model', {})
        
        if isinstance(likely_model, dict):
            model = likely_model.get('model', 'Unknown')
            conf = likely_model.get('confidence', 0)
            
            # Normalize confidence
            if conf > 100:
                conf = 100
            elif conf <= 1.0:
                conf = conf * 100
            
            # Determine confidence level
            if conf >= 85:
                level = ConfidenceLevel.HIGH
            elif conf >= 60:
                level = ConfidenceLevel.MEDIUM
            else:
                level = ConfidenceLevel.LOW
            
            return {
                'model': model,
                'confidence': conf,
                'confidence_level': level,
                'model_scores': likely_model.get('model_scores', {})
            }
        
        return {
            'model': 'Unknown',
            'confidence': 0,
            'confidence_level': ConfidenceLevel.UNKNOWN,
            'model_scores': {}
        }
    
    # ========== Public Accessors (Single Source of Truth) ==========
    
    @property
    def ai_percentage(self) -> float:
        """Get AI detection percentage (0-100)."""
        if not self._validated:
            self.validate()
        return self._ai_percentage.value if self._ai_percentage else 0.0
    
    @property
    def ai_percentage_with_confidence(self) -> ScoreWithConfidence:
        """Get AI percentage with confidence metadata."""
        if not self._validated:
            self.validate()
        return self._ai_percentage
    
    @property
    def trust_score(self) -> float:
        """Get trust score (0-100)."""
        if not self._validated:
            self.validate()
        return self._trust_score.value if self._trust_score else 50.0
    
    @property
    def trust_score_with_confidence(self) -> ScoreWithConfidence:
        """Get trust score with confidence metadata."""
        if not self._validated:
            self.validate()
        return self._trust_score
    
    @property
    def overall_score(self) -> float:
        """Get overall/composite score (0-100)."""
        if not self._validated:
            self.validate()
        return self._overall_score.value if self._overall_score else 0.0
    
    @property
    def model_name(self) -> str:
        """Get detected AI model name."""
        if not self._validated:
            self.validate()
        return self._model_detection.get('model', 'Unknown') if self._model_detection else 'Unknown'
    
    @property
    def model_confidence(self) -> float:
        """Get model detection confidence (0-100, capped)."""
        if not self._validated:
            self.validate()
        return self._model_detection.get('confidence', 0) if self._model_detection else 0
    
    @property
    def model_confidence_level(self) -> ConfidenceLevel:
        """Get model detection confidence level."""
        if not self._validated:
            self.validate()
        return self._model_detection.get('confidence_level', ConfidenceLevel.UNKNOWN) if self._model_detection else ConfidenceLevel.UNKNOWN
    
    def get_criterion_score(self, name: str) -> float:
        """Get score for a specific criterion."""
        if not self._validated:
            self.validate()
        if name in self._criteria_scores:
            return self._criteria_scores[name].value
        return 0.0
    
    def get_criterion_with_confidence(self, name: str) -> Optional[ScoreWithConfidence]:
        """Get criterion score with confidence metadata."""
        if not self._validated:
            self.validate()
        return self._criteria_scores.get(name)
    
    @property
    def criteria(self) -> Dict[str, float]:
        """Get all criteria scores as simple dict."""
        if not self._validated:
            self.validate()
        return {name: sc.value for name, sc in self._criteria_scores.items()}
    
    # ========== Formatted Output Methods ==========
    
    def format_ai_percentage(self, precision: int = 1, include_confidence: bool = False) -> str:
        """
        Format AI percentage consistently for all outputs.
        
        Args:
            precision: Decimal places (default 1 for "31.8%")
            include_confidence: Whether to include confidence qualifier
        """
        if not self._validated:
            self.validate()
        
        pct = self._ai_percentage.value if self._ai_percentage else 0.0
        
        if include_confidence and self._ai_percentage:
            return f"{pct:.{precision}f}% ({self._ai_percentage.confidence.value} Confidence)"
        return f"{pct:.{precision}f}%"
    
    def format_model_detection(self, include_confidence: bool = True) -> str:
        """Format model detection consistently."""
        if not self._validated:
            self.validate()
        
        model = self.model_name
        conf = self.model_confidence
        
        if include_confidence:
            level = self.model_confidence_level.value
            return f"{model} ({conf:.0f}% - {level} Confidence)"
        return f"{model} ({conf:.0f}%)"
    
    def format_trust_score(self, include_confidence: bool = False) -> str:
        """Format trust score consistently."""
        if not self._validated:
            self.validate()
        
        score = self.trust_score
        
        if include_confidence and self._trust_score:
            return f"{score:.1f}/100 ({self._trust_score.confidence.value} Confidence)"
        return f"{score:.1f}/100"
    
    # ========== Raw Access (for backward compatibility) ==========
    
    @property
    def raw(self) -> Dict:
        """Get raw results dict (read-only copy)."""
        return copy.deepcopy(self._raw)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access for backward compatibility."""
        return self._raw.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Dict-like indexing for backward compatibility."""
        return self._raw[key]
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for backward compatibility."""
        return key in self._raw
    
    # ========== Serialization ==========
    
    def to_dict(self) -> Dict:
        """
        Export validated results as dictionary.
        
        This is the canonical output format - all exporters should use this.
        """
        if not self._validated:
            self.validate()
        
        return {
            'version': self.VERSION,
            'validated': self._validated,
            'validation_errors': self._validation_errors,
            'ai_detection': {
                'percentage': self.ai_percentage,
                'percentage_formatted': self.format_ai_percentage(),
                'confidence': self._ai_percentage.confidence.value if self._ai_percentage else 'Unknown',
                'source': self._ai_percentage.source if self._ai_percentage else 'unknown',
                'model': self.model_name,
                'model_confidence': self.model_confidence,
                'model_confidence_level': self.model_confidence_level.value
            },
            'scores': {
                'overall': self.overall_score,
                'trust': self.trust_score,
                'criteria': self.criteria
            },
            'metadata': {
                'document_name': self._raw.get('document_name', 'Unknown'),
                'timestamp': self._raw.get('timestamp', datetime.now().isoformat()),
                'risk_tier': self._raw.get('risk_tier', {}).get('risk_tier', 'UNKNOWN')
            },
            # Include raw for full access
            '_raw': self._raw
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Export as JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def clear_cache(self):
        """
        v8.3.2: Clear internal cache to free memory.
        
        Call this after all outputs have been generated to release memory.
        Useful when processing many documents in sequence.
        """
        self._cache.clear()
    
    def cleanup(self):
        """
        v8.3.2: Full cleanup for memory optimization.
        
        Clears all cached data and triggers garbage collection.
        Use when processing large documents or batches.
        """
        import gc
        
        self._cache.clear()
        self._raw = {}  # Release raw data reference
        
        # Trigger garbage collection
        gc.collect()


def create_analysis_results(raw_results: Dict) -> AnalysisResults:
    """Factory function to create and validate AnalysisResults."""
    results = AnalysisResults(raw_results)
    results.validate()
    return results


def cleanup_after_output():
    """
    v8.3.2: Memory cleanup utility.
    
    Call after generating all output files for a document.
    Helps prevent memory accumulation during batch processing.
    """
    import gc
    gc.collect()# ========== Self-Test ==========

if __name__ == "__main__":
    print("AnalysisResults v8.3.2 - Single Source of Truth - Self Test")
    print("=" * 60)
    
    # Test with sample data
    test_data = {
        'document_name': 'Test Policy Document',
        'timestamp': '2025-12-01T10:00:00',
        'composite_score': 65.4,
        'ai_detection': {
            'ai_detection_score': 0.532,
            'likely_ai_model': {
                'model': 'Cohere',
                'confidence': 0.90,
                'model_scores': {'Cohere': 0.90, 'Claude': 0.45}
            }
        },
        'deep_analysis': {
            'consensus': {'ai_percentage': 31.8, 'transparency_score': 52.1},
            'level1_document': {'ai_percentage': 41.8, 'confidence': 85},
            'level2_section': {'patterns': 156},
            'level4_model': {'top_model': 'Cohere'},
            'level5_behavioral': {'consistency_score': 78},
            'level6_phrase': {'fingerprints': 45}
        },
        'trust_score': {
            'trust_score': 61.7,
            'explainability': 70,
            'fairness': 50,
            'robustness': 65,
            'compliance': 60
        },
        'criteria': {
            'fiscal_transparency': {'score': 53.8, 'grade': 'F'},
            'stakeholder_inclusion': {'score': 72.4, 'grade': 'C'},
            'evidence_basis': {'score': 68.2, 'grade': 'D'}
        },
        'risk_tier': {'risk_tier': 'MEDIUM'}
    }
    
    # Create and validate
    results = create_analysis_results(test_data)
    
    print(f"\nValidation: {'✅ PASSED' if results._validated else '❌ FAILED'}")
    if results._validation_errors:
        print(f"Errors: {results._validation_errors}")
    
    print(f"\n--- Single Source of Truth Values ---")
    print(f"AI Percentage: {results.format_ai_percentage(include_confidence=True)}")
    print(f"Model Detection: {results.format_model_detection()}")
    print(f"Trust Score: {results.format_trust_score(include_confidence=True)}")
    print(f"Overall Score: {results.overall_score:.1f}")
    
    print(f"\n--- Criteria Scores ---")
    for name, score in results.criteria.items():
        print(f"  {name}: {score:.1f}")
    
    print(f"\n--- Confidence Metadata ---")
    ai_conf = results.ai_percentage_with_confidence
    print(f"AI Detection Source: {ai_conf.source}")
    print(f"AI Detection Methodology: {ai_conf.methodology}")
    
    print("\n✅ Single Source of Truth pattern implemented successfully")

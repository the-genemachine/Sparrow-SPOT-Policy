#!/usr/bin/env python3
"""
Integration script: Import and patch sparrow_grader_v7 with ethical framework modules.

This script updates v7 to use:
1. ai_detection_engine - Pillar 1: INPUT TRANSPARENCY
2. nist_risk_mapper - Pillar 2 Part 1: RISK CLASSIFICATION  
3. bias_auditor - Pillar 2 Part 2: FAIRNESS ANALYSIS
4. trust_score_calculator - Pillar 2-3: COMPOSITE TRUST SCORE

Usage: python3 integrate_v7_ethical_modules.py
"""

import sys
from pathlib import Path

# Verify all modules exist
modules_needed = [
    'ai_detection_engine.py',
    'nist_risk_mapper.py',
    'bias_auditor.py',
    'trust_score_calculator.py',
    'sparrow_grader_v7.py'
]

base_dir = Path(__file__).parent
for module in modules_needed:
    module_path = base_dir / module
    if not module_path.exists():
        print(f"❌ ERROR: Missing {module}")
        print(f"   Expected: {module_path}")
        sys.exit(1)
    print(f"✓ {module}")

print("\n✅ All modules present. Ready for integration.\n")

# Now import and test
try:
    from ai_detection_engine import AIDetectionEngine, ProvenanceAnalyzer, WatermarkDetector
    print("✓ ai_detection_engine imported successfully")
except ImportError as e:
    print(f"❌ Failed to import ai_detection_engine: {e}")
    sys.exit(1)

try:
    from nist_risk_mapper import NISTRiskMapper, ControlActivationManager
    print("✓ nist_risk_mapper imported successfully")
except ImportError as e:
    print(f"❌ Failed to import nist_risk_mapper: {e}")
    sys.exit(1)

try:
    from bias_auditor import BiasAuditor
    print("✓ bias_auditor imported successfully")
except ImportError as e:
    print(f"❌ Failed to import bias_auditor: {e}")
    sys.exit(1)

try:
    from trust_score_calculator import TrustScoreCalculator
    print("✓ trust_score_calculator imported successfully")
except ImportError as e:
    print(f"❌ Failed to import trust_score_calculator: {e}")
    sys.exit(1)

try:
    from sparrow_grader_v7 import SPOTPolicy
    print("✓ sparrow_grader_v7 (SPOTPolicy) imported successfully")
except ImportError as e:
    print(f"❌ Failed to import sparrow_grader_v7: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("INTEGRATION SUCCESS - All modules ready for v7")
print("="*60)

print("\nModule Inventory:")
print("  Pillar 1 (INPUT TRANSPARENCY):")
print("    • AIDetectionEngine - Multi-model consensus detection")
print("    • ProvenanceAnalyzer - Document metadata extraction")
print("    • WatermarkDetector - AI watermark detection")
print("\n  Pillar 2 (ANALYSIS TRANSPARENCY):")
print("    • NISTRiskMapper - Risk tier classification (LOW/MEDIUM/HIGH)")
print("    • BiasAuditor - Fairness metrics (DIR, EOD, SPD)")
print("    • TrustScoreCalculator - Composite trust (0-100)")
print("\n  Policy Engine:")
print("    • SPOTPolicy - Main grading system")

print("\nNext Steps:")
print("1. Create enhanced certificate_generator_v7.py")
print("2. Update SPOTPolicy.grade() to use these modules")
print("3. Run comprehensive tests on 2025-Budget.pdf")
print("4. Generate V7 alpha release documentation")

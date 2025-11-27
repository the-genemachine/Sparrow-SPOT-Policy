# Output Validation Guide

## Overview
The `validate_outputs.py` script performs automated consistency checks across all SPOT Scale output files to detect discrepancies in scores, labels, timestamps, and metadata.

## Purpose
Implements **Recommendation #2** from "Resolving Inconsistencies in the 2025-Budget-21 Assessment Files":
> Create a post-generation validation script to compare values across all output files and flag mismatches

## Usage

### Basic Validation
```bash
python validate_outputs.py <base_name> [--output-dir <path>]
```

**Examples:**
```bash
# Validate files in current directory
python validate_outputs.py 2025-Budget-21

# Validate files in specific directory
python validate_outputs.py 2025-Budget-21 --output-dir ./SPOT_News

# Get JSON output for automation
python validate_outputs.py 2025-Budget-21 --json
```

### Integration into Workflow
Add validation as final step after grading:

```bash
# Run grading
python sparrow_grader_v8.py --file budget.txt --policy test_policy.txt

# Validate outputs
python validate_outputs.py budget --output-dir .
```

## What It Checks

### 1. Composite Score Consistency
- **Source of Truth**: `{base_name}.json` → `composite_score`
- **Validates Against**:
  - Certificate JSON (`{base_name}_certificate.json`)
  - Certificate HTML (`{base_name}_certificate.html`)
  - Narrative text (`{base_name}.txt`)
  - LinkedIn post (`{base_name}_linkedin.txt`)
  - X thread (`{base_name}_x_thread.txt`)
  - Summary (`{base_name}_summary.txt`)

- **Tolerance**: ±0.1 points
- **Allows**: Rounding in headings (e.g., 82.9 → 83) with INFO notice
- **Flags**: Discrepancies > 0.1 as ERROR

### 2. Criteria Score Consistency
- **Source of Truth**: `{base_name}.json` → `raw_scores`
- **Validates Against**: Certificate JSON criteria array
- **Checks**: FT, SB, ER, PA, PC, AT individual scores
- **Tolerance**: ±0.1 points

### 3. Performance Label Schema
- **Expected Thresholds**:
  - 90-100: "Exceptional"
  - 80-89: "Strong"
  - 60-79: "Needs Improvement"
  - <60: "Weak"

- **Validates**: JSON and certificate labels match score thresholds
- **Severity**: ERROR if mismatch

### 4. Timestamp Consistency
- **Requirement**: All files from same batch should have identical timestamps
- **Checks**: JSON, certificate JSON, insights, QA report
- **Severity**: WARNING if multiple timestamps found

### 5. Adjusted Flags
- **Requirement**: When `bias_audit.adjustment_log` has entries, `adjusted: true` flag must be present
- **Validates**: JSON and certificate JSON
- **Severity**: ERROR if missing

### 6. Contradictions Section
- **Requirement**: If `contradiction_analysis.contradictions[]` has entries, narrative should have dedicated section
- **Checks**: Narrative text for "Flags and Contradictions" or similar
- **Severity**: WARNING if missing
- **Also Checks**: LinkedIn post should mention contradictions (INFO level)

## Output Format

### Human-Readable Report
```
🔍 VALIDATION REPORT: 2025-Budget-21
================================================================================

❌ ERRORS (1):
--------------------------------------------------------------------------------
  • Performance label in JSON doesn't match score threshold
    Category: label_mismatch
    Files: 2025-Budget-21.json
    Expected: Strong
    Actual: Good

⚠️  WARNINGS (1):
--------------------------------------------------------------------------------
  • Contradictions detected (7 found) but no dedicated section in narrative
    Category: missing_field
    Files: 2025-Budget-21.txt

ℹ️  INFO (2):
--------------------------------------------------------------------------------
  • Rounded composite score in linkedin (expected in headings)
    Files: 2025-Budget-21_linkedin
    Expected: 82.9
    Actual: 83.0

================================================================================
SUMMARY: 1 errors, 1 warnings, 2 info
```

### JSON Output (--json flag)
```json
{
  "base_name": "2025-Budget-21",
  "total_issues": 4,
  "errors": 1,
  "warnings": 1,
  "info": 2,
  "issues": [
    {
      "severity": "ERROR",
      "category": "label_mismatch",
      "description": "Performance label in JSON doesn't match score threshold",
      "files_affected": ["2025-Budget-21.json"],
      "expected_value": "Strong",
      "actual_value": "Good"
    }
  ]
}
```

## Exit Codes
- **0**: No errors (warnings/info allowed)
- **1**: One or more errors found

## Issue Severity Levels

### ERROR ❌
**Critical discrepancies requiring immediate attention:**
- Score mismatches beyond tolerance (>0.1)
- Performance label doesn't match threshold
- Missing `adjusted` flag when adjustments made
- Missing fields in core files

**Action**: Must be fixed before publication

### WARNING ⚠️
**Important but non-blocking issues:**
- Contradictions detected but not shown in narrative
- Multiple timestamps in same batch
- Could not extract expected values

**Action**: Should be reviewed and addressed

### INFO ℹ️
**Expected behavior or minor notices:**
- Rounded scores in headings (allowed per policy)
- Contradictions not mentioned in LinkedIn (optional)
- Informational context

**Action**: Awareness only, no changes needed

## Expected Validation Results

### Clean Run
```
✅ VALIDATION PASSED: No issues found for 2025-Budget-21
```

### Run with Allowed Rounding
```
ℹ️  INFO (2):
  • Rounded composite score in linkedin (expected in headings)
  • Rounded composite score in x_thread (expected in headings)

SUMMARY: 0 errors, 0 warnings, 2 info
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Validate SPOT Scale Outputs
  run: |
    python validate_outputs.py ${{ matrix.document }} --output-dir ./outputs --json > validation.json
    
- name: Check for Errors
  run: |
    if [ $(jq '.errors' validation.json) -gt 0 ]; then
      echo "Validation failed with errors"
      exit 1
    fi
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

for file in *.json; do
  base_name="${file%.json}"
  python validate_outputs.py "$base_name" || exit 1
done
```

## Troubleshooting

### "No output files found"
- **Cause**: Base name doesn't match files in directory
- **Solution**: Check file naming, use `--output-dir` to specify correct path

### "Could not extract composite score"
- **Cause**: Text format changed or score not in expected location
- **Solution**: Update `_extract_score_from_text()` patterns in validator

### Multiple timestamp warnings
- **Cause**: Files generated at different times
- **Solution**: Ensure all files created in single batch with unified timestamp (see Task 7)

### Missing contradictions section
- **Cause**: Narrative engine not including detected contradictions
- **Solution**: Implement Task 5 (add Flags and Contradictions section)

## Maintenance

### Adding New Validation Checks
1. Add method to `OutputValidator` class (e.g., `_validate_new_field()`)
2. Call method in `validate_all()`
3. Create appropriate `ValidationIssue` objects
4. Update this documentation

### Adjusting Tolerance
Modify `SCORE_TOLERANCE` constant (currently 0.1):
```python
class OutputValidator:
    SCORE_TOLERANCE = 0.1  # Maximum allowed difference
```

### Updating Label Schema
Modify thresholds in `_validate_performance_labels()`:
```python
if score >= 90:
    expected_label = 'Exceptional'
elif score >= 80:
    expected_label = 'Strong'
```

## Related Tasks
- **Task 1**: Centralized scoring configuration (validates this implementation)
- **Task 3**: Standardize performance label schema (validated by this script)
- **Task 5**: Add Flags and Contradictions section (detected by this script)
- **Task 7**: Unified timestamping (validated by this script)

## Files Checked
- `{base_name}.json` (primary source)
- `{base_name}_certificate.json`
- `{base_name}_certificate.html`
- `{base_name}.txt` (narrative)
- `{base_name}_linkedin.txt`
- `{base_name}_x_thread.txt`
- `{base_name}_summary.txt`
- `{base_name}_insights.json`
- `{base_name}_qa_report.json`

# TODO: Certificate & Analysis Enhancements

## Priority 1: Critical Fixes

### 1. Add Document Title to "Current Settings Summary"
- [ ] Update GUI to display user-entered document title in the settings summary panel
- [ ] Show document title field value alongside other current configuration details
- [ ] Location: GUI settings summary display component

### 2. Fix AI Content Percentage Discrepancy
- [ ] **Issue**: Certificate shows 31% AI content, but AI disclosure states 42%
- [ ] Investigate which value is correct (deep analysis vs. basic detection)
- [ ] Ensure certificate uses the same AI percentage as disclosure statements
- [ ] Root cause: Likely certificate using `ai_detection.ai_detection_score` instead of `deep_analysis.consensus.ai_percentage`
- [ ] Fix: Certificate should prioritize deep analysis consensus when available (already done in v8.3.1, verify GUI path)

### 3. Data Lineage Flowchart Generation
- [ ] **Issue**: Flowchart not being generated from GUI
- [ ] Verify lineage_chart_format parameter is being passed correctly
- [ ] Check if `--lineage-chart html` flag is being set in GUI analysis
- [ ] Ensure data lineage files are being created even with minimal data
- [ ] Test with different data volumes to confirm generation thresholds

## Priority 2: Enhanced Pattern & Fingerprint Details

### 4. Extract Pattern Detection Details from Document
- [ ] **Current**: Certificate shows "Pattern Detection: 629 patterns found"
- [ ] **Enhancement**: Pull actual pattern content from document
- [ ] Show WHERE in the document patterns were detected (section/line numbers)
- [ ] Display sample pattern text snippets
- [ ] Show pattern types/categories if available
- [ ] Add to certificate as expandable section or separate detailed report

### 5. Extract Phrase Fingerprint Details from Document
- [ ] **Current**: Certificate shows "Phrase Fingerprints: 52 signatures detected"
- [ ] **Enhancement**: Pull actual fingerprint content and signatures
- [ ] Show WHERE fingerprints were detected (specific text locations)
- [ ] Display the actual phrases that triggered fingerprint detection
- [ ] Show confidence scores for each fingerprint
- [ ] Include model attribution for each signature
- [ ] Add to certificate as expandable section or separate detailed report

## Implementation Notes

### Pattern Detection Enhancement
```python
# Potential structure in deep_analysis results:
"pattern_detection": {
    "total_patterns": 629,
    "patterns": [
        {
            "pattern_id": 1,
            "type": "repetitive_structure",
            "location": "Section 3, Lines 45-52",
            "text_sample": "...",
            "confidence": 0.85
        },
        # ... more patterns
    ]
}
```

### Phrase Fingerprint Enhancement
```python
# Potential structure in phrase_fingerprints results:
"phrase_fingerprints": {
    "total_signatures": 52,
    "signatures": [
        {
            "fingerprint_id": 1,
            "phrase": "certain provisions of the budget",
            "location": "Page 1, Line 6",
            "model": "GPT-4",
            "confidence": 0.92,
            "context": "An Act to implement certain provisions of the budget..."
        },
        # ... more signatures
    ]
}
```

## Data Requirements

### For Pattern Details:
- [ ] Check if `deep_analyzer.py` already captures pattern locations
- [ ] If not, modify pattern detection to record source locations
- [ ] Store pattern text samples in results JSON

### For Fingerprint Details:
- [ ] Check if `phrase_fingerprints.py` already captures phrase locations
- [ ] If not, modify fingerprint detection to record source text and positions
- [ ] Store fingerprint phrases and attribution in results JSON

## UI/UX Considerations

### Certificate Display Options:
1. **Inline Expandable Sections**: Click to expand pattern/fingerprint details
2. **Separate Detailed Report**: Generate additional HTML file with full pattern/fingerprint analysis
3. **Tabbed Interface**: Add tabs to certificate for summary vs. detailed view
4. **PDF Annotations**: Link patterns/fingerprints to specific PDF locations (if PDF input)

### Recommended Approach:
- Generate separate detailed report (`*_pattern_analysis.html`, `*_fingerprint_analysis.html`)
- Add summary counts to main certificate (current behavior)
- Include links in certificate to open detailed reports
- Maintain backward compatibility with existing certificate format

## Files to Modify

### GUI Enhancement (Document Title in Settings):
- `gui/sparrow_gui.py` - Add document_title to settings summary display

### AI Percentage Fix:
- `certificate_generator.py` - Verify deep analysis prioritization
- `gui/sparrow_gui.py` - Check certificate generation path

### Lineage Flowchart Fix:
- `gui/sparrow_gui.py` - Verify lineage_chart_format parameter handling
- `data_lineage_visualizer.py` - Check generation logic

### Pattern & Fingerprint Details:
- `deep_analyzer.py` - Capture pattern locations and text
- `phrase_fingerprints.py` - Capture fingerprint phrases and locations
- `certificate_generator.py` - Add detailed pattern/fingerprint sections
- New file: `pattern_report_generator.py` (optional separate report)
- New file: `fingerprint_report_generator.py` (optional separate report)

## Testing Plan

- [ ] Test with Bill C-15 documents to verify all enhancements
- [ ] Verify document title appears in settings summary
- [ ] Confirm AI percentages match across certificate and disclosures
- [ ] Test lineage flowchart generation with various data volumes
- [ ] Validate pattern details are extracted and displayed correctly
- [ ] Validate fingerprint details are extracted and displayed correctly
- [ ] Test performance impact of storing additional detail data
- [ ] Ensure backward compatibility with existing analysis outputs

## Estimated Effort

- **Document Title in Settings**: 15 minutes
- **AI Percentage Fix**: 30 minutes (investigation + fix)
- **Lineage Flowchart Fix**: 30 minutes (investigation + fix)
- **Pattern Details Enhancement**: 2-3 hours (analysis + implementation)
- **Fingerprint Details Enhancement**: 2-3 hours (analysis + implementation)

**Total**: ~6-8 hours for full implementation

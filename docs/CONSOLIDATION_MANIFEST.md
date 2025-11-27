# SPOT_News Workspace Consolidation Manifest

**Date:** 2025 (Session Complete)  
**Status:** ✅ CONSOLIDATION COMPLETE  
**Purpose:** Isolated v8 narrative engine development workspace

## Overview

The `SPOT_News` directory consolidates all essential files for v8 development, organized for clean namespace management and scalable narrative engine integration.

---

## Directory Structure

```
SPOT_News/
├── Core v8 Implementation (Ready for Development)
│   ├── sparrow_grader_v8.py              (1,587 lines) - v8 main grader
│   └── sparrow_grader_v7.py              (1,588 lines) - v7 reference
│
├── Ethical Framework Modules (4 files, 71 KB)
│   ├── ai_detection_engine.py            (280+ lines) - Pillar 1: Input transparency
│   ├── nist_risk_mapper.py               (350+ lines) - Pillar 2: Risk classification
│   ├── bias_auditor.py                   (350+ lines) - Pillar 2: Fairness auditing
│   └── trust_score_calculator.py         (200+ lines) - Pillar 2: Trust metrics
│
├── Output Generation
│   ├── certificate_generator.py          (917 lines) - Enhanced HTML certificates
│   └── integrate_v7_ethical_modules.py   (3.1 KB) - Integration verification
│
├── Documentation (Strategic)
│   └── docs/
│       ├── Suitability of SPOT-Policy™ v7.0 for Social Media Articles.md
│       └── SPOT-Policy™ for News Articles.md
│
├── Test Data (Reference)
│   ├── test_articles/
│   │   ├── 2025_budget/ (5 budget analyses with JSON, TXT, HTML outputs)
│   │   ├── Canada-US-Tariffs.md
│   │   ├── Canada-US-Relations.md
│   │   ├── Billion-Dollar-Raket.md
│   │   ├── Billion-Dollar-Raket.json
│   │   └── Billion-Dollar-Raket-Narrative.md
│   │
│   └── v7_reference/
│       ├── Complete v7 Codebase (8 files, 200+ KB)
│       │   ├── sparrow_grader_v7.py
│       │   ├── ai_detection_engine.py
│       │   ├── nist_risk_mapper.py
│       │   ├── bias_auditor.py
│       │   ├── trust_score_calculator.py
│       │   ├── certificate_generator.py
│       │   ├── integrate_v7_ethical_modules.py
│       │   └── v7_ethical_integration_patch.py
│       │
│       └── v7 Test Reports (backup/)
│           ├── report.json
│           ├── report.txt
│           ├── report_certificate.html
│           └── report_summary.txt
│
└── Release Documentation
    ├── V8_SETUP_MANIFEST.txt             (v8 setup inventory)
    └── V7_PHASE2_COMPLETION_SUMMARY.md   (v7 Phase 2 final status)
```

---

## File Inventory

### Core Implementation Files (v8 Ready)

| File | Lines | Size | Purpose | Status |
|------|-------|------|---------|--------|
| `sparrow_grader_v8.py` | 1,587 | 71 KB | v8 main grader (v7 foundation) | ✅ Ready for v8 enhancements |
| `sparrow_grader_v7.py` | 1,588 | 71 KB | v7 reference implementation | ✅ Reference for v8 development |

### Ethical Framework Modules

| File | Lines | Size | Component | Pillar |
|------|-------|------|-----------|--------|
| `ai_detection_engine.py` | 280+ | 20 KB | Multi-model consensus detection | 1: Input |
| `nist_risk_mapper.py` | 350+ | 17 KB | Risk tier classification (7-factor) | 2: Analysis |
| `bias_auditor.py` | 350+ | 19 KB | Fairness metrics (DIR, EOD, SPD) | 2: Analysis |
| `trust_score_calculator.py` | 200+ | 15 KB | Composite trust (4-component) | 2: Analysis |

### Output & Integration

| File | Lines | Size | Purpose | Status |
|------|-------|------|---------|--------|
| `certificate_generator.py` | 917 | 46 KB | HTML certificates + ethical badges | ✅ v7.0 Phase 2 enhanced |
| `integrate_v7_ethical_modules.py` | ~120 | 3.1 KB | Integration verification | ✅ Ready |

### Strategic Documentation

| File | Size | Purpose |
|------|------|---------|
| `Suitability of SPOT-Policy™ v7.0 for Social Media Articles.md` | ~217 lines | Best practices for social media use |
| `SPOT-Policy™ for News Articles.md` | ~129 lines | SPOT-News™ media accountability variant |

### Test Data

| Directory | Contents | Purpose |
|-----------|----------|---------|
| `test_articles/2025_budget/` | 5 budget analyses (JSON, TXT, HTML) | Budget scoring examples |
| `test_articles/` | Canada tariffs, relations, billion-dollar analyses | Media analysis test cases |
| `v7_reference/sparrow_grader_v7_backup/` | v7 report outputs (JSON, TXT, HTML, summary) | v7 baseline outputs |

---

## v8 Development Roadmap

### Phase v8.1: Narrative Engine (4-6 hours)

**Objective:** Build core narrative generation capability

```
5 Narrative Modules (to be created):

1. narrative_engine.py (NEW)
   - Core: Translate v7 JSON → story components
   - Implements: Lede generator, criterion interpreters, tension detector
   - Input: v7 JSON analysis report
   - Output: Narrative components dict

2. tone_adaptor.py (NEW)
   - Adjusts narrative voice: journalistic, academic, civic, critical, explanatory
   - Applies platform conventions (X vs LinkedIn vs blog)
   - Input: Narrative components + tone setting
   - Output: Voice-adjusted text

3. insight_extractor.py (NEW)
   - Identifies surprising findings, gaps, mismatches, escalations
   - Flags policy implications
   - Input: v7 analysis JSON
   - Output: Notable insights list

4. format_renderer.py (NEW)
   - Multi-format output: X thread, LinkedIn, badge/caption, HTML certificate
   - Input: Narrative components + format choice
   - Output: Ready-to-share formatted text/HTML

5. narrative_qa.py (NEW)
   - Validation: accuracy vs JSON, bias detection, escalation verification
   - Input: Generated narrative + original v7 JSON
   - Output: QA report + validated narrative
```

### Phase v8.2: Integration (2-3 hours)

- Update `sparrow_grader_v8.py` to call narrative modules
- Add narrative generation to `grade()` method
- Test with existing v7 output (test_articles/2025_budget/)

### Phase v8.3: Dual-Mode & Testing (1-2 hours)

- Implement mode detection: Policy narratives vs Media accountability
- Run narratives on sample analyses
- Generate format examples (X thread, LinkedIn, badge, certificate)
- Document API and usage

---

## Key v7 Enhancements (Phase 2 Complete)

All Phase 2 enhancements are integrated into `sparrow_grader_v7.py`:

1. ✅ **Vision Auto-Activation**: Both journalism and policy variants
2. ✅ **Enhanced Escalation**: Detailed reason tracking (4 conditions)
3. ✅ **Economic Rigor**: Confidence intervals with sensitivity analysis
4. ✅ **Ethical Badges**: 4-badge system (Trust Score, AI Detection, Risk Tier, Fairness)
5. ✅ **v4 Reference Updates**: 17+ replacements fixed

---

## Dual-Mode Architecture

### SPOT-Policy™ Mode (v7 Current)
- Analyzes policy documents for fiscal transparency, stakeholder balance, economic rigor, accessibility, consequentiality
- Outputs: Policy assessment score (0-100), risk tier, trust score
- Narrative focus: "How sound is this policy?"

### SPOT-News™ Mode (v8 Planned)
- Analyzes media coverage for source quality, perspective balance, evidence quality, accessibility, accountability
- Outputs: Media assessment score (0-100), credibility tier, trust score
- Narrative focus: "How credible is this coverage?"

---

## Import Dependencies

### Core Python Modules
```python
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
```

### External Libraries (from requirements.txt)
- `transformers` - HuggingFace models
- `torch` - PyTorch
- `requests` - HTTP calls
- `pydantic` - Data validation
- `ollama` - Local LLM inference
- `pypdf` - PDF processing
- `pillow` - Image processing
- `pandas` - Data analysis

### Granite Vision Model
- `granite3.2-vision` (via Ollama or direct API)
- Input: PDF/image files
- Output: Extracted text + metadata

---

## Next Steps

### Immediate (First Session)
1. ✅ Verify all files copied to SPOT_News/
2. ✅ Confirm imports work (modules can load)
3. ✅ Test v7 output reading (sample JSON from test_articles/)

### Short-term (This Sprint)
1. Create `narrative_engine.py` (core story generation)
2. Create `tone_adaptor.py` (voice adjustment)
3. Create `insight_extractor.py` (find findings)
4. Create `format_renderer.py` (multi-format output)
5. Create `narrative_qa.py` (validation)
6. Integrate all 5 into `sparrow_grader_v8.py`
7. Test with 2025 budget examples

### Medium-term (v8 RC)
1. Implement dual-mode detection
2. Create narrative templates for each format
3. Add SPOT-News™ specific criterions
4. Generate example narratives for documentation
5. Build web interface (optional)

---

## Files to Ignore (Not Copied)

These files remain in root `/home/gene/Wave-2-2025-Methodology/` and are NOT duplicated:

- `sparrow_grader_v1.py` through `sparrow_grader_v6.py` (earlier versions)
- `sparrow_grader_v8/` (v7 snapshot directory - reference maintained via `v7_reference/`)
- Root-level analysis scripts (`article_analyzer.py`, `quick_analysis.py`, etc.)
- Root-level configuration (`config.json`, `test_context.json`)
- Legacy output files (`.html`, `.json`, `.txt` in root)

**Rationale:** Keep root directory for legacy support; SPOT_News is clean workspace for v8

---

## Reference Locations

**Within SPOT_News:**
- v7 Complete Codebase: `./v7_reference/` (full backup)
- v8 Development Base: `./sparrow_grader_v8.py` (main v8 file)
- Strategic Docs: `./docs/` (SPOT-Policy™ and SPOT-News™ specifications)
- Test Data: `./test_articles/` (5 budget analyses + media examples)

**In Parent Directory (Root):**
- Original v7: `./sparrow_grader_v7.py` (unchanged)
- Original v6: `./sparrow_grader_v6/` (archive)
- v7 Snapshot: `./sparrow_grader_v8/` (v7 reference backup)

---

## Success Criteria

### Consolidation ✅
- [x] All core v8 files in `./`
- [x] All ethical modules in `./`
- [x] v7 complete backup in `./v7_reference/`
- [x] Strategic documentation in `./docs/`
- [x] Test data in `./test_articles/`
- [x] Clean namespace (no redundant files)

### v8 Development (Next)
- [ ] 5 narrative modules created and tested
- [ ] Multi-format output working (X, LinkedIn, badge, certificate)
- [ ] Dual-mode detection functioning
- [ ] All narratives validated against source JSON
- [ ] Documentation complete

---

## Maintenance Notes

- **Root Directory**: Contains all v1-v8 versions for historical reference
- **SPOT_News**: Isolated v8 development environment
- **v7_reference**: Frozen v7 state for rollback or reference
- **test_articles**: Growing dataset for v8 narrative testing

All files version-controlled in Git. Create branch for v8 work:
```bash
cd /home/gene/Wave-2-2025-Methodology
git checkout -b v8-narrative-engine
```

---

**Consolidation Complete:** Ready for v8 narrative engine development

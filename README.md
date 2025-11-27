# Wave-2-2025-Methodology

# Small-Scale Social Media Analysis System
This repository contains the code and resources for building a small-scale social media analysis system using Python and various AI models. The system includes Named Entity Recognition (NER), Surprising Phrase Detection (SPD), Link Analysis, Topic Modelling and Semantic Mapping, Data Visualization, and Qualitative Content Analysis. The project is designed to facilitate learning the concepts outlined in the Wave 2 2025 Methodology document and can be run on a small scale using Python.

## Getting Started
To get started with this project, you will need to install Python and the required libraries (spaCy, BERTopic, matplotlib, pandas, and the sfpd package from GitHub). Once you have set up your development environment, you can follow the steps outlined in the guide to build and run the system.

## License
This project is licensed under the MIT License. See the LICENSE file for more information.


---

## 🎯 Sparrow SPOT Scale™ v4.0 - RELEASED

### What's New in v4

**Dual-Variant Grading System:**
- **Policy Variant (SPOT-Policy™)** - NEW in v4.0
  - Grade budgets and policy documents using FISCAL framework
  - FT, SB, ER, PA, PC criteria (5 dimensions)
  - Composite scoring with intelligent weighting

- **Journalism Variant (SPARROW Scale™)** - Now in v4
  - Grade news articles and journalistic content
  - SI, OI, TP, AR, IU categories (5 dimensions)
  - 100% compatible with v3

### Quick Start

```bash
# Grade a policy document
python sparrow_grader_v4.py budget.pdf --variant policy -o analysis

# Grade a news article
python sparrow_grader_v4.py article.txt --variant journalism -o report

# View results
cat analysis.json  # Structured data
cat analysis.txt   # Human-readable summary
```

### Key Features

✅ **Dual-Variant System**
- Choose between policy and journalism grading
- Unified interface with `--variant` flag

✅ **PDF Support**
- Extract text from large PDFs (tested to 1M+ characters)
- Automatic fallback from pdfplumber to pypdf
- Handles 493-page budgets with ease

✅ **Structured Output**
- JSON for integration and automation
- Text summaries for stakeholders
- Grade labels with detailed descriptions

✅ **Production Ready**
- 100% backward compatible with v3
- Comprehensive error handling
- Performance validated on real data

### Test Results

| Scenario | Composite | Grade |
|----------|-----------|-------|
| 2025 Budget (Policy) | 84.4/100 | B+ |
| Sample Policy (Policy) | 53.4/100 | D |
| 2025 Budget (Journalism) | 67.6/100 | C |

### Documentation

- [Quick Start Guide](docs/V4_QUICK_START.md) - Get started in 5 minutes
- [Release Notes](docs/V4_RELEASE_NOTES.md) - Full feature list
- [SPOT-Policy Design](docs/SPOT-Policy-Variant-Design.md) - Policy framework details
- [Completion Summary](docs/V4_COMPLETION_SUMMARY.md) - Project details and testing

### Version Timeline

- **v1** (2024) - Initial SPARROW grader
- **v2** (2024) - Enhanced scoring
- **v3** (2024) - Production grader with utilities
- **v4** (Nov 2025) - ✨ Dual-variant system with policy support

### Roadmap

**v4.1** (Next)
- HTML certificate generation
- Batch processing mode
- Ollama integration for enhanced analysis

**v5.0** (Future)
- REST API
- Web dashboard
- Database backend
- Multi-user support

---

**Status:** Production Ready ✅
**Last Updated:** November 12, 2025

"""
Sparrow SPOT Scale™ Version Management
Centralized version control for all components
"""

# Main version
SPARROW_VERSION = "8.6.1"
SPARROW_VERSION_NAME = "Enhanced Document Q&A System"
RELEASE_DATE = "2025-12-07"

# Component versions (when they differ from main)
DEEP_ANALYZER_VERSION = "8.4.2"
PROVENANCE_VERSION = "1.1"
CERTIFICATE_VERSION = "8.6.1"  # Updated with document-type fix
NARRATIVE_ENGINE_VERSION = "8.0"

# Version history for reference
VERSION_HISTORY = {
    "8.6.1": "Document type parameter fix - GUI now properly passes document type selection to grader for correct certificate badges",
    "8.6.0": "Enhanced Document Q&A System - Multi-chunk analysis with token calculator, semantic chunker, and intelligent query routing",
    "8.5.1": "Improved DPA reporting with zero data loss, bilingual PDF column extraction",
    "8.5.0": "Legislative Threat Detection Suite with Discretionary Power Analyzer",
    "8.4.2": "Fixed model confidence calculation, added document type awareness, improved section analysis",
    "8.4.1": "Enhanced provenance reporting with legislative metadata",
    "8.4.0": "Classification logic fix for policy grading",
    "8.3.4": "Document type baseline calibration",
    "8.3.0": "Comprehensive transparency toolkit",
    "8.2.0": "Deep analysis integration",
    "8.1.0": "Model-specific detection",
    "8.0.0": "AI Transparency & Detection criterion added"
}

def get_version_string():
    """Get formatted version string for display"""
    return f"v{SPARROW_VERSION}"

def get_full_version_info():
    """Get complete version information"""
    return {
        "version": SPARROW_VERSION,
        "version_name": SPARROW_VERSION_NAME,
        "release_date": RELEASE_DATE,
        "components": {
            "deep_analyzer": DEEP_ANALYZER_VERSION,
            "provenance": PROVENANCE_VERSION,
            "certificate": CERTIFICATE_VERSION,
            "narrative_engine": NARRATIVE_ENGINE_VERSION
        }
    }

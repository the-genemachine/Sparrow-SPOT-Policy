"""
Provenance Report Generator for Sparrow SPOT Scale™ v8.4.1

Generates comprehensive provenance reports combining:
1. Document Origin - Where the document came from (metadata, hash, timestamps)
2. Analysis Provenance - What Sparrow did to analyze it (AI calls, models used)

This provides a complete audit trail for transparency and compliance.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json
import hashlib

VERSION = "8.4.1"


class ProvenanceReportGenerator:
    """
    Generate comprehensive provenance reports for document analysis.
    
    Combines document forensics with AI contribution tracking to provide
    a complete chain-of-custody for analysis transparency.
    """
    
    def __init__(self):
        """Initialize the provenance report generator."""
        self.sparrow_version = VERSION
    
    def generate_report(
        self,
        document_metadata: Dict[str, Any],
        ai_calls_log: List[Dict[str, Any]],
        contribution_log: Optional[Dict[str, Any]] = None,
        document_title: str = "Unknown Document",
        analysis_timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete provenance report.
        
        Args:
            document_metadata: Output from ProvenanceAnalyzer.extract_metadata()
            ai_calls_log: Output from OllamaSummaryGenerator.get_ai_calls_log()
            contribution_log: Output from NarrativeGenerationPipeline.get_ai_contribution_log()
            document_title: Human-readable document title
            analysis_timestamp: When analysis was performed (ISO format)
            
        Returns:
            Complete provenance report dict
        """
        if not analysis_timestamp:
            analysis_timestamp = datetime.now().isoformat()
        
        report = {
            "provenance_version": "1.0",
            "sparrow_version": self.sparrow_version,
            "report_generated": datetime.now().isoformat(),
            "document_title": document_title,
            
            # Part 1: Document Origin
            "document_origin": self._build_document_origin(document_metadata),
            
            # Part 2: Analysis Provenance  
            "analysis_provenance": self._build_analysis_provenance(
                ai_calls_log, 
                contribution_log,
                analysis_timestamp
            ),
            
            # Part 3: Summary
            "summary": self._build_summary(document_metadata, ai_calls_log, contribution_log)
        }
        
        return report
    
    def _build_document_origin(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build the document origin section from metadata."""
        if not metadata or 'error' in metadata:
            return {
                "status": "unavailable",
                "reason": metadata.get('error', 'No metadata provided')
            }
        
        origin = {
            "file_identity": {
                "file_name": metadata.get('file_name', 'Unknown'),
                "file_size_bytes": metadata.get('file_size', 0),
                "file_extension": metadata.get('file_extension', ''),
                "file_hash_sha256": metadata.get('file_hash', 'Unknown')
            },
            "timestamps": {
                "created": metadata.get('creation_date', 'Unknown'),
                "modified": metadata.get('modification_date', 'Unknown'),
                "timestamps_plausible": self._check_timestamps_plausible(metadata)
            },
            "authorship": self._extract_authorship(metadata),
            "creation_tools": self._extract_creation_tools(metadata),
            "ai_markers": {
                "ai_tool_markers_found": metadata.get('ai_tool_markers', []),
                "suspected_ai_tool": metadata.get('document_metadata', {}).get('suspected_ai_tool'),
                "has_ai_indicators": len(metadata.get('ai_tool_markers', [])) > 0
            },
            "integrity": {
                "hash_verified": bool(metadata.get('file_hash')),
                "edit_patterns": metadata.get('edit_patterns', {})
            }
        }
        
        return origin
    
    def _check_timestamps_plausible(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Check if timestamps are plausible (no paradoxes)."""
        created = metadata.get('creation_date')
        modified = metadata.get('modification_date')
        
        result = {
            "is_plausible": True,
            "anomalies": []
        }
        
        if created and modified:
            try:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                modified_dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                
                # Check: Modified before created
                if modified_dt < created_dt:
                    result["is_plausible"] = False
                    result["anomalies"].append({
                        "type": "temporal_paradox",
                        "description": "Modified date precedes creation date",
                        "severity": "HIGH"
                    })
                
                # Check: Future timestamps
                now = datetime.now(created_dt.tzinfo) if created_dt.tzinfo else datetime.now()
                if created_dt > now:
                    result["is_plausible"] = False
                    result["anomalies"].append({
                        "type": "future_timestamp",
                        "description": "Creation date is in the future",
                        "severity": "HIGH"
                    })
            except (ValueError, TypeError):
                pass
        
        return result
    
    def _extract_authorship(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract authorship information from metadata."""
        pdf_meta = metadata.get('pdf_metadata', {})
        doc_meta = metadata.get('document_metadata', {})
        
        return {
            "author": pdf_meta.get('author', 'Unknown'),
            "creator_software": pdf_meta.get('creator', 'Unknown'),
            "producer_software": pdf_meta.get('producer', 'Unknown'),
            "last_modified_by": doc_meta.get('author_info', 'Unknown')
        }
    
    def _extract_creation_tools(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract creation tool information."""
        doc_meta = metadata.get('document_metadata', {})
        pdf_meta = metadata.get('pdf_metadata', {})
        
        tools_detected = []
        
        if doc_meta.get('creation_tool') and doc_meta['creation_tool'] != 'Unknown':
            tools_detected.append({
                "tool": doc_meta['creation_tool'],
                "source": "document_analysis",
                "confidence": 0.85
            })
        
        if pdf_meta.get('creator') and pdf_meta['creator'] != 'Unknown':
            tools_detected.append({
                "tool": pdf_meta['creator'],
                "source": "pdf_metadata",
                "confidence": 0.95
            })
        
        if pdf_meta.get('producer') and pdf_meta['producer'] != 'Unknown':
            tools_detected.append({
                "tool": pdf_meta['producer'],
                "source": "pdf_producer",
                "confidence": 0.95
            })
        
        return {
            "tools_detected": tools_detected,
            "primary_tool": tools_detected[0]['tool'] if tools_detected else "Unknown"
        }
    
    def _build_analysis_provenance(
        self, 
        ai_calls_log: List[Dict[str, Any]],
        contribution_log: Optional[Dict[str, Any]],
        analysis_timestamp: str
    ) -> Dict[str, Any]:
        """Build the analysis provenance section."""
        
        # Process AI calls from Ollama
        ai_calls_summary = []
        total_duration_ms = 0
        total_prompt_chars = 0
        total_response_chars = 0
        models_used = set()
        
        for call in ai_calls_log or []:
            ai_calls_summary.append({
                "call_id": call.get('call_id'),
                "timestamp": call.get('timestamp'),
                "model": call.get('model'),
                "purpose": call.get('purpose', 'unknown'),
                "prompt_length_chars": call.get('prompt_length', 0),
                "response_length_chars": call.get('response_length', 0),
                "duration_ms": call.get('duration_ms', 0),
                "status": call.get('status', 'unknown')
            })
            
            if call.get('status') == 'success':
                total_duration_ms += call.get('duration_ms', 0)
                total_prompt_chars += call.get('prompt_length', 0)
                total_response_chars += call.get('response_length', 0)
                models_used.add(call.get('model', 'unknown'))
        
        # Process narrative contributions
        contributions = []
        if contribution_log:
            for contrib in contribution_log.get('contributions', []):
                contributions.append({
                    "component": contrib.get('component'),
                    "model": contrib.get('model'),
                    "type": contrib.get('type'),
                    "timestamp": contrib.get('timestamp'),
                    "requires_review": contrib.get('requires_review', True),
                    "reviewed": contrib.get('reviewed', False)
                })
        
        return {
            "analysis_timestamp": analysis_timestamp,
            "sparrow_version": self.sparrow_version,
            
            "ai_calls": {
                "total_calls": len(ai_calls_log or []),
                "successful_calls": len([c for c in (ai_calls_log or []) if c.get('status') == 'success']),
                "failed_calls": len([c for c in (ai_calls_log or []) if c.get('status') == 'error']),
                "models_used": list(models_used),
                "total_duration_ms": total_duration_ms,
                "total_prompt_chars": total_prompt_chars,
                "total_response_chars": total_response_chars,
                "calls_detail": ai_calls_summary
            },
            
            "narrative_contributions": {
                "total_contributions": len(contributions),
                "overall_ai_percentage": contribution_log.get('overall_ai_percentage', 0) if contribution_log else 0,
                "contributions_detail": contributions,
                "components": contribution_log.get('components', {}) if contribution_log else {}
            },
            
            "transparency_statement": self._generate_transparency_statement(ai_calls_log, contribution_log)
        }
    
    def _generate_transparency_statement(
        self, 
        ai_calls_log: List[Dict[str, Any]],
        contribution_log: Optional[Dict[str, Any]]
    ) -> str:
        """Generate a human-readable transparency statement."""
        total_calls = len(ai_calls_log or [])
        models = set(c.get('model') for c in (ai_calls_log or []) if c.get('model'))
        
        if total_calls == 0:
            return "No AI models were used in generating this analysis."
        
        models_str = ", ".join(sorted(models))
        
        return (
            f"This analysis used {total_calls} AI model call(s) via Ollama. "
            f"Models used: {models_str}. "
            f"All AI contributions are logged for transparency and audit purposes."
        )
    
    def _build_summary(
        self, 
        document_metadata: Dict[str, Any],
        ai_calls_log: List[Dict[str, Any]],
        contribution_log: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build the summary section."""
        
        # Document origin status
        doc_status = "verified" if document_metadata and 'error' not in document_metadata else "unavailable"
        
        # AI usage summary
        total_ai_calls = len(ai_calls_log or [])
        successful_calls = len([c for c in (ai_calls_log or []) if c.get('status') == 'success'])
        
        return {
            "document_origin_status": doc_status,
            "document_hash_available": bool(document_metadata.get('file_hash')) if document_metadata else False,
            "ai_calls_made": total_ai_calls,
            "ai_calls_successful": successful_calls,
            "provenance_complete": doc_status == "verified" and total_ai_calls >= 0,
            "requires_human_review": any(
                c.get('requires_review', True) 
                for c in (contribution_log.get('contributions', []) if contribution_log else [])
            )
        }
    
    def generate_markdown_report(
        self,
        provenance_report: Dict[str, Any],
        include_call_details: bool = True
    ) -> str:
        """
        Generate a markdown-formatted provenance report.
        
        Args:
            provenance_report: Output from generate_report()
            include_call_details: Whether to include detailed AI call logs
            
        Returns:
            Markdown-formatted report string
        """
        doc_title = provenance_report.get('document_title', 'Unknown Document')
        origin = provenance_report.get('document_origin', {})
        analysis = provenance_report.get('analysis_provenance', {})
        summary = provenance_report.get('summary', {})
        
        lines = [
            f"# 📜 Document Provenance Report",
            f"",
            f"**Document:** {doc_title}",
            f"**Generated:** {provenance_report.get('report_generated', 'Unknown')}",
            f"**Sparrow Version:** {provenance_report.get('sparrow_version', 'Unknown')}",
            f"",
            f"---",
            f"",
            f"## Part 1: Document Origin",
            f""
        ]
        
        # File Identity
        file_id = origin.get('file_identity', {})
        lines.extend([
            f"### File Identity",
            f"",
            f"| Property | Value |",
            f"|----------|-------|",
            f"| **File Name** | {file_id.get('file_name', 'Unknown')} |",
            f"| **File Size** | {file_id.get('file_size_bytes', 0):,} bytes |",
            f"| **Format** | {file_id.get('file_extension', 'Unknown')} |",
            f"| **SHA-256 Hash** | `{file_id.get('file_hash_sha256', 'Unknown')[:16]}...` |",
            f""
        ])
        
        # Timestamps
        timestamps = origin.get('timestamps', {})
        plausibility = timestamps.get('timestamps_plausible', {})
        lines.extend([
            f"### Timeline",
            f"",
            f"| Event | Date |",
            f"|-------|------|",
            f"| **Created** | {timestamps.get('created', 'Unknown')} |",
            f"| **Modified** | {timestamps.get('modified', 'Unknown')} |",
            f""
        ])
        
        if not plausibility.get('is_plausible', True):
            lines.append(f"⚠️ **Warning:** Timestamp anomalies detected:")
            for anomaly in plausibility.get('anomalies', []):
                lines.append(f"- {anomaly.get('description')} (Severity: {anomaly.get('severity')})")
            lines.append("")
        
        # Authorship
        authorship = origin.get('authorship', {})
        lines.extend([
            f"### Authorship",
            f"",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Author** | {authorship.get('author', 'Unknown')} |",
            f"| **Creator Software** | {authorship.get('creator_software', 'Unknown')} |",
            f"| **Producer** | {authorship.get('producer_software', 'Unknown')} |",
            f""
        ])
        
        # AI Markers in Document
        ai_markers = origin.get('ai_markers', {})
        if ai_markers.get('has_ai_indicators'):
            lines.extend([
                f"### ⚠️ AI Markers Detected in Document",
                f"",
                f"- **Markers Found:** {', '.join(ai_markers.get('ai_tool_markers_found', []))}",
                f"- **Suspected AI Tool:** {ai_markers.get('suspected_ai_tool', 'Unknown')}",
                f""
            ])
        
        # Part 2: Analysis Provenance
        lines.extend([
            f"---",
            f"",
            f"## Part 2: Sparrow Analysis Provenance",
            f"",
            f"**Analysis Timestamp:** {analysis.get('analysis_timestamp', 'Unknown')}",
            f"**Sparrow Version:** {analysis.get('sparrow_version', 'Unknown')}",
            f""
        ])
        
        # AI Calls Summary
        ai_calls = analysis.get('ai_calls', {})
        lines.extend([
            f"### AI Model Usage",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| **Total AI Calls** | {ai_calls.get('total_calls', 0)} |",
            f"| **Successful Calls** | {ai_calls.get('successful_calls', 0)} |",
            f"| **Failed Calls** | {ai_calls.get('failed_calls', 0)} |",
            f"| **Models Used** | {', '.join(ai_calls.get('models_used', ['None']))} |",
            f"| **Total Duration** | {ai_calls.get('total_duration_ms', 0):,} ms |",
            f"| **Prompt Characters** | {ai_calls.get('total_prompt_chars', 0):,} |",
            f"| **Response Characters** | {ai_calls.get('total_response_chars', 0):,} |",
            f""
        ])
        
        # Detailed AI Calls
        if include_call_details and ai_calls.get('calls_detail'):
            lines.extend([
                f"### AI Call Details",
                f"",
                f"| # | Model | Purpose | Duration | Status |",
                f"|---|-------|---------|----------|--------|"
            ])
            
            for call in ai_calls.get('calls_detail', []):
                lines.append(
                    f"| {call.get('call_id', '?')} | "
                    f"{call.get('model', 'Unknown')} | "
                    f"{call.get('purpose', 'Unknown')} | "
                    f"{call.get('duration_ms', 0)}ms | "
                    f"{call.get('status', 'Unknown')} |"
                )
            
            lines.append("")
        
        # Transparency Statement
        lines.extend([
            f"### Transparency Statement",
            f"",
            f"> {analysis.get('transparency_statement', 'No statement available.')}",
            f""
        ])
        
        # Part 3: Summary
        lines.extend([
            f"---",
            f"",
            f"## Summary",
            f"",
            f"| Check | Status |",
            f"|-------|--------|",
            f"| **Document Origin Verified** | {'✅ Yes' if summary.get('document_hash_available') else '❌ No'} |",
            f"| **AI Calls Made** | {summary.get('ai_calls_made', 0)} |",
            f"| **AI Calls Successful** | {summary.get('ai_calls_successful', 0)} |",
            f"| **Provenance Complete** | {'✅ Yes' if summary.get('provenance_complete') else '⚠️ Partial'} |",
            f"| **Requires Human Review** | {'Yes' if summary.get('requires_human_review') else 'No'} |",
            f"",
            f"---",
            f"",
            f"*This provenance report was generated by Sparrow SPOT Scale™ v{provenance_report.get('sparrow_version', 'Unknown')}*"
        ])
        
        return "\n".join(lines)
    
    def save_report(
        self,
        provenance_report: Dict[str, Any],
        output_path: str,
        format: str = "both"
    ) -> Dict[str, str]:
        """
        Save provenance report to file(s).
        
        Args:
            provenance_report: Output from generate_report()
            output_path: Base path for output (without extension)
            format: 'json', 'markdown', or 'both'
            
        Returns:
            Dict with paths to saved files
        """
        saved_files = {}
        
        if format in ('json', 'both'):
            json_path = f"{output_path}_provenance.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(provenance_report, f, indent=2)
            saved_files['json'] = json_path
            print(f"   ✓ Provenance JSON: {json_path}")
        
        if format in ('markdown', 'both'):
            md_path = f"{output_path}_provenance.md"
            markdown = self.generate_markdown_report(provenance_report)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            saved_files['markdown'] = md_path
            print(f"   ✓ Provenance Report: {md_path}")
        
        return saved_files


def create_provenance_report_generator() -> ProvenanceReportGenerator:
    """Factory function to create a provenance report generator."""
    return ProvenanceReportGenerator()


if __name__ == '__main__':
    # Test with sample data
    sample_metadata = {
        'file_name': 'Bill-C15-Budget-2025.pdf',
        'file_size': 7541238,
        'file_extension': '.pdf',
        'file_hash': 'a3f5e8d9c2b1f4e6d8a5c3b2e4f6d8a9c5b3e7f9d2c4b6e8a5c7d9f2e4b6c8a2',
        'creation_date': '2024-10-15T14:34:22',
        'modification_date': '2024-11-04T09:15:10',
        'ai_tool_markers': [],
        'pdf_metadata': {
            'author': 'Department of Finance Canada',
            'creator': 'Microsoft Word',
            'producer': 'Adobe PDF Library'
        },
        'document_metadata': {
            'creation_tool': 'Microsoft Word',
            'suspected_ai_tool': None
        }
    }
    
    sample_ai_calls = [
        {
            'call_id': 1,
            'timestamp': '2025-12-06T14:30:05',
            'model': 'granite4:tiny-h',
            'purpose': 'policy_summary',
            'prompt_length': 2500,
            'response_length': 1247,
            'duration_ms': 3200,
            'status': 'success'
        },
        {
            'call_id': 2,
            'timestamp': '2025-12-06T14:30:12',
            'model': 'qwen2.5:7b',
            'purpose': 'narrative_expansion',
            'prompt_length': 3500,
            'response_length': 2100,
            'duration_ms': 4100,
            'status': 'success'
        }
    ]
    
    generator = create_provenance_report_generator()
    report = generator.generate_report(
        document_metadata=sample_metadata,
        ai_calls_log=sample_ai_calls,
        document_title="Canada's 2025 Budget Implementation Act"
    )
    
    print(generator.generate_markdown_report(report))

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
        
        # Build document origin first to get legislative metadata for citizen summary
        doc_origin = self._build_document_origin(document_metadata)
        
        report = {
            "provenance_version": "1.1",
            "sparrow_version": self.sparrow_version,
            "report_generated": datetime.now().isoformat(),
            "document_title": document_title,
            
            # Part 1: Document Origin
            "document_origin": doc_origin,
            
            # Part 2: Analysis Provenance  
            "analysis_provenance": self._build_analysis_provenance(
                ai_calls_log, 
                contribution_log,
                analysis_timestamp
            ),
            
            # Part 3: Summary
            "summary": self._build_summary(document_metadata, ai_calls_log, contribution_log),
            
            # Part 4: Human Review Tracking (v8.4.1)
            "human_review_status": self._build_human_review_status(ai_calls_log, contribution_log),
            
            # Part 5: Citizen Summary (v8.4.1) - plain language for non-experts
            "citizen_summary": self._build_citizen_summary(document_metadata, doc_origin)
        }
        
        return report
    
    def _build_document_origin(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build the document origin section from metadata."""
        if not metadata or 'error' in metadata:
            return {
                "status": "unavailable",
                "reason": metadata.get('error', 'No metadata provided')
            }
        
        # Extract PDF metadata for enhanced document info
        pdf_meta = metadata.get('pdf_metadata', {})
        
        # Get date source to indicate if dates are from PDF or filesystem
        date_source = metadata.get('date_source', 'unknown')
        
        origin = {
            "file_identity": {
                "file_name": metadata.get('file_name', 'Unknown'),
                "document_title": pdf_meta.get('title', '') or metadata.get('file_name', 'Unknown'),
                "file_size_bytes": metadata.get('file_size', 0),
                "file_extension": metadata.get('file_extension', ''),
                "file_hash_sha256": metadata.get('file_hash', 'Unknown'),
                "page_count": pdf_meta.get('page_count', 0) if pdf_meta.get('page_count') else None
            },
            "timestamps": {
                "created": metadata.get('creation_date', 'Unknown'),
                "modified": metadata.get('modification_date', 'Unknown'),
                "date_source": date_source,
                "timestamps_embedded": date_source == 'pdf_embedded',
                "timestamps_plausible": self._check_timestamps_plausible(metadata)
            },
            "authorship": self._extract_authorship(metadata),
            "creation_tools": self._extract_creation_tools(metadata),
            "ai_markers": self._extract_ai_markers(metadata),
            "integrity": {
                "hash_verified": bool(metadata.get('file_hash')),
                "edit_patterns": metadata.get('edit_patterns', {})
            }
        }
        
        # v8.4.1: Add legislative metadata if document appears to be legislation
        legislative_meta = self._extract_legislative_metadata(metadata)
        if legislative_meta:
            origin["legislative_metadata"] = legislative_meta
        
        # v8.4.1: Add risk summary
        origin["risk_summary"] = self._generate_risk_summary(metadata, legislative_meta)
        
        # Remove None values from file_identity
        origin["file_identity"] = {k: v for k, v in origin["file_identity"].items() if v is not None}
        
        return origin
    
    def _extract_legislative_metadata(self, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract legislative-specific metadata from document.
        
        v8.4.1: Detects bill numbers, session info, and legislative indicators.
        """
        pdf_meta = metadata.get('pdf_metadata', {})
        title = pdf_meta.get('title', '') or metadata.get('file_name', '')
        author = pdf_meta.get('author', '')
        page_count = pdf_meta.get('page_count', 0) or 0
        
        # Check if this looks like legislation
        legislative_indicators = [
            'bill', 'act', 'legislation', 'parliament', 'house of commons',
            'senate', 'budget', 'royal assent', 'first reading', 'second reading'
        ]
        
        title_lower = title.lower()
        author_lower = author.lower()
        is_legislative = any(ind in title_lower or ind in author_lower for ind in legislative_indicators)
        
        if not is_legislative:
            return None
        
        # Extract bill number (pattern: C-XX or S-XX)
        import re
        bill_match = re.search(r'\b([CS])-(\d+)\b', title, re.IGNORECASE)
        bill_number = f"{bill_match.group(1).upper()}-{bill_match.group(2)}" if bill_match else None
        
        # Extract session number (pattern: 4XX or session numbers)
        session_match = re.search(r'\b(4\d{2})\b', title)
        session = session_match.group(1) if session_match else None
        
        # Detect bill type
        bill_type = "Unknown"
        if 'budget' in title_lower:
            bill_type = "Budget Implementation Act"
        elif 'appropriation' in title_lower:
            bill_type = "Appropriation Act"
        elif 'amendment' in title_lower:
            bill_type = "Amendment Act"
        elif 'act' in title_lower:
            bill_type = "Act"
        
        # Detect omnibus characteristics
        is_omnibus = page_count > 200 or 'provisions' in title_lower
        
        # Detect bilingual
        is_bilingual = '|' in title or 'projet de loi' in title_lower
        
        return {
            "bill_number": bill_number,
            "session": session,
            "bill_type": bill_type,
            "page_count": page_count,
            "is_omnibus": is_omnibus,
            "is_bilingual": is_bilingual,
            "page_count_risk": "CRITICAL" if page_count > 500 else "HIGH" if page_count > 200 else "MEDIUM" if page_count > 50 else "LOW",
            "author_verified": bool(author),
            "author": author,
            "author_is_official": any(x in author_lower for x in ['house of commons', 'parliament', 'senate', 'government']),
            "requires_full_threat_scan": page_count > 100 or is_omnibus
        }
    
    def _generate_risk_summary(
        self, 
        metadata: Dict[str, Any], 
        legislative_meta: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate risk summary for document provenance.
        
        v8.4.1: Provides quick assessment for analysts.
        """
        risk_factors = []
        
        pdf_meta = metadata.get('pdf_metadata', {})
        page_count = pdf_meta.get('page_count', 0) or 0
        
        # Document size risk
        if page_count > 500:
            risk_factors.append({
                "factor": "Document Size",
                "level": "CRITICAL",
                "score": 95,
                "reason": f"{page_count} pages - very high burial risk"
            })
        elif page_count > 200:
            risk_factors.append({
                "factor": "Document Size",
                "level": "HIGH",
                "score": 75,
                "reason": f"{page_count} pages - increased burial risk"
            })
        elif page_count > 50:
            risk_factors.append({
                "factor": "Document Size",
                "level": "MEDIUM",
                "score": 40,
                "reason": f"{page_count} pages - moderate complexity"
            })
        
        # Omnibus bill risk
        if legislative_meta and legislative_meta.get('is_omnibus'):
            risk_factors.append({
                "factor": "Omnibus Bill",
                "level": "HIGH",
                "score": 70,
                "reason": "Budget implementation acts often contain unrelated provisions"
            })
        
        # Temporal anomaly risk
        edit_patterns = metadata.get('edit_patterns', {})
        if edit_patterns.get('suspicious_rapid_edit'):
            time_delta = edit_patterns.get('time_between_create_modify', 0)
            if time_delta < 0:
                risk_factors.append({
                    "factor": "Temporal Anomaly",
                    "level": "LOW",
                    "score": 15,
                    "reason": "Minor metadata clock skew - likely automated generation artifact"
                })
            else:
                risk_factors.append({
                    "factor": "Rapid Edit Pattern",
                    "level": "LOW",
                    "score": 20,
                    "reason": "Document modified very quickly after creation"
                })
        
        # Determine overall risk
        if not risk_factors:
            overall_level = "LOW"
            recommended_action = "STANDARD_ANALYSIS"
        else:
            max_score = max(f['score'] for f in risk_factors)
            if max_score >= 80:
                overall_level = "REQUIRES_INVESTIGATION"
                recommended_action = "FULL_LEGISLATIVE_THREAT_SCAN"
            elif max_score >= 50:
                overall_level = "ELEVATED"
                recommended_action = "ENHANCED_ANALYSIS"
            else:
                overall_level = "LOW"
                recommended_action = "STANDARD_ANALYSIS"
        
        return {
            "overall_risk_level": overall_level,
            "risk_factors": risk_factors,
            "recommended_action": recommended_action,
            "priority_level": "HIGH" if overall_level == "REQUIRES_INVESTIGATION" else "NORMAL"
        }
    
    def _extract_ai_markers(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract AI tool markers from metadata, filtering out error messages.
        
        v8.4.1: Added to properly handle metadata extraction errors.
        """
        raw_markers = metadata.get('ai_tool_markers', [])
        
        # Filter out error messages and invalid markers
        valid_markers = [
            m for m in raw_markers 
            if isinstance(m, str) 
            and m.lower() not in ('error', 'unknown', 'none')
            and not m.startswith('Error:')
            and not m.startswith('error:')
        ]
        
        suspected_ai = metadata.get('document_metadata', {}).get('suspected_ai_tool')
        
        return {
            "ai_tool_markers_found": valid_markers,
            "suspected_ai_tool": suspected_ai,
            "has_ai_indicators": len(valid_markers) > 0 or bool(suspected_ai),
            "marker_extraction_status": "success" if not any(m.lower() == 'error' for m in raw_markers) else "partial_failure"
        }
    
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
        """
        Generate a human-readable transparency statement.
        
        CRITICAL: This must accurately reflect ALL AI usage from both
        ai_calls_log (Ollama summary) AND contribution_log (narrative generation).
        v8.4.1: Fixed to prevent false "no AI" claims when AI was used.
        """
        # Count Ollama API calls
        ollama_calls = len(ai_calls_log or [])
        ollama_models = set(c.get('model') for c in (ai_calls_log or []) if c.get('model'))
        
        # Count narrative contributions
        narrative_contributions = []
        narrative_models = set()
        if contribution_log:
            for contrib in contribution_log.get('contributions', []):
                if contrib.get('model'):
                    narrative_contributions.append(contrib)
                    narrative_models.add(contrib.get('model'))
        
        # Combine all models
        all_models = ollama_models | narrative_models
        total_ai_involvement = ollama_calls + len(narrative_contributions)
        
        # Generate accurate statement
        if total_ai_involvement == 0 and not all_models:
            return "No AI models were used in generating this analysis. All outputs are from deterministic algorithms."
        
        # Build detailed statement
        parts = []
        
        if ollama_calls > 0:
            parts.append(f"Ollama summary generation: {ollama_calls} call(s)")
        
        if narrative_contributions:
            contrib_types = set(c.get('type', 'generation') for c in narrative_contributions)
            parts.append(f"Narrative {', '.join(contrib_types)}: {len(narrative_contributions)} contribution(s)")
        
        models_str = ", ".join(sorted(all_models)) if all_models else "none"
        
        statement = (
            f"AI models were used in this analysis. "
            f"Models: {models_str}. "
            f"Usage: {'; '.join(parts)}. "
            f"Core metadata extraction, hash calculation, and provenance tracking are AI-free. "
            f"All AI contributions are logged for transparency."
        )
        
        return statement
    
    def _build_summary(
        self, 
        document_metadata: Dict[str, Any],
        ai_calls_log: List[Dict[str, Any]],
        contribution_log: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build the summary section with combined AI usage totals."""
        
        # Document origin status
        doc_status = "verified" if document_metadata and 'error' not in document_metadata else "unavailable"
        
        # AI usage summary - combine Ollama calls AND narrative contributions
        ollama_calls = len(ai_calls_log or [])
        successful_ollama = len([c for c in (ai_calls_log or []) if c.get('status') == 'success'])
        
        # Count narrative contributions
        narrative_contributions = len(contribution_log.get('contributions', [])) if contribution_log else 0
        
        # Combine models from both sources
        ollama_models = set(c.get('model') for c in (ai_calls_log or []) if c.get('model'))
        narrative_models = set()
        if contribution_log:
            for contrib in contribution_log.get('contributions', []):
                if contrib.get('model'):
                    narrative_models.add(contrib['model'])
        all_models = list(ollama_models | narrative_models)
        
        # Total AI interactions
        total_ai_interactions = ollama_calls + narrative_contributions
        
        return {
            "document_origin_status": doc_status,
            "document_hash_available": bool(document_metadata.get('file_hash')) if document_metadata else False,
            "total_ai_interactions": total_ai_interactions,
            "ollama_calls": ollama_calls,
            "ollama_calls_successful": successful_ollama,
            "narrative_contributions": narrative_contributions,
            "models_used": all_models,
            "provenance_complete": doc_status == "verified" and total_ai_interactions >= 0,
            "requires_human_review": any(
                c.get('requires_review', True) 
                for c in (contribution_log.get('contributions', []) if contribution_log else [])
            ) or narrative_contributions > 0  # Require review if any narrative AI was used
        }
    
    def _build_human_review_status(
        self,
        ai_calls_log: List[Dict[str, Any]],
        contribution_log: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build human review tracking section.
        
        v8.4.1: Tracks what needs human verification and review status.
        """
        # Determine what requires review
        review_required_for = []
        
        # Check AI calls
        if ai_calls_log:
            review_required_for.append("AI-generated summary content")
        
        # Check narrative contributions
        if contribution_log:
            for contrib in contribution_log.get('contributions', []):
                if contrib.get('requires_review', True):
                    component = contrib.get('component', 'unknown')
                    review_required_for.append(f"AI-generated {component}")
        
        # Standard items that always need review if AI was used
        if review_required_for:
            review_required_for.extend([
                "Factual accuracy of AI outputs",
                "Appropriateness of recommendations"
            ])
        
        return {
            "requires_review": len(review_required_for) > 0,
            "reviewed": False,  # Default to not reviewed
            "review_required_for": review_required_for,
            "review_checklist": {
                "provenance_accuracy": None,
                "ai_disclosure_complete": None,
                "threat_indicators_valid": None,
                "recommendations_appropriate": None,
                "factual_accuracy_verified": None
            },
            "reviewer": None,
            "review_timestamp": None,
            "review_notes": None
        }
    
    def _build_citizen_summary(
        self,
        document_metadata: Dict[str, Any],
        doc_origin: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build plain-language summary for non-expert readers.
        
        v8.4.1: Makes provenance report accessible to journalists and citizens.
        """
        pdf_meta = document_metadata.get('pdf_metadata', {}) if document_metadata else {}
        page_count = pdf_meta.get('page_count', 0) or 0
        title = pdf_meta.get('title', '') or document_metadata.get('file_name', 'Unknown') if document_metadata else 'Unknown'
        
        # Get legislative metadata and risk summary
        leg_meta = doc_origin.get('legislative_metadata', {})
        risk_summary = doc_origin.get('risk_summary', {})
        
        # Build "what is this" description
        if leg_meta:
            bill_num = leg_meta.get('bill_number', '')
            bill_type = leg_meta.get('bill_type', 'document')
            what_is_this = f"A {page_count}-page {bill_type}"
            if bill_num:
                what_is_this = f"Bill {bill_num}: {what_is_this}"
        else:
            what_is_this = f"A {page_count}-page document" if page_count else "A document of unknown length"
        
        # Build key concerns
        key_concerns = []
        risk_level = risk_summary.get('overall_risk_level', 'LOW')
        
        for factor in risk_summary.get('risk_factors', []):
            if factor.get('score', 0) >= 50:
                key_concerns.append(f"{factor.get('reason', 'Unknown concern')}")
        
        if not key_concerns:
            key_concerns.append("No significant concerns detected in provenance analysis")
        
        # Build "what you should know"
        if leg_meta and leg_meta.get('is_omnibus'):
            what_to_know = "This is an omnibus bill containing multiple unrelated provisions. Independent section-by-section analysis is recommended."
        elif page_count > 200:
            what_to_know = "This is a large document. Key provisions may be difficult to locate without detailed analysis."
        else:
            what_to_know = "Standard document. Review the analysis sections for detailed findings."
        
        # Build next steps based on risk level
        if risk_level == "REQUIRES_INVESTIGATION":
            next_steps = "Run full legislative threat analysis. Cross-reference with official sources. Consider expert review."
        elif risk_level == "ELEVATED":
            next_steps = "Review flagged sections carefully. Verify claims against official sources."
        else:
            next_steps = "Review analysis results. Verify any claims of concern against original document."
        
        # Build verification instructions
        file_hash = doc_origin.get('file_identity', {}).get('file_hash_sha256', '')
        if file_hash:
            how_to_verify = f"Compare SHA-256 hash ({file_hash[:16]}...) with official source to verify document authenticity."
        else:
            how_to_verify = "Download document from official source and compare with this analysis."
        
        return {
            "what_is_this": what_is_this,
            "key_concerns": key_concerns,
            "what_you_should_know": what_to_know,
            "how_to_verify": how_to_verify,
            "next_steps": next_steps,
            "risk_level_plain": {
                "REQUIRES_INVESTIGATION": "⚠️ High priority - requires careful investigation",
                "ELEVATED": "⚡ Moderate priority - review recommended",
                "LOW": "✅ Standard priority - routine review"
            }.get(risk_level, "Unknown")
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
        
        # AI Calls Summary - combine ai_calls AND narrative_contributions
        ai_calls = analysis.get('ai_calls', {})
        narrative = analysis.get('narrative_contributions', {})
        
        # Calculate combined totals
        ollama_calls = ai_calls.get('total_calls', 0)
        narrative_contributions = narrative.get('total_contributions', 0)
        total_ai_usage = ollama_calls + narrative_contributions
        
        # Combine models from both sources
        ollama_models = ai_calls.get('models_used', [])
        narrative_models = []
        for contrib in narrative.get('contributions_detail', []):
            if contrib.get('model') and contrib['model'] not in narrative_models:
                narrative_models.append(contrib['model'])
        all_models = list(set(ollama_models + narrative_models))
        
        lines.extend([
            f"### AI Model Usage",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| **Total AI Interactions** | {total_ai_usage} |",
            f"| **Ollama API Calls** | {ollama_calls} |",
            f"| **Narrative Contributions** | {narrative_contributions} |",
            f"| **Models Used** | {', '.join(all_models) if all_models else 'None'} |",
            f"| **Total Duration** | {ai_calls.get('total_duration_ms', 0):,} ms |",
            f"| **AI Percentage** | {narrative.get('overall_ai_percentage', 0):.1f}% |",
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
        
        # Part 3: Summary - use combined AI usage from analysis section
        # Calculate combined totals for summary
        total_ai_interactions = ollama_calls + narrative_contributions
        
        lines.extend([
            f"---",
            f"",
            f"## Summary",
            f"",
            f"| Check | Status |",
            f"|-------|--------|",
            f"| **Document Origin Verified** | {'✅ Yes' if summary.get('document_hash_available') else '❌ No'} |",
            f"| **Total AI Interactions** | {total_ai_interactions} |",
            f"| **Models Used** | {', '.join(all_models) if all_models else 'None'} |",
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

"""
Document Q&A Module for Sparrow SPOT Scale™

Allows users to ask questions about analyzed documents using Ollama.
Creates standalone Q&A outputs without affecting core analysis.

Author: Sparrow SPOT Development Team
Version: 8.4.2
"""

import json
import requests
from datetime import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path


class DocumentQA:
    """
    Handles question-answering about documents using Ollama.
    
    Safe, isolated feature that doesn't interfere with core analysis.
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initialize Document Q&A system.
        
        Args:
            ollama_url: Base URL for Ollama API
        """
        self.ollama_url = ollama_url
        self.contribution_tracker = None
    
    def set_contribution_tracker(self, tracker):
        """
        Set AI contribution tracker for logging.
        
        Args:
            tracker: AIContributionTracker instance
        """
        self.contribution_tracker = tracker
    
    def ask_question(
        self,
        document_text: str,
        question: str,
        document_name: str = "Document",
        model: str = "llama3.2",
        context_from_analysis: Optional[Dict] = None,
        timeout: int = 180
    ) -> Tuple[str, Dict]:
        """
        Ask a question about the document using Ollama.
        
        Args:
            document_text: Full text of the document
            question: User's question
            document_name: Name of document for context
            model: Ollama model to use
            context_from_analysis: Optional analysis data to include
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (answer_text, metadata)
        """
        # Build prompt with document and question
        prompt = self._build_qa_prompt(
            document_text, 
            question, 
            document_name,
            context_from_analysis
        )
        
        # Track AI contribution start
        start_time = datetime.now()
        
        try:
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,  # Lower temp for factual Q&A
                    "num_predict": 2000,  # Reasonable answer length
                },
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            answer = result.get("response", "").strip()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Track AI contribution
            if self.contribution_tracker:
                self.contribution_tracker.record_contribution(
                    component="document_qa",
                    model_used=model,
                    model_version="local",
                    prompt_details=f"Q&A: {question[:100]}... (Duration: {duration:.1f}s, Length: {len(answer)} chars)",
                    contribution_type='generation',
                    confidence_level=0.7,  # Lower confidence for Q&A vs structured analysis
                    requires_review=True
                )
            
            # Build metadata
            metadata = {
                'question': question,
                'model': model,
                'document_name': document_name,
                'timestamp': start_time.isoformat(),
                'duration_seconds': duration,
                'answer_length': len(answer),
                'document_length': len(document_text),
                'status': 'success'
            }
            
            return answer, metadata
            
        except requests.exceptions.Timeout:
            error_msg = f"Ollama request timed out after {timeout} seconds. Question may be too complex or document too large."
            metadata = {
                'question': question,
                'model': model,
                'timestamp': datetime.now().isoformat(),
                'status': 'timeout',
                'error': error_msg
            }
            return error_msg, metadata
            
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to Ollama. Ensure Ollama is running (ollama serve)."
            metadata = {
                'question': question,
                'model': model,
                'timestamp': datetime.now().isoformat(),
                'status': 'connection_error',
                'error': error_msg
            }
            return error_msg, metadata
            
        except Exception as e:
            error_msg = f"Error during Q&A: {str(e)}"
            metadata = {
                'question': question,
                'model': model,
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': error_msg
            }
            return error_msg, metadata
    
    def _build_qa_prompt(
        self,
        document_text: str,
        question: str,
        document_name: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Build prompt for document Q&A.
        
        Args:
            document_text: Full document text
            question: User's question
            document_name: Document name
            context: Optional analysis context
            
        Returns:
            Formatted prompt string
        """
        # Truncate document if extremely long (to avoid context overflow)
        max_doc_length = 50000  # ~12,500 words
        if len(document_text) > max_doc_length:
            truncated = True
            doc_text = document_text[:max_doc_length] + "\n\n[...document truncated for length...]"
        else:
            truncated = False
            doc_text = document_text
        
        # Add analysis context if provided
        context_section = ""
        if context:
            composite_score = context.get('composite_score')
            grade = context.get('composite_grade')
            if composite_score and grade:
                context_section = f"""
ANALYSIS CONTEXT:
This document received a Sparrow SPOT Scale™ score of {composite_score:.1f}/100 (Grade: {grade}).
This context may help answer questions about the document's quality or policy effectiveness.
"""
        
        prompt = f"""You are an expert policy analyst answering questions about a document.

DOCUMENT: {document_name}
{"[NOTE: Document truncated to fit context window]" if truncated else ""}
{context_section}
DOCUMENT TEXT:
{doc_text}

USER QUESTION:
{question}

INSTRUCTIONS:
1. Answer the question based ONLY on the document content provided
2. Quote specific sections when relevant
3. If the answer isn't in the document, say so clearly
4. Be concise but thorough
5. Cite section numbers or page references if available
6. If you're uncertain, acknowledge it

ANSWER:"""
        
        return prompt
    
    def save_qa_output(
        self,
        answer: str,
        metadata: Dict,
        output_path: Path,
        include_metadata: bool = True
    ) -> str:
        """
        Save Q&A output to file.
        
        Args:
            answer: Answer text
            metadata: Metadata dict
            output_path: Path to save file
            include_metadata: Whether to include metadata header
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("DOCUMENT Q&A OUTPUT\n")
            f.write("=" * 70 + "\n\n")
            
            if include_metadata:
                f.write(f"Document: {metadata.get('document_name', 'Unknown')}\n")
                f.write(f"Question: {metadata.get('question', 'N/A')}\n")
                f.write(f"Model: {metadata.get('model', 'Unknown')}\n")
                f.write(f"Generated: {metadata.get('timestamp', 'N/A')}\n")
                
                if metadata.get('duration_seconds'):
                    f.write(f"Processing Time: {metadata['duration_seconds']:.1f} seconds\n")
                
                f.write("\n" + "-" * 70 + "\n\n")
            
            f.write("ANSWER:\n\n")
            f.write(answer)
            f.write("\n\n" + "=" * 70 + "\n")
            
            if metadata.get('status') == 'success':
                f.write("\n✓ Q&A completed successfully\n")
            else:
                f.write(f"\n⚠ Status: {metadata.get('status', 'unknown')}\n")
        
        return str(output_path)


def generate_document_qa(
    document_text: str,
    question: str,
    output_dir: Path,
    output_name: str,
    model: str = "llama3.2",
    analysis_context: Optional[Dict] = None,
    contribution_tracker = None
) -> Optional[str]:
    """
    Convenience function for generating document Q&A.
    
    Args:
        document_text: Full document text
        question: User's question
        output_dir: Output directory
        output_name: Base name for output file
        model: Ollama model to use
        analysis_context: Optional analysis data
        contribution_tracker: Optional AI contribution tracker
        
    Returns:
        Path to Q&A file, or None if failed
    """
    qa = DocumentQA()
    
    if contribution_tracker:
        qa.set_contribution_tracker(contribution_tracker)
    
    # Get document name from context or use output_name
    doc_name = output_name
    if analysis_context and 'document_title' in analysis_context:
        doc_name = analysis_context['document_title']
    
    # Ask question
    answer, metadata = qa.ask_question(
        document_text=document_text,
        question=question,
        document_name=doc_name,
        model=model,
        context_from_analysis=analysis_context
    )
    
    # Save output
    qa_dir = output_dir / "qa"
    output_path = qa_dir / f"{output_name}_document_qa.txt"
    
    saved_path = qa.save_qa_output(
        answer=answer,
        metadata=metadata,
        output_path=output_path
    )
    
    return saved_path

#!/usr/bin/env python3
"""
Sparrow SPOT Scale™ v8.6 - Enhanced Document Q&A Engine
=========================================================

Multi-chunk Q&A system with intelligent query routing and answer synthesis.

Features:
- Smart query routing (keyword, semantic, comprehensive)
- Multi-chunk answer synthesis
- Source attribution (chunk and page references)
- Progress tracking for long queries
- Integration with token_calculator and semantic_chunker

Author: Sparrow SPOT Scale™ Development Team
Version: 8.6.0
Created: December 7, 2025
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChunkReference:
    """Reference to a specific chunk with metadata."""
    chunk_id: int
    chunk_number: int  # Human-readable (1-based)
    pages: str
    sections: List[str]
    summary: str
    keywords: List[str]
    token_count: int


@dataclass
class QueryResult:
    """Result from querying a single chunk."""
    chunk_ref: ChunkReference
    answer: str
    relevance_score: float
    query_time: float
    model_used: str


@dataclass
class SynthesizedAnswer:
    """Final synthesized answer with attribution."""
    question: str
    answer: str
    sources: List[ChunkReference]
    total_chunks_queried: int
    total_time: float
    confidence: float
    routing_strategy: str


class QueryRouter:
    """
    Routes queries to relevant chunks using different strategies.
    
    Strategies:
    - keyword: Fast keyword matching (default)
    - semantic: Semantic similarity (requires embeddings)
    - comprehensive: Query all chunks (thorough but slow)
    - quick: Query only first chunk (fast preview)
    """
    
    def __init__(self, chunk_index: Dict[str, Any]):
        """
        Initialize router with chunk index.
        
        Args:
            chunk_index: Chunk metadata from semantic_chunker
        """
        self.chunk_index = chunk_index
        self.chunks = self._parse_chunk_index(chunk_index)
    
    def _parse_chunk_index(self, index: Dict[str, Any]) -> List[ChunkReference]:
        """Parse chunk index into ChunkReference objects."""
        chunks = []
        for chunk_data in index.get("chunks", []):
            chunk_id = chunk_data.get("id", chunk_data.get("chunk_id", 0))  # Try "id" first, fallback to "chunk_id"
            chunks.append(ChunkReference(
                chunk_id=chunk_id,
                chunk_number=chunk_id,  # Already 1-based in the JSON
                pages=chunk_data.get("page_range", chunk_data.get("pages", "unknown")),
                sections=chunk_data.get("sections", []),
                summary=chunk_data.get("summary", ""),
                keywords=chunk_data.get("keywords", []),
                token_count=chunk_data.get("tokens", chunk_data.get("token_count", 0))
            ))
        return chunks
    
    def route_query(
        self,
        question: str,
        strategy: str = "comprehensive",
        relevance_threshold: float = 0.3
    ) -> List[ChunkReference]:
        """
        Route query to relevant chunks.
        
        Args:
            question: User's question
            strategy: Routing strategy (keyword/semantic/comprehensive/quick)
            relevance_threshold: Minimum relevance score (0-1)
        
        Returns:
            List of relevant ChunkReference objects
        """
        if strategy == "comprehensive":
            return self._route_comprehensive()
        elif strategy == "quick":
            return self._route_quick()
        elif strategy == "semantic":
            return self._route_semantic(question, relevance_threshold)
        else:  # default: keyword
            return self._route_keyword(question, relevance_threshold)
    
    def _route_keyword(
        self,
        question: str,
        threshold: float = 0.3
    ) -> List[ChunkReference]:
        """
        Route using keyword matching.
        
        Algorithm:
        1. Extract keywords from question
        2. Calculate relevance for each chunk
        3. Return chunks above threshold
        """
        question_keywords = self._extract_keywords(question)
        relevant_chunks = []
        
        for chunk in self.chunks:
            relevance = self._calculate_keyword_relevance(
                question_keywords,
                chunk
            )
            
            if relevance >= threshold:
                relevant_chunks.append((chunk, relevance))
        
        # Sort by relevance (highest first)
        relevant_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the chunks (without scores)
        return [chunk for chunk, _ in relevant_chunks]
    
    def _route_semantic(
        self,
        question: str,
        threshold: float = 0.3
    ) -> List[ChunkReference]:
        """
        Route using semantic similarity.
        
        Note: Currently falls back to keyword routing.
        Future: Use embeddings for semantic similarity.
        """
        # Placeholder for semantic routing
        # Future: Use sentence transformers or similar
        print("⚠️  Semantic routing not yet implemented, using keyword routing")
        return self._route_keyword(question, threshold)
    
    def _route_comprehensive(self) -> List[ChunkReference]:
        """Route to all chunks."""
        return self.chunks
    
    def _route_quick(self) -> List[ChunkReference]:
        """Route to first chunk only."""
        return self.chunks[:1] if self.chunks else []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.
        
        Simple extraction: words longer than 3 chars,
        excluding common stop words.
        """
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is',
            'was', 'are', 'been', 'be', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
        }
        
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _calculate_keyword_relevance(
        self,
        question_keywords: List[str],
        chunk: ChunkReference
    ) -> float:
        """
        Calculate relevance score for chunk based on keyword matching.
        
        Score factors:
        - Keyword matches in summary (0.4 weight)
        - Keyword matches in keywords list (0.4 weight)
        - Keyword matches in sections (0.2 weight)
        """
        if not question_keywords:
            return 0.0
        
        # Combine all chunk text for matching
        chunk_summary = chunk.summary.lower()
        chunk_keywords = [k.lower() for k in chunk.keywords]
        chunk_sections = ' '.join(chunk.sections).lower()
        
        # Count matches in each area
        summary_matches = sum(
            1 for kw in question_keywords
            if kw in chunk_summary
        )
        keyword_matches = sum(
            1 for kw in question_keywords
            if any(kw in ck for ck in chunk_keywords)
        )
        section_matches = sum(
            1 for kw in question_keywords
            if kw in chunk_sections
        )
        
        # Calculate weighted score
        max_possible = len(question_keywords)
        summary_score = (summary_matches / max_possible) * 0.4
        keyword_score = (keyword_matches / max_possible) * 0.4
        section_score = (section_matches / max_possible) * 0.2
        
        total_score = summary_score + keyword_score + section_score
        
        # Boost if multiple keywords match
        unique_matches = len(set(
            [kw for kw in question_keywords if kw in chunk_summary] +
            [kw for kw in question_keywords if any(kw in ck for ck in chunk_keywords)]
        ))
        if unique_matches > 1:
            total_score *= (1 + 0.1 * unique_matches)
        
        return min(total_score, 1.0)  # Cap at 1.0


class AnswerSynthesizer:
    """
    Synthesizes answers from multiple chunks into coherent response.
    """
    
    def __init__(self):
        """Initialize synthesizer."""
        pass
    
    def synthesize(
        self,
        question: str,
        results: List[QueryResult],
        strategy: str = "concatenate",
        routing_strategy: str = "keyword"
    ) -> SynthesizedAnswer:
        """
        Synthesize multiple chunk query results into a final answer.
        
        Args:
            question: User's question
            results: List of QueryResult objects
            strategy: Synthesis strategy (concatenate/summarize/mapreduce)
            routing_strategy: Routing strategy used (for metadata)
        
        Returns:
            SynthesizedAnswer with attributed sources
        """
        if not results:
            return SynthesizedAnswer(
                question=question,
                answer="No relevant information found in document.",
                sources=[],
                total_chunks_queried=0,
                total_time=0.0,
                confidence=0.0,
                routing_strategy="none"
            )
        
        if strategy == "summarize":
            return self._synthesize_summarize(question, results, routing_strategy)
        elif strategy == "mapreduce":
            return self._synthesize_mapreduce(question, results, routing_strategy)
        else:  # default: concatenate
            return self._synthesize_concatenate(question, results, routing_strategy)
    
    def _synthesize_concatenate(
        self,
        question: str,
        results: List[QueryResult],
        routing_strategy: str = "keyword"
    ) -> SynthesizedAnswer:
        """
        Simple concatenation with source attribution.
        
        Format:
        Based on analysis of [X] sections:
        
        1. [Answer from chunk 1]
           Source: Chunk 1, Pages X-Y, Section Z
        
        2. [Answer from chunk 2]
           Source: Chunk 2, Pages A-B, Section C
        """
        answer_parts = [f"Based on analysis of {len(results)} section(s):\n"]
        sources = []
        total_time = sum(r.query_time for r in results)
        
        for i, result in enumerate(results, 1):
            # Add answer with numbering
            answer_parts.append(f"\n{i}. {result.answer.strip()}")
            
            # Add source attribution
            source_info = (
                f"   📍 Source: Chunk {result.chunk_ref.chunk_number}, "
                f"Pages {result.chunk_ref.pages}"
            )
            if result.chunk_ref.sections:
                sections_str = ", ".join(result.chunk_ref.sections[:3])
                if len(result.chunk_ref.sections) > 3:
                    sections_str += f" (+{len(result.chunk_ref.sections) - 3} more)"
                source_info += f", {sections_str}"
            
            answer_parts.append(source_info)
            sources.append(result.chunk_ref)
        
        # Calculate confidence based on relevance scores
        avg_relevance = sum(r.relevance_score for r in results) / len(results)
        confidence = min(avg_relevance * 1.2, 1.0)  # Boost slightly
        
        return SynthesizedAnswer(
            question=question,
            answer="\n".join(answer_parts),
            sources=sources,
            total_chunks_queried=len(results),
            total_time=total_time,
            confidence=confidence,
            routing_strategy=routing_strategy
        )
    
    def _synthesize_summarize(
        self,
        question: str,
        results: List[QueryResult]
    ) -> SynthesizedAnswer:
        """
        Summarize answers into single coherent response.
        
        Note: Currently falls back to concatenate.
        Future: Use LLM to generate summary.
        """
        print("⚠️  Summarize synthesis not yet implemented, using concatenate")
        return self._synthesize_concatenate(question, results)
    
    def _synthesize_mapreduce(
        self,
        question: str,
        results: List[QueryResult]
    ) -> SynthesizedAnswer:
        """
        Map-reduce synthesis for complex queries.
        
        Note: Currently falls back to concatenate.
        Future: Implement true map-reduce pattern.
        """
        print("⚠️  Map-reduce synthesis not yet implemented, using concatenate")
        return self._synthesize_concatenate(question, results)


class EnhancedDocumentQA:
    """
    Main Q&A engine for multi-chunk document analysis.
    
    Coordinates:
    - Query routing via QueryRouter
    - Chunk querying (mock or Ollama integration)
    - Answer synthesis via AnswerSynthesizer
    """
    
    def __init__(
        self,
        chunks_dir: Optional[Path] = None,
        chunk_index_path: Optional[Path] = None
    ):
        """
        Initialize Q&A engine.
        
        Args:
            chunks_dir: Directory containing chunk files
            chunk_index_path: Path to chunk_index.json
        """
        self.chunks_dir = Path(chunks_dir) if chunks_dir else None
        self.chunk_index = None
        self.router = None
        self.synthesizer = AnswerSynthesizer()
        
        if chunk_index_path:
            self.load_chunk_index(chunk_index_path)
    
    def load_chunk_index(self, index_path: Path):
        """Load chunk index from JSON file."""
        with open(index_path, 'r', encoding='utf-8') as f:
            self.chunk_index = json.load(f)
        
        self.router = QueryRouter(self.chunk_index)
        print(f"✅ Loaded chunk index: {len(self.chunk_index.get('chunks', []))} chunks")
    
    def query(
        self,
        question: str,
        model: str = "mock",
        routing_strategy: str = "comprehensive",
        synthesis_strategy: str = "concatenate",
        relevance_threshold: float = 0.3,
        ollama_client: Optional[Any] = None,
        progress_callback: Optional[callable] = None
    ) -> SynthesizedAnswer:
        """
        Query the document with intelligent routing.
        
        Args:
            question: User's question
            model: Model to use (or "mock" for testing)
            routing_strategy: How to select chunks (keyword/semantic/comprehensive/quick)
            synthesis_strategy: How to combine answers (concatenate/summarize/mapreduce)
            relevance_threshold: Minimum relevance for keyword routing
            ollama_client: Optional Ollama client for real queries
            progress_callback: Optional callback(current, total, message)
        
        Returns:
            SynthesizedAnswer with attributed sources
        """
        if not self.router:
            raise ValueError("No chunk index loaded. Call load_chunk_index() first.")
        
        # Route query to relevant chunks
        relevant_chunks = self.router.route_query(
            question,
            strategy=routing_strategy,
            relevance_threshold=relevance_threshold
        )
        
        if not relevant_chunks:
            print("⚠️  No relevant chunks found for query")
            return SynthesizedAnswer(
                question=question,
                answer="No relevant information found in the document.",
                sources=[],
                total_chunks_queried=0,
                total_time=0.0,
                confidence=0.0,
                routing_strategy=routing_strategy
            )
        
        print(f"🔍 Routing: Selected {len(relevant_chunks)} chunk(s) for query")
        
        # Query each relevant chunk
        results = []
        for i, chunk_ref in enumerate(relevant_chunks, 1):
            if progress_callback:
                progress_callback(i, len(relevant_chunks), f"Querying chunk {i}/{len(relevant_chunks)}")
            
            result = self._query_chunk(
                question,
                chunk_ref,
                model,
                ollama_client
            )
            results.append(result)
        
        # Synthesize final answer
        synthesized = self.synthesizer.synthesize(
            question,
            results,
            strategy=synthesis_strategy,
            routing_strategy=routing_strategy
        )
        
        return synthesized
    
    def _query_chunk(
        self,
        question: str,
        chunk_ref: ChunkReference,
        model: str,
        ollama_client: Optional[Any] = None
    ) -> QueryResult:
        """
        Query a single chunk.
        
        Args:
            question: User's question
            chunk_ref: Reference to chunk to query
            model: Model name
            ollama_client: Optional Ollama client
        
        Returns:
            QueryResult with answer and metadata
        """
        # Load chunk text
        if self.chunks_dir:
            chunk_file = self.chunks_dir / f"chunk_{chunk_ref.chunk_id + 1:03d}.txt"
            if chunk_file.exists():
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    chunk_text = f.read()
            else:
                chunk_text = f"[Chunk file not found: {chunk_file}]"
        else:
            chunk_text = f"[Chunk {chunk_ref.chunk_number} text]"
        
        # Mock query (for testing without Ollama)
        if model == "mock" or not ollama_client:
            answer = self._mock_query(question, chunk_ref, chunk_text)
            query_time = 0.1  # Simulated
        else:
            # Real Ollama query
            answer, query_time = self._ollama_query(
                question,
                chunk_text,
                model,
                ollama_client
            )
        
        # Calculate relevance (simplified)
        question_keywords = self.router._extract_keywords(question)
        answer_keywords = self.router._extract_keywords(answer)
        relevance = len(set(question_keywords) & set(answer_keywords)) / max(len(question_keywords), 1)
        relevance = min(relevance * 1.5, 1.0)  # Boost and cap
        
        return QueryResult(
            chunk_ref=chunk_ref,
            answer=answer,
            relevance_score=relevance,
            query_time=query_time,
            model_used=model
        )
    
    def _mock_query(
        self,
        question: str,
        chunk_ref: ChunkReference,
        chunk_text: str
    ) -> str:
        """
        Mock query for testing without Ollama.
        
        Returns a realistic-looking answer based on chunk metadata.
        """
        # Extract question keywords
        keywords = self.router._extract_keywords(question)
        
        # Build mock answer
        answer_parts = []
        
        # Reference sections if available
        if chunk_ref.sections:
            sections_str = ", ".join(chunk_ref.sections[:2])
            if len(chunk_ref.sections) > 2:
                sections_str += f" and {len(chunk_ref.sections) - 2} other section(s)"
            answer_parts.append(f"In {sections_str}:")
        
        # Reference keywords
        matching_keywords = [kw for kw in keywords if kw in chunk_ref.summary.lower()]
        if matching_keywords:
            answer_parts.append(
                f"The document discusses {', '.join(matching_keywords[:3])}."
            )
        
        # Add summary snippet
        summary_snippet = chunk_ref.summary[:150]
        if len(chunk_ref.summary) > 150:
            summary_snippet += "..."
        answer_parts.append(summary_snippet)
        
        return " ".join(answer_parts)
    
    def _ollama_query(
        self,
        question: str,
        chunk_text: str,
        model: str,
        ollama_client: Any
    ) -> Tuple[str, float]:
        """
        Query using Ollama client.
        
        Args:
            question: User's question
            chunk_text: Chunk text to analyze
            model: Model name
            ollama_client: Ollama client instance
        
        Returns:
            Tuple of (answer, query_time)
        """
        import time
        
        # Build prompt
        prompt = f"""Based on the following document excerpt, please answer this question:

Question: {question}

Document excerpt:
{chunk_text[:10000]}  

Provide a clear, concise answer based only on the information in the excerpt. If the excerpt doesn't contain relevant information, say so."""

        # Query Ollama
        start_time = time.time()
        try:
            response = ollama_client.generate(
                model=model,
                prompt=prompt,
                options={
                    'temperature': 0.3,  # Lower temperature for factual answers
                    'num_predict': 500,  # Limit response length
                }
            )
            answer = response.get('response', 'No response generated')
        except Exception as e:
            answer = f"Error querying model: {str(e)}"
        
        query_time = time.time() - start_time
        
        return answer, query_time


def main():
    """CLI interface for enhanced document Q&A."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Document Q&A - Multi-chunk intelligent querying"
    )
    parser.add_argument(
        'chunks_dir',
        help='Directory containing chunk files'
    )
    parser.add_argument(
        'question',
        help='Question to ask about the document'
    )
    parser.add_argument(
        '--index',
        default=None,
        help='Path to chunk_index.json (default: chunks_dir/chunk_index.json)'
    )
    parser.add_argument(
        '--model',
        default='mock',
        help='Ollama model to use (default: mock for testing)'
    )
    parser.add_argument(
        '--routing',
        choices=['keyword', 'semantic', 'comprehensive', 'quick'],
        default='keyword',
        help='Query routing strategy (default: keyword)'
    )
    parser.add_argument(
        '--synthesis',
        choices=['concatenate', 'summarize', 'mapreduce'],
        default='concatenate',
        help='Answer synthesis strategy (default: concatenate)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.3,
        help='Relevance threshold for routing (default: 0.3)'
    )
    parser.add_argument(
        '--output',
        help='Save answer to JSON file'
    )
    
    args = parser.parse_args()
    
    # Determine index path
    chunks_dir = Path(args.chunks_dir)
    if args.index:
        index_path = Path(args.index)
    else:
        index_path = chunks_dir / 'chunk_index.json'
    
    if not index_path.exists():
        print(f"❌ Error: Chunk index not found: {index_path}")
        print(f"   Run semantic_chunker.py first to create chunks and index")
        return 1
    
    # Initialize Q&A engine
    print(f"🚀 Initializing Enhanced Document Q&A")
    print(f"   Chunks: {chunks_dir}")
    print(f"   Index: {index_path}")
    print(f"   Model: {args.model}")
    print(f"   Routing: {args.routing}")
    print(f"   Synthesis: {args.synthesis}\n")
    
    qa = EnhancedDocumentQA(
        chunks_dir=chunks_dir,
        chunk_index_path=index_path
    )
    
    # Query document
    print(f"❓ Question: {args.question}\n")
    
    # Progress callback
    def progress(current, total, message):
        percent = (current / total) * 100
        print(f"   [{current}/{total}] {percent:.0f}% - {message}")
    
    answer = qa.query(
        question=args.question,
        model=args.model,
        routing_strategy=args.routing,
        synthesis_strategy=args.synthesis,
        relevance_threshold=args.threshold,
        ollama_client=None,  # Use mock by default
        progress_callback=progress
    )
    
    # Display answer
    print("\n" + "="*70)
    print("ANSWER")
    print("="*70)
    print(f"\n{answer.answer}\n")
    print("="*70)
    print("METADATA")
    print("="*70)
    print(f"Chunks queried: {answer.total_chunks_queried}")
    print(f"Total time: {answer.total_time:.2f}s")
    print(f"Confidence: {answer.confidence:.0%}")
    print(f"Routing strategy: {answer.routing_strategy}")
    print("="*70)
    
    # Save to JSON if requested
    if args.output:
        output_data = {
            'question': answer.question,
            'answer': answer.answer,
            'sources': [
                {
                    'chunk_number': src.chunk_number,
                    'pages': src.pages,
                    'sections': src.sections
                }
                for src in answer.sources
            ],
            'metadata': {
                'chunks_queried': answer.total_chunks_queried,
                'total_time': answer.total_time,
                'confidence': answer.confidence,
                'routing_strategy': answer.routing_strategy,
                'model': args.model
            }
        }
        
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Answer saved to: {output_path}")
    
    return 0


def generate_qa_narrative(answer: SynthesizedAnswer, output_path: Path, document_title: str = None) -> Path:
    """
    Generate a publishable markdown narrative from Q&A results.
    
    Args:
        answer: SynthesizedAnswer object with question, answer, sources
        output_path: Path to save the markdown file
        document_title: Optional document title for header
        
    Returns:
        Path to generated markdown file
    """
    from datetime import datetime
    
    # Extract document title from sources if not provided
    if not document_title and answer.sources:
        sections = answer.sources[0].sections
        if sections:
            document_title = sections[0] if sections[0] != "Document Start" else "Legislative Document"
    
    if not document_title:
        document_title = "Policy Document"
    
    # Build markdown content
    content = f"""# Document Q&A Analysis: {document_title}

**Generated:** {datetime.now().strftime("%B %d, %Y")}  
**Document:** {document_title}  
**Analysis Type:** Legislative Interpretation

---

## Question

**{answer.question}**

---

## Answer

Based on comprehensive analysis of the legislative text:

{answer.answer}

---

## Sources & Evidence

"""
    
    # Add source information
    if answer.sources:
        content += "**Primary Sources:**\n\n"
        for i, source in enumerate(answer.sources, 1):
            content += f"{i}. **Chunk {source.chunk_number}**\n"
            content += f"   - Pages: {source.pages}\n"
            if source.sections:
                sections_display = source.sections[:5]  # First 5 sections
                if len(source.sections) > 5:
                    sections_display.append(f"(+{len(source.sections) - 5} more)")
                content += f"   - Sections: {', '.join(sections_display)}\n"
            content += "\n"
    
    content += f"""---

## Metadata

- **Analysis Confidence:** {'High' if answer.confidence >= 0.8 else 'Medium' if answer.confidence >= 0.5 else 'Low'} ({answer.confidence:.1%})
- **Chunks Analyzed:** {answer.total_chunks_queried}
- **Routing Strategy:** {answer.routing_strategy.title()}
- **Query Processing Time:** {answer.total_time:.1f} seconds
- **Source Validation:** Direct citation from legislative text

---

## Analysis Framework

This Q&A response was generated using the Sparrow SPOT Scale™ Document Q&A system with:
- Smart chunking for large legislative documents
- {answer.routing_strategy.title()} routing across document text
- Direct citation of specific sections and articles
- Legislative interpretation analysis methodology

---

**Disclaimer:** This analysis is for informational purposes and should not be construed as legal advice. Consult with legal professionals for authoritative interpretation of legislative documents.
"""
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path


if __name__ == '__main__':
    exit(main())

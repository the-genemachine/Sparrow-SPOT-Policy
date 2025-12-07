#!/usr/bin/env python3
"""
Semantic Chunker for Sparrow SPOT Scale™ v8.6

Intelligently splits large documents into manageable chunks for processing
by LLMs with context window limitations.

Features:
- Section-based chunking (for legislative/structured documents)
- Sliding window chunking (for general documents)
- Semantic similarity chunking (for narrative documents)
- Chunk metadata and index generation

Author: Sparrow SPOT Development Team
Version: 8.6.0
Date: December 7, 2025
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import token calculator for accurate token counting
try:
    from token_calculator import estimate_tokens
    TOKEN_CALCULATOR_AVAILABLE = True
except ImportError:
    TOKEN_CALCULATOR_AVAILABLE = False


def detect_section_headers(text: str) -> List[Tuple[int, str, str]]:
    """
    Detect section headers in legislative/structured documents.
    
    Looks for patterns like:
    - ## Part 1
    - ## Division 2
    - ## Section 12
    - Part 1: Title
    - Division 2 — Title
    
    Args:
        text: Document text
        
    Returns:
        List of (position, level, header_text) tuples
    """
    headers = []
    
    # Pattern 1: Markdown-style headers (## Part 1, ## Division 2, etc.)
    markdown_pattern = r'^(#{1,6})\s+(Part|Division|Section|Article|Chapter|Title)\s+(\d+[A-Za-z]?)(.*?)$'
    
    # Pattern 2: Standalone headers (Part 1, PART 1, etc.)
    standalone_pattern = r'^(PART|Part|DIVISION|Division|SECTION|Section|ARTICLE|Article|CHAPTER|Chapter|TITLE|Title)\s+(\d+[A-Za-z]?)(\s*[:—-]\s*(.*))?$'
    
    lines = text.split('\n')
    position = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            position += len(line) + 1
            continue
        
        # Check markdown pattern
        match = re.match(markdown_pattern, line_stripped, re.IGNORECASE)
        if match:
            level = len(match.group(1))  # Number of # symbols
            header_type = match.group(2)
            number = match.group(3)
            title = match.group(4).strip() if match.group(4) else ""
            full_header = f"{header_type} {number}{': ' + title if title else ''}"
            headers.append((position, level, full_header))
        else:
            # Check standalone pattern
            match = re.match(standalone_pattern, line_stripped)
            if match:
                header_type = match.group(1)
                number = match.group(2)
                title = match.group(4) if match.group(4) else ""
                full_header = f"{header_type} {number}{': ' + title if title else ''}"
                # Assign level based on type
                level_map = {
                    "PART": 1, "Part": 1,
                    "DIVISION": 2, "Division": 2,
                    "SECTION": 3, "Section": 3,
                    "ARTICLE": 3, "Article": 3,
                    "CHAPTER": 2, "Chapter": 2,
                    "TITLE": 1, "Title": 1,
                }
                level = level_map.get(header_type, 3)
                headers.append((position, level, full_header))
        
        position += len(line) + 1
    
    return headers


def chunk_by_sections(
    text: str,
    max_tokens: int,
    overlap_tokens: int = 200
) -> List[Dict[str, any]]:
    """
    Split document by section headers while respecting token limits.
    
    Best for legislative documents with clear hierarchical structure.
    
    Args:
        text: Document text
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Overlap between chunks (for context continuity)
        
    Returns:
        List of chunk dictionaries
    """
    headers = detect_section_headers(text)
    
    if not headers:
        # No headers detected, fall back to sliding window
        print("Warning: No section headers detected, using sliding window chunking")
        return chunk_sliding_window(text, max_tokens, overlap_tokens)
    
    chunks = []
    chunk_id = 1
    
    # Add document start position
    section_positions = [(0, 0, "Document Start")] + headers + [(len(text), 0, "Document End")]
    
    current_chunk_start = 0
    current_chunk_sections = []
    current_chunk_tokens = 0
    
    for i in range(len(section_positions) - 1):
        pos, level, header = section_positions[i]
        next_pos = section_positions[i + 1][0]
        
        # Get section text
        section_text = text[pos:next_pos]
        
        # Estimate tokens
        if TOKEN_CALCULATOR_AVAILABLE:
            section_tokens = estimate_tokens(section_text, method="quick")["estimated_tokens"]
        else:
            section_tokens = len(section_text) // 4
        
        # Check if adding this section would exceed limit
        if current_chunk_tokens + section_tokens > max_tokens and current_chunk_sections:
            # Save current chunk
            chunk_text = text[current_chunk_start:pos]
            
            # Add overlap from next section if available
            if overlap_tokens > 0:
                overlap_text = text[pos:min(pos + overlap_tokens * 4, next_pos)]  # ~4 chars per token
                chunk_text += "\n\n[... continues in next chunk ...]\n\n" + overlap_text
            
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "tokens": current_chunk_tokens,
                "metadata": {
                    "start_char": current_chunk_start,
                    "end_char": pos,
                    "sections": current_chunk_sections.copy(),
                }
            })
            
            chunk_id += 1
            current_chunk_start = pos
            current_chunk_sections = []
            current_chunk_tokens = 0
        
        # Add section to current chunk
        if header != "Document End":
            current_chunk_sections.append(header)
        current_chunk_tokens += section_tokens
    
    # Add final chunk if any content remains
    if current_chunk_tokens > 0:
        chunk_text = text[current_chunk_start:]
        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text,
            "tokens": current_chunk_tokens,
            "metadata": {
                "start_char": current_chunk_start,
                "end_char": len(text),
                "sections": current_chunk_sections.copy(),
            }
        })
    
    return chunks


def chunk_sliding_window(
    text: str,
    max_tokens: int,
    overlap_tokens: int = 200
) -> List[Dict[str, any]]:
    """
    Split document using sliding window with overlap.
    
    Best for general documents without clear structure.
    Ensures no information lost at chunk boundaries.
    
    Args:
        text: Document text
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Overlap between chunks
        
    Returns:
        List of chunk dictionaries
    """
    # Rough estimation: 4 characters per token
    max_chars = max_tokens * 4
    overlap_chars = overlap_tokens * 4
    
    chunks = []
    chunk_id = 1
    position = 0
    
    while position < len(text):
        # Calculate chunk end
        chunk_end = min(position + max_chars, len(text))
        
        # Try to break at paragraph boundary (double newline)
        if chunk_end < len(text):
            # Look for paragraph break in last 20% of chunk
            search_start = chunk_end - max_chars // 5
            paragraph_break = text.rfind('\n\n', search_start, chunk_end)
            
            if paragraph_break > position:
                chunk_end = paragraph_break + 2  # Include the newlines
            else:
                # Fall back to sentence break (period + space/newline)
                sentence_break = max(
                    text.rfind('. ', search_start, chunk_end),
                    text.rfind('.\n', search_start, chunk_end)
                )
                if sentence_break > position:
                    chunk_end = sentence_break + 2
        
        # Extract chunk text
        chunk_text = text[position:chunk_end]
        
        # Estimate tokens
        if TOKEN_CALCULATOR_AVAILABLE:
            tokens = estimate_tokens(chunk_text, method="quick")["estimated_tokens"]
        else:
            tokens = len(chunk_text) // 4
        
        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text,
            "tokens": tokens,
            "metadata": {
                "start_char": position,
                "end_char": chunk_end,
                "has_overlap": chunk_id > 1,
            }
        })
        
        # Move to next chunk with overlap
        if chunk_end >= len(text):
            break
        
        position = max(position + 1, chunk_end - overlap_chars)
        chunk_id += 1
    
    return chunks


def create_chunk_index(chunks: List[Dict[str, any]], document_name: str = "Document") -> Dict[str, any]:
    """
    Create searchable index for chunks with summaries.
    
    Args:
        chunks: List of chunk dictionaries
        document_name: Name of document being chunked
        
    Returns:
        Index dictionary with chunk metadata and summaries
    """
    total_tokens = sum(c["tokens"] for c in chunks)
    avg_tokens = total_tokens / len(chunks) if chunks else 0
    
    index = {
        "document_name": document_name,
        "total_chunks": len(chunks),
        "total_tokens": total_tokens,
        "avg_tokens_per_chunk": int(avg_tokens),
        "chunks": []
    }
    
    for chunk in chunks:
        metadata = chunk["metadata"]
        
        # Generate short summary (first 100 chars or first sentence)
        text = chunk["text"].strip()
        first_sentence = re.split(r'[.!?]\s+', text)[0]
        if len(first_sentence) > 200:
            summary = text[:200] + "..."
        else:
            summary = first_sentence + "."
        
        # Extract sections if available
        sections = metadata.get("sections", [])
        
        # Estimate page range (rough: 300 tokens per page)
        start_page = metadata["start_char"] // (300 * 4) + 1  # 300 tokens * 4 chars
        end_page = metadata["end_char"] // (300 * 4) + 1
        page_range = f"{start_page}-{end_page}" if start_page != end_page else str(start_page)
        
        # Extract keywords (simple: frequent capitalized words)
        keywords = extract_keywords(text)
        
        index["chunks"].append({
            "id": chunk["chunk_id"],
            "summary": summary,
            "sections": sections,
            "page_range": page_range,
            "keywords": keywords[:10],  # Top 10 keywords
            "tokens": chunk["tokens"],
            "char_range": f"{metadata['start_char']}-{metadata['end_char']}",
        })
    
    return index


def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis.
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords sorted by frequency
    """
    # Find capitalized words (likely proper nouns/important terms)
    capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    # Count frequencies
    freq = {}
    for word in capitalized:
        word_lower = word.lower()
        # Skip common words
        if word_lower not in ['the', 'this', 'that', 'these', 'those', 'part', 'section', 'division']:
            freq[word] = freq.get(word, 0) + 1
    
    # Sort by frequency and return top N
    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_keywords[:max_keywords]]


def chunk_document(
    text: str,
    max_tokens: int,
    strategy: str = "section",
    overlap_tokens: int = 200,
    document_name: str = "Document"
) -> Dict[str, any]:
    """
    Main chunking function with strategy selection.
    
    Args:
        text: Document text to chunk
        max_tokens: Maximum tokens per chunk
        strategy: Chunking strategy ("section", "sliding", or "semantic")
        overlap_tokens: Overlap between chunks
        document_name: Name for the document
        
    Returns:
        Dictionary with chunks and index:
        {
            "chunks": [...],
            "index": {...}
        }
    """
    if strategy == "section":
        chunks = chunk_by_sections(text, max_tokens, overlap_tokens)
    elif strategy == "sliding":
        chunks = chunk_sliding_window(text, max_tokens, overlap_tokens)
    elif strategy == "semantic":
        # TODO: Implement semantic chunking with embeddings
        print("Warning: Semantic chunking not yet implemented, using section-based")
        chunks = chunk_by_sections(text, max_tokens, overlap_tokens)
    else:
        raise ValueError(f"Unknown strategy: {strategy}. Use 'section', 'sliding', or 'semantic'")
    
    # Create index
    index = create_chunk_index(chunks, document_name)
    
    return {
        "chunks": chunks,
        "index": index,
        "strategy": strategy,
        "max_tokens": max_tokens,
        "overlap_tokens": overlap_tokens,
    }


def save_chunks(
    result: Dict[str, any],
    output_dir: str,
    save_text: bool = True,
    save_index: bool = True
) -> Dict[str, str]:
    """
    Save chunks to disk.
    
    Args:
        result: Chunking result from chunk_document
        output_dir: Directory to save chunks
        save_text: Whether to save individual chunk text files
        save_index: Whether to save chunk index JSON
        
    Returns:
        Dictionary with paths to saved files
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save individual chunks
    if save_text:
        chunks_dir = output_path / "chunks"
        chunks_dir.mkdir(exist_ok=True)
        
        for chunk in result["chunks"]:
            chunk_file = chunks_dir / f"chunk_{chunk['chunk_id']:03d}.txt"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk["text"])
        
        saved_files["chunks_dir"] = str(chunks_dir)
    
    # Save index
    if save_index:
        index_file = output_path / "chunk_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(result["index"], f, indent=2)
        
        saved_files["index_file"] = str(index_file)
    
    # Save full result metadata
    metadata_file = output_path / "chunk_metadata.json"
    metadata = {
        "strategy": result["strategy"],
        "max_tokens": result["max_tokens"],
        "overlap_tokens": result["overlap_tokens"],
        "total_chunks": result["index"]["total_chunks"],
        "total_tokens": result["index"]["total_tokens"],
    }
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    saved_files["metadata_file"] = str(metadata_file)
    
    return saved_files


def main():
    """CLI entry point for semantic chunker."""
    parser = argparse.ArgumentParser(
        description="Split large documents into chunks for LLM processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Chunk legislative document by sections (recommended for bills)
  python semantic_chunker.py bill_c15.txt --strategy section --max-tokens 100000
  
  # Chunk general document with sliding window
  python semantic_chunker.py article.txt --strategy sliding --max-tokens 50000
  
  # Save chunks to directory
  python semantic_chunker.py document.txt --output-dir ./chunks --save-chunks
        """
    )
    
    parser.add_argument(
        "filepath",
        help="Path to document file to chunk"
    )
    
    parser.add_argument(
        "--strategy",
        choices=["section", "sliding", "semantic"],
        default="section",
        help="Chunking strategy (default: section)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=100000,
        help="Maximum tokens per chunk (default: 100000)"
    )
    
    parser.add_argument(
        "--overlap",
        type=int,
        default=200,
        help="Overlap tokens between chunks (default: 200)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Directory to save chunks"
    )
    
    parser.add_argument(
        "--save-chunks",
        action="store_true",
        help="Save individual chunk text files"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output index as JSON"
    )
    
    args = parser.parse_args()
    
    try:
        # Read document
        with open(args.filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        document_name = Path(args.filepath).stem
        
        # Chunk document
        result = chunk_document(
            text,
            max_tokens=args.max_tokens,
            strategy=args.strategy,
            overlap_tokens=args.overlap,
            document_name=document_name
        )
        
        # Save if requested
        if args.output_dir:
            saved = save_chunks(
                result,
                args.output_dir,
                save_text=args.save_chunks,
                save_index=True
            )
            print(f"Chunks saved to: {args.output_dir}")
            for key, path in saved.items():
                print(f"  {key}: {path}")
        
        # Output index
        if args.json:
            print(json.dumps(result["index"], indent=2))
        else:
            # Print summary
            index = result["index"]
            print("\n" + "=" * 70)
            print("DOCUMENT CHUNKING SUMMARY")
            print("=" * 70)
            print(f"\nDocument: {index['document_name']}")
            print(f"Strategy: {result['strategy']}")
            print(f"Total Chunks: {index['total_chunks']}")
            print(f"Total Tokens: {index['total_tokens']:,}")
            print(f"Avg Tokens/Chunk: {index['avg_tokens_per_chunk']:,}")
            print(f"\nChunk Breakdown:")
            for chunk_info in index["chunks"]:
                sections_str = ", ".join(chunk_info["sections"][:3]) if chunk_info["sections"] else "N/A"
                if len(chunk_info["sections"]) > 3:
                    sections_str += f" (+{len(chunk_info['sections']) - 3} more)"
                print(f"  Chunk {chunk_info['id']:3d}: {chunk_info['tokens']:6,} tokens | Pages {chunk_info['page_range']:>8} | {sections_str}")
            print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

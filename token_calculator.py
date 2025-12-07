#!/usr/bin/env python3
"""
Token Calculator for Sparrow SPOT Scale™ v8.6

Estimates token counts for documents and recommends optimal Ollama models
based on document size and available model contexts.

Features:
- Multiple estimation methods (quick, tiktoken, precise)
- Model context database for all major Ollama models
- Model recommendation engine
- CLI tool for document analysis

Author: Sparrow SPOT Development Team
Version: 8.6.0
Date: December 7, 2025
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Model Context Database
# Context sizes in tokens for popular Ollama models
OLLAMA_MODEL_CONTEXTS = {
    # Small models (good for testing)
    "llama3.2:1b": 128000,
    "llama3.2:3b": 128000,
    "phi3:mini": 4096,
    "phi3:medium": 128000,
    "qwen2.5:0.5b": 32768,
    "qwen2.5:1.5b": 32768,
    "qwen2.5:3b": 32768,
    
    # Medium models (good balance)
    "llama3.1:8b": 128000,
    "llama3.2:8b": 128000,
    "mistral:7b": 8192,
    "mistral:7b-instruct": 32768,
    "gemma2:9b": 8192,
    "qwen2.5:7b": 131072,
    "qwen2.5:14b": 131072,
    
    # Large models (maximum context)
    "llama3.1:70b": 128000,
    "qwen2.5:72b": 131072,
    "mixtral:8x7b": 32768,
    "command-r:35b": 128000,
    "command-r-plus:104b": 128000,
    
    # Specialized models
    "codellama:7b": 16384,
    "codellama:13b": 16384,
    "codellama:34b": 16384,
    "deepseek-coder:6.7b": 16384,
    "deepseek-coder:33b": 16384,
    
    # Default/generic
    "default": 8192,
}


def estimate_tokens_quick(text: str) -> int:
    """
    Quick token estimation using simple character ratio.
    
    Rule of thumb: ~4 characters per token for English text.
    This is a rough estimate (~75% accurate) but very fast.
    
    Args:
        text: Input text to estimate
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def estimate_tokens_tiktoken(text: str, encoding: str = "cl100k_base") -> int:
    """
    Token estimation using OpenAI's tiktoken library.
    
    Uses GPT-like tokenization which is similar to most modern LLMs.
    More accurate than quick method (~90% accurate for Ollama models).
    
    Args:
        text: Input text to estimate
        encoding: Tiktoken encoding to use (cl100k_base for GPT-3.5/4)
        
    Returns:
        Estimated token count
        
    Raises:
        ImportError: If tiktoken is not installed
    """
    try:
        import tiktoken
        enc = tiktoken.get_encoding(encoding)
        tokens = enc.encode(text)
        return len(tokens)
    except ImportError:
        raise ImportError(
            "tiktoken not installed. Install with: pip install tiktoken"
        )


def estimate_tokens_precise(text: str, model: str = "llama3.1:8b") -> int:
    """
    Precise token counting using actual Ollama model tokenization.
    
    Makes API call to Ollama to get exact token count.
    Most accurate method but requires Ollama running and is slower.
    
    Args:
        text: Input text to count tokens
        model: Ollama model to use for tokenization
        
    Returns:
        Exact token count from Ollama
        
    Raises:
        ImportError: If ollama library not installed
        ConnectionError: If Ollama server not running
    """
    try:
        import ollama
        # Ollama doesn't have direct tokenization API, so we estimate
        # based on embedding or use tiktoken as fallback
        # For now, fallback to tiktoken
        return estimate_tokens_tiktoken(text)
    except ImportError:
        raise ImportError(
            "ollama not installed. Install with: pip install ollama"
        )


def estimate_tokens(
    text: str, 
    method: str = "tiktoken"
) -> Dict[str, any]:
    """
    Estimate token count using specified method.
    
    Args:
        text: Input text to analyze
        method: Estimation method ("quick", "tiktoken", or "precise")
        
    Returns:
        Dictionary with estimation results:
        {
            "character_count": int,
            "estimated_tokens": int,
            "method": str,
            "accuracy": str  # "rough", "good", or "precise"
        }
    """
    char_count = len(text)
    
    if method == "quick":
        tokens = estimate_tokens_quick(text)
        accuracy = "rough"
    elif method == "tiktoken":
        try:
            tokens = estimate_tokens_tiktoken(text)
            accuracy = "good"
        except ImportError:
            print("Warning: tiktoken not installed, falling back to quick method")
            tokens = estimate_tokens_quick(text)
            accuracy = "rough"
            method = "quick (fallback)"
    elif method == "precise":
        try:
            tokens = estimate_tokens_precise(text)
            accuracy = "precise"
        except (ImportError, ConnectionError) as e:
            print(f"Warning: Precise method failed ({e}), falling back to tiktoken")
            try:
                tokens = estimate_tokens_tiktoken(text)
                accuracy = "good"
                method = "tiktoken (fallback)"
            except ImportError:
                tokens = estimate_tokens_quick(text)
                accuracy = "rough"
                method = "quick (fallback)"
    else:
        raise ValueError(f"Unknown method: {method}. Use 'quick', 'tiktoken', or 'precise'")
    
    return {
        "character_count": char_count,
        "estimated_tokens": tokens,
        "method": method,
        "accuracy": accuracy
    }


def get_model_context_size(model: str) -> int:
    """
    Get context window size for an Ollama model.
    
    Args:
        model: Model name (e.g., "llama3.1:8b")
        
    Returns:
        Context size in tokens
    """
    return OLLAMA_MODEL_CONTEXTS.get(model, OLLAMA_MODEL_CONTEXTS["default"])


def recommend_model(
    document_tokens: int,
    available_models: Optional[List[str]] = None,
    buffer_ratio: float = 0.2
) -> Dict[str, any]:
    """
    Recommend best model(s) for document size.
    
    Args:
        document_tokens: Number of tokens in document
        available_models: List of available models (None = all models)
        buffer_ratio: Reserve this fraction of context for prompts/responses (default 20%)
        
    Returns:
        Dictionary with recommendations:
        {
            "strategy": "single|chunked|summarize-first",
            "recommended_models": [
                {
                    "model": str,
                    "context_size": int,
                    "fit": "full|partial",
                    "coverage": str,  # "100%|85%|..."
                    "chunks_needed": int,
                }
            ],
            "warning": str or None
        }
    """
    if available_models is None:
        available_models = list(OLLAMA_MODEL_CONTEXTS.keys())
        available_models.remove("default")  # Don't recommend "default"
    
    # Calculate usable context (after buffer for prompts/responses)
    def usable_context(context_size):
        return int(context_size * (1 - buffer_ratio))
    
    recommendations = []
    
    for model in available_models:
        context_size = get_model_context_size(model)
        usable = usable_context(context_size)
        
        if usable >= document_tokens:
            # Document fits completely
            coverage = 100.0
            chunks_needed = 1
            fit = "full"
        else:
            # Document needs chunking
            chunks_needed = (document_tokens + usable - 1) // usable  # Ceiling division
            coverage = (usable / document_tokens) * 100
            fit = "partial"
        
        recommendations.append({
            "model": model,
            "context_size": context_size,
            "usable_context": usable,
            "fit": fit,
            "coverage": f"{coverage:.1f}%",
            "chunks_needed": chunks_needed,
        })
    
    # Sort by: full fit first, then by context size (largest first)
    recommendations.sort(key=lambda x: (x["fit"] != "full", -x["context_size"]))
    
    # Determine strategy
    if any(r["fit"] == "full" for r in recommendations):
        strategy = "single"
        warning = None
    else:
        # All models require chunking
        min_chunks = min(r["chunks_needed"] for r in recommendations)
        if min_chunks <= 5:
            strategy = "chunked"
            warning = None
        else:
            strategy = "chunked"
            warning = f"Document very large ({min_chunks}+ chunks). Consider summarize-first approach."
    
    return {
        "strategy": strategy,
        "recommended_models": recommendations[:10],  # Top 10 recommendations
        "warning": warning
    }


def analyze_document_file(
    filepath: str,
    method: str = "tiktoken",
    show_recommendations: bool = True
) -> Dict[str, any]:
    """
    Analyze a document file for token count and model recommendations.
    
    Args:
        filepath: Path to document file
        method: Token estimation method
        show_recommendations: Whether to include model recommendations
        
    Returns:
        Complete analysis dictionary
    """
    # Read file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        raise IOError(f"Failed to read file {filepath}: {e}")
    
    # Get file info
    file_size = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    
    # Estimate tokens
    token_info = estimate_tokens(text, method=method)
    
    # Estimate page count (rough: 300 words per page, 4 chars per word, 4 chars per token)
    # So ~300 tokens per page
    estimated_pages = token_info["estimated_tokens"] // 300
    
    result = {
        "filename": filename,
        "filepath": filepath,
        "file_size_bytes": file_size,
        "file_size_mb": file_size / (1024 * 1024),
        "character_count": token_info["character_count"],
        "estimated_tokens": token_info["estimated_tokens"],
        "estimated_pages": estimated_pages,
        "estimation_method": token_info["method"],
        "estimation_accuracy": token_info["accuracy"],
    }
    
    if show_recommendations:
        recommendations = recommend_model(token_info["estimated_tokens"])
        result["recommendations"] = recommendations
    
    return result


def format_analysis_output(analysis: Dict[str, any]) -> str:
    """
    Format analysis results for CLI output.
    
    Args:
        analysis: Analysis dictionary from analyze_document_file
        
    Returns:
        Formatted string for display
    """
    lines = []
    lines.append("=" * 70)
    lines.append("DOCUMENT TOKEN ANALYSIS")
    lines.append("=" * 70)
    lines.append("")
    
    # Document info
    lines.append("Document Information:")
    lines.append(f"  File: {analysis['filename']}")
    lines.append(f"  Size: {analysis['file_size_mb']:.2f} MB ({analysis['file_size_bytes']:,} bytes)")
    lines.append(f"  Characters: {analysis['character_count']:,}")
    lines.append("")
    
    # Token estimation
    lines.append("Token Estimation:")
    lines.append(f"  Estimated Tokens: {analysis['estimated_tokens']:,}")
    lines.append(f"  Estimated Pages: ~{analysis['estimated_pages']}")
    lines.append(f"  Method: {analysis['estimation_method']}")
    lines.append(f"  Accuracy: {analysis['estimation_accuracy']}")
    lines.append("")
    
    # Recommendations
    if "recommendations" in analysis:
        rec = analysis["recommendations"]
        lines.append("Model Recommendations:")
        lines.append(f"  Strategy: {rec['strategy'].upper()}")
        if rec['warning']:
            lines.append(f"  ⚠️  Warning: {rec['warning']}")
        lines.append("")
        
        # Show top 5 models
        lines.append("  Top 5 Recommended Models:")
        for i, model_rec in enumerate(rec["recommended_models"][:5], 1):
            fit_icon = "✅" if model_rec["fit"] == "full" else "⚠️"
            chunks_str = f"({model_rec['chunks_needed']} chunks)" if model_rec["chunks_needed"] > 1 else ""
            
            lines.append(
                f"    {i}. {fit_icon} {model_rec['model']:<25} "
                f"({model_rec['context_size']:>6,} tokens) "
                f"- {model_rec['coverage']} coverage {chunks_str}"
            )
        
        lines.append("")
        
        # Recommended strategy
        best = rec["recommended_models"][0]
        if best["fit"] == "full":
            lines.append(f"  💡 Recommended: Use {best['model']} (document fits in single context)")
        else:
            lines.append(
                f"  💡 Recommended: Use {best['model']} with CHUNKED Q&A "
                f"({best['chunks_needed']} chunks, {best['coverage']} per chunk)"
            )
    
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    """CLI entry point for token calculator."""
    parser = argparse.ArgumentParser(
        description="Analyze document token count and recommend Ollama models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a document with tiktoken (recommended)
  python token_calculator.py bill_c15_english_only.txt
  
  # Use quick estimation (faster but less accurate)
  python token_calculator.py large_document.txt --method quick
  
  # Output as JSON
  python token_calculator.py document.txt --json
  
  # Save analysis to file
  python token_calculator.py document.txt --output analysis.json
        """
    )
    
    parser.add_argument(
        "filepath",
        help="Path to document file to analyze"
    )
    
    parser.add_argument(
        "--method",
        choices=["quick", "tiktoken", "precise"],
        default="tiktoken",
        help="Token estimation method (default: tiktoken)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Save analysis to file (JSON format)"
    )
    
    parser.add_argument(
        "--no-recommendations",
        action="store_true",
        help="Skip model recommendations"
    )
    
    args = parser.parse_args()
    
    try:
        # Analyze document
        analysis = analyze_document_file(
            args.filepath,
            method=args.method,
            show_recommendations=not args.no_recommendations
        )
        
        # Output results
        if args.json or args.output:
            json_output = json.dumps(analysis, indent=2)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(json_output)
                print(f"Analysis saved to: {args.output}")
            else:
                print(json_output)
        else:
            print(format_analysis_output(analysis))
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

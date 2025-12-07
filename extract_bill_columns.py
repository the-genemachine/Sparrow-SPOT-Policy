#!/usr/bin/env python3
"""
Extract Bill C-15 PDF with proper column detection.
Separates English (left column) from French (right column).
"""

import pdfplumber
import argparse
from pathlib import Path
import re


def extract_english_column(pdf_path: str, output_path: str):
    """
    Extract only the English (left) column from a two-column bilingual PDF.
    
    Args:
        pdf_path: Path to input PDF
        output_path: Path to output text file
    """
    print(f"📄 Extracting English column from: {pdf_path}")
    
    english_text = []
    page_count = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"   Total pages: {total_pages}")
        
        for page_num, page in enumerate(pdf.pages, 1):
            # Get page dimensions
            page_width = page.width
            page_height = page.height
            
            # Define left column boundary (approximately left half)
            # Adjust margins to avoid page numbers and artifacts
            left_column_bbox = (
                30,              # left margin
                50,              # top margin
                page_width / 2 - 20,  # right edge of left column (leave gap)
                page_height - 50      # bottom margin
            )
            
            # Crop to left column only
            left_column = page.crop(left_column_bbox)
            
            # Extract text from left column
            text = left_column.extract_text()
            
            if text:
                # Clean up extracted text
                text = clean_extracted_text(text)
                english_text.append(text)
                page_count += 1
                
                if page_num % 50 == 0:
                    print(f"   Processed {page_num}/{total_pages} pages...")
    
    # Join all pages
    full_text = "\n\n".join(english_text)
    
    # Save to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"✅ Extracted {page_count} pages")
    print(f"   Total characters: {len(full_text):,}")
    print(f"   Saved to: {output_path}")
    
    return full_text


def clean_extracted_text(text: str) -> str:
    """
    Clean up extracted text to remove artifacts.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Remove standalone page numbers
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove excessive spaces
    text = re.sub(r' {3,}', '  ', text)
    
    # Remove form feed characters
    text = text.replace('\f', '\n')
    
    return text.strip()


def extract_both_columns(pdf_path: str, output_english: str, output_french: str):
    """
    Extract both English and French columns separately.
    
    Args:
        pdf_path: Path to input PDF
        output_english: Path for English text output
        output_french: Path for French text output
    """
    print(f"📄 Extracting both columns from: {pdf_path}")
    
    english_text = []
    french_text = []
    page_count = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"   Total pages: {total_pages}")
        
        for page_num, page in enumerate(pdf.pages, 1):
            page_width = page.width
            page_height = page.height
            
            # Define left column (English)
            left_bbox = (
                30,
                50,
                page_width / 2 - 20,
                page_height - 50
            )
            
            # Define right column (French)
            right_bbox = (
                page_width / 2 + 20,
                50,
                page_width - 30,
                page_height - 50
            )
            
            # Extract both columns
            left_text = page.crop(left_bbox).extract_text()
            right_text = page.crop(right_bbox).extract_text()
            
            if left_text:
                english_text.append(clean_extracted_text(left_text))
            if right_text:
                french_text.append(clean_extracted_text(right_text))
            
            page_count += 1
            
            if page_num % 50 == 0:
                print(f"   Processed {page_num}/{total_pages} pages...")
    
    # Save English
    english_full = "\n\n".join(english_text)
    Path(output_english).parent.mkdir(parents=True, exist_ok=True)
    with open(output_english, 'w', encoding='utf-8') as f:
        f.write(english_full)
    
    # Save French
    french_full = "\n\n".join(french_text)
    Path(output_french).parent.mkdir(parents=True, exist_ok=True)
    with open(output_french, 'w', encoding='utf-8') as f:
        f.write(french_full)
    
    print(f"✅ Extracted {page_count} pages")
    print(f"   English: {len(english_full):,} characters → {output_english}")
    print(f"   French: {len(french_full):,} characters → {output_french}")
    
    return english_full, french_full


def main():
    parser = argparse.ArgumentParser(
        description="Extract Bill C-15 with proper column separation"
    )
    parser.add_argument(
        'pdf_path',
        help="Path to Bill C-15 PDF file"
    )
    parser.add_argument(
        '--output-english',
        '-e',
        default='bill_c15_english.txt',
        help="Output path for English text (default: bill_c15_english.txt)"
    )
    parser.add_argument(
        '--output-french',
        '-f',
        help="Output path for French text (optional, extracts both if provided)"
    )
    parser.add_argument(
        '--both',
        action='store_true',
        help="Extract both columns to separate files"
    )
    
    args = parser.parse_args()
    
    # Check if PDF exists
    if not Path(args.pdf_path).exists():
        print(f"❌ Error: PDF file not found: {args.pdf_path}")
        return 1
    
    try:
        if args.both or args.output_french:
            # Extract both columns
            french_output = args.output_french or args.output_english.replace('.txt', '_french.txt')
            extract_both_columns(args.pdf_path, args.output_english, french_output)
        else:
            # Extract English only
            extract_english_column(args.pdf_path, args.output_english)
        
        print("\n✅ Extraction complete!")
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

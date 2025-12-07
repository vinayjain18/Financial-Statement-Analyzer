"""
PDF Extraction Service
Uses pdfplumber as primary extractor with pymupdf4llm as fallback.
Text extraction only - tables are parsed from text by LLM.
Optimizes extracted text by filtering redundant headers/footers from middle pages.
"""

import logging
import re
import pdfplumber
from typing import Dict, Any, List

# Setup logging
logger = logging.getLogger('pdf_extractor')

# Regex patterns for identifying transaction lines
# Universal date pattern - matches DD/MM/YY, DD-MM-YYYY, etc.
DATE_PATTERN = re.compile(r'\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}')
# Amount pattern - matches amounts like 1,234.56 or 1,23,456.78
AMOUNT_PATTERN = re.compile(r'\d{1,3}(?:,\d{2,3})*\.\d{2}')

# Keywords that indicate important summary sections to always keep
SUMMARY_KEYWORDS = [
    'statement summary',
    'opening balance',
    'closing balance',
    'total credits',
    'total debits',
    'account summary',
]


def is_transaction_line(line: str) -> bool:
    """
    Check if a line is a transaction line.
    Transaction lines contain a date and at least one amount.

    Args:
        line: A single line of text

    Returns:
        True if line matches transaction pattern
    """
    stripped = line.strip()
    if not stripped or len(stripped) < 15:
        return False

    # Check if line contains a date pattern
    has_date = bool(DATE_PATTERN.search(stripped))

    # Check if line contains an amount pattern
    has_amount = bool(AMOUNT_PATTERN.search(stripped))

    return has_date and has_amount


def is_summary_line(line: str) -> bool:
    """
    Check if a line contains important summary information.

    Args:
        line: A single line of text

    Returns:
        True if line contains summary keywords
    """
    lower_line = line.lower()
    return any(keyword in lower_line for keyword in SUMMARY_KEYWORDS)


def filter_page_text(text: str) -> str:
    """
    Filter a page's text to keep only transaction lines and summary information.
    Used for middle pages to remove redundant headers/footers.

    Args:
        text: Full text of a page

    Returns:
        Filtered text containing only relevant lines
    """
    if not text:
        return ""

    lines = text.split('\n')
    filtered_lines = []

    for line in lines:
        # Keep transaction lines
        if is_transaction_line(line):
            filtered_lines.append(line)
        # Keep summary lines
        elif is_summary_line(line):
            filtered_lines.append(line)

    return '\n'.join(filtered_lines)


def extract_pdf_data(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text from a PDF file with smart filtering.

    - First 2 pages: Keep complete text (contains account info, headers)
    - Last 2 pages: Keep complete text (contains statement summary)
    - Middle pages: Keep only transaction lines (filter out repeated headers/footers)

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dict with 'text' key containing optimized extracted text
    """
    logger.info(f"Extracting data from PDF: {pdf_path}")
    all_text: List[str] = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"PDF has {total_pages} pages")

            for i, page in enumerate(pdf.pages):
                # Extract text from page
                text = page.extract_text()
                if not text:
                    continue

                # Determine if this is a first/last 2 pages or middle page
                is_first_pages = i < 2  # Pages 1 and 2 (index 0, 1)
                is_last_pages = i >= total_pages - 2  # Last 2 pages

                if is_first_pages or is_last_pages:
                    # Keep complete text for first and last 2 pages
                    all_text.append(text)
                else:
                    # Filter middle pages to keep only transaction lines
                    filtered_text = filter_page_text(text)
                    if filtered_text:
                        all_text.append(filtered_text)

        total_text = '\n\n'.join(all_text)
        logger.info(f"Extraction complete: {len(total_text)} characters from {total_pages} pages")

    except Exception as e:
        logger.error(f"pdfplumber failed: {e}")
        # If pdfplumber fails, try pymupdf4llm (no filtering for fallback)
        try:
            logger.info("Trying pymupdf4llm as fallback")
            import pymupdf4llm
            md_text = pymupdf4llm.to_markdown(pdf_path)
            all_text = [md_text]
            total_text = md_text
            logger.info(f"pymupdf4llm extracted {len(md_text)} characters")
        except Exception as e2:
            logger.error(f"pymupdf4llm also failed: {e2}")
            total_text = ""

    return {
        "text": total_text
    }

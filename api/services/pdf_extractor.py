"""
PDF Extraction Service
Uses pdfplumber as primary extractor with pymupdf4llm as fallback.
"""

import logging
import pdfplumber
from typing import Dict, Any, List

# Setup logging
logger = logging.getLogger('pdf_extractor')


def extract_pdf_data(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text and tables from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dict with 'text' and 'tables' keys
    """
    logger.info(f"Extracting data from PDF: {pdf_path}")
    all_text = []
    all_tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"PDF opened successfully. Pages: {len(pdf.pages)}")

            for i, page in enumerate(pdf.pages):
                logger.info(f"Processing page {i + 1}")

                # Extract text
                text = page.extract_text()
                if text:
                    all_text.append(text)
                    logger.info(f"Page {i + 1}: Extracted {len(text)} characters of text")

                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 0:
                        all_tables.append(table)
                        logger.info(f"Page {i + 1}: Extracted table with {len(table)} rows")

        logger.info(f"Total text extracted: {len(''.join(all_text))} characters")
        logger.info(f"Total tables extracted: {len(all_tables)}")

    except Exception as e:
        logger.error(f"pdfplumber failed: {e}")
        # If pdfplumber fails, try pymupdf4llm
        try:
            logger.info("Trying pymupdf4llm as fallback")
            import pymupdf4llm
            md_text = pymupdf4llm.to_markdown(pdf_path)
            all_text = [md_text]
            logger.info(f"pymupdf4llm extracted {len(md_text)} characters")
        except Exception as e2:
            logger.error(f"pymupdf4llm also failed: {e2}")

    return {
        "text": "\n\n".join(all_text),
        "tables": all_tables
    }


def format_tables_for_prompt(tables: List[List[List[str]]]) -> str:
    """
    Format extracted tables into a readable string for LLM prompt.
    """
    if not tables:
        return "No tables found."

    formatted = []
    for i, table in enumerate(tables):
        formatted.append(f"Table {i + 1}:")
        for row in table:
            if row:
                formatted.append(" | ".join(str(cell) if cell else "" for cell in row))
        formatted.append("")

    result = "\n".join(formatted)
    logger.info(f"Formatted {len(tables)} tables into {len(result)} characters")
    return result

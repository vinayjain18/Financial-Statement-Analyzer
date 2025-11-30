"""
PDF Extraction Service
Uses pdfplumber as primary extractor with pymupdf4llm as fallback.
"""

import pdfplumber
from typing import Dict, Any, List


def extract_pdf_data(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text and tables from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dict with 'text' and 'tables' keys
    """
    all_text = []
    all_tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract text
                text = page.extract_text()
                if text:
                    all_text.append(text)

                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 0:
                        all_tables.append(table)

    except Exception as e:
        # If pdfplumber fails, try pymupdf4llm
        try:
            import pymupdf4llm
            md_text = pymupdf4llm.to_markdown(pdf_path)
            all_text = [md_text]
        except Exception:
            pass

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

    return "\n".join(formatted)

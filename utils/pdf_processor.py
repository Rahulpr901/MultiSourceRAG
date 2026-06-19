# utils/pdf_processor.py

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional

import fitz  # PyMuPDF


def extract_pdf_pages(pdf_path: str | Path) -> List[Dict]:
    """
    Extract text page-by-page from a PDF.

    Returns:
        [
            {
                "page_number": 1,
                "text": "...",
                "source": "filename.pdf"
            },
            ...
        ]
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages_data: List[Dict] = []

    with fitz.open(pdf_path) as doc:
        for page_index in range(len(doc)):
            page = doc[page_index]
            text = page.get_text("text").strip()

            if text:
                pages_data.append(
                    {
                        "page_number": page_index + 1,
                        "text": text,
                        "source": pdf_path.name,
                    }
                )

    return pages_data


def extract_pdf_text(pdf_path: str | Path) -> str:
    """
    Extract all text from a PDF and return it as a single string.
    """
    pages_data = extract_pdf_pages(pdf_path)
    return "\n\n".join(
        f"[Page {item['page_number']}]\n{item['text']}"
        for item in pages_data
    )


def extract_pdf_metadata(pdf_path: str | Path) -> Dict:
    """
    Return basic PDF metadata.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with fitz.open(pdf_path) as doc:
        meta = doc.metadata or {}

        return {
            "file_name": pdf_path.name,
            "page_count": len(doc),
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "creator": meta.get("creator", ""),
            "producer": meta.get("producer", ""),
        }


def save_pdf_text(pdf_path: str | Path, output_path: str | Path) -> Path:
    """
    Save extracted PDF text to a .txt file.
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    text = extract_pdf_text(pdf_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")

    return output_path
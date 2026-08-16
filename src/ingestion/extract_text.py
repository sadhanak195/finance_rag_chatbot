"""
MODULE: Extracts raw text from uploaded PDF files.
DEPENDS ON: pypdf
"""

import os
from pathlib import Path
from typing import Union, BinaryIO, Optional
from pypdf import PdfReader

def extract_text_from_pdf(pdf_source: Union[str, Path, BinaryIO], file_name: Optional[str] = None) -> list[dict]:
    """
    Extracts raw text from every page of a PDF document.

    Logic:
        - Resolves the explicit file name from the path or file-like object.
        - Reads the PDF page by page, extracting the text.
        - Verifies that at least some text was extracted (guards against scanned images).

    Args:
        pdf_source: path string, Path object, or file-like object containing the PDF data
        file_name: explicit name of the file to override inference

    Returns:
        List of dictionaries containing file_name, page number, and extracted text per page
    """
    reader = PdfReader(pdf_source)

    if file_name is None:
        if hasattr(pdf_source, "name"):
            file_name = os.path.basename(pdf_source.name)
        elif isinstance(pdf_source, (str, Path)):
            file_name = os.path.basename(str(pdf_source))
        else:
            file_name = "unknown.pdf"

    pages = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({
            "file_name": file_name,
            "page": page_num,
            "text": text,
        })

    if all(p["text"].strip() == "" for p in pages):
        raise ValueError(
            f"'{file_name}' produced no extractable text on any page. "
            "It may be a scanned-image PDF. OCR is not supported."
        )

    return pages

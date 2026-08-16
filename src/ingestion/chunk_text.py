"""
MODULE: Splits extracted pages into chunks and applies source metadata.
DEPENDS ON: langchain_text_splitters, config.settings
"""

import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

QUARTER_PATTERN = re.compile(r"(Q[1-4])_(FY\d{2,4})", re.IGNORECASE)

def _infer_quarter(file_name: str) -> str:
    """
    Infers the financial quarter string from the file name.

    Logic:
        - Searches the filename for a known quarter and fiscal year pattern.
        - Returns the formatted quarter string or an empty string.

    Args:
        file_name: the name of the file to parse

    Returns:
        The matched quarter string (e.g., 'Q1 FY26') or an empty string
    """
    match = QUARTER_PATTERN.search(file_name)
    if match:
        return f"{match.group(1).upper()} {match.group(2).upper()}"
    return ""

def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Splits page texts into overlapping chunks with source prefixes.

    Logic:
        - Uses a recursive character splitter to break large pages into chunks.
        - Infers the quarter from the file name for metadata.
        - Prefixes every chunk with its explicit source filename and page number.

    Args:
        pages: list of dictionaries containing page text and metadata

    Returns:
        List of chunk dictionaries containing a unique id, prefixed text, and metadata
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for page_info in pages:
        file_name = page_info["file_name"]
        page = page_info["page"]
        text = page_info["text"]

        if not text.strip():
            continue

        quarter = _infer_quarter(file_name)
        base_name = os.path.splitext(file_name)[0]

        page_chunks = splitter.split_text(text)
        for idx, chunk_text in enumerate(page_chunks):
            prefixed_text = f"[Source: {file_name}, Page {page}]\n{chunk_text}"
            chunk_id = f"{base_name}_p{page}_c{idx}"

            chunks.append({
                "id": chunk_id,
                "text": prefixed_text,
                "metadata": {
                    "file_name": file_name,
                    "page": page,
                    "quarter": quarter,
                    "chunk_index": idx,
                },
            })

    return chunks

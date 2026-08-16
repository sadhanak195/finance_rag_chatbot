"""
MODULE: Configuration settings and constants for the FinBuddy application.
DEPENDS ON: None
"""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = str(PROJECT_ROOT / "chroma_db")

# Ingestion
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

# Models & Retrieval
COLLECTION_NAME = "financial_reports"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_NAME = "llama-3.3-70b-versatile"
REWRITE_MODEL_NAME = "llama3-8b-8192"
DEFAULT_TOP_K = 4

# Thresholding
# Distance threshold for confidence gate (lower is more similar).
CONFIDENCE_THRESHOLD = 1.0 

def get_chroma_dir() -> str:
    """
    Return the absolute path to the ChromaDB directory.

    Logic:
        - Retrieves the CHROMA_DIR constant.

    Args:
        None

    Returns:
        The string path to the Chroma directory.
    """
    return CHROMA_DIR

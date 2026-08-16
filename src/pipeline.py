"""
MODULE: Wires ingestion, retrieval, and generation together into a complete pipeline.
DEPENDS ON: config.settings, dotenv, chromadb, sentence_transformers, src.ingestion.*, src.retrieval.*, src.conversation.*, src.generation.*
"""

import os
import logging
from pathlib import Path
from typing import Union, BinaryIO
from dotenv import load_dotenv
import streamlit as st
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer

from config.settings import (
    PROJECT_ROOT, COLLECTION_NAME, EMBEDDING_MODEL_NAME, 
    LLM_MODEL_NAME, DEFAULT_TOP_K
)
from src.ingestion.extract_text import extract_text_from_pdf
from src.ingestion.chunk_text import chunk_pages
from src.ingestion.embed_and_store import embed_and_store
from src.retrieval.embed_query import embed_question
from src.retrieval.search_index import search_index
from src.retrieval.confidence_gate import is_confident
from src.conversation.rewrite_followup import rewrite_query
from src.generation.build_messages import build_messages
from src.generation.call_llm import call_llm
from config.settings import get_chroma_dir

logger = logging.getLogger(__name__)

load_dotenv(PROJECT_ROOT / ".env")

_embedding_model = None
_chroma_client = None
_collection = None

@st.cache_resource
def get_embedding_model() -> SentenceTransformer:
    """
    Returns the loaded sentence transformer model, initializing it if necessary.

    Logic:
        - Checks if the global model instance exists.
        - Loads it using the configured model name if it doesn't.

    Args:
        None

    Returns:
        The SentenceTransformer instance
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model

@st.cache_resource
def get_collection() -> chromadb.Collection:
    """
    Returns the ChromaDB collection, initializing the client and collection if necessary.

    Logic:
        - Checks if the global collection instance exists.
        - Initializes the PersistentClient and retrieves or creates the configured collection.

    Args:
        None

    Returns:
        The ChromaDB Collection instance
    """
    global _chroma_client, _collection
    if _collection is None:
        chroma_dir = get_chroma_dir()
        logger.info("Initializing ChromaDB at: %s", chroma_dir)
        _chroma_client = chromadb.PersistentClient(path=chroma_dir)
        _collection = _chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection

def _get_api_key() -> str:
    """
    Retrieves the Groq API key from the environment.

    Logic:
        - Fetches the GROQ_API_KEY environment variable.
        - Raises an EnvironmentError if it is missing.

    Args:
        None

    Returns:
        The string API key
    """
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise EnvironmentError("GROQ_API_KEY not found. Make sure it is set in the .env file.")
    return key

@st.cache_data(show_spinner=False)
def _cached_ingestion(file_hashes: tuple, _file_bytes: tuple, _file_names: tuple) -> tuple[int, int]:
    """
    Cached worker for ingestion that bypasses extraction and chunking if inputs match.
    """
    import io
    collection = get_collection()
    model = get_embedding_model()
    
    all_chunks = []
    file_count = 0

    for fb, fname in zip(_file_bytes, _file_names):
        src = io.BytesIO(fb)
        src.name = fname
        logger.info("Extracting text from: %s", fname)
        pages = extract_text_from_pdf(src, file_name=fname)
        chunks = chunk_pages(pages)
        all_chunks.extend(chunks)
        file_count += 1

    total_chunks = embed_and_store(all_chunks, collection, model)
    return file_count, total_chunks

def run_ingestion(pdf_sources: list[Union[str, Path, BinaryIO]]) -> tuple[int, int]:
    """
    Orchestrates the extraction, chunking, and storage of multiple PDFs.

    Logic:
        - Iterates over the given PDF sources.
        - Calculates hashes and bytes to serve as stable cache keys.
        - Passes to the cached ingestion worker.

    Args:
        pdf_sources: list of file paths or uploaded file objects

    Returns:
        A tuple containing the number of files ingested and the total chunks stored
    """
    file_hashes = []
    file_bytes_list = []
    file_names = []

    for src in pdf_sources:
        if isinstance(src, (str, Path)):
            fname = os.path.basename(str(src))
            with open(src, "rb") as f:
                fb = f.read()
        else:
            if hasattr(src, "name"):
                fname = src.name
            else:
                fname = "unknown.pdf"
            src.seek(0)
            fb = src.read()

        file_bytes_list.append(fb)
        file_names.append(fname)
        file_hashes.append(hashlib.md5(fb).hexdigest())

    return _cached_ingestion(tuple(file_hashes), tuple(file_bytes_list), tuple(file_names))

def run_query(question: str, top_k: int = DEFAULT_TOP_K, history: list = None, history_str: str = ""):
    """
    Orchestrates the retrieval and generation pipeline to answer a user question.

    Logic:
        - Rewrites the question using history if necessary.
        - Embeds the query and searches the index.
        - Checks confidence gating; returns a failure message if not confident.
        - Builds messages and returns the generator from the LLM.

    Args:
        question: the latest user question
        top_k: the maximum number of chunks to retrieve
        history: the list of Q&A dictionaries for the prompt
        history_str: the formatted string of history for rewriting

    Returns:
        A generator yielding chunks of text and finally a dict with sources.
    """
    collection = get_collection()
    model = get_embedding_model()
    api_key = _get_api_key()

    search_query = question
    if history_str:
        search_query = rewrite_query(question, history_str, api_key)

    q_vector = embed_question(search_query, model)
    retrieved = search_index(q_vector, collection, k=top_k)

    if not is_confident(retrieved):
        logger.warning(f"No confident documents found for query: {search_query}")
        # Yield a string then the dict format that the generator would
        def _fail():
            yield "No relevant documents were found. Please index some PDFs first."
            yield {"sources": [], "final_answer": "No relevant documents were found. Please index some PDFs first."}
        return _fail()

    messages = build_messages(question, retrieved, history=history)
    return call_llm(messages, retrieved, api_key)

def get_stats() -> dict:
    """
    Returns system statistics for the interface.

    Logic:
        - Queries the loaded collection for its count and returns constants.

    Args:
        None

    Returns:
        A dictionary containing system statistics
    """
    collection = get_collection()
    return {
        "collection_name": COLLECTION_NAME,
        "chunk_count": collection.count(),
        "embedding_model": EMBEDDING_MODEL_NAME,
        "llm_model": LLM_MODEL_NAME,
    }

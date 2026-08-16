"""
MODULE: Embeds chunk texts and upserts them into a ChromaDB collection.
DEPENDS ON: chromadb, sentence_transformers
"""

import logging
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

def embed_and_store(chunks: list[dict], collection: chromadb.Collection, model: SentenceTransformer) -> int:
    """
    Batch-embeds chunk texts and upserts them into ChromaDB.

    Logic:
        - Extracts plain texts, ids, and metadata from the input chunks.
        - Generates embeddings in batches using the specified model.
        - Upserts the generated embeddings and chunks into ChromaDB in batches of 5000.

    Args:
        chunks: list of dictionaries representing document chunks
        collection: the ChromaDB collection to insert into
        model: the sentence transformer model to encode text with

    Returns:
        The total number of chunks successfully stored
    """
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    embeddings_list = embeddings.tolist()

    batch_size = 5000
    for i in range(0, len(ids), batch_size):
        end = i + batch_size
        collection.upsert(
            ids=ids[i:end],
            documents=texts[i:end],
            metadatas=metadatas[i:end],
            embeddings=embeddings_list[i:end],
        )

    logger.info("Upserted %d chunks into collection '%s'", len(ids), collection.name)
    return len(ids)

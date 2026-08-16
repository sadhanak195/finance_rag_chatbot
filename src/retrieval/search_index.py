"""
MODULE: Queries ChromaDB with a vector and returns formatted chunks.
DEPENDS ON: chromadb
"""

import chromadb

def search_index(query_vector: list[float], collection: chromadb.Collection, k: int = 4) -> list[dict]:
    """
    Queries ChromaDB with a vector to find the nearest document chunks.

    Logic:
        - Executes a vector search against the provided ChromaDB collection.
        - Extracts and formats the text, metadata, and distance score from the results.

    Args:
        query_vector: list of floats representing the embedded question
        collection: the ChromaDB collection to search against
        k: the maximum number of results to return

    Returns:
        A list of dictionaries representing the retrieved chunks with metadata and distances
    """
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    if results and results["documents"]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            retrieved.append({
                "text": doc,
                "file_name": meta.get("file_name", "unknown"),
                "page": meta.get("page", 0),
                "quarter": meta.get("quarter", ""),
                "distance": dist,
            })

    return retrieved

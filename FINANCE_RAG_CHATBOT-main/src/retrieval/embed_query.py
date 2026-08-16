"""
MODULE: Turns a question string into an embedding vector.
DEPENDS ON: sentence_transformers
"""

from sentence_transformers import SentenceTransformer

def embed_question(question: str, model: SentenceTransformer) -> list[float]:
    """
    Transforms a user question into a numerical vector using the embedding model.

    Logic:
        - Passes the question string into the sentence transformer encode function.
        - Converts the resulting numpy array to a standard Python list for ChromaDB.

    Args:
        question: the string question to embed
        model: the sentence transformer model to use

    Returns:
        A list of floats representing the embedding vector
    """
    q_embedding = model.encode([question]).tolist()
    return q_embedding[0]

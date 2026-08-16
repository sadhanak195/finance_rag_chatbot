"""
MODULE: Pure decision logic to determine if retrieved chunks are confident enough to use.
DEPENDS ON: config.settings
"""

from config.settings import CONFIDENCE_THRESHOLD

def is_confident(retrieved_chunks: list[dict]) -> bool:
    """
    Evaluates if the retrieval results are confident enough to generate an answer.

    Logic:
        - Checks if there are any retrieved chunks.
        - Verifies if the top result's distance is below the configured confidence threshold.

    Args:
        retrieved_chunks: list of dictionaries representing the search results, ordered by distance

    Returns:
        True if the top result passes the confidence threshold, False otherwise
    """
    if not retrieved_chunks:
        return False
        
    top_distance = retrieved_chunks[0].get("distance", float("inf"))
    return top_distance <= CONFIDENCE_THRESHOLD

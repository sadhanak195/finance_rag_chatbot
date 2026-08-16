"""
MODULE: Computes generation metrics like groundedness and hallucination rate.
DEPENDS ON: None
"""

def groundedness_score(hit_rate: float) -> float:
    """
    Calculates the groundedness of the generated answer.

    Logic:
        - Uses a mock proxy logic based on hit rate for demonstration.

    Args:
        hit_rate: the hit rate score of the retrieval step

    Returns:
        A mock groundedness float between 0.0 and 1.0
    """
    return 0.9 if hit_rate > 0 else 0.2

def hallucination_rate_score(hit_rate: float) -> float:
    """
    Calculates the hallucination rate of the generated answer.

    Logic:
        - Uses a mock proxy logic based on hit rate for demonstration.

    Args:
        hit_rate: the hit rate score of the retrieval step

    Returns:
        A mock hallucination rate float between 0.0 and 1.0
    """
    return 0.1 if hit_rate > 0 else 0.8

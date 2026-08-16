"""
MODULE: Computes basic retrieval metrics like precision, recall, F1, hit rate, and reciprocal rank.
DEPENDS ON: None
"""

def precision_score(retrieved_ids: list[str], true_ids: set[str]) -> float:
    """
    Calculates the precision of retrieved chunks.

    Logic:
        - Intersects retrieved and true sets to find hits.
        - Divides hits by the number of retrieved items.

    Args:
        retrieved_ids: list of retrieved chunk identifiers
        true_ids: set of relevant true chunk identifiers

    Returns:
        A float representing precision score
    """
    if not retrieved_ids:
        return 0.0
    hits = len(set(retrieved_ids) & true_ids)
    # Precision = TP / (TP + FP)
    return hits / len(retrieved_ids)

def recall_score(retrieved_ids: list[str], true_ids: set[str]) -> float:
    """
    Calculates the recall of retrieved chunks.

    Logic:
        - Intersects retrieved and true sets to find hits.
        - Divides hits by the total number of relevant true items.

    Args:
        retrieved_ids: list of retrieved chunk identifiers
        true_ids: set of relevant true chunk identifiers

    Returns:
        A float representing recall score
    """
    if not true_ids:
        return 0.0
    hits = len(set(retrieved_ids) & true_ids)
    # Recall = TP / (TP + FN)
    return hits / len(true_ids)

def f1_score(precision: float, recall: float) -> float:
    """
    Calculates the F1 score from precision and recall.

    Logic:
        - Calculates the harmonic mean of precision and recall.

    Args:
        precision: precision score float
        recall: recall score float

    Returns:
        A float representing F1 score
    """
    if (precision + recall) == 0.0:
        return 0.0
    # F1 = 2 * (Precision * Recall) / (Precision + Recall)
    return 2 * (precision * recall) / (precision + recall)

def hit_rate(retrieved_ids: list[str], true_ids: set[str]) -> float:
    """
    Calculates whether any relevant document was retrieved.

    Logic:
        - Checks if the intersection of retrieved and true IDs is non-empty.

    Args:
        retrieved_ids: list of retrieved chunk identifiers
        true_ids: set of relevant true chunk identifiers

    Returns:
        1.0 if there is at least one hit, otherwise 0.0
    """
    hits = len(set(retrieved_ids) & true_ids)
    return 1.0 if hits > 0 else 0.0

def reciprocal_rank(retrieved_ids: list[str], true_ids: set[str]) -> float:
    """
    Calculates the reciprocal rank of the first relevant document.

    Logic:
        - Iterates over the retrieved list sequentially.
        - Returns 1 divided by the rank (1-indexed) of the first true hit.

    Args:
        retrieved_ids: list of retrieved chunk identifiers
        true_ids: set of relevant true chunk identifiers

    Returns:
        A float representing the reciprocal rank
    """
    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in true_ids:
            return 1.0 / (i + 1)
    return 0.0

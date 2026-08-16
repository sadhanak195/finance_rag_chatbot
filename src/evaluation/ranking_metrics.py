"""
MODULE: Computes ranking metrics like Mean Average Precision and nDCG.
DEPENDS ON: math
"""

import math

def average_precision(true_docs: set[str], retrieved_docs: list[str]) -> float:
    """
    Calculates the average precision for a single query.

    Logic:
        - Iterates over the retrieved list and tracks correct hits.
        - Sums precision at each hit and averages over total hits.

    Args:
        true_docs: set of relevant chunk identifiers
        retrieved_docs: list of retrieved chunk identifiers

    Returns:
        A float representing the average precision
    """
    if not true_docs:
        return 0.0
    hits, precision_sum = 0, 0.0
    for rank, doc_id in enumerate(retrieved_docs, start=1):
        if doc_id in true_docs:
            hits += 1
            precision_sum += hits / rank
    # Average Precision
    return precision_sum / len(true_docs)

def mean_average_precision(true_docs_list: list[set[str]], retrieved_docs_list: list[list[str]]) -> float:
    """
    Calculates the mean average precision across multiple queries.

    Logic:
        - Calculates the average precision for each query.
        - Sums them up and divides by the number of queries.

    Args:
        true_docs_list: list of true doc sets for each query
        retrieved_docs_list: list of retrieved doc lists for each query

    Returns:
        A float representing the Mean Average Precision (MAP)
    """
    if not true_docs_list:
        return 0.0
    aps = [
        average_precision(t, r)
        for t, r in zip(true_docs_list, retrieved_docs_list)
    ]
    # MAP = sum(AP) / N
    return sum(aps) / len(aps)

def ndcg_at_k(true_docs: set[str], retrieved_docs: list[str], k: int = 5) -> float:
    """
    Calculates the normalized Discounted Cumulative Gain at rank K.

    Logic:
        - Calculates DCG by assigning a relevance of 1 for hits and discounting by log2 of rank.
        - Calculates Ideal DCG (IDCG) assuming all true docs were ranked first.
        - Divides DCG by IDCG.

    Args:
        true_docs: set of relevant chunk identifiers
        retrieved_docs: list of retrieved chunk identifiers
        k: the cut-off rank

    Returns:
        A float representing the nDCG at K
    """
    retrieved_k = retrieved_docs[:k]
    # DCG = sum(rel_i / log2(i + 1))
    dcg = sum(1 / math.log2(i + 2) for i, d in enumerate(retrieved_k) if d in true_docs)
    ideal_hits = min(len(true_docs), k)
    idcg = sum(1 / math.log2(i + 2) for i in range(ideal_hits))
    return dcg / idcg if idcg > 0 else 0.0

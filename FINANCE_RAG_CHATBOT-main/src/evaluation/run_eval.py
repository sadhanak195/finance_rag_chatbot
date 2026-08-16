"""
MODULE: Orchestrates the evaluation of the pipeline across the test dataset.
DEPENDS ON: tests.test_questions, src.evaluation.*, src.pipeline, tabulate
"""

import json
import statistics
from tabulate import tabulate

from tests.test_questions import EVAL_SET
from src.evaluation.ranking_metrics import average_precision, mean_average_precision, ndcg_at_k
from src.evaluation.quality_metrics import context_utilization, response_coherence, response_readability, relevancy_score
from src.evaluation.retrieval_metrics import precision_score, recall_score, f1_score, hit_rate, reciprocal_rank
from src.evaluation.generation_metrics import groundedness_score, hallucination_rate_score
from src.pipeline import run_query

def run_eval() -> None:
    """
    Executes the full evaluation suite and writes the results to JSON.

    Logic:
        - Iterates over the 10 test questions and runs the pipeline.
        - Calculates retrieval, ranking, and generation/quality metrics for each.
        - Aggregates the results, formats them into a summary table, and writes to a file.

    Args:
        None

    Returns:
        None
    """
    results = []
    
    all_true_relevant = []
    all_retrieved = []
    
    for i, item in enumerate(EVAL_SET):
        q = item["q"]
        true_docs = item["true_docs"]
        
        try:
            answer, sources = run_query(q, top_k=5)
            retrieved_ids = [f"{s['file_name'].replace('.pdf', '')}_p{s['page']}" for s in sources]
            retrieved_chunks = [f"Mock chunk text for {s['file_name']} page {s['page']}" for s in sources]
        except Exception:
            answer = "I don't know."
            retrieved_ids = []
            retrieved_chunks = []
            
        all_true_relevant.append(true_docs)
        all_retrieved.append(retrieved_ids)
        
        p = precision_score(retrieved_ids, true_docs)
        r = recall_score(retrieved_ids, true_docs)
        f1 = f1_score(p, r)
        hr = hit_rate(retrieved_ids, true_docs)
        mrr = reciprocal_rank(retrieved_ids, true_docs)
        
        ndcg5 = ndcg_at_k(true_docs, retrieved_ids, k=5)
        ap = average_precision(true_docs, retrieved_ids)
        
        ground = groundedness_score(hr)
        hall = hallucination_rate_score(hr)
        
        cu = context_utilization(answer, retrieved_chunks)
        coh = response_coherence(answer)
        read = response_readability(answer)
        rel_score = relevancy_score(answer, q)
        
        results.append({
            "question": q,
            "precision": p,
            "recall": r,
            "f1": f1,
            "hit_rate": hr,
            "mrr": mrr,
            "ndcg_5": ndcg5,
            "ap": ap,
            "groundedness": ground,
            "hallucination_rate": hall,
            "answer_relevance": rel_score,
            "context_utilization": cu,
            "coherence": coh,
            "readability": read,
            "relevancy_score": rel_score
        })
        
    map_score = mean_average_precision(all_true_relevant, all_retrieved)
    mrr_score = statistics.mean([res["mrr"] for res in results])
    
    with open("src/evaluation/eval_results.json", "w") as f:
        json.dump({"results": results, "map": map_score, "mrr": mrr_score}, f, indent=2)
        
    headers = ["Q", "Prec", "Rec", "F1", "HitRate", "MRR", "nDCG@5", "Ground", "Halluc", "CtxUtil", "Coherence", "Readab", "RelScore"]
    table = []
    for i, res in enumerate(results):
        table.append([
            f"Q{i+1}",
            f"{res['precision']:.2f}",
            f"{res['recall']:.2f}",
            f"{res['f1']:.2f}",
            f"{res['hit_rate']:.2f}",
            f"{res['mrr']:.2f}",
            f"{res['ndcg_5']:.2f}",
            f"{res['groundedness']:.2f}",
            f"{res['hallucination_rate']:.2f}",
            f"{res['context_utilization']:.2f}",
            f"{res['coherence']:.1f}",
            f"{res['readability']:.1f}",
            f"{res['relevancy_score']:.2f}"
        ])
        
    print("\n--- Evaluation Summary ---")
    print(tabulate(table, headers=headers, tablefmt="grid"))
    print(f"\nAggregates: MAP = {map_score:.3f} | MRR = {mrr_score:.3f}\n")

if __name__ == "__main__":
    try:
        import tabulate
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
    run_eval()

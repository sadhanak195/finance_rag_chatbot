"""
MODULE: Computes generation quality metrics based on readability and relevance heuristics.
DEPENDS ON: nltk, textstat, re
"""

import re
try:
    import nltk
    from nltk.tokenize import sent_tokenize
    nltk.download('punkt', quiet=True)
except ImportError:
    sent_tokenize = lambda text: text.split('. ')

try:
    import textstat
except ImportError:
    textstat = None

def context_utilization(answer_text: str, retrieved_chunks: list[str]) -> float:
    """
    Estimates how much of the retrieved context was utilized.

    Logic:
        - Extracts significant vocabulary words from the answer.
        - Counts how many of those words also appear in the retrieved context chunks.

    Args:
        answer_text: the generated response
        retrieved_chunks: list of raw text from the context chunks

    Returns:
        A float between 0.0 and 1.0 representing utilization
    """
    answer_words = set(re.findall(r'\b\w{4,}\b', answer_text.lower()))
    if not answer_words:
        return 0.0
        
    context_text = " ".join(retrieved_chunks).lower()
    used_words = sum(1 for w in answer_words if w in context_text)
    # Utilization = used_words / total_words
    return used_words / len(answer_words)

def response_coherence(answer_text: str) -> float:
    """
    Heuristic check for average sentence length.

    Logic:
        - Tokenizes the answer into sentences.
        - Returns a scaled metric based on word counts.

    Args:
        answer_text: the generated response

    Returns:
        A float representing basic sentence-level coherence (0.0 to 1.0)
    """
    sentences = sent_tokenize(answer_text)
    if not sentences:
        return 0.0
    avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
    # Penalty if average length is too short (< 5) or too long (> 30)
    if 5 <= avg_len <= 30:
        return 1.0
    return 0.5

def response_readability(answer_text: str) -> float:
    """
    Computes the Flesch Reading Ease score.

    Logic:
        - Uses the textstat library to compute Flesch Reading Ease.
        - Maps the raw score to a 0.0 to 1.0 scale.

    Args:
        answer_text: the generated response

    Returns:
        A float representing the scaled readability score
    """
    if textstat is None:
        return 0.5
    raw_score = textstat.flesch_reading_ease(answer_text)
    # Clamp between 0 and 100, then scale to 0-1
    score = max(0.0, min(100.0, raw_score)) / 100.0
    return score

def relevancy_score(answer_text: str, question: str) -> float:
    """
    Estimates the relevancy of the answer to the question.

    Logic:
        - Checks for overlapping significant vocabulary between question and answer.

    Args:
        answer_text: the generated response
        question: the original query string

    Returns:
        A float representing simple keyword overlap relevancy
    """
    q_words = set(re.findall(r'\b\w{4,}\b', question.lower()))
    if not q_words:
        return 1.0
        
    a_words = set(re.findall(r'\b\w{4,}\b', answer_text.lower()))
    overlap = len(q_words & a_words)
    # Relevancy = intersection / question_words
    return min(1.0, overlap / len(q_words) * 2.0)

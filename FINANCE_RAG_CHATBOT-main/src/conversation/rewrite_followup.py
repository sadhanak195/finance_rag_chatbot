"""
MODULE: Transforms a follow-up question and history into a standalone question using Groq.
DEPENDS ON: groq, src.utils.retry, config.settings
"""

import logging
from groq import Groq
from src.utils.retry import retry_with_backoff
from config.settings import REWRITE_MODEL_NAME

logger = logging.getLogger(__name__)

REWRITE_PROMPT = """Given the recent conversation and a new question, rewrite the new question
to be fully self-contained (resolve pronouns like "that", "it", "the previous quarter" into
explicit terms), using only what's in the conversation. If the question is already standalone,
return it unchanged. Return ONLY the rewritten question, nothing else.

Conversation history:
{history}

New question: {question}

Standalone question:"""

@retry_with_backoff(retries=3, base_delay=1.0)
def rewrite_query(question: str, history_str: str, api_key: str) -> str:
    """
    Rewrites the question based on conversation history.

    Logic:
        - Checks if there's any conversation history to rewrite against.
        - Formats the rewrite prompt with the history and new question.
        - Calls the Groq API using a fast model to get the standalone question.
        - Falls back to the original question if the API call fails.

    Args:
        question: the latest user question string
        history_str: the formatted string of conversation history
        api_key: the Groq API key

    Returns:
        The rewritten standalone question or the original question on failure
    """
    if not history_str:
        return question

    prompt = REWRITE_PROMPT.format(history=history_str, question=question)
    client = Groq(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model=REWRITE_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=256,
        )
        rewritten = response.choices[0].message.content.strip()
        logger.info(f"Rewrote query: '{question}' -> '{rewritten}'")
        return rewritten
    except Exception as e:
        logger.warning(f"Failed to rewrite query, falling back to original: {e}")
        return question

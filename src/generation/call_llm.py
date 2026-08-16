"""
MODULE: Sends pre-built messages to Groq and returns the raw response text.
DEPENDS ON: groq, src.utils.retry, config.settings
"""

import logging
from groq import Groq
from src.utils.retry import retry_with_backoff
from config.settings import LLM_MODEL_NAME

logger = logging.getLogger(__name__)

@retry_with_backoff(retries=3, base_delay=1.0)
def call_llm(messages: list[dict], retrieved_chunks: list[dict], api_key: str):
    """
    Executes the API call to Groq and yields tokens as they arrive.

    Logic:
        - Initializes the Groq client and issues a streaming chat completion request.
        - Yields the string chunks one by one for UI streaming.
        - Returns the unique sources at the end of the generator (as a dict in the final yield).

    Args:
        messages: pre-built list of formatted message dictionaries
        retrieved_chunks: the chunks passed originally to extract sources from
        api_key: string API key for Groq authorization

    Yields:
        String chunks of the generated answer, then finally a dict containing the deduplicated sources
    """
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=messages,
        temperature=0.2,
        max_tokens=2048,
        stream=True,
    )

    answer_text = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            text_chunk = chunk.choices[0].delta.content
            answer_text += text_chunk
            yield text_chunk

    seen = set()
    sources: list[dict] = []
    for chunk in retrieved_chunks:
        key = (chunk["file_name"], chunk["page"])
        if key not in seen:
            seen.add(key)
            sources.append({
                "file_name": chunk["file_name"],
                "page": chunk["page"],
            })

    logger.info("Generated answer (%d chars) with %d sources", len(answer_text), len(sources))
    yield {"sources": sources, "final_answer": answer_text}

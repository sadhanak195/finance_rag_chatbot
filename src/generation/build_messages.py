"""
MODULE: Assembles the system prompt, context, and question into the final messages list.
DEPENDS ON: src.generation.system_prompt
"""

from src.generation.system_prompt import SYSTEM_PROMPT

def build_messages(question: str, retrieved_chunks: list[dict], history: list = None) -> list[dict]:
    """
    Constructs the messages list for the Groq chat completion API.

    Logic:
        - Joins all retrieved chunk texts into a single context block.
        - Appends the system prompt as the first message.
        - Appends conversation history iteratively to maintain conversational flow.
        - Appends the user's latest query along with the context block.

    Args:
        question: the current user question string
        retrieved_chunks: list of dictionary chunks containing search results
        history: list of previous Q&A exchange dictionaries

    Returns:
        A list of formatted message dictionaries containing role and content
    """
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_parts.append(f"--- Context chunk {i} ---\n{chunk['text']}")
    context_block = "\n\n".join(context_parts)

    user_content = (
        f"## Context\n\n{context_block}\n\n"
        f"## Question\n\n{question}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    if history:
        for exchange in history:
            messages.append({"role": "user", "content": exchange["question"]})
            messages.append({"role": "assistant", "content": exchange["answer"]})

    messages.append({"role": "user", "content": user_content})
    return messages

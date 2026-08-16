import os
import json
from src.pipeline import run_query
from src.conversation.session_memory import ConversationMemory

memory = ConversationMemory()
q1 = "What was the revenue in Q1?"
print(f"Q1: {q1}")
try:
    ans1, sources = run_query(q1)
    memory.add_exchange(q1, ans1)
    print(f"A1: {ans1}")
except Exception as e:
    print(f"Error on Q1: {e}")

q2 = "How does that compare to Q2?"
print(f"\nQ2: {q2}")
try:
    history = memory.get_history()
    history_str = memory.format_history_for_rewrite()
    ans2, sources = run_query(q2, history=history, history_str=history_str)
    memory.add_exchange(q2, ans2)
    print(f"A2: {ans2}")
except Exception as e:
    print(f"Error on Q2: {e}")

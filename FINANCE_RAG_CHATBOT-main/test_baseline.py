import os
from src.pipeline import run_query

# Simulate questions
q1 = "What was the revenue in Q1?"
print(f"Q1: {q1}")
try:
    ans, sources = run_query(q1)
    print(f"A1: {ans}")
except Exception as e:
    print(f"Error on Q1: {e}")

q2 = "How does that compare to Q2?"
print(f"\nQ2: {q2}")
try:
    ans, sources = run_query(q2)
    print(f"A2: {ans}")
except Exception as e:
    print(f"Error on Q2: {e}")

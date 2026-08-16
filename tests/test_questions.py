"""
MODULE: Holds the evaluation dataset consisting of test questions and hand-labeled true-relevant chunk ids.
DEPENDS ON: None
"""

EVAL_SET = [
    {"q": "What was the revenue in Q1?", "true_docs": {"report_q1_p2"}},
    {"q": "How did profit change in Q2?", "true_docs": {"report_q2_p3", "report_q1_p3"}},
    {"q": "What are the key risks mentioned?", "true_docs": {"report_q1_p10"}},
    {"q": "What was the total expenditure for Q3?", "true_docs": {"report_q3_p4"}},
    {"q": "Did the company issue new shares in Q4?", "true_docs": {"report_q4_p5"}},
    {"q": "How much cash on hand at end of Q1?", "true_docs": {"report_q1_p8"}},
    {"q": "What is the guidance for next year?", "true_docs": {"report_q4_p1"}},
    {"q": "Who is the current CEO?", "true_docs": {"report_q1_p1"}},
    {"q": "What were the marketing expenses?", "true_docs": {"report_q2_p6"}},
    {"q": "What is the debt to equity ratio?", "true_docs": {"report_q3_p7"}},
]

# Architecture — where to look for what

| I want to understand... | Open this file |
|---|---|
| How PDFs get read | [src/ingestion/extract_text.py](file:///c:/HC_TECH_ASSIGNMENT/src/ingestion/extract_text.py) |
| How text gets split into chunks | [src/ingestion/chunk_text.py](file:///c:/HC_TECH_ASSIGNMENT/src/ingestion/chunk_text.py) |
| How chunks get embedded and stored | [src/ingestion/embed_and_store.py](file:///c:/HC_TECH_ASSIGNMENT/src/ingestion/embed_and_store.py) |
| How a question gets turned into a search | [src/retrieval/embed_query.py](file:///c:/HC_TECH_ASSIGNMENT/src/retrieval/embed_query.py), [src/retrieval/search_index.py](file:///c:/HC_TECH_ASSIGNMENT/src/retrieval/search_index.py) |
| How the app decides to refuse | [src/retrieval/confidence_gate.py](file:///c:/HC_TECH_ASSIGNMENT/src/retrieval/confidence_gate.py) |
| The bot's personality and rules | [src/generation/system_prompt.py](file:///c:/HC_TECH_ASSIGNMENT/src/generation/system_prompt.py) |
| How the final prompt to the LLM is built | [src/generation/build_messages.py](file:///c:/HC_TECH_ASSIGNMENT/src/generation/build_messages.py) |
| How the LLM gets called | [src/generation/call_llm.py](file:///c:/HC_TECH_ASSIGNMENT/src/generation/call_llm.py) |
| How everything is wired together | [src/pipeline.py](file:///c:/HC_TECH_ASSIGNMENT/src/pipeline.py) |
| How answers get scored/evaluated | `src/evaluation/` ([retrieval_metrics.py](file:///c:/HC_TECH_ASSIGNMENT/src/evaluation/retrieval_metrics.py), [ranking_metrics.py](file:///c:/HC_TECH_ASSIGNMENT/src/evaluation/ranking_metrics.py), [generation_metrics.py](file:///c:/HC_TECH_ASSIGNMENT/src/evaluation/generation_metrics.py), [quality_metrics.py](file:///c:/HC_TECH_ASSIGNMENT/src/evaluation/quality_metrics.py), [run_eval.py](file:///c:/HC_TECH_ASSIGNMENT/src/evaluation/run_eval.py)) |
| The Streamlit UI | [interface/app.py](file:///c:/HC_TECH_ASSIGNMENT/interface/app.py) |

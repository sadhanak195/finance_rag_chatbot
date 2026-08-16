"""
Streamlit interface for the Financial Reports RAG Chatbot.

Run with:  streamlit run app.py
"""

import streamlit as st

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Enterprise Reports AI",
    page_icon=":material/monitoring:",
    layout="wide",
)

import os
import sys
from pathlib import Path
import json
import uuid
import datetime

# Add project root to sys.path so we can import 'src'
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.pipeline import run_ingestion, run_query, get_stats
from src.conversation.session_memory import ConversationMemory


# Startup Validation
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    api_key_input = st.sidebar.text_input("Setup: Enter Groq API Key", type="password")
    if not api_key_input:
        st.sidebar.warning("API Key is required to use FinBuddy.")
        st.info("Please set your GROQ_API_KEY in the sidebar to get started.", icon="🔑")
        st.stop()
    else:
        os.environ["GROQ_API_KEY"] = api_key_input


# Custom styling
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #f8fafc;
    }
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    .qa-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .question-label {
        color: #8b949e;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.25rem;
    }
    .question-text {
        color: #e6edf3;
        font-size: 1rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    .answer-text {
        color: #c9d1d9;
        font-size: 0.95rem;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .source-chip {
        display: inline-block;
        background-color: #21262d;
        border: 1px solid #30363d;
        color: #8b949e;
        border-radius: 6px;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        color: #58a6ff;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .metric-label {
        color: #8b949e;
        font-size: 0.75rem;
        text-transform: uppercase;
    }
    .stTextInput > div > div > input {
        border-radius: 6px !important;
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
    }
    .stButton > button {
        border-radius: 6px !important;
        background-color: #238636 !important;
        color: #ffffff !important;
        border: 1px solid rgba(240, 246, 252, 0.1) !important;
        font-weight: 600 !important;
        transition: 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #2ea043 !important;
    }
    section[data-testid="stFileUploader"] {
        border: 1px dashed #30363d !important;
        border-radius: 8px !important;
        background-color: #0d1117 !important;
    }
    hr {
        border-color: #21262d !important;
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Session state init
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory(max_history=5)
if "indexed" not in st.session_state:
    st.session_state.indexed = False
if "file_count" not in st.session_state:
    st.session_state.file_count = 0
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0

# Check if there's an existing collection with data (persistence)
try:
    stats = get_stats()
    if stats["chunk_count"] > 0:
        st.session_state.indexed = True
        st.session_state.chunk_count = stats["chunk_count"]
except Exception:
    pass

# Feedback function
def capture_feedback(qa, feedback_type):
    record = {
        "session_id": st.session_state.session_id,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "question": qa["question"],
        "answer": qa["answer"],
        "sources": qa["sources"],
        "feedback": feedback_type
    }
    with open("feedback.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    st.toast("Thank you for your feedback!")

# Sidebar
with st.sidebar:
    st.markdown("## :material/folder: Document Management")
    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Upload new documents",
        type=["pdf"],
        accept_multiple_files=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        index_uploaded_btn = st.button("Index Uploads", use_container_width=True, disabled=not uploaded_files)
    with col2:
        import glob
        local_pdfs = glob.glob(str(Path(__file__).resolve().parent.parent / "data" / "*.pdf"))
        index_local_btn = st.button("Index Data Folder", use_container_width=True, disabled=not local_pdfs)

    if index_uploaded_btn or index_local_btn:
        files_to_index = uploaded_files if index_uploaded_btn else local_pdfs
        
        # Validate that all files end in .pdf
        valid = True
        for f in files_to_index:
            fname = f.name if hasattr(f, "name") else os.path.basename(f)
            if not fname.lower().endswith(".pdf"):
                st.error(f"'{fname}' is not a PDF file. Only PDFs are accepted.", icon="⚠️")
                valid = False
        
        
        if valid:
            with st.spinner("Extracting, chunking, and embedding… (This may take a minute)"):
                try:
                    file_count, chunk_count = run_ingestion(files_to_index)
                    st.session_state.indexed = True
                    st.session_state.file_count = file_count
                    st.session_state.chunk_count = chunk_count
                    st.success(f"Indexed {file_count} file(s)", icon=":material/check_circle:")
                except ValueError as e:
                    st.error(f"{e}", icon=":material/warning:")
                except Exception as e:
                    st.error(f"Indexing failed: {e}", icon=":material/error:")

    st.markdown("---")

    # Stats display
    if st.session_state.indexed:
        st.markdown("### :material/bar_chart: Index Stats")
        try:
            stats = get_stats()
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">{stats["chunk_count"]}</div>'
                    f'<div class="metric-label">Chunks</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">{st.session_state.file_count or "—"}</div>'
                    f'<div class="metric-label">Files</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("---")
            st.caption(f":material/memory: Embeddings: `{stats['embedding_model']}`")
            st.caption(f":material/smart_toy: LLM: `{stats['llm_model']}`")
        except Exception:
            pass

    st.markdown("---")
    st.caption(f"Session: `{st.session_state.session_id[:8]}`")


# Main area
st.markdown("# :material/monitoring: Enterprise Reports AI")
st.markdown("**Powered by FinBuddy.** Chat securely with your local context and financial reports (e.g., Infosys Quarterly Reports).")
st.markdown("---")

if not st.session_state.indexed:
    st.info("Upload and index your documents, or index the local data folder, to begin.", icon="ℹ️")
else:
    with st.form("chat_form", clear_on_submit=False):
        question = st.text_input(
            "Ask your enterprise AI assistant...",
            key="question_input",
            placeholder="e.g., What are the key business highlights in Q1?"
        )
        submitted = st.form_submit_button("Ask", use_container_width=True, icon=":material/chat:")

    if submitted:
        if not question or not question.strip():
            st.warning("Please enter a question.")
        elif len(question.strip()) > 500:
            st.warning("Your question is too long! Please limit it to 500 characters.")
        else:
            try:
                q = question.strip()
                history = st.session_state.memory.get_history()
                history_str = st.session_state.memory.format_history_for_rewrite()
                
                # Show the user question immediately
                st.markdown(f"**You:** {q}")
                
                with st.spinner("Retrieving context..."):
                    generator = run_query(q, history=history, history_str=history_str)
                
                final_data = {}
                def stream_handler():
                    for chunk in generator:
                        if isinstance(chunk, str):
                            yield chunk
                        elif isinstance(chunk, dict):
                            final_data.update(chunk)

                st.markdown("**FinBuddy:**")
                # write_stream expects a generator of strings
                answer = st.write_stream(stream_handler())
                sources = final_data.get("sources", [])
                
                st.session_state.memory.add_exchange(q, answer)
                
                # Store sources for feedback logic
                if not hasattr(st.session_state.memory, "sources_history"):
                    st.session_state.memory.sources_history = []
                st.session_state.memory.sources_history.append(sources)
                    
            except Exception as e:
                st.error(f"Error: {e}", icon=":material/error:")

# Q&A history display
history = st.session_state.memory.get_history()
if history:
    st.markdown("## :material/forum: Conversation")
    st.markdown("---")

    for i, qa in enumerate(history):
        st.markdown(
            f'<div class="qa-card">'
            f'<div class="question-label">Question</div>'
            f'<div class="question-text">{qa["question"]}</div>'
            f'<div class="answer-text">{qa["answer"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Sources section
        sources = getattr(st.session_state.memory, "sources_history", [])
        if i < len(sources) and sources[i]:
            source_chips = ""
            for src in sources[i]:
                source_chips += (
                    f'<span class="source-chip">'
                    f':material/description: {src["file_name"]} - Page {src["page"]}'
                    f'</span>'
                )
            st.markdown(
                f'<div style="margin-bottom: 0.5rem;">'
                f'<span style="color: #8888aa; font-size: 0.75rem; '
                f'text-transform: uppercase; letter-spacing: 1px;">'
                f'Sources</span><br>{source_chips}</div>',
                unsafe_allow_html=True,
            )
            
        # Feedback buttons
        col1, col2, _ = st.columns([1, 1, 10])
        qa_with_sources = {
            "question": qa["question"],
            "answer": qa["answer"],
            "sources": sources[i] if i < len(sources) else []
        }
        with col1:
            if st.button("Upvote", key=f"up_{i}", icon=":material/thumb_up:"):
                capture_feedback(qa_with_sources, "positive")
        with col2:
            if st.button("Downvote", key=f"down_{i}", icon=":material/thumb_down:"):
                capture_feedback(qa_with_sources, "negative")
                
        st.markdown("---")

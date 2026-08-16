
Financial Reports RAG Chatbot 💼📑

Project Context: This project was developed as a task assigned by HCLTECH, completed in my capacity as an Ambassador. It demonstrates an end-to-end, enterprise-ready Retrieval-Augmented Generation (RAG) system tailored for analyzing and extracting insights from dense financial documents.

📌 Overview

The Financial Reports RAG Chatbot is an intelligent web application designed to help users instantly navigate and query quarterly financial reports. By combining semantic vector search with blazing-fast Large Language Models via Groq, the bot delivers highly accurate, context-aware answers complete with strict source citations (page numbers and file names) to prevent hallucination.

🧩 Architecture & Workflow

The system is broken into highly modular, single-responsibility pipelines:

Document Ingestion (src/pipeline.py & src/ingestion/):
Extraction: PyMuPDF reads uploaded PDF reports and extracts text page-by-page.
Chunking: The text is split into semantic chunks with targeted overlap to maintain context.
Embedding: A local lightweight model (all-MiniLM-L6-v2 via sentence-transformers) converts chunks into high-dimensional vector embeddings.
Storage: Embeddings are persisted locally in a ChromaDB vector database.
Query & Retrieval (src/conversation/ & src/retrieval/):
Contextual Rewrite: If you ask a follow-up question (e.g., "How does that compare to Q2?"), an LLM rewrites the query into a standalone question using the session memory.
Semantic Search: The standalone query is embedded and compared against the ChromaDB collection to retrieve the top 4 most relevant chunks.
Generation & UI (src/generation/ & interface/app.py):
Response Generation: The retrieved context and question are passed to a Groq (Llama-3) model. The model is strictly prompted to answer only using the provided context.
Streaming UI: The Streamlit frontend processes the streamed tokens in real-time, resulting in a near-instantaneous user experience wrapped in a sleek, enterprise-grade dark mode interface.
⚙️ Setup & Installation
📋 Prerequisites
Python 3.9+ (Python 3.10 recommended)
A Groq API Key
1. 📥 Clone the Repository and Install Dependencies
# It is highly recommended to use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install required packages
pip install -r requirements.txt

Note: If you encounter import errors related to numpy.core.umath, ensure you are using NumPy 1.x by running:

pip install "numpy<2"
---
2. 🔐 Configure Environment Variables

Create a .env file in the root directory and add your Groq API key:

GROQ_API_KEY=your_groq_api_key_here
▶️ How to Run the App

Launch the application using Streamlit from the root directory:

streamlit run interface/app.py

The application will open automatically in your browser at:

http://localhost:8501
---
🧪 How to Test and Use
Upload Documents: Use the sidebar on the left to browse and upload one or more PDF financial reports.
Index the Data: Click the Index Documents button. The system will extract, chunk, embed, and store the text. You will see a success message with the total chunk count once completed. (This step is cached for speed on repeat uploads.)
Ask Questions: Use the main chat interface to ask questions about the reports.
Example 1: "What was the total operating revenue for the quarter?"
Example 2: "What were the primary risk factors mentioned by the CEO?"
Follow-ups: Ask a direct follow-up like "Did it increase from last year?" and the system will intelligently rewrite your query using the conversation history.
Verify Citations: Every answer will contain a Sources section detailing exactly which PDF and page the model used to construct its response.
🏁 Key Features
📄 Multi-document financial report analysis
🔎 Semantic vector search
🧠 Context-aware conversational retrieval
📚 ChromaDB-powered document storage
⚡ Groq-powered LLM responses
🛡️ Source-grounded answers with page-level citations
🖥️ Streamlit-based interactive interface
🔄 Follow-up question support

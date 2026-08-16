"""
MODULE: FastAPI endpoint definitions acting as thin wrappers around the pipeline.
DEPENDS ON: fastapi, api.schemas, src.pipeline
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from api.schemas import AskRequest, AskResponse, IndexResponse, SourceItem, StatsResponse
from src.pipeline import run_ingestion, run_query, get_stats

app = FastAPI(
    title="Financial Reports RAG API",
    description="A Retrieval-Augmented Generation API for querying quarterly financial reports.",
    version="1.0.0",
)

@app.post("/index", response_model=IndexResponse, summary="Index uploaded PDFs")
async def index_documents(files: list[UploadFile] = File(...)):
    """
    Accepts uploaded PDF files, runs ingestion, and returns counts.

    Logic:
        - Validates that provided files are PDFs.
        - Seeks and assigns filenames to temporary file objects.
        - Invokes the ingestion pipeline and returns the result.

    Args:
        files: a list of FastAPI UploadFile objects

    Returns:
        An IndexResponse containing the counts of files indexed and chunks created
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"'{f.filename}' is not a PDF file.",
            )

    try:
        file_objects = []
        for f in files:
            f.file.seek(0)
            f.file.name = f.filename
            file_objects.append(f.file)

        file_count, chunk_count = run_ingestion(file_objects)
        return IndexResponse(files_indexed=file_count, chunks_created=chunk_count)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {e}")

@app.post("/ask", response_model=AskResponse, summary="Ask a question")
async def ask_question(request: AskRequest):
    """
    Accepts a question, runs retrieval + generation, and returns a grounded answer.

    Logic:
        - Validates the question is not empty.
        - Calls the pipeline query function with the requested parameters.
        - Formats the sources and returns the response.

    Args:
        request: AskRequest payload containing the question string

    Returns:
        An AskResponse containing the generated answer and source citations
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer, sources = run_query(request.question.strip(), top_k=request.top_k)
        return AskResponse(
            answer=answer,
            sources=[SourceItem(**s) for s in sources],
        )
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {e}")

@app.get("/stats", response_model=StatsResponse, summary="System statistics")
async def system_stats():
    """
    Returns metadata about the current state of the RAG system.

    Logic:
        - Invokes the pipeline get_stats function.
        - Wraps the result in a StatsResponse payload.

    Args:
        None

    Returns:
        A StatsResponse containing index statistics and configuration
    """
    try:
        stats = get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {e}")

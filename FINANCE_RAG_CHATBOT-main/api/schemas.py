"""
MODULE: Pydantic request and response models for the API.
DEPENDS ON: pydantic
"""

from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str
    top_k: int = 4

class SourceItem(BaseModel):
    file_name: str
    page: int

class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]

class IndexResponse(BaseModel):
    files_indexed: int
    chunks_created: int

class StatsResponse(BaseModel):
    collection_name: str
    chunk_count: int
    embedding_model: str
    llm_model: str

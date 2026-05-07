from pydantic import BaseModel, Field
from typing import Optional


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    year_from: Optional[int] = None
    year_to: Optional[int] = None


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    top_k: int = 5


class IngestRequest(BaseModel):
    query: str = Field(description="PubMed search query to fetch papers")
    max_results: int = Field(default=10, ge=1, le=100)


class DocumentChunk(BaseModel):
    id: str
    text: str
    metadata: dict
    score: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict]


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict]
    conversation_id: str


class IngestResponse(BaseModel):
    message: str
    documents_ingested: int
    chunks_created: int


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    vector_store_ready: bool
    documents_count: int

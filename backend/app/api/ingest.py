from fastapi import APIRouter, HTTPException
from app.models.schemas import IngestRequest, IngestResponse
from app.core.rag_engine import RAGEngine

router = APIRouter()
engine = RAGEngine()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    try:
        result = engine.ingest(
            query=request.query, max_results=request.max_results
        )
        return IngestResponse(
            message=f"Successfully ingested papers for query: {request.query}",
            documents_ingested=result["documents_ingested"],
            chunks_created=result["chunks_created"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

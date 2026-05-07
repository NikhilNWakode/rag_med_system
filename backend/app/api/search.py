from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest, SearchResponse
from app.core.rag_engine import RAGEngine

router = APIRouter()
engine = RAGEngine()


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        result = engine.search(
            query=request.query,
            top_k=request.top_k,
            year_from=request.year_from,
            year_to=request.year_to,
        )
        return SearchResponse(
            query=request.query,
            answer=result["answer"],
            sources=result["sources"],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

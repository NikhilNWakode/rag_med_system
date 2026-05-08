import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import search, chat, ingest, export
from app.api import auth
from app.models.schemas import HealthResponse
from app.core.llm import LLMClient
from app.db.vector_store import VectorStore
from app.db.chat_store import init_db
from app.db.user_store import init_users_table

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_users_table()
    logger.info("MediSearch AI ready")
    yield


app = FastAPI(
    title="MediSearch AI",
    description="AI-powered semantic medical research assistant using RAG",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(ingest.router, prefix="/api", tags=["Ingest"])
app.include_router(export.router, prefix="/api", tags=["Export"])


@app.get("/api/health")
async def health_check():
    """Lightweight health check for Railway deploy. Always returns 200."""
    return {"status": "ok"}


@app.get("/api/health/detail", response_model=HealthResponse, tags=["Health"])
async def health_check_detail():
    try:
        llm = LLMClient()
        vs = VectorStore()
        return HealthResponse(
            status="ok",
            ollama_connected=llm.is_available(),
            vector_store_ready=True,
            documents_count=vs.count(),
        )
    except Exception:
        return HealthResponse(
            status="ok",
            ollama_connected=False,
            vector_store_ready=False,
            documents_count=0,
        )

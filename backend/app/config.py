from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM — Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # LLM — Groq (cloud, free tier)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "BAAI/bge-reranker-base"

    # Qdrant — local
    qdrant_path: str = "./data/qdrant"

    # Qdrant — cloud
    qdrant_url: str = ""
    qdrant_api_key: str = ""

    collection_name: str = "medical_papers"
    pubmed_email: str = "medisearch@example.com"

    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_retrieval: int = 20
    top_k_rerank: int = 5

    bm25_weight: float = 0.3
    semantic_weight: float = 0.7

    # Auth
    jwt_secret: str = "medisearch-dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    @property
    def use_groq(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def use_qdrant_cloud(self) -> bool:
        return bool(self.qdrant_url)

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()

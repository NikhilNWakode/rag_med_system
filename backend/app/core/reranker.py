import logging
from sentence_transformers import CrossEncoder
from app.config import get_settings

logger = logging.getLogger(__name__)

_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        settings = get_settings()
        logger.info(f"Loading reranker model: {settings.reranker_model}")
        _reranker = CrossEncoder(settings.reranker_model)
        logger.info("Reranker model loaded")
    return _reranker


class Reranker:
    def __init__(self):
        self.model = get_reranker()
        self.settings = get_settings()

    def rerank(
        self, query: str, documents: list[dict], top_k: int | None = None
    ) -> list[dict]:
        top_k = top_k or self.settings.top_k_rerank

        if not documents:
            return []

        pairs = [[query, doc["text"]] for doc in documents]
        scores = self.model.predict(pairs)

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]

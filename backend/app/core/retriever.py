import logging
from rank_bm25 import BM25Okapi
from app.config import get_settings
from app.db.vector_store import VectorStore
from app.ingestion.embedder import Embedder

logger = logging.getLogger(__name__)


class HybridRetriever:
    def __init__(self):
        self.settings = get_settings()
        self.vector_store = VectorStore()
        self.embedder = Embedder()
        self.bm25_index: BM25Okapi | None = None
        self.bm25_corpus: list[dict] = []

    def build_bm25_index(self):
        logger.info("Building BM25 index from vector store...")
        self.bm25_corpus = self.vector_store.get_all_texts()
        if not self.bm25_corpus:
            logger.info("No documents in vector store, BM25 index empty")
            return

        tokenized = [doc["text"].lower().split() for doc in self.bm25_corpus]
        self.bm25_index = BM25Okapi(tokenized)
        logger.info(f"BM25 index built with {len(self.bm25_corpus)} documents")

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[dict]:
        top_k = top_k or self.settings.top_k_retrieval

        query_embedding = self.embedder.embed_query(query)
        semantic_results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
            year_from=year_from,
            year_to=year_to,
        )

        if self.bm25_index is None or not self.bm25_corpus:
            return semantic_results

        bm25_scores = self.bm25_index.get_scores(query.lower().split())
        scored_bm25 = sorted(
            enumerate(bm25_scores), key=lambda x: x[1], reverse=True
        )[:top_k]

        bm25_results = []
        for idx, score in scored_bm25:
            if score > 0:
                doc = self.bm25_corpus[idx]
                bm25_results.append({**doc, "score": float(score)})

        return self._reciprocal_rank_fusion(semantic_results, bm25_results)

    def _reciprocal_rank_fusion(
        self, semantic: list[dict], bm25: list[dict], k: int = 60
    ) -> list[dict]:
        scores: dict[str, float] = {}
        doc_map: dict[str, dict] = {}

        for rank, doc in enumerate(semantic):
            doc_id = doc["id"]
            scores[doc_id] = scores.get(doc_id, 0) + self.settings.semantic_weight / (k + rank + 1)
            doc_map[doc_id] = doc

        for rank, doc in enumerate(bm25):
            doc_id = doc["id"]
            scores[doc_id] = scores.get(doc_id, 0) + self.settings.bm25_weight / (k + rank + 1)
            if doc_id not in doc_map:
                doc_map[doc_id] = doc

        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        results = []
        for doc_id in sorted_ids:
            doc = doc_map[doc_id]
            doc["score"] = scores[doc_id]
            results.append(doc)

        return results

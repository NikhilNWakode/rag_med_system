import logging
import uuid
from app.core.llm import LLMClient
from app.ingestion.pubmed_fetcher import PubMedFetcher
from app.ingestion.processor import DocumentProcessor
from app.ingestion.embedder import Embedder
from app.db.vector_store import VectorStore

logger = logging.getLogger(__name__)

conversations: dict[str, list[dict]] = {}


class RAGEngine:
    def __init__(self):
        self._retriever = None
        self._reranker = None
        self.llm = LLMClient()
        self.fetcher = PubMedFetcher()
        self.processor = DocumentProcessor()
        self.embedder = Embedder()
        self.vector_store = VectorStore()

    @property
    def retriever(self):
        if self._retriever is None:
            from app.core.retriever import HybridRetriever

            self._retriever = HybridRetriever()
            self._retriever.build_bm25_index()
        return self._retriever

    @property
    def reranker(self):
        if self._reranker is None:
            from app.core.reranker import Reranker

            self._reranker = Reranker()
        return self._reranker

    def ingest(self, query: str, max_results: int = 10) -> dict:
        articles = self.fetcher.search(query, max_results)
        if not articles:
            return {"documents_ingested": 0, "chunks_created": 0}

        chunks = self.processor.process_articles(articles)
        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.embed_texts(texts)

        self.vector_store.ensure_collection(self.embedder.dimension)
        self.vector_store.upsert_chunks(chunks, embeddings)

        if self._retriever is not None:
            self._retriever.build_bm25_index()

        return {"documents_ingested": len(articles), "chunks_created": len(chunks)}

    def search(
        self,
        query: str,
        top_k: int = 5,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> dict:
        candidates = self.retriever.retrieve(
            query, year_from=year_from, year_to=year_to
        )

        if not candidates:
            return {
                "answer": "No relevant documents found. Please ingest some papers first using the /api/ingest endpoint.",
                "sources": [],
            }

        top_docs = self.reranker.rerank(query, candidates, top_k)
        answer = self.llm.generate(query, top_docs)
        sources = self._format_sources(top_docs)

        return {"answer": answer, "sources": sources}

    def chat(
        self,
        query: str,
        conversation_id: str | None = None,
        top_k: int = 5,
        history: list[dict] | None = None,
    ) -> dict:
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        history = history or []

        candidates = self.retriever.retrieve(query)
        top_docs = self.reranker.rerank(query, candidates, top_k)

        if not top_docs:
            answer = "No relevant documents found. Please ingest some papers first."
        else:
            answer = self.llm.generate(query, top_docs, history=history)

        sources = self._format_sources(top_docs)
        return {
            "answer": answer,
            "sources": sources,
            "conversation_id": conversation_id,
        }

    def _format_sources(self, documents: list[dict]) -> list[dict]:
        sources = []
        seen_pmids = set()
        for i, doc in enumerate(documents, 1):
            meta = doc.get("metadata", {})
            pmid = meta.get("pmid", "")
            if pmid in seen_pmids:
                continue
            seen_pmids.add(pmid)
            sources.append(
                {
                    "source_number": i,
                    "title": meta.get("title", ""),
                    "authors": meta.get("authors", ""),
                    "journal": meta.get("journal", ""),
                    "year": meta.get("year", ""),
                    "pmid": pmid,
                    "doi": meta.get("doi", ""),
                    "url": meta.get("source_url", ""),
                }
            )
        return sources

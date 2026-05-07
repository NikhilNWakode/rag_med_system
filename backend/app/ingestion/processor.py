import logging
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import get_settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def process_articles(self, articles: list[dict]) -> list[dict]:
        all_chunks = []
        for article in articles:
            chunks = self._chunk_article(article)
            all_chunks.extend(chunks)
        logger.info(f"Processed {len(articles)} articles into {len(all_chunks)} chunks")
        return all_chunks

    def _chunk_article(self, article: dict) -> list[dict]:
        full_text = self._build_document_text(article)
        text_chunks = self.splitter.split_text(full_text)

        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunks.append(
                {
                    "id": str(uuid.uuid4()),
                    "text": chunk_text,
                    "metadata": {
                        "pmid": article["pmid"],
                        "title": article["title"],
                        "authors": ", ".join(article["authors"][:3]),
                        "journal": article["journal"],
                        "year": article["year"],
                        "doi": article["doi"],
                        "source_url": article["source_url"],
                        "chunk_index": i,
                        "total_chunks": len(text_chunks),
                    },
                }
            )
        return chunks

    def _build_document_text(self, article: dict) -> str:
        parts = []
        if article.get("title"):
            parts.append(f"Title: {article['title']}")
        if article.get("abstract"):
            parts.append(f"Abstract: {article['abstract']}")
        if article.get("mesh_terms"):
            parts.append(f"Keywords: {', '.join(article['mesh_terms'][:10])}")
        return "\n\n".join(parts)

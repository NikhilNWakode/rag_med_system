import logging
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    PointStruct,
    Range,
    VectorParams,
)
from app.config import get_settings

logger = logging.getLogger(__name__)

_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        settings = get_settings()
        if settings.use_qdrant_cloud:
            logger.info(f"Connecting to Qdrant Cloud: {settings.qdrant_url}")
            _client = QdrantClient(
                url=settings.qdrant_url, api_key=settings.qdrant_api_key
            )
        else:
            logger.info(f"Initializing local Qdrant at: {settings.qdrant_path}")
            _client = QdrantClient(path=settings.qdrant_path)
    return _client


class VectorStore:
    def __init__(self):
        self.client = get_qdrant_client()
        self.settings = get_settings()
        self.collection_name = self.settings.collection_name

    def ensure_collection(self, vector_size: int):
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size, distance=Distance.COSINE
                ),
            )
            logger.info(f"Created collection: {self.collection_name}")

    def upsert_chunks(
        self, chunks: list[dict], embeddings: list[list[float]]
    ) -> int:
        points = [
            PointStruct(
                id=chunk["id"],
                vector=embedding,
                payload={"text": chunk["text"], **chunk["metadata"]},
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]

        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name, points=batch
            )

        logger.info(f"Upserted {len(points)} chunks")
        return len(points)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 20,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[dict]:
        query_filter = self._build_filter(year_from, year_to)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
        )

        return [
            {
                "id": str(hit.id),
                "text": hit.payload.get("text", ""),
                "metadata": {
                    k: v for k, v in hit.payload.items() if k != "text"
                },
                "score": hit.score,
            }
            for hit in results
        ]

    def get_all_texts(self) -> list[dict]:
        all_points = []
        offset = None
        while True:
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            points, next_offset = result
            for point in points:
                all_points.append(
                    {
                        "id": str(point.id),
                        "text": point.payload.get("text", ""),
                        "metadata": {
                            k: v
                            for k, v in point.payload.items()
                            if k != "text"
                        },
                    }
                )
            if next_offset is None:
                break
            offset = next_offset
        return all_points

    def count(self) -> int:
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        except Exception:
            return 0

    def _build_filter(
        self, year_from: int | None, year_to: int | None
    ) -> Filter | None:
        conditions = []
        if year_from is not None:
            conditions.append(
                FieldCondition(key="year", range=Range(gte=year_from))
            )
        if year_to is not None:
            conditions.append(
                FieldCondition(key="year", range=Range(lte=year_to))
            )
        if conditions:
            return Filter(must=conditions)
        return None

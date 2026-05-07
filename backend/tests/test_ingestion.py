import pytest
from app.ingestion.processor import DocumentProcessor


def test_chunk_article():
    processor = DocumentProcessor()
    article = {
        "pmid": "12345",
        "title": "Test Article on Diabetes",
        "abstract": "This is a test abstract about type 2 diabetes treatment. " * 20,
        "authors": ["Author A", "Author B"],
        "journal": "Test Journal",
        "year": 2024,
        "doi": "10.1234/test",
        "source_url": "https://pubmed.ncbi.nlm.nih.gov/12345/",
        "mesh_terms": ["Diabetes", "Treatment"],
    }
    chunks = processor.process_articles([article])
    assert len(chunks) > 0
    assert all("text" in c for c in chunks)
    assert all("metadata" in c for c in chunks)
    assert chunks[0]["metadata"]["pmid"] == "12345"


def test_empty_articles():
    processor = DocumentProcessor()
    chunks = processor.process_articles([])
    assert chunks == []


def test_chunk_metadata_fields():
    processor = DocumentProcessor()
    article = {
        "pmid": "99999",
        "title": "Metadata Test",
        "abstract": "Short abstract",
        "authors": ["Dr. Smith"],
        "journal": "Nature",
        "year": 2023,
        "doi": "10.5678/meta",
        "source_url": "https://example.com",
        "mesh_terms": [],
    }
    chunks = processor.process_articles([article])
    meta = chunks[0]["metadata"]
    assert meta["title"] == "Metadata Test"
    assert meta["journal"] == "Nature"
    assert meta["year"] == 2023
    assert meta["chunk_index"] == 0

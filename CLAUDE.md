# MediSearch AI

AI-powered semantic medical research assistant using RAG (Retrieval-Augmented Generation).

## Tech Stack
- **Backend**: FastAPI (Python)
- **LLM**: Llama3 via Ollama (local) OR Groq API (cloud, free tier)
- **Embeddings**: BAAI/bge-small-en-v1.5 (sentence-transformers)
- **Vector DB**: Qdrant local OR Qdrant Cloud (free tier)
- **Reranker**: BAAI/bge-reranker-base (cross-encoder)
- **Data Source**: PubMed/NCBI (free API)
- **Retrieval**: Hybrid (BM25 + semantic) with reciprocal rank fusion

## Project Structure
```
backend/
  app/
    main.py          — FastAPI app entry point
    config.py        — Settings with auto-detection (local vs cloud)
    api/             — Route handlers (search, chat, ingest)
    core/            — RAG engine, hybrid retriever, reranker, LLM client
    ingestion/       — PubMed fetcher, document processor, embedder
    db/              — Qdrant vector store (local + cloud)
    models/          — Pydantic schemas
  download_models.py — Pre-downloads ML models for Docker builds
Dockerfile           — Production container (CPU torch + pre-baked models)
railway.json         — Railway deployment config
render.yaml          — Render deployment config
```

## Dual Mode
The app auto-detects local vs cloud based on env vars:
- **GROQ_API_KEY** set → uses Groq for LLM; empty → uses Ollama
- **QDRANT_URL** set → uses Qdrant Cloud; empty → uses local file storage

## Running Locally
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Deploying (Railway / Render)
1. Push to GitHub
2. Connect repo to Railway or Render
3. Set env vars: GROQ_API_KEY, QDRANT_URL, QDRANT_API_KEY
4. Deploy — Dockerfile handles everything

## API Endpoints
- `POST /api/ingest` — Fetch and index papers from PubMed
- `POST /api/search` — One-shot RAG search with citations
- `POST /api/chat`   — Conversational RAG with memory
- `GET  /api/health`  — System health check

## Prerequisites
- Python 3.11+
- Local mode: Ollama with `ollama pull llama3`
- Cloud mode: Groq API key + Qdrant Cloud cluster

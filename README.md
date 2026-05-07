# MediSearch AI

An AI-powered semantic medical research assistant that retrieves, analyzes, and summarizes medical literature using Retrieval-Augmented Generation (RAG).

Search PubMed with natural language queries and get cited, evidence-based answers grounded in real research papers.

---

## Features

- **Hybrid Retrieval** — Combines BM25 keyword search + semantic vector search with Reciprocal Rank Fusion
- **Cross-Encoder Reranking** — BGE-reranker-base reranks candidates for higher relevance
- **Citation-Backed Answers** — Every response includes `[Source N]` citations linked to real PubMed papers
- **Conversational Chat** — Multi-turn conversations with context memory and persistent history
- **PubMed Ingestion** — Fetch and index papers directly from NCBI PubMed API
- **Metadata Filtering** — Filter search results by publication year range
- **Dark Mode** — Full dark/light theme support
- **PDF Export** — Export any conversation as a downloadable PDF
- **Authentication** — JWT-based user registration and login
- **Dual Deployment** — Runs locally (Ollama) or in cloud (Groq + Qdrant Cloud)

---

## Architecture

```
                    ┌──────────────────────────┐
                    │        Frontend          │
                    │  Next.js + TypeScript    │
                    │  Tailwind + Shadcn UI    │
                    └────────────┬─────────────┘
                                 │
                          REST API
                                 │
                    ┌────────────▼─────────────┐
                    │      FastAPI Backend     │
                    ├──────────────────────────┤
                    │  Auth (JWT)              │
                    │  Chat + Search + Ingest  │
                    │  PDF Export              │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
     ┌────────▼────────┐ ┌──────▼───────┐ ┌───────▼────────┐
     │ BM25 Retriever  │ │   Vector     │ │   Metadata     │
     │ Keyword Search  │ │   Search     │ │   Filtering    │
     └────────┬────────┘ └──────┬───────┘ └───────┬────────┘
              │                 │                  │
              └─────────┬──────┴──────────┬───────┘
                        │                 │
               ┌────────▼─────────────────▼──────┐
               │    Hybrid Retrieval (RRF)       │
               └────────────────┬────────────────┘
                                │
                  ┌─────────────▼──────────────┐
                  │   Cross-Encoder Reranker   │
                  │   (bge-reranker-base)      │
                  └─────────────┬──────────────┘
                                │
                  ┌─────────────▼──────────────┐
                  │       LLM Generation       │
                  │   Llama 3 (Ollama/Groq)    │
                  └─────────────┬──────────────┘
                                │
                  ┌─────────────▼──────────────┐
                  │   Cited Answer + Sources   │
                  └────────────────────────────┘
```

### Data Ingestion Pipeline

```
  PubMed API ──▶ Document Fetcher ──▶ Text Chunking ──▶ BGE Embeddings ──▶ Qdrant Vector DB
                 (Biopython)          (512 tokens)      (bge-small-en-v1.5)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, Shadcn UI |
| Backend | FastAPI (Python) |
| LLM | Llama 3 via Ollama (local) / Groq API (cloud) |
| Embeddings | BAAI/bge-small-en-v1.5 (sentence-transformers) |
| Vector DB | Qdrant (local file storage / Qdrant Cloud) |
| Reranker | BAAI/bge-reranker-base (cross-encoder) |
| BM25 | rank-bm25 |
| Database | SQLite (chat history + users) |
| Auth | JWT (PyJWT + bcrypt) |
| Data Source | PubMed / NCBI Entrez API |
| Evaluation | RAGAS pipeline |
| Deployment | Docker, Railway, Render, Vercel |

---

## Project Structure

```
rag_med_system/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Settings (auto-detects local vs cloud)
│   │   ├── api/
│   │   │   ├── auth.py             # Register, login, JWT
│   │   │   ├── search.py           # One-shot RAG search
│   │   │   ├── chat.py             # Conversational RAG + history
│   │   │   ├── ingest.py           # PubMed paper ingestion
│   │   │   └── export.py           # PDF export
│   │   ├── core/
│   │   │   ├── rag_engine.py       # Orchestrates full pipeline
│   │   │   ├── retriever.py        # Hybrid retrieval (BM25 + semantic + RRF)
│   │   │   ├── reranker.py         # Cross-encoder reranking
│   │   │   └── llm.py              # Ollama / Groq LLM client
│   │   ├── ingestion/
│   │   │   ├── pubmed_fetcher.py   # PubMed API integration
│   │   │   ├── processor.py        # Document chunking
│   │   │   └── embedder.py         # BGE embedding generation
│   │   ├── db/
│   │   │   ├── vector_store.py     # Qdrant (local + cloud)
│   │   │   ├── chat_store.py       # SQLite conversation persistence
│   │   │   └── user_store.py       # SQLite user management
│   │   └── models/
│   │       └── schemas.py          # Pydantic request/response models
│   ├── evaluation/
│   │   └── evaluate.py             # RAGAS evaluation pipeline
│   ├── tests/
│   │   ├── test_api.py             # API endpoint tests
│   │   └── test_ingestion.py       # Ingestion pipeline tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Landing page + ingest
│   │   │   ├── chat/page.tsx       # Chat with history sidebar
│   │   │   ├── search/page.tsx     # Search with year filters
│   │   │   └── login/page.tsx      # Auth (register/login)
│   │   ├── components/
│   │   │   ├── navbar.tsx          # Navigation + auth + theme toggle
│   │   │   ├── markdown-answer.tsx # Markdown rendering for LLM output
│   │   │   ├── source-card.tsx     # PubMed source citation card
│   │   │   ├── auth-provider.tsx   # Auth context
│   │   │   ├── theme-provider.tsx  # Dark mode
│   │   │   └── theme-toggle.tsx    # Theme switch button
│   │   └── lib/
│   │       └── api.ts              # Backend API client
│   └── package.json
├── Dockerfile                      # Production container
├── railway.json                    # Railway deployment config
├── render.yaml                     # Render deployment config
└── Procfile
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) installed with Llama 3 model

### 1. Clone the repository

```bash
git clone https://github.com/NikhilNWakode/rag_med_system.git
cd rag_med_system
```

### 2. Set up the backend

```bash
# Pull the Llama 3 model
ollama pull llama3

# Create virtual environment and install dependencies
cd backend
python -m venv venv
source venv/Scripts/activate    # Windows
# source venv/bin/activate      # macOS/Linux

pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start the backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

> First run downloads embedding (~130MB) and reranker (~110MB) models automatically.

### 3. Set up the frontend

```bash
# In a new terminal
cd frontend
npm install

# Start the dev server
npm run dev
```

### 4. Use the app

1. Open **http://localhost:3000**
2. Ingest papers: enter a medical topic (e.g., "type 2 diabetes treatment 2024") on the home page
3. Go to **Chat** or **Search** and ask questions
4. Register an account to save conversations

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Create a new account |
| `POST` | `/api/auth/login` | Sign in and get JWT token |
| `GET` | `/api/auth/me` | Get current user info |
| `POST` | `/api/ingest` | Fetch & index papers from PubMed |
| `POST` | `/api/search` | One-shot RAG search with citations |
| `POST` | `/api/chat` | Conversational RAG with memory |
| `GET` | `/api/conversations` | List conversation history |
| `GET` | `/api/conversations/{id}/messages` | Get messages for a conversation |
| `DELETE` | `/api/conversations/{id}` | Delete a conversation |
| `GET` | `/api/conversations/{id}/export` | Export conversation as PDF |
| `GET` | `/api/health` | System health check |

### Example: Ingest papers

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"query": "type 2 diabetes treatment 2024", "max_results": 10}'
```

### Example: Search

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest treatments for type 2 diabetes?", "top_k": 5}'
```

Interactive API docs available at **http://localhost:8000/docs**

---

## Deployment

The app supports dual-mode deployment — same codebase works locally and in the cloud.

### Environment Variables for Cloud

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key (free tier, runs Llama 3 70B) |
| `QDRANT_URL` | Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | Qdrant Cloud API key |
| `JWT_SECRET` | Secret key for JWT tokens |

When `GROQ_API_KEY` is set, the app uses Groq instead of Ollama. When `QDRANT_URL` is set, it connects to Qdrant Cloud instead of local storage.

### Deploy to Railway

1. Push code to GitHub
2. Connect the repo on [Railway](https://railway.app)
3. Set environment variables (above)
4. Railway auto-detects the `Dockerfile` and deploys

### Deploy to Render

1. Push code to GitHub
2. Connect the repo on [Render](https://render.com)
3. Set environment variables
4. Render uses `render.yaml` for configuration

### Deploy Frontend to Vercel

1. Import the repo on [Vercel](https://vercel.com)
2. Set root directory to `frontend`
3. Set `NEXT_PUBLIC_API_URL` to your deployed backend URL

---

## Evaluation

Run the RAGAS evaluation pipeline to measure retrieval quality:

```bash
cd backend
python -m evaluation.evaluate
```

Metrics evaluated:
- **Substantive Answers** — Does the pipeline produce meaningful responses?
- **Citation Coverage** — Are sources properly cited with `[Source N]`?
- **Source Retrieval** — Are relevant papers retrieved for each query?

Results are saved to `data/evaluation_results.json`.

---

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

---

## How It Works

1. **Ingest** — User provides a medical topic. The system fetches papers from PubMed, chunks them into ~512 token segments, generates BGE embeddings, and stores them in Qdrant.

2. **Query** — User asks a natural language question. The system runs hybrid retrieval (BM25 keyword search + semantic vector search), combines results using Reciprocal Rank Fusion, and reranks the top candidates using a cross-encoder.

3. **Generate** — The top-ranked chunks are assembled into a context prompt. Llama 3 generates a cited, evidence-based answer grounded in the retrieved papers.

4. **Cite** — Every claim in the answer is linked to a specific source with `[Source N]` notation. Sources include title, authors, journal, year, and PubMed URL.

---

## License

MIT

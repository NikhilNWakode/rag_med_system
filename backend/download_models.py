"""Pre-download ML models during Docker build so startup is fast."""
from sentence_transformers import SentenceTransformer

print("Downloading embedding model: BAAI/bge-small-en-v1.5 ...")
SentenceTransformer("BAAI/bge-small-en-v1.5")

print("All models downloaded successfully.")
# Note: Reranker (bge-reranker-base) skipped in cloud mode to save memory.
# It loads on-demand in local mode only.

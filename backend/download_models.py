"""Pre-download ML models during Docker build so startup is fast."""
from sentence_transformers import SentenceTransformer, CrossEncoder

print("Downloading embedding model: BAAI/bge-small-en-v1.5 ...")
SentenceTransformer("BAAI/bge-small-en-v1.5")

print("Downloading reranker model: BAAI/bge-reranker-base ...")
CrossEncoder("BAAI/bge-reranker-base")

print("All models downloaded successfully.")

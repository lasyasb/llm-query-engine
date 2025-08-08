import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Dict

VECTOR_STORE_PATH = "app/document_store/vector_store.pkl"
CHUNKS_PATH = "app/document_store/raw_texts/chunks.pkl"

# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_relevant_clauses(document_text: str, question: str, top_k: int = 5) -> List[str]:
    """
    Retrieve top_k relevant text chunks (clauses) based on full document and question.
    This is a wrapper that simulates retrieval logic for the HackRx submission.
    """
    if not os.path.exists(VECTOR_STORE_PATH) or not os.path.exists(CHUNKS_PATH):
        raise FileNotFoundError("Vector store or text chunks not found. Run preprocessing first.")

    # Load vector index and chunk mapping
    with open(VECTOR_STORE_PATH, "rb") as f:
        index = pickle.load(f)

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)  # list of chunk_texts

    # Combine document and question into one string for context-aware embedding
    combined_query = f"{question}\n{document_text}"

    # Embed the query
    query_embedding = embedding_model.encode([combined_query])

    # Search top_k similar vectors
    D, I = index.search(query_embedding, top_k)

    return [chunks[i] for i in I[0]] 

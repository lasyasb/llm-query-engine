import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from typing import List

VECTOR_STORE_PATH = "app/document_store/vector_store.pkl"
CHUNKS_PATH = "app/document_store/raw_texts/chunks.pkl"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_relevant_clauses(question: str, top_k: int = 5) -> List[str]:
    """
    Retrieve top_k relevant text chunks (clauses) based on user question.
    """
    if not os.path.exists(VECTOR_STORE_PATH) or not os.path.exists(CHUNKS_PATH):
        raise FileNotFoundError("Vector store or text chunks not found. Run preprocessing first.")

    # Load FAISS index and document chunks
    with open(VECTOR_STORE_PATH, "rb") as f:
        index = pickle.load(f)

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    # Embed just the question (not full doc)
    query_embedding = embedding_model.encode([question])

    # Search in the vector store
    D, I = index.search(query_embedding, top_k)

    # Debug
    print("\n🔍 Top matched chunks:")
    for i in I[0]:
        print(f"---\n{chunks[i]}\n")

    return [chunks[i] for i in I[0]]

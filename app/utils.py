
import os
import re
import pickle
from typing import List
from sentence_transformers import SentenceTransformer
import faiss

UPLOAD_DIR = "app/document_store/uploads"
TEXT_DIR = "app/document_store/raw_texts"
VECTOR_STORE_PATH = "app/document_store/vector_store.pkl"
CHUNKS_PATH = "app/document_store/raw_texts/chunks.pkl"

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".pdf":
            import fitz
            with fitz.open(filepath) as doc:
                return "\n".join([page.get_text() for page in doc])
        elif ext == ".docx":
            from docx import Document
            doc = Document(filepath)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext == ".eml":
            from email import policy
            from email.parser import BytesParser
            with open(filepath, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)
            return msg.get_body(preferencelist=('plain')).get_content()
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to extract text from {filepath}: {e}")

def chunk_text(text: str, max_len: int = 512) -> List[str]:
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, chunk = [], ""
    for sentence in sentences:
        if len(chunk) + len(sentence) <= max_len:
            chunk += " " + sentence
        else:
            chunks.append(chunk.strip())
            chunk = sentence
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def build_vector_store():
    all_chunks = []
    print(f"📂 Scanning uploaded files in: {UPLOAD_DIR}")
    if not os.path.exists(UPLOAD_DIR):
        print("⚠️ No uploaded files found.")
        return
    for fname in os.listdir(UPLOAD_DIR):
        fpath = os.path.join(UPLOAD_DIR, fname)
        try:
            raw_text = extract_text(fpath)
            chunks = chunk_text(raw_text)
            all_chunks.extend(chunks)
            print(f"✅ Processed {fname} into {len(chunks)} chunks.")
        except Exception as e:
            print(f"❌ Error in {fname}: {e}")
    if not all_chunks:
        raise RuntimeError("No valid text chunks found. Cannot build vector store.")
    os.makedirs(TEXT_DIR, exist_ok=True)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(all_chunks, f)
    embeddings = model.encode(all_chunks, show_progress_bar=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    with open(VECTOR_STORE_PATH, "wb") as f:
        pickle.dump(index, f)
    print("🎉 Vector store created and saved!")

def vector_store_exists() -> bool:
    return os.path.exists(VECTOR_STORE_PATH) and os.path.exists(CHUNKS_PATH)

if __name__ == "__main__":
    build_vector_store()

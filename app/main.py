
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.models import QueryResponse
from app.parser import parse_query
from app.retriever import retrieve_relevant_clauses

from app.reasoner import get_llm_decision
from app.utils import build_vector_store, vector_store_exists
from app.hackrx_api import router as hackrx_router
from app import hackrx_api
import os

app = FastAPI()
app.include_router(hackrx_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "app/document_store/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/query", response_model=QueryResponse)
async def process_query(query: str = Form(...), file: UploadFile = File(None)):
    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        print(f"📂 Uploaded file saved to: {file_path}")

    if not vector_store_exists():
        build_vector_store()

    parsed = parse_query(query)
    clauses = get_relevant_clauses(parsed)
    decision = get_llm_decision(query, clauses)
    return decision

# 🔥 MOUNT STATIC LAST
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

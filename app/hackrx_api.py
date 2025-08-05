from fastapi import APIRouter, Request, HTTPException, status, Header
from pydantic import BaseModel
from typing import List, Optional

from app.retriever import retrieve_relevant_clauses
from app.reasoner import get_llm_decision  # ✅ Correct function import

import os
from dotenv import load_dotenv

router = APIRouter()


load_dotenv()
API_KEY = os.getenv("API_KEY", "test-key")  # Fallback is optional
# ✅ Wrap in quotes

class HackRxRequest(BaseModel):
    documents: str  # (currently unused)
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]
@router.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(
    request: Request,
    body: HackRxRequest,
    authorization: Optional[str] = Header(None)
):
    print("👉 Received Authorization Header:", authorization)
    print("🔒 Expected API_KEY:", API_KEY)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.replace("Bearer", "").strip()

    if token != API_KEY:
        print("❌ Token mismatch:", token, "!=", API_KEY)
        raise HTTPException(status_code=401, detail="Invalid API Key")

    print("✅ Authorization successful")



    answers = []
    for question in body.questions:
        try:
        # Pass both the document and the question
            clauses = retrieve_relevant_clauses(body.documents, question)


            result = get_llm_decision(question, clauses)
            answer = result.justification.summary  # Or use .dict() for detailed structure
        except Exception as e:
            answer = f"Error processing question: {str(e)}"

        answers.append(answer)


    return {"answers": answers}


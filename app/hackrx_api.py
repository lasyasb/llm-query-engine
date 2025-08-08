# app/main.py or wherever your router is defined
from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Union
import os
from dotenv import load_dotenv

from app.retriever import retrieve_relevant_clauses
from app.reasoner import get_llm_decision
router = APIRouter()
load_dotenv()
API_KEY = os.getenv("API_KEY", "test-key")
class HackRxRequest(BaseModel):
    documents: Optional[str] = None
    questions: List[str]
    instruction: Optional[str] = None  # future use

class HackRxResponse(BaseModel):
    answers: List[str]

@router.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(
    request: Request,
    body: HackRxRequest,
    authorization: Optional[str] = Header(None)
):
    print("👉 Received Authorization Header:", authorization)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    print("✅ Authorization header received and accepted")

    answers = []
    for idx, question in enumerate(body.questions):
        print(f"\n📌 Q{idx+1}: {question}")
        try:
            if body.documents:
                clauses = retrieve_relevant_clauses(body.documents, question)
                result = get_llm_decision(question, clauses)
                source = "📄 (from document)"
            else:
                result = get_llm_decision(question, clauses=[])
                source = "🧠 (general knowledge)"

            answer = result.justification.summary.strip()
            print(f"🟩 {answer} {source}")
        except Exception as e:
            answer = f"❌ Error processing question: {str(e)}"
            print(answer)
        answers.append(answer)

    return {"answers": answers}

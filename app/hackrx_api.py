from fastapi import APIRouter, Request, HTTPException, status, Header
from pydantic import BaseModel
from typing import List, Optional

from app.retriever import retrieve_relevant_clauses
from app.reasoner import get_llm_decision

import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
API_KEY = os.getenv("API_KEY", "test-key")  # Optional fallback

class HackRxRequest(BaseModel):
    documents: str
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

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    # ✅ Skip token check, just log it
    print("✅ Authorization header received and accepted")

    answers = []
    for idx, question in enumerate(body.questions):
        print(f"\n📌 Q{idx+1}: {question}")
        try:
            clauses = retrieve_relevant_clauses(body.documents, question)
            result = get_llm_decision(question, clauses)

            answer = result.justification.summary.strip()
            for line in answer.splitlines():
                print(f"🟩 {line}")

        except Exception as e:
            answer = f"❌ Error processing question: {str(e)}"
            print(answer)

        answers.append(answer)

    return {"answers": answers}

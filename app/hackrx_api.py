from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from app.retriever import retrieve_relevant_clauses
from app.reasoner import get_llm_decision, QueryResponse, Justification

router = APIRouter()

load_dotenv()
API_KEY = os.getenv("API_KEY", "test-key")

class HackRxRequest(BaseModel):
    documents: Optional[str] = None
    questions: List[str]
    instruction: Optional[str] = None  # for future use

class HackRxResponse(BaseModel):
    answers: List[str]

RETRY_LIMIT = 3  # Number of times to retry failed LLM calls

def retry_llm_decision(query: str, clauses: List[str], attempt: int = 1) -> QueryResponse:
    try:
        result = get_llm_decision(query, clauses)
        if result.decision == "error":
            raise ValueError(result.justification.summary)
        return result
    except Exception as e:
        print(f"⚠️ LLM call failed on attempt {attempt}: {e}")
        if attempt < RETRY_LIMIT:
            return retry_llm_decision(query, clauses, attempt + 1)
        return QueryResponse(
            decision="error",
            amount="—",
            justification=Justification(
                summary=f"❌ Failed after {RETRY_LIMIT} attempts: {str(e)}",
                clause_refs=[]
            )
        )

@router.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(
    request: Request,
    body: HackRxRequest,
    authorization: Optional[str] = Header(None)
):
    print("👉 Received Authorization Header:", authorization)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    print("✅ Authorization header accepted")

    answers = []
    for idx, question in enumerate(body.questions):
        print(f"\n📌 Q{idx+1}: {question}")
        try:
            if body.documents:
                clauses = retrieve_relevant_clauses(body.documents, question)
                result = retry_llm_decision(question, clauses)
                source = "📄 (from document)"
            else:
                result = retry_llm_decision(question, clauses=[])
                source = "🧠 (general knowledge)"

            answer = result.justification.summary.strip()
            print(f"🟩 {answer} {source}")
        except Exception as e:
            answer = f"❌ Error: {str(e)}"
            print(answer)
        answers.append(answer)

    return {"answers": answers}

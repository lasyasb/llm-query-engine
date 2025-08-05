import os
from dotenv import load_dotenv
import requests
from app.models import QueryResponse, Justification

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
API_URL = os.getenv("MISTRAL_API_BASE", "https://api.mistral.ai/v1")
MODEL_NAME = "mistral-small-latest"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

ESTIMATED_PAYOUTS = {
    "laparoscopic appendectomy": 40000,
    "tympanoplasty": 25000,
    "fissurectomy": 20000,
    "bariatric surgery": 120000,
    "dental extraction": 5000,
    "knee replacement": 180000,
    "fracture surgery": 60000,
    "appendectomy": 35000,
    "lipoma excision": 15000,
    "c-section": 45000,
    "cancer treatment": 200000,
    "heart bypass": 250000,
    "stroke hospitalization": 220000,
    "cataract surgery": 30000
}

def estimate_payout(procedure: str) -> int:
    for key, amount in ESTIMATED_PAYOUTS.items():
        if key in procedure.lower():
            return amount
    return 0

def build_prompt(user_query: str, clauses: list[str]) -> str:
    return f"""You are an intelligent insurance assistant.

Only use the retrieved policy clauses to answer the questions. If a clause is not found, say 'Not mentioned in the provided document.' Do not assume or guess general policy rules.
Always specify exact figures like waiting periods, limits, or percentages if mentioned.
If "cataract" is not mentioned in the retrieved document, say: "Not mentioned."
Never assume or generalize across policies.

User Question:
\"\"\"{user_query}\"\"\"

Relevant Policy Clauses:
{chr(10).join(f"- {clause}" for clause in clauses)}

Answer the question in a single sentence or two lines max, using simple and concise language.
"""

def get_llm_decision(user_query: str, clauses: list[str]) -> QueryResponse:
    prompt = build_prompt(user_query, clauses)

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    response = requests.post(f"{API_URL}/chat/completions", headers=HEADERS, json=payload)
    reply = response.json()
    content = reply["choices"][0]["message"]["content"].strip()

    ref_lines = [line for line in content.splitlines() if "clause" in line.lower() or "section" in line.lower()]

    return QueryResponse(
        decision="informational",
        amount="—",
        justification=Justification(
            summary=content,
            clause_refs=ref_lines[:3]
        )
    )

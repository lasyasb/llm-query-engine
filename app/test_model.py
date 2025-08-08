import csv
import requests
from tqdm import tqdm

CSV_PATH = "data/test_queries.csv"
MAX_CASES = 1000

API_URL = "https://scaling-telegram-5gxvwvxr5x963vg6r-8000.app.github.dev/hackrx/run"
AUTH_TOKEN = "test-token"

DOCUMENT_URL = "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D"

def call_hackrx_api(question):
    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "documents": DOCUMENT_URL,
                "questions": [question]
            },
            timeout=30
        )
        data = response.json()
        return data["answers"][0] if "answers" in data else "error"
    except Exception as e:
        return f"❌ API error: {str(e)}"

def extract_decision(text):
    if not isinstance(text, str):
        return "error"
    lowered = text.lower()
    if any(x in lowered for x in ["not covered", "excluded", "denied", "not payable", "no"]):
        return "no"
    if any(x in lowered for x in ["covered", "included", "approved", "payable", "yes"]):
        return "yes"
    return "error"

results = []

with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    for i, row in enumerate(tqdm(reader, total=MAX_CASES, desc="Evaluating via API")):
        if i >= MAX_CASES:
            break

        query = row["query"].strip()
        expected = row["expected"].strip().lower()

        raw_answer = call_hackrx_api(query)
        predicted = extract_decision(raw_answer)
        match = predicted == expected

        results.append({
            "query": query,
            "expected": expected,
            "decision": predicted,
            "match": match,
            "answer": raw_answer
        })

# Stats
successful = [r for r in results if r["decision"] != "error"]
errors = len(results) - len(successful)
correct = sum(1 for r in successful if r["match"])

print(f"\n📊 Evaluation Results (n={len(successful)}):")
print(f"✅ Correct: {correct} ({correct / len(successful):.1%})")
print(f"❌ Incorrect: {len(successful) - correct}")
print(f"🚨 Errors: {errors}")

# Save full report
with open("evaluation_report.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["query", "expected", "decision", "match", "answer"])
    writer.writeheader()
    for r in results:
        writer.writerow(r)

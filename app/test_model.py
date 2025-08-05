import sys
import os
import csv
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.reasoner import get_llm_decision
from app.retriever import get_relevant_clauses

CSV_PATH = "data/test_queries.csv"
MAX_CASES = 1000
RETRY_LIMIT = 3  # Max retries for failed API calls

def evaluate_case(query, clauses, attempt=1):
    try:
        result = get_llm_decision(query, clauses)
        if result.decision == "error":
            raise ValueError(result.justification.summary)
        return result
    except Exception as e:
        if attempt < RETRY_LIMIT:
            return evaluate_case(query, clauses, attempt+1)
        return QueryResponse(
            decision="error",
            amount="—",
            justification=Justification(
                summary=f"Failed after {RETRY_LIMIT} attempts: {str(e)}",
                clause_refs=[]
            )
        )

with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    results = []
    
    for row in tqdm(reader, desc="Evaluating", total=MAX_CASES):
        if len(results) >= MAX_CASES:
            break
            
        query = row["query"].strip()
        expected = row["expected"].strip().lower()
        clauses = get_relevant_clauses({"query": query})
        
        result = evaluate_case(query, clauses)
        results.append({
            "query": query,
            "expected": expected,
            "result": result,
            "match": result.decision.lower() == expected if result.decision != "error" else False
        })

# Calculate statistics
successful = [r for r in results if r["result"].decision != "error"]
errors = len(results) - len(successful)
correct = sum(1 for r in successful if r["match"])

print(f"\nEvaluation Results (n={len(successful)}):")
print(f"✅ Correct: {correct} ({correct/len(successful):.1%})")
print(f"❌ Incorrect: {len(successful)-correct}")
print(f"🚨 Errors: {errors} (API failures)")

# Save detailed report
with open("evaluation_report.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["query", "expected", "decision", "amount", "match", "error"])
    writer.writeheader()
    for r in results:
        writer.writerow({
            "query": r["query"],
            "expected": r["expected"],
            "decision": r["result"].decision,
            "amount": r["result"].amount,
            "match": r.get("match", "N/A"),
            "error": r["result"].justification.summary if r["result"].decision == "error" else ""
        })
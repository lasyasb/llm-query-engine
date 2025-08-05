import re
from typing import Dict

def parse_query(query: str) -> Dict[str, str]:
    """
    Parse a user query like:
    '46M, knee surgery in Pune, 3-month-old insurance policy'
    into structured components.
    """
    result = {
        "age": None,
        "gender": None,
        "procedure": None,
        "location": None,
        "policy_duration_months": None,
    }

    # Extract age + gender (e.g., 46M, 32F)
    age_gender_match = re.search(r"(?P<age>\d{2})(?P<gender>[MF])", query, re.IGNORECASE)
    if age_gender_match:
        result["age"] = age_gender_match.group("age")
        result["gender"] = age_gender_match.group("gender").upper()

    # Extract policy duration (e.g., "3-month", "6 months", etc.)
    duration_match = re.search(r"(\d+)\s*[- ]?(month|months)", query, re.IGNORECASE)
    if duration_match:
        result["policy_duration_months"] = duration_match.group(1)

    # Extract procedure (greedy grab of common medical keywords)
    procedure_match = re.search(r"(surgery|operation|treatment|procedure|injury|fracture|therapy|scan|replacement)", query, re.IGNORECASE)
    if procedure_match:
        start = procedure_match.start()
        result["procedure"] = query[start:].split(",")[0].strip()

    # Extract location (after 'in <location>')
    location_match = re.search(r"in ([A-Z][a-zA-Z ]+)", query)
    if location_match:
        result["location"] = location_match.group(1).strip()

    return result

from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., example="46M, knee surgery, Pune, 3-month policy")


class Justification(BaseModel):
    summary: str
    clause_refs: List[str]


class QueryResponse(BaseModel):
    decision: str = Field(..., example="approved")
    amount: Optional[str] = Field(None, example="₹50,000")
    justification: Justification

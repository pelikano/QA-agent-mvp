from pydantic import BaseModel
from typing import List, Literal

class QAAnalysis(BaseModel):
    summary: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    missing_definitions: List[str]
    acceptance_criteria_proposed: List[str]
    edge_cases: List[str]
    automation_notes: str

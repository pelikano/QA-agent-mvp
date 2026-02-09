from .schemas import QAAnalysis
from pydantic import ValidationError

def validate_output(output: dict) -> dict:
    try:
        return QAAnalysis(**output).dict()
    except ValidationError as e:
        raise ValueError(f"Invalid output schema: {e}")

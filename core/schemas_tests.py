from typing import List
from pydantic import BaseModel


class Scenario(BaseModel):
    name: str
    steps: List[str]


class Feature(BaseModel):
    feature_name: str
    description: str
    scenarios: List[Scenario]


class UpdatedTestSuite(BaseModel):
    features: List[Feature]
    change_summary: List[str]

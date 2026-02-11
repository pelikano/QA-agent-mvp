
from typing import List
from pydantic import BaseModel

class Scenario(BaseModel):
    name: str
    steps: List[str]

class Feature(BaseModel):
    feature_name: str
    scenarios: List[Scenario]

class TestSuite(BaseModel):
    features: List[Feature]

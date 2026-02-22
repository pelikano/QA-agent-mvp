from pydantic import BaseModel
from typing import List


class Scenario(BaseModel):
    name: str
    steps: List[str]


class Feature(BaseModel):
    screen_name: str
    feature_group: str
    feature_name: str
    description: str
    scenarios: List[Scenario]


class InitialGeneration(BaseModel):
    features: List[Feature]
    change_summary: List[str]
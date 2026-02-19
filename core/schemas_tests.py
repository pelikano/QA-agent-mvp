
from pydantic import BaseModel
from typing import List, Optional


class ChangeAction(BaseModel):
    action: str  # create_feature | delete_feature | create_scenario | delete_scenario | update_step
    screen: str
    feature: str
    scenario: Optional[str] = None
    step_index: Optional[int] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class UpdatePlan(BaseModel):
    changes: List[ChangeAction]

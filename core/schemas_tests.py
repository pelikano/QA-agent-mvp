from pydantic import BaseModel, model_validator
from typing import List, Optional
from enum import Enum


class ActionType(str, Enum):
    create_feature = "create_feature"
    delete_feature = "delete_feature"
    create_scenario = "create_scenario"
    delete_scenario = "delete_scenario"
    update_step = "update_step"


class ChangeAction(BaseModel):
    action: ActionType
    screen: str
    feature: str
    scenario: Optional[str]
    step_index: Optional[int]
    old_value: Optional[str]
    new_value: Optional[str]

    @model_validator(mode="after")
    def validate_update_step_fields(self):
        if self.action == ActionType.update_step:
            if self.old_value is None or self.new_value is None:
                raise ValueError("update_step requires old_value and new_value")
        return self


class UpdatePlan(BaseModel):
    changes: List[ChangeAction]

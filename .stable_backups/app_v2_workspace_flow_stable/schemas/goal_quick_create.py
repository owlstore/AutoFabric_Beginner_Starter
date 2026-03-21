from pydantic import BaseModel
from typing import Optional

class GoalQuickCreateRequest(BaseModel):
    user_input: str

class GoalQuickCreateResponse(BaseModel):
    id: int
    raw_input: str
    parsed_goal: dict
    goal_type: Optional[str] = None
    risk_level: Optional[str] = None
    recommended_next_action: str

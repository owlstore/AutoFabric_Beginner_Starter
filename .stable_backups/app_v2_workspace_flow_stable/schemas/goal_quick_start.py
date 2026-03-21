from pydantic import BaseModel
from typing import Any

class GoalQuickStartRequest(BaseModel):
    user_input: str

class GoalQuickStartResponse(BaseModel):
    goal: dict[str, Any]
    outcome: dict[str, Any]
    recommended_next_action: dict[str, Any]

from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class GoalCreate(BaseModel):
    raw_input: str
    parsed_goal: dict[str, Any]
    goal_type: Optional[str] = None
    risk_level: Optional[str] = None

class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    raw_input: str
    parsed_goal: dict[str, Any]
    goal_type: Optional[str]
    risk_level: Optional[str]
    created_at: datetime

class OutcomeCreate(BaseModel):
    goal_id: int
    title: str
    status: str = "draft"
    current_result: dict[str, Any] = {}
    next_action: Optional[str] = None
    risk_boundary: Optional[str] = None

class OutcomeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    title: str
    status: str
    current_result: dict[str, Any]
    next_action: Optional[str]
    risk_boundary: Optional[str]
    created_at: datetime
    updated_at: datetime

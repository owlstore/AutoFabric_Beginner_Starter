from typing import Any, Optional
from pydantic import BaseModel


class GoalParseRequest(BaseModel):
    user_input: str


class ParserMeta(BaseModel):
    source: str
    llm_enabled: bool


class GoalParseResponse(BaseModel):
    raw_input: str
    parsed_goal: dict[str, Any]
    goal_type: str
    risk_level: str
    parser_meta: Optional[ParserMeta] = None

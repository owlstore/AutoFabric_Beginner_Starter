from pydantic import BaseModel
from typing import Any, Optional

class ActionExecuteRequest(BaseModel):
    action_type: str
    target: str
    payload: Optional[dict[str, Any]] = None

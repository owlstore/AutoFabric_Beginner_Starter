from pydantic import BaseModel
from typing import Any, Optional

class OutcomeProgressRequest(BaseModel):
    status: str
    stage: str
    summary: str
    next_action: Optional[dict[str, Any]] = None

from pydantic import BaseModel
from typing import Any

class OpenClawRunRequest(BaseModel):
    task_name: str
    payload: dict[str, Any]

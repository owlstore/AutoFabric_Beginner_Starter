from pydantic import BaseModel
from typing import Optional

class EntrySubmitRequest(BaseModel):
    user_input: str
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    notes: Optional[str] = None

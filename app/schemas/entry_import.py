from pydantic import BaseModel
from typing import Optional

class EntryImportRequest(BaseModel):
    user_input: str
    source_type: str
    source_ref: str
    notes: Optional[str] = None

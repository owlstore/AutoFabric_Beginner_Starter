from pydantic import BaseModel

class EntryStartRequest(BaseModel):
    user_input: str

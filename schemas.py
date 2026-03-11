from pydantic import BaseModel
from typing import List
from datetime import datetime

class MessageRequest(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str | None = None
    file_path: str | None = None
    file_type: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    system_prompt: str | None = None

class SessionResponse(BaseModel):
    id: int
    system_prompt: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class SessionHistoryResponse(SessionResponse):
    messages: List[MessageResponse] = []

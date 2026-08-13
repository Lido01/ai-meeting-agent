from pydantic import BaseModel
from typing import Optional


# Data the client sends when creating a meeting
class MeetingCreate(BaseModel):
    title: str
    user_id: int


# Data the API returns
class MeetingResponse(MeetingCreate):
    id: int
    transcript_text: Optional[str] = None
    summary_text: Optional[str] = None
    status: str

    class Config:
        from_attributes = True
from pydantic import BaseModel
from typing import Optional


class MeetingCreate(BaseModel):
    title: str
    user_id: int


class MeetingResponse(MeetingCreate):
    id: int
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    transcript_text: Optional[str] = None
    summary_text: Optional[str] = None
    status: str

    class Config:
        from_attributes = True
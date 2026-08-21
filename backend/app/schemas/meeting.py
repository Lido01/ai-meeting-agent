from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.task import TaskResponse

class MeetingCreate(BaseModel):
    title: str
    user_id: int


class MeetingResponse(BaseModel):
    id: int
    title: str
    user_id: int

    file_name: str | None = None
    file_path: str | None = None

    transcript_text: str | None = None
    summary_text: str | None = None
    status: str | None = None

    tasks: list[TaskResponse] = []

    class Config:
        from_attributes = True
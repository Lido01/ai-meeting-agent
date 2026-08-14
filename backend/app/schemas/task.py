from pydantic import BaseModel
from typing import Optional
from datetime import date


# Data sent when creating a task
class TaskCreate(BaseModel):
    description: str
    assigned_to: Optional[str] = None
    deadline: Optional[date] = None
    meeting_id: int


# Data returned by API
class TaskResponse(TaskCreate):
    id: int
    status: str

    class Config:
        from_attributes = True
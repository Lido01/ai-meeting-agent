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
class TaskResponse(BaseModel):
    id: int
    description: str
    assigned_to: str | None = None
    deadline: date | None = None
    status: str
    meeting_id: int

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    description: str | None = None
    assigned_to: str | None = None
    deadline: date | None = None
    status: str | None = None
    

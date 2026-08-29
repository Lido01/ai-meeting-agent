from typing import Optional, List

from pydantic import BaseModel


class ActionItem(BaseModel):
    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None


class ContextChangeResult(BaseModel):
    change_type: str

    task: str

    previous_value: Optional[str] = None

    new_value: Optional[str] = None

    evidence: str

    previous_meeting_id: Optional[int] = None


class MeetingAnalysisResult(BaseModel):

    meeting_summary: str

    action_items: List[ActionItem]

    context_changes: List[ContextChangeResult]
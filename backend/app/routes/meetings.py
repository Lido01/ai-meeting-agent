from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingResponse


router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)


# Create a new meeting
@router.post("/", response_model=MeetingResponse)
def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db)
):
    new_meeting = Meeting(
        title=meeting.title,
        user_id=meeting.user_id
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting
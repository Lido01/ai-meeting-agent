from fastapi import APIRouter, Depends, HTTPException
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


# Get all meetings
@router.get("/", response_model=list[MeetingResponse])
def get_meetings(db: Session = Depends(get_db)):

    # Get all meetings from PostgreSQL
    meetings = db.query(Meeting).all()

    return meetings


# Get one meeting by ID
@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):

    # Search PostgreSQL for the meeting
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id
    ).first()

    # If meeting doesn't exist
    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meeting
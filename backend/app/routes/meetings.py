from fastapi import APIRouter, Depends, HTTPException
from fastapi import UploadFile, File
from sqlalchemy.orm import Session

import os
import shutil

from app.database import get_db
from app.models.meeting import Meeting
from app.models.task import Task
from app.schemas.meeting import MeetingCreate, MeetingResponse

from app.services.gemini_service import transcribe_audio
from app.services.meeting_analysis import analyze_meeting


router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)


# ============================================================
# CREATE MEETING
# ============================================================

@router.post("/", response_model=MeetingResponse)
def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db)
):
    # Create a meeting manually
    new_meeting = Meeting(
        title=meeting.title,
        user_id=meeting.user_id
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting


# ============================================================
# GET ALL MEETINGS
# ============================================================

@router.get("/", response_model=list[MeetingResponse])
def get_meetings(
    db: Session = Depends(get_db)
):

    # Get all meetings from PostgreSQL
    meetings = db.query(Meeting).all()

    return meetings


# ============================================================
# GET ONE MEETING
# ============================================================

@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):

    # Search for the meeting
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id
    ).first()

    # Meeting doesn't exist
    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meeting


# ============================================================
# UPLOAD MEETING AUDIO
# ============================================================

@router.post("/upload")
def upload_meeting(
    title: str,
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # STEP 1: Save uploaded audio file
    # --------------------------------------------------------

    upload_dir = "uploads/meetings"

    # Create directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(
        upload_dir,
        file.filename
    )

    # Save uploaded file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    print("===== FILE SAVED =====")
    print(file_path)


    # --------------------------------------------------------
    # STEP 2: Transcribe audio using Gemini
    # --------------------------------------------------------

    try:

        transcript = transcribe_audio(file_path)

        print("===== TRANSCRIPT =====")
        print(transcript)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


    # --------------------------------------------------------
    # STEP 3: Analyze transcript
    # --------------------------------------------------------

    try:

        analysis = analyze_meeting(transcript)

        print("===== GEMINI ANALYSIS =====")
        print(analysis)

        summary = analysis.get(
            "summary",
            ""
        )

        action_items = analysis.get(
            "action_items",
            []
        )

        print("===== ACTION ITEMS =====")
        print(action_items)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Meeting analysis failed: {str(e)}"
        )


    # --------------------------------------------------------
    # STEP 4: Create Meeting database record
    # --------------------------------------------------------

    new_meeting = Meeting(
        title=title,
        user_id=user_id,
        file_name=file.filename,
        file_path=file_path,
        transcript_text=transcript,
        summary_text=summary,
        status="analyzed"
    )

    try:

        db.add(new_meeting)

        # Save meeting first
        db.commit()

        # Get generated meeting ID
        db.refresh(new_meeting)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not save meeting: {str(e)}"
        )


    # --------------------------------------------------------
    # STEP 5: Create Tasks from Gemini action items
    # --------------------------------------------------------

    created_tasks = []

    try:

        for item in action_items:

            print("===== CREATING TASK =====")
            print(item)

            # Safely get values from Gemini
            description = item.get(
                "description",
                ""
            )

            assignee = item.get(
                "assignee"
            )

            deadline = item.get(
                "deadline"
            )

            # Create Task
            new_task = Task(
                description=description,
                assigned_to=assignee,
                deadline=deadline,
                status="open",
                meeting_id=new_meeting.id
            )

            db.add(new_task)

            created_tasks.append({
                "description": description,
                "assigned_to": assignee,
                "deadline": deadline,
                "status": "open"
            })

        # Save tasks
        db.commit()

    except Exception as e:

        # Cancel failed database transaction
        db.rollback()

        print("===== TASK ERROR =====")
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Could not save tasks: {str(e)}"
        )


    # --------------------------------------------------------
    # STEP 6: Return result
    # --------------------------------------------------------

    return {
        "message": "Meeting processed successfully",

        "meeting_id": new_meeting.id,

        "status": new_meeting.status,

        "summary": summary,

        "action_items": action_items,

        "created_tasks": created_tasks
    }
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

import os
import shutil
import uuid
import json

from app.database import get_db

from app.models.meeting import Meeting
from app.models.task import Task

from app.schemas.meeting import MeetingCreate, MeetingResponse

from app.services.gemini_service import transcribe_audio
from app.services.mcp_service import get_previous_context
from app.services.meeting_agent import create_meeting_agent
from app.services.date_parser import parse_deadline
from app.dependencies.auth import get_current_user

# ROUTER
router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)

# CREATE MEETING MANUALLY
@router.post("/", response_model=MeetingResponse)
def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a meeting without uploading an audio file.

    This is useful for creating a basic meeting record.
    """

    new_meeting = Meeting(
        title=meeting.title,
        user_id=meeting.user_id,
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting

# GET ALL MEETINGS FOR A USER
@router.get("/", response_model=list[MeetingResponse])
def get_meetings(
    user_id: int,
    db: Session = Depends(get_db)
    
):
    """
    Return only meetings belonging to this user.
    """

    meetings = (
        db.query(Meeting)
        .filter(Meeting.user_id == user_id)
        .all()
    )

    return meetings

# GET A SPECIFIC MEETING BY ID
@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    meeting = (
        db.query(Meeting)
        .filter(
            Meeting.id == meeting_id,
            Meeting.user_id == current_user_id
        )
        .first()
    )

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meeting
# UPLOAD AND PROCESS MEETING AUDIO
@router.post("/upload")
def upload_meeting(
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    
    # STEP 1: SAVE UPLOADED AUDIO
    

    upload_dir = "uploads/meetings"

    # Create upload directory if it doesn't exist
    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    # Create a unique filename. This prevents two users from having the same filename.
    file_extension = os.path.splitext(
        file.filename
    )[1].lower()

    safe_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    file_path = os.path.join(
        upload_dir,
        safe_filename
    )

    # Save uploaded file to disk
    try:

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        print("===== FILE SAVED =====")
        print(file_path)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save uploaded file: {str(e)}"
        )

    # STEP 2: TRANSCRIBE AUDIO
    try:

        # Send audio to Gemini transcription service
        transcript = transcribe_audio(
            file_path
        )

        print("===== TRANSCRIPT =====")
        print(transcript)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )

    # STEP 3: GET PREVIOUS MEETING CONTEXT
    try:

        # Get previous meetings belonging to this user.
        # This is our current MCP/context layer.
        previous_context = get_previous_context(
            db=db,
            user_id=current_user_id
        )

        print("===== PREVIOUS CONTEXT =====")
        print(previous_context)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not get previous meeting context: {str(e)}"
        )

    # STEP 4: CONVERT CONTEXT TO TEXT
    context_text = ""

    for previous_meeting in previous_context:

        context_text += f"""
Previous Meeting ID:
{previous_meeting["meeting_id"]}

Title:
{previous_meeting["title"]}

Summary:
{previous_meeting["summary"]}

Transcript:
{previous_meeting["transcript"]}

--------------------------------
"""

    # If this is the user's first meeting
    if not context_text:

        context_text = (
            "No previous meeting context is available."
        )

    # STEP 5: RUN AI MEETING AGENT
    try:

        # Send: Current transcript + Previous meeting context to Gemini through our AI Agent.
        agent_result = create_meeting_agent(
            transcript=transcript,
            context=context_text
        )

        print("===== RAW AI AGENT RESULT =====")
        print(agent_result)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI Agent failed: {str(e)}"
        )

    # STEP 6: CONVERT AI RESPONSE TO PYTHON DICTIONARY
    try:

        agent_result = (
            agent_result
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        # Convert JSON string → Python dictionary
        analysis = json.loads(
            agent_result
        )

        print("===== AI ANALYSIS =====")
        print(analysis)

    except json.JSONDecodeError as e:

        print("===== JSON ERROR =====")
        print(agent_result)

        raise HTTPException(
            status_code=500,
            detail=f"AI Agent returned invalid JSON: {str(e)}"
        )

    # STEP 7: GET SUMMARY AND ACTION ITEMS
    summary = analysis.get(
        "meeting_summary",
        ""
    )

    action_items = analysis.get(
        "action_items",
        []
    )

    print("===== SUMMARY =====")
    print(summary)

    print("===== ACTION ITEMS =====")
    print(action_items)

    # STEP 8: CREATE MEETING DATABASE RECORD
    new_meeting = Meeting(
        title=title,
        user_id=current_user_id,
        file_name=safe_filename,
        file_path=file_path,
        transcript_text=transcript,
        summary_text=summary,

        status="analyzed"
    )

    try:
        db.add(new_meeting)
        db.commit()
        db.refresh(new_meeting) # Get generated meeting ID

        print("===== MEETING SAVED =====")
        print("Meeting ID:", new_meeting.id)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not save meeting: {str(e)}"
        )

    # STEP 9: CREATE TASKS
    created_tasks = []

    try:

        for item in action_items:

            print("===== CREATING TASK =====")
            print(item)

            description = (
                item.get("task")
                or item.get("description")
                or ""
            )


            # Person responsible
            assignee = item.get(
                "assignee"
            )

            deadline = parse_deadline(
                item.get("deadline")
            )

            print(
                "Parsed deadline:",
                deadline
            )


            # Don't create an empty task
            if not description:

                print(
                    "Skipping task because description is empty."
                )

                continue


            # Create PostgreSQL Task object
            new_task = Task(
                description=description,
                assigned_to=assignee,
                deadline=deadline,
                status="open",

                # Connect task to this meeting
                meeting_id=new_meeting.id
            )

            db.add(new_task)


            # Add task to response
            created_tasks.append({
                "description": description,
                "assigned_to": assignee,
                "deadline": (
                    str(deadline)
                    if deadline
                    else None
                ),
                "status": "open",
                "meeting_id": new_meeting.id
            })


        # Save all tasks
        db.commit()

        print("===== TASKS SAVED =====")
        print(
            f"{len(created_tasks)} task(s) created."
        )

    except Exception as e:

        # Cancel failed database transaction
        db.rollback()

        print("===== TASK ERROR =====")
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Could not save tasks: {str(e)}"
        )

    # STEP 10: RETURN FINAL RESULT
    return {

        "message": (
            "Meeting processed successfully"
        ),

        "meeting_id": new_meeting.id,

        "status": new_meeting.status,

        "summary": summary,

        "action_items": action_items,

        "created_tasks": created_tasks
    }
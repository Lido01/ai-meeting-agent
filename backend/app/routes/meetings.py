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


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)


# ============================================================
# CREATE MEETING MANUALLY
# ============================================================

@router.post("/", response_model=MeetingResponse)
def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Create a meeting manually.

    The user_id is taken from the authenticated JWT token.
    The client should NOT send user_id manually.
    """

    new_meeting = Meeting(
        title=meeting.title,
        user_id=current_user_id,
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting


# ============================================================
# GET ALL MEETINGS FOR CURRENT USER
# ============================================================

@router.get("/", response_model=list[MeetingResponse])
def get_meetings(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Return only meetings belonging to the authenticated user.

    IMPORTANT:
    The frontend does not need to send ?user_id=...
    The user ID comes from the JWT authentication token.
    """

    meetings = (
        db.query(Meeting)
        .filter(
            Meeting.user_id == current_user_id
        )
        .order_by(
            Meeting.id.desc()
        )
        .all()
    )

    return meetings


# ============================================================
# GET SPECIFIC MEETING
# ============================================================

@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse
)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Return one meeting only if it belongs to the authenticated user.
    """

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


# ============================================================
# UPLOAD AND PROCESS MEETING AUDIO
# ============================================================

@router.post("/upload")
def upload_meeting(
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Upload meeting audio, transcribe it, analyze it with the
    AI meeting agent, save the meeting, and create action items.
    """

    # ========================================================
    # STEP 1: SAVE UPLOADED AUDIO
    # ========================================================

    upload_dir = "uploads/meetings"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    file_extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    safe_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    file_path = os.path.join(
        upload_dir,
        safe_filename
    )

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

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

    # ========================================================
    # STEP 2: TRANSCRIBE AUDIO
    # ========================================================

    try:

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

    # ========================================================
    # STEP 3: GET PREVIOUS MEETING CONTEXT
    # ========================================================

    try:

        previous_context = get_previous_context(
            db=db,
            user_id=current_user_id
        )

        print("===== PREVIOUS CONTEXT =====")
        print(previous_context)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not get previous meeting context: "
                f"{str(e)}"
            )
        )

    # ========================================================
    # STEP 4: CONVERT CONTEXT TO TEXT
    # ========================================================

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

    if not context_text:

        context_text = (
            "No previous meeting context is available."
        )

    # ========================================================
    # STEP 5: RUN AI MEETING AGENT
    # ========================================================

    try:

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

    # ========================================================
    # STEP 6: CONVERT AI RESPONSE TO DICTIONARY
    # ========================================================

    try:

        # Handle Gemini markdown JSON fences.
        if isinstance(agent_result, str):

            agent_result = (
                agent_result
                .replace("```json", "")
                .replace("```JSON", "")
                .replace("```", "")
                .strip()
            )

            analysis = json.loads(
                agent_result
            )

        elif isinstance(agent_result, dict):

            analysis = agent_result

        else:

            raise ValueError(
                "Unexpected AI agent response type."
            )

        print("===== AI ANALYSIS =====")
        print(analysis)

    except (
        json.JSONDecodeError,
        ValueError,
        TypeError
    ) as e:

        print("===== JSON ERROR =====")
        print(agent_result)

        raise HTTPException(
            status_code=500,
            detail=(
                "AI Agent returned invalid JSON: "
                f"{str(e)}"
            )
        )

    # ========================================================
    # STEP 7: GET SUMMARY AND ACTION ITEMS
    # ========================================================

    summary = analysis.get(
        "meeting_summary",
        ""
    )

    action_items = analysis.get(
        "action_items",
        []
    )

    # Make sure action_items is always a list.
    if not isinstance(
        action_items,
        list
    ):
        action_items = []

    print("===== SUMMARY =====")
    print(summary)

    print("===== ACTION ITEMS =====")
    print(action_items)

    # ========================================================
    # STEP 8: CREATE MEETING DATABASE RECORD
    # ========================================================

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

        db.refresh(
            new_meeting
        )

        print("===== MEETING SAVED =====")
        print(
            "Meeting ID:",
            new_meeting.id
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save meeting: "
                f"{str(e)}"
            )
        )

    # ========================================================
    # STEP 9: CREATE TASKS
    # ========================================================

    created_tasks = []

    try:

        for item in action_items:

            print("===== CREATING TASK =====")
            print(item)

            # Protect against malformed AI output.
            if not isinstance(
                item,
                dict
            ):
                continue

            description = (
                item.get("task")
                or item.get("description")
                or ""
            )

            description = str(
                description
            ).strip()

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

            # Do not create empty tasks.
            if not description:

                print(
                    "Skipping task because "
                    "description is empty."
                )

                continue

            new_task = Task(
                description=description,
                assigned_to=assignee,
                deadline=deadline,
                status="open",
                meeting_id=new_meeting.id
            )

            db.add(
                new_task
            )

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

        db.commit()

        print("===== TASKS SAVED =====")
        print(
            f"{len(created_tasks)} task(s) created."
        )

    except Exception as e:

        db.rollback()

        print("===== TASK ERROR =====")
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save tasks: "
                f"{str(e)}"
            )
        )

    # ========================================================
    # STEP 10: RETURN FINAL RESULT
    # ========================================================

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
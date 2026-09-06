from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from sqlalchemy.orm import Session

import os
import shutil
import uuid
import json

from app.database import get_db

from app.models.meeting import Meeting
from app.models.task import Task

from app.schemas.meeting import (
    MeetingCreate,
    MeetingResponse
)

from app.services.gemini_service import transcribe_audio
from app.services.mcp_service import get_previous_context
from app.services.meeting_agent import create_meeting_agent
from app.services.date_parser import parse_deadline
from app.services.context_continuity import (
    get_comparable_previous_meeting,
    run_context_continuity,
)

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

    This does not upload or analyze audio.
    """

    new_meeting = Meeting(
        title=meeting.title,
        user_id=current_user_id
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
    Return only meetings belonging to the logged-in user.
    """

    meetings = (
        db.query(Meeting)
        .filter(
            Meeting.user_id == current_user_id
        )
        .all()
    )

    return meetings


# ============================================================
# GET ONE MEETING
# ============================================================

@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get one meeting.

    The meeting must belong to the logged-in user.
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
    Main meeting processing pipeline.

    Flow:

    1. Save audio
    2. Transcribe audio
    3. Get previous meeting context
    4. Analyze current meeting
    5. Detect context continuity changes
    6. Save meeting
    7. Create tasks
    8. Save context changes as PENDING

    IMPORTANT:

    A detected context change does NOT automatically update
    an old task.

    It waits for user confirmation.
    """

    # ========================================================
    # STEP 1: SAVE UPLOADED AUDIO
    # ========================================================

    upload_dir = "uploads/meetings"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    # Get original file extension.
    file_extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    # Generate unique filename.
    # This prevents duplicate filenames.
    safe_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    file_path = os.path.join(
        upload_dir,
        safe_filename
    )

    try:

        # Save uploaded file to disk.
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
    # STEP 4: FIND THE MOST RECENT PREVIOUS MEETING
    # ========================================================

    previous_meeting = get_comparable_previous_meeting(
        db=db,
        user_id=current_user_id,
    )

    previous_meeting_id = (
        previous_meeting.id
        if previous_meeting is not None
        else None
    )

    print("===== PREVIOUS MEETING ID =====")
    print(previous_meeting_id)


    # ========================================================
    # STEP 5: CONVERT PREVIOUS CONTEXT INTO TEXT
    # ========================================================

    context_text = ""

    for previous_meeting in previous_context:

        context_text += f"""
Previous Meeting ID:
{previous_meeting.get("meeting_id")}

Title:
{previous_meeting.get("title")}

Summary:
{previous_meeting.get("summary")}

Transcript:
{previous_meeting.get("transcript")}

--------------------------------
"""


    # If this is the first meeting,
    # there is no previous context.

    if not context_text:

        context_text = (
            "No previous meeting context is available."
        )


    # ========================================================
    # STEP 6: RUN AI MEETING AGENT
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
    # STEP 7: CONVERT AI AGENT RESULT TO DICTIONARY
    # ========================================================

    try:

        # Gemini sometimes returns:

        # ```json
        # {...}
        # ```

        # Remove markdown if it appears.

        agent_result = (
            agent_result
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        analysis = json.loads(
            agent_result
        )

        if isinstance(analysis, str):
            analysis = json.loads(analysis)

        if not isinstance(analysis, dict):
            analysis = {}

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
    # STEP 8: GET SUMMARY AND ACTION ITEMS
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
    # STEP 9: CREATE CURRENT MEETING DATABASE RECORD
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

        db.add(
            new_meeting
        )

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
    # STEP 10: CREATE NEW TASKS
    # ========================================================

    created_tasks = []

    try:

        for item in action_items:

            print(
                "===== CREATING TASK ====="
            )

            print(item)

            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except (
                    json.JSONDecodeError,
                    TypeError,
                    ValueError
                ):
                    item = {"description": item}

            if not isinstance(item, dict):
                print(
                    "Skipping action item because it is not an object."
                )
                continue

            # Support both possible names:
            #
            # "task"
            #
            # or
            #
            # "description"

            description = (
                item.get("task")
                or item.get("description")
                or ""
            )

            # Person responsible.
            assignee = item.get(
                "assignee"
            )

            # Convert values such as:
            #
            # "2026-09-03"
            #
            # into Python date.
            #
            # Invalid values such as "Tomorrow"
            # should be handled by parse_deadline().

            deadline = parse_deadline(
                item.get("deadline")
            )

            print(
                "Parsed deadline:",
                deadline
            )

            # Never create an empty task.

            if not description:

                print(
                    "Skipping task because "
                    "description is empty."
                )

                continue

            # Create PostgreSQL Task.

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

            # Keep a copy for the API response.

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


        # Save all new tasks.

        db.commit()

        print(
            "===== TASKS SAVED ====="
        )

        print(
            f"{len(created_tasks)} task(s) created."
        )

    except Exception as e:

        db.rollback()

        print(
            "===== TASK ERROR ====="
        )

        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save tasks: "
                f"{str(e)}"
            )
        )


    # ========================================================
    # STEP 11: CONTEXT CONTINUITY ANALYSIS
    # ========================================================

    context_changes = []

    try:
        print("===== CONTEXT CONTINUITY CHECK =====")

        context_changes = run_context_continuity(
            db=db,
            user_id=current_user_id,
            current_meeting=new_meeting,
            previous_meeting=previous_meeting,
            current_transcript=transcript,
        )

        print("===== CONTEXT CHANGE RESULT =====")
        print(context_changes)

    except Exception as e:
        print("===== CONTEXT CONTINUITY ERROR =====")
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save context changes: "
                f"{str(e)}"
            )
        )


    # ========================================================
    # STEP 12: RETURN FINAL RESULT
    # ========================================================
    
    
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

        "created_tasks": created_tasks,

        # NEW:
        #
        # The frontend uses this to show
        # the Context Continuity Alert.

        "context_changes": context_changes
    }
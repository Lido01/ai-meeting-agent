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
from app.models.context_change import ContextChange

from app.schemas.meeting import (
    MeetingCreate,
    MeetingResponse
)

from app.services.gemini_service import transcribe_audio
from app.services.mcp_service import get_previous_context
from app.services.meeting_agent import create_meeting_agent
from app.services.date_parser import parse_deadline
from app.services.context_continuity import analyze_context_change

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
    db: Session = Depends(get_db)
):
    """
    Create a meeting manually.

    This does not upload or analyze audio.
    """

    new_meeting = Meeting(
        title=meeting.title,
        user_id=meeting.user_id
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

    previous_meeting_id = None

    if previous_context:

        # The context returned by MCP contains meeting_id.
        #
        # We use the latest item as the previous meeting
        # for the Context Continuity comparison.

        latest_previous_meeting = previous_context[-1]

        previous_meeting_id = (
            latest_previous_meeting.get(
                "meeting_id"
            )
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

        print("===== AI ANALYSIS =====")
        print(analysis)

    except json.JSONDecodeError as e:

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

    # Only compare if there is a previous meeting.

    if previous_meeting_id:

        try:

            print(
                "===== CONTEXT CONTINUITY CHECK ====="
            )

            # Compare:
            #
            # Previous meeting
            #
            # VS
            #
            # Current meeting

            context_result = analyze_context_change(
                previous_context=context_text,
                current_transcript=transcript,
                previous_meeting_id=previous_meeting_id
            )

            print(
                "===== CONTEXT CHANGE RESULT ====="
            )

            print(
                context_result
            )


            # =================================================
            # HANDLE THE CONTEXT ANALYSIS RESULT
            # =================================================

            change_type = context_result.get(
                "change_type"
            )

            task_name = context_result.get(
                "task"
            )

            previous_value = context_result.get(
                "previous_value"
            )

            new_value = context_result.get(
                "new_value"
            )

            evidence = context_result.get(
                "evidence"
            )

            detected_previous_meeting_id = (
                context_result.get(
                    "previous_meeting_id"
                )
            )


            # =================================================
            # ONLY SAVE A CHANGE IF A REAL CHANGE WAS FOUND
            # =================================================

            if (
                change_type
                and change_type.lower()
                not in [
                    "none",
                    "no_change",
                    "no change"
                ]
            ):

                # Try to find the related existing task.

                related_task = None

                if task_name:

                    # Search user's previous tasks
                    # through meetings.

                    related_task = (
                        db.query(Task)
                        .join(Meeting)
                        .filter(
                            Meeting.user_id
                            == current_user_id,

                            Task.description.ilike(
                                f"%{task_name}%"
                            )
                        )
                        .order_by(
                            Task.id.desc()
                        )
                        .first()
                    )


                # =================================================
                # CREATE PENDING CONTEXT CHANGE
                # =================================================

                new_change = ContextChange(

                    # Current meeting where
                    # the change was detected.
                    meeting_id=new_meeting.id,

                    # Previous meeting where
                    # the old value came from.
                    previous_meeting_id=(
                        detected_previous_meeting_id
                        or previous_meeting_id
                    ),

                    # Example:
                    #
                    # deadline_changed
                    # owner_changed
                    # decision_changed
                    #
                    change_type=change_type,

                    # Existing task that may need updating.
                    task_id=(
                        related_task.id
                        if related_task
                        else None
                    ),

                    # Old value.
                    previous_value=(
                        str(previous_value)
                        if previous_value is not None
                        else None
                    ),

                    # New value.
                    new_value=(
                        str(new_value)
                        if new_value is not None
                        else None
                    ),

                    # Evidence from transcript.
                    evidence=evidence,

                    # IMPORTANT:
                    #
                    # Do NOT automatically update the task.
                    #
                    # The frontend will later show:
                    #
                    # "Deadline changed from Aug 28
                    #  to Sep 3.
                    #
                    #  Confirm update?"
                    #
                    status="pending"
                )

                db.add(
                    new_change
                )

                db.commit()

                db.refresh(
                    new_change
                )


                # Add context change to response.

                context_changes.append({

                    "id": new_change.id,

                    "change_type": change_type,

                    "task": task_name,

                    "task_id": (
                        related_task.id
                        if related_task
                        else None
                    ),

                    "previous_value": (
                        previous_value
                    ),

                    "new_value": (
                        new_value
                    ),

                    "evidence": evidence,

                    "status": "pending",

                    "previous_meeting_id": (
                        detected_previous_meeting_id
                        or previous_meeting_id
                    ),

                    "meeting_id": new_meeting.id
                })

                print(
                    "===== CONTEXT CHANGE SAVED ====="
                )

                print(
                    context_changes[-1]
                )

            else:

                print(
                    "===== NO CONTEXT CHANGE DETECTED ====="
                )


        except Exception as e:

            db.rollback()

            print(
                "===== CONTEXT CONTINUITY ERROR ====="
            )

            print(str(e))

            # We do not want a context-analysis problem
            # to delete an already-successful meeting.
            #
            # The meeting and tasks are already saved.
            #
            # Therefore we return the meeting result
            # and report the context-analysis error.

            context_changes.append({
                "error": (
                    "Context continuity analysis failed"
                ),
                "detail": str(e)
            })


    # ========================================================
    # STEP 12: RETURN FINAL RESULT
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
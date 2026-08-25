from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.context_change import ContextChange
from app.models.task import Task
from app.models.meeting import Meeting

from app.dependencies.auth import get_current_user

from app.services.date_parser import parse_deadline


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/context-changes",
    tags=["Context Continuity"]
)


# ============================================================
# GET ALL CONTEXT CHANGES
# ============================================================

@router.get("/")
def get_context_changes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Return all context changes belonging to the logged-in user.

    The frontend can use this endpoint to display:

        Context Continuity Alerts

    Example:

        Payment API deadline changed
        August 28 -> September 3

        [Confirm] [Reject]
    """

    changes = (
        db.query(ContextChange)
        .join(
            Meeting,
            ContextChange.meeting_id == Meeting.id
        )
        .filter(
            Meeting.user_id == user_id
        )
        .order_by(
            ContextChange.created_at.desc()
        )
        .all()
    )

    return changes


# ============================================================
# GET PENDING CONTEXT CHANGES
# ============================================================

@router.get("/pending")
def get_pending_context_changes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Return only pending context changes.

    This is the main endpoint the frontend can call
    to display alerts that still need confirmation.
    """

    changes = (
        db.query(ContextChange)
        .join(
            Meeting,
            ContextChange.meeting_id == Meeting.id
        )
        .filter(
            Meeting.user_id == user_id,
            ContextChange.status == "pending"
        )
        .order_by(
            ContextChange.created_at.desc()
        )
        .all()
    )

    return changes


# ============================================================
# GET ONE CONTEXT CHANGE
# ============================================================

@router.get("/{change_id}")
def get_context_change(
    change_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Get one context change.

    The context change must belong to a meeting
    owned by the logged-in user.
    """

    change = (
        db.query(ContextChange)
        .join(
            Meeting,
            ContextChange.meeting_id == Meeting.id
        )
        .filter(
            ContextChange.id == change_id,
            Meeting.user_id == user_id
        )
        .first()
    )

    if not change:
        raise HTTPException(
            status_code=404,
            detail="Context change not found"
        )

    return change


# ============================================================
# CONFIRM CONTEXT CHANGE
# ============================================================

@router.post("/{change_id}/confirm")
def confirm_context_change(
    change_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Confirm a detected context change.

    Example:

        Previous deadline:
            August 28, 2026

        New deadline:
            September 3, 2026

    After the user confirms:

        Task.deadline
            becomes
        2026-09-03

    The ContextChange status becomes:

        confirmed
    """

    # ========================================================
    # STEP 1: FIND CONTEXT CHANGE
    # ========================================================

    change = (
        db.query(ContextChange)
        .join(
            Meeting,
            ContextChange.meeting_id == Meeting.id
        )
        .filter(
            ContextChange.id == change_id,
            Meeting.user_id == user_id
        )
        .first()
    )

    if not change:
        raise HTTPException(
            status_code=404,
            detail="Context change not found"
        )

    print("======================================")
    print("CONFIRMING CONTEXT CHANGE")
    print("Change ID:", change.id)
    print("Change type:", change.change_type)
    print("Task ID:", change.task_id)
    print("Previous value:", change.previous_value)
    print("New value:", change.new_value)
    print("Current status:", change.status)
    print("======================================")


    # ========================================================
    # STEP 2: MAKE SURE IT IS STILL PENDING
    # ========================================================

    if change.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Change is already {change.status}"
        )


    # ========================================================
    # STEP 3: FIND THE RELATED TASK
    # ========================================================

    task = None

    if change.task_id:

        task = (
            db.query(Task)
            .join(
                Meeting,
                Task.meeting_id == Meeting.id
            )
            .filter(
                Task.id == change.task_id,
                Meeting.user_id == user_id
            )
            .first()
        )

    # If the task does not exist, stop.
    #
    # We don't want to mark the context change as confirmed
    # when there is no task that can actually be updated.

    if not task:

        raise HTTPException(
            status_code=404,
            detail="Related task not found"
        )


    # ========================================================
    # STEP 4: UPDATE TASK
    # ========================================================

    if change.change_type == "deadline":

        print("===== DEADLINE UPDATE =====")

        print(
            "Old task deadline:",
            task.deadline
        )

        print(
            "New deadline text:",
            change.new_value
        )


        # ----------------------------------------------------
        # Convert Gemini text into Python date
        # ----------------------------------------------------

        parsed_deadline = parse_deadline(
            change.new_value
        )


        print(
            "Parsed deadline:",
            parsed_deadline
        )


        # ----------------------------------------------------
        # IMPORTANT:
        # Never save NULL when parsing fails.
        # ----------------------------------------------------

        if parsed_deadline is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not parse the new deadline: "
                    f"{change.new_value}"
                )
            )


        # ----------------------------------------------------
        # Update PostgreSQL Task
        # ----------------------------------------------------

        task.deadline = parsed_deadline


        print(
            "Task deadline after update:",
            task.deadline
        )


    # ========================================================
    # ASSIGNEE / OWNER CHANGE
    # ========================================================

    elif change.change_type in [
        "assignee",
        "owner"
    ]:

        print("===== ASSIGNEE UPDATE =====")

        print(
            "Old assignee:",
            task.assigned_to
        )

        print(
            "New assignee:",
            change.new_value
        )

        task.assigned_to = change.new_value


    # ========================================================
    # DECISION CHANGE
    # ========================================================

    elif change.change_type == "decision":

        """
        We don't update the Task for decision changes yet.

        Later we can create a MeetingDecision model/table.

        For now, the context change can still be confirmed.
        """

        print(
            "Decision change confirmed."
        )


    # ========================================================
    # UNKNOWN CHANGE TYPE
    # ========================================================

    else:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported context change type: "
                f"{change.change_type}"
            )
        )


    # ========================================================
    # STEP 5: MARK CHANGE AS CONFIRMED
    # ========================================================

    change.status = "confirmed"


    # ========================================================
    # STEP 6: SAVE EVERYTHING
    # ========================================================

    try:

        db.commit()

    except Exception as e:

        db.rollback()

        print(
            "===== CONFIRMATION DATABASE ERROR ====="
        )

        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not confirm context change: "
                f"{str(e)}"
            )
        )


    # ========================================================
    # STEP 7: REFRESH DATABASE OBJECTS
    # ========================================================

    db.refresh(task)
    db.refresh(change)


    print("======================================")
    print("CONTEXT CHANGE CONFIRMED")
    print("Change ID:", change.id)
    print("Task ID:", task.id)
    print("Task deadline:", task.deadline)
    print("Task assignee:", task.assigned_to)
    print("Status:", change.status)
    print("======================================")


    # ========================================================
    # STEP 8: RETURN RESULT
    # ========================================================

    return {

        "message": (
            "Context change confirmed successfully"
        ),

        "change_id": change.id,

        "status": change.status,

        "task_id": task.id,

        "task": task.description,

        "assigned_to": task.assigned_to,

        "updated_deadline": (
            str(task.deadline)
            if task.deadline
            else None
        ),

        "previous_deadline": (
            change.previous_value
            if change.change_type == "deadline"
            else None
        ),

        "new_deadline": (
            change.new_value
            if change.change_type == "deadline"
            else None
        )
    }


# ============================================================
# REJECT CONTEXT CHANGE
# ============================================================

@router.post("/{change_id}/reject")
def reject_context_change(
    change_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Reject a context change.

    IMPORTANT:

    The related Task is NOT changed.

    Only the ContextChange status becomes:

        rejected
    """

    # ========================================================
    # STEP 1: FIND CONTEXT CHANGE
    # ========================================================

    change = (
        db.query(ContextChange)
        .join(
            Meeting,
            ContextChange.meeting_id == Meeting.id
        )
        .filter(
            ContextChange.id == change_id,
            Meeting.user_id == user_id
        )
        .first()
    )

    if not change:
        raise HTTPException(
            status_code=404,
            detail="Context change not found"
        )


    # ========================================================
    # STEP 2: MAKE SURE IT IS STILL PENDING
    # ========================================================

    if change.status != "pending":

        raise HTTPException(
            status_code=400,
            detail=f"Change is already {change.status}"
        )


    # ========================================================
    # STEP 3: REJECT CHANGE
    # ========================================================

    change.status = "rejected"


    # ========================================================
    # STEP 4: SAVE
    # ========================================================

    try:

        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not reject context change: "
                f"{str(e)}"
            )
        )


    db.refresh(change)


    # ========================================================
    # STEP 5: RETURN RESULT
    # ========================================================

    return {

        "message": (
            "Context change rejected successfully"
        ),

        "change_id": change.id,

        "status": change.status
    }
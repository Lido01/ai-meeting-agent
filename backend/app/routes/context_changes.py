from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.context_change import ContextChange
from app.models.task import Task
from app.models.meeting import Meeting

from app.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/context-changes",
    tags=["Context Continuity"]
)


# ============================================================
# GET PENDING CONTEXT CHANGES
# ============================================================

@router.get("/")
def get_context_changes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Return context changes belonging to the logged-in user.

    The frontend will use this endpoint to display
    Context Continuity Alerts.
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

    The change must belong to the logged-in user.
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

    Old deadline:
        August 28

    New deadline:
        September 3

    When the user confirms, the related Task
    will be updated.
    """

    # --------------------------------------------------------
    # Find the context change
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Prevent confirming twice
    # --------------------------------------------------------

    if change.status != "pending":

        raise HTTPException(
            status_code=400,
            detail=f"Change is already {change.status}"
        )

    # --------------------------------------------------------
    # Find related task
    # --------------------------------------------------------

    task = None

    if change.task_id:

        task = (
            db.query(Task)
            .filter(
                Task.id == change.task_id
            )
            .first()
        )

    # --------------------------------------------------------
    # Update task
    # --------------------------------------------------------

    if task:

        if change.change_type == "deadline":

          from app.services.date_parser import parse_deadline

          parsed_deadline = parse_deadline(
              change.new_value
          )

          task.deadline = parsed_deadline

        elif change.change_type == "assignee":

            task.assigned_to = change.new_value

        # Decision changes may later require
        # a separate decision field.

    # --------------------------------------------------------
    # Mark change as confirmed
    # --------------------------------------------------------

    change.status = "confirmed"

    db.commit()

    if task:
        db.refresh(task)

    db.refresh(change)

    return {
        "message": "Context change confirmed",
        "change_id": change.id,
        "status": change.status,
        "updated_task_id": task.id if task else None
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

    The task will NOT be changed.
    """

    # --------------------------------------------------------
    # Find context change
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Prevent rejecting twice
    # --------------------------------------------------------

    if change.status != "pending":

        raise HTTPException(
            status_code=400,
            detail=f"Change is already {change.status}"
        )

    # --------------------------------------------------------
    # Reject the change
    # --------------------------------------------------------

    change.status = "rejected"

    db.commit()

    db.refresh(change)

    return {
        "message": "Context change rejected",
        "change_id": change.id,
        "status": change.status
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.models.meeting import Meeting
from app.schemas.task import TaskResponse, TaskUpdate

from app.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)



# GET ALL TASKS FOR A USER
@router.get("/")
def get_tasks(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    tasks = (
        db.query(Task)
        .join(Meeting)
        .filter(Meeting.user_id == user_id)
        .all()
    )

    return tasks



# GET ONE TASK


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get one task only if it belongs to the user.
    """

    task = (
        db.query(Task)
        .join(Meeting)
        .filter(
            Task.id == task_id,
            Meeting.user_id == user_id
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task



# UPDATE TASK


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    user_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a task.

    Example:
    Change status from open → completed.
    """

    task = (
        db.query(Task)
        .join(Meeting)
        .filter(
            Task.id == task_id,
            Meeting.user_id == user_id
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Only update fields provided by the user
    if task_data.description is not None:
        task.description = task_data.description

    if task_data.assigned_to is not None:
        task.assigned_to = task_data.assigned_to

    if task_data.deadline is not None:
        task.deadline = task_data.deadline

    if task_data.status is not None:
        task.status = task_data.status

    db.commit()
    db.refresh(task)

    return task



# DELETE TASK


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a task belonging to the user.
    """

    task = (
        db.query(Task)
        .join(Meeting)
        .filter(
            Task.id == task_id,
            Meeting.user_id == user_id
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# CREATE a task
@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    new_task = Task(
        description=task.description,
        assigned_to=task.assigned_to,
        deadline=task.deadline,
        meeting_id=task.meeting_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# GET all tasks
@router.get("/", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):

    tasks = db.query(Task).all()

    return tasks


# GET one task
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# UPDATE a task
@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Update task status
    task.status = status

    db.commit()
    db.refresh(task)

    return task
"""
Development-only seed for the MCP assistant demo.

Creates (or updates) one meeting/task for an existing user:

    Meeting: Product Planning Meeting
    Task:    API follow-up
    Assignee: Sarah
    Deadline: 2026-09-05

This script is not used by the assistant endpoint.
Run from the backend directory:

    python scripts/seed_demo_mcp_memory.py
    python scripts/seed_demo_mcp_memory.py --email you@example.com
"""

import argparse
import sys
from datetime import date
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.models.meeting import Meeting  # noqa: E402
from app.models.task import Task  # noqa: E402
from app.models.user import User  # noqa: E402


DEMO_TITLE = "Product Planning Meeting"
DEMO_SUMMARY = (
    "The team discussed product planning. Sarah was assigned to "
    "follow up with the API team."
)
DEMO_TASK = "API follow-up"
DEMO_ASSIGNEE = "Sarah"
DEMO_DEADLINE = date(2026, 9, 5)


def seed(email: str | None) -> None:
    db = SessionLocal()

    try:
        if email:
            user = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )
        else:
            user = (
                db.query(User)
                .order_by(User.id.asc())
                .first()
            )

        if not user:
            raise SystemExit(
                "No user found. Register/login first, then rerun this script."
            )

        meeting = (
            db.query(Meeting)
            .filter(
                Meeting.user_id == user.id,
                Meeting.title == DEMO_TITLE,
            )
            .first()
        )

        if meeting is None:
            meeting = Meeting(
                title=DEMO_TITLE,
                user_id=user.id,
                summary_text=DEMO_SUMMARY,
                transcript_text=DEMO_SUMMARY,
                status="analyzed",
            )
            db.add(meeting)
            db.flush()
        else:
            meeting.summary_text = meeting.summary_text or DEMO_SUMMARY
            meeting.status = meeting.status or "analyzed"

        task = (
            db.query(Task)
            .filter(
                Task.meeting_id == meeting.id,
                Task.description == DEMO_TASK,
            )
            .first()
        )

        if task is None:
            task = Task(
                description=DEMO_TASK,
                assigned_to=DEMO_ASSIGNEE,
                deadline=DEMO_DEADLINE,
                status="open",
                meeting_id=meeting.id,
            )
            db.add(task)
        else:
            task.assigned_to = DEMO_ASSIGNEE
            task.deadline = DEMO_DEADLINE
            task.status = task.status or "open"

        db.commit()

        print("===== DEMO MCP MEMORY SEEDED =====")
        print(f"user_id: {user.id}")
        print(f"email: {user.email}")
        print(f"meeting_id: {meeting.id}")
        print(f"task_id: {task.id}")
        print(f"task: {task.description}")
        print(f"assigned_to: {task.assigned_to}")
        print(f"deadline: {task.deadline}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--email",
        help="Seed data for this user email. Defaults to the first user.",
    )
    args = parser.parse_args()
    seed(args.email)

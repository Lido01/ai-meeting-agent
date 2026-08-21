from mcp.server import MCPServer

from app.database import SessionLocal
from app.models.meeting import Meeting
from app.models.task import Task


# Create MCP server
mcp = MCPServer(
    "AI Meeting Agent",
    instructions="Provides previous meeting and task context."
)


@mcp.tool()
def search_previous_meetings(
    user_id: int,
    limit: int = 5
) -> list:
    """
    Search previous meetings for a user.
    """

    db = SessionLocal()

    try:
        meetings = (
            db.query(Meeting)
            .filter(Meeting.user_id == user_id)
            .order_by(Meeting.id.desc())
            .limit(limit)
            .all()
        )

        results = []

        for meeting in meetings:
            results.append({
                "meeting_id": meeting.id,
                "title": meeting.title,
                "summary": meeting.summary_text,
                "transcript": meeting.transcript_text
            })

        return results

    finally:
        db.close()


@mcp.tool()
def get_previous_tasks(
    user_id: int,
    limit: int = 10
) -> list:
    """
    Get previous tasks for a user.
    """

    db = SessionLocal()

    try:
        tasks = (
            db.query(Task)
            .join(
                Meeting,
                Task.meeting_id == Meeting.id
            )
            .filter(Meeting.user_id == user_id)
            .order_by(Task.id.desc())
            .limit(limit)
            .all()
        )

        results = []

        for task in tasks:
            results.append({
                "task_id": task.id,
                "description": task.description,
                "assigned_to": task.assigned_to,
                "deadline": (
                    str(task.deadline)
                    if task.deadline
                    else None
                ),
                "status": task.status,
                "meeting_id": task.meeting_id
            })

        return results

    finally:
        db.close()

@mcp.tool()
def get_meeting_context(
    user_id: int,
    limit: int = 5
):
    """
    Get previous meetings and tasks for a user.

    The AI agent can use this to understand
    what happened in previous meetings.
    """

    db = SessionLocal()

    try:
        meetings = (
            db.query(Meeting)
            .filter(Meeting.user_id == user_id)
            .order_by(Meeting.id.desc())
            .limit(limit)
            .all()
        )

        results = []

        for meeting in meetings:

            tasks = (
                db.query(Task)
                .filter(Task.meeting_id == meeting.id)
                .all()
            )

            meeting_data = {
                "meeting_id": meeting.id,
                "title": meeting.title,
                "summary": meeting.summary_text,
                "tasks": []
            }

            for task in tasks:

                meeting_data["tasks"].append({
                    "task_id": task.id,
                    "description": task.description,
                    "assigned_to": task.assigned_to,
                    "deadline": (
                        str(task.deadline)
                        if task.deadline
                        else None
                    ),
                    "status": task.status
                })

            results.append(meeting_data)

        return results

    finally:
        db.close()
        
# Start MCP server
if __name__ == "__main__":
    mcp.run()
from mcp.server.fastmcp import FastMCP

from app.database import SessionLocal
from app.models.meeting import Meeting
from app.models.task import Task


# Create MCP server
mcp = FastMCP("AI Meeting Agent")


@mcp.tool()
def search_previous_meetings(
    user_id: int,
    limit: int = 5
):
    """
    Find previous meetings for a user.

    This gives the AI context from earlier meetings.
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
):
    """
    Get previous tasks connected to the user's meetings.
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
                "deadline": str(task.deadline)
                if task.deadline
                else None,
                "status": task.status,
                "meeting_id": task.meeting_id
            })

        return results

    finally:
        db.close()


# Start MCP server
if __name__ == "__main__":
    mcp.run()
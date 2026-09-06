import re
import sys

from sqlalchemy import or_

from mcp.server import MCPServer

from app.database import SessionLocal
from app.models.meeting import Meeting
from app.models.task import Task


# Create MCP server
mcp = MCPServer(
    "AI Meeting Agent",
    instructions="Provides previous meeting and task context."
)

_QUERY_STOPWORDS = {
    "a", "about", "an", "and", "did", "for", "from", "in", "my",
    "of", "or", "our", "previous", "the", "to", "was", "we",
    "what", "who", "with",
}


def _query_tokens(query: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", (query or "").lower())
    return [
        word for word in words
        if word not in _QUERY_STOPWORDS and len(word) >= 3
    ]


def _serialize_meeting(db, meeting) -> dict:
    tasks = (
        db.query(Task)
        .filter(Task.meeting_id == meeting.id)
        .all()
    )

    return {
        "meeting_id": meeting.id,
        "title": meeting.title,
        "summary": meeting.summary_text,
        "tasks": [
            {
                "task_id": task.id,
                "description": task.description,
                "assigned_to": task.assigned_to,
                "deadline": (
                    str(task.deadline)
                    if task.deadline
                    else None
                ),
                "status": task.status
            }
            for task in tasks
        ]
    }


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
    query: str = "",
    limit: int = 5
) -> list:
    """
    Get previous meetings and their tasks for a user.

    Optional query filters by meeting title/summary/transcript
    or task description/assignee using simple keyword matching.
    If nothing matches, the most recent meetings are returned.
    """

    # Log to stderr only. stdout is reserved for MCP JSON-RPC.
    print(
        f"MCP tool get_meeting_context user_id={user_id} "
        f"query={query!r} limit={limit}",
        file=sys.stderr
    )

    db = SessionLocal()

    try:
        meetings = []
        tokens = _query_tokens(query)

        if tokens:
            meeting_filters = []
            task_filters = []

            for token in tokens:
                pattern = f"%{token}%"
                meeting_filters.extend([
                    Meeting.title.ilike(pattern),
                    Meeting.summary_text.ilike(pattern),
                    Meeting.transcript_text.ilike(pattern),
                ])
                task_filters.extend([
                    Task.description.ilike(pattern),
                    Task.assigned_to.ilike(pattern),
                ])

            meeting_ids = {
                row[0]
                for row in (
                    db.query(Meeting.id)
                    .filter(Meeting.user_id == user_id)
                    .filter(or_(*meeting_filters))
                    .all()
                )
            }

            task_meeting_ids = {
                row[0]
                for row in (
                    db.query(Task.meeting_id)
                    .join(Meeting, Task.meeting_id == Meeting.id)
                    .filter(Meeting.user_id == user_id)
                    .filter(or_(*task_filters))
                    .all()
                )
            }

            ids = sorted(
                meeting_ids | task_meeting_ids,
                reverse=True
            )[:limit]

            if ids:
                meetings = (
                    db.query(Meeting)
                    .filter(Meeting.id.in_(ids))
                    .order_by(Meeting.id.desc())
                    .all()
                )

        if not meetings:
            meetings = (
                db.query(Meeting)
                .filter(Meeting.user_id == user_id)
                .order_by(Meeting.id.desc())
                .limit(limit)
                .all()
            )

        return [
            _serialize_meeting(db, meeting)
            for meeting in meetings
        ]

    finally:
        db.close()
        
# Start MCP server
if __name__ == "__main__":
    mcp.run()
from sqlalchemy.orm import Session

from app.models.meeting import Meeting


def get_previous_context(
    db: Session,
    user_id: int,
    current_transcript: str,
    limit: int = 5
):
    """
    Get previous meetings for this user.

    This is our first simple MCP context layer.
    Later we can replace/improve this with a real MCP server.
    """

    previous_meetings = (
        db.query(Meeting)
        .filter(
            Meeting.user_id == user_id,
            Meeting.transcript_text.isnot(None)
        )
        .order_by(Meeting.id.desc())
        .limit(limit)
        .all()
    )

    context = []

    for meeting in previous_meetings:

        context.append({
            "meeting_id": meeting.id,
            "title": meeting.title,
            "summary": meeting.summary_text,
            "transcript": meeting.transcript_text
        })

    return context
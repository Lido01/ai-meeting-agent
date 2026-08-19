from sqlalchemy.orm import Session
from app.models.meeting import Meeting


def get_previous_context(
    db: Session,
    user_id: int,
    limit: int = 5
):
    """
    Get the user's previous meetings.

    These meetings will be given to Gemini
    as context for the new meeting.
    """

    meetings = (
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

    for meeting in meetings:
        context.append({
            "meeting_id": meeting.id,
            "title": meeting.title,
            "summary": meeting.summary_text,
            "transcript": meeting.transcript_text
        })

    return context
from sqlalchemy.orm import Session

from app.models.meeting import Meeting


def get_previous_context(
    db: Session,
    user_id: int,
    limit: int = 5
):
    """
    Get the user's previous meetings.

    This gives the AI previous meeting information
    that can be used as context for the new meeting.
    """

    previous_meetings = (
        db.query(Meeting)
        .filter(
            Meeting.user_id == user_id
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
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class ContextChange(Base):
    __tablename__ = "context_changes"

    id = Column(Integer, primary_key=True, index=True)

    # Current meeting where the change was detected
    meeting_id = Column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=False
    )

    # Previous meeting containing the old information
    previous_meeting_id = Column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=True
    )

    # Example: deadline, assignee, decision
    change_type = Column(
        String,
        nullable=False
    )

    # Existing task affected by this change
    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=True
    )

    # Old value
    previous_value = Column(Text)

    # New value
    new_value = Column(Text)

    # Transcript sentence supporting the change
    evidence = Column(Text)

    # pending → confirmed / rejected
    status = Column(
        String,
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
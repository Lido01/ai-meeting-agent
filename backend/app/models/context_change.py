from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from app.database import Base


class ContextChange(Base):
    __tablename__ = "context_changes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    meeting_id = Column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=False
    )

    previous_meeting_id = Column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=True
    )

    change_type = Column(
        String,
        nullable=False
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=True
    )

    previous_value = Column(
        Text,
        nullable=True
    )

    new_value = Column(
        Text,
        nullable=True
    )

    evidence = Column(
        Text,
        nullable=True
    )

    status = Column(
        String,
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    description = Column(
        String,
        nullable=False
    )

    assigned_to = Column(String)

    deadline = Column(Date)

    status = Column(
        String,
        default="open"
    )

    meeting_id = Column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=False
    )

    # Link task back to its meeting
    meeting = relationship(
        "Meeting",
        back_populates="tasks"
    )
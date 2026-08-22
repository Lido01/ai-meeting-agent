from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    # Information about the uploaded meeting file
    file_name = Column(String)
    file_path = Column(String)

    # These will be filled later by Gemini
    transcript_text = Column(Text)
    summary_text = Column(Text)
    
    tasks = relationship(
        "Task",
        back_populates="meeting",
        cascade="all, delete-orphan"
    )

    status = Column(String, default="processing")

    user_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, server_default=func.now())
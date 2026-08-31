import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.interview_session import InterviewSession


class Interview(Base):
    """
    Template/definition for an interview (e.g. 'Backend Engineer - Senior').
    Groups target role metadata, difficulty, and associated questions.
    """

    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Medium",
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="Question.created_at",
    )
    sessions: Mapped[List["InterviewSession"]] = relationship(
        "InterviewSession",
        back_populates="interview",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Interview id={self.id} title='{self.title}' role='{self.role}' difficulty='{self.difficulty}'>"
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession
    from app.models.question import Question
    from app.models.feedback import Feedback


class Answer(Base):
    """
    User response for a specific question within a given interview session.
    """

    __tablename__ = "answers"
    __table_args__ = (
        # Ensures one answer record per question per interview session
        UniqueConstraint("session_id", "question_id", name="uq_session_question_answer"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    session: Mapped["InterviewSession"] = relationship(
        "InterviewSession",
        back_populates="answers",
    )
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="answers",
    )
    feedback: Mapped[Optional["Feedback"]] = relationship(
        "Feedback",
        back_populates="answer",
        cascade="all, delete-orphan",
        uselist=False,  # 1:1 relationship with Feedback
    )

    def __repr__(self) -> str:
        return f"<Answer id={self.id} session_id={self.session_id} question_id={self.question_id}>"
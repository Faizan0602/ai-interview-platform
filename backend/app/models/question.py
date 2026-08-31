import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.interview import Interview
    from app.models.answer import Answer


class Question(Base):
    """
    Individual question belonging to an Interview template.
    """

    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    question_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Technical",  # e.g., Technical, Behavioral, System Design
        index=True,
    )
    expected_answer: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    interview: Mapped["Interview"] = relationship(
        "Interview",
        back_populates="questions",
    )
    answers: Mapped[List["Answer"]] = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Question id={self.id} type='{self.question_type}' interview_id={self.interview_id}>"
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.answer import Answer


class Feedback(Base):
    """AI-generated evaluation for a submitted answer."""

    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("answers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    strengths: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    weaknesses: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    suggestions: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    answer: Mapped["Answer"] = relationship(
        "Answer",
        back_populates="feedback",
    )

    def __repr__(self) -> str:
        return f"<Feedback id={self.id} answer_id={self.answer_id} score={self.score}>"

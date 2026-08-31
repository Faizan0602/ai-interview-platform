import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewUpdate


class InterviewService:
    """Service layer encapsulating business logic for Interview templates."""

    @staticmethod
    def create_interview(db: Session, interview_in: InterviewCreate) -> Interview:
        """
        Create and persist a new interview template.

        :param db: SQLAlchemy database session.
        :param interview_in: Validated interview creation payload.
        :return: Created Interview ORM instance.
        """
        interview = Interview(
            title=interview_in.title.strip(),
            role=interview_in.role.strip(),
            difficulty=interview_in.difficulty.strip(),
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)
        return interview

    @staticmethod
    def get_interview(db: Session, interview_id: uuid.UUID) -> Interview:
        """
        Retrieve a single interview by its UUID. Raises 404 if not found.

        :param db: SQLAlchemy database session.
        :param interview_id: Primary UUID of the interview.
        :return: Interview ORM instance.
        :raises HTTPException: 404 Not Found if record does not exist.
        """
        stmt = select(Interview).where(Interview.id == interview_id)
        interview: Optional[Interview] = db.scalar(stmt)

        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview with ID '{interview_id}' was not found.",
            )
        return interview

    @staticmethod
    def get_all_interviews(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        role: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> List[Interview]:
        """
        Retrieve a paginated list of interviews with optional filters.

        :param db: SQLAlchemy database session.
        :param skip: Number of records to skip for pagination.
        :param limit: Maximum number of records to return.
        :param role: Optional case-insensitive substring filter on role.
        :param difficulty: Optional filter on difficulty level.
        :return: List of Interview ORM instances.
        """
        stmt = select(Interview).order_by(Interview.created_at.desc())

        if role:
            stmt = stmt.where(Interview.role.ilike(f"%{role.strip()}%"))
        if difficulty:
            stmt = stmt.where(Interview.difficulty.ilike(difficulty.strip()))

        stmt = stmt.offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    @classmethod
    def update_interview(
        cls,
        db: Session,
        interview_id: uuid.UUID,
        interview_in: InterviewUpdate,
    ) -> Interview:
        """
        Update fields of an existing interview template.

        :param db: SQLAlchemy database session.
        :param interview_id: Primary UUID of the interview to update.
        :param interview_in: Validated payload with fields to update.
        :return: Updated Interview ORM instance.
        :raises HTTPException: 404 Not Found if record does not exist.
        """
        interview = cls.get_interview(db, interview_id)

        update_data = interview_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if isinstance(value, str):
                setattr(interview, field, value.strip())
            else:
                setattr(interview, field, value)

        db.commit()
        db.refresh(interview)
        return interview

    @classmethod
    def delete_interview(cls, db: Session, interview_id: uuid.UUID) -> None:
        """
        Delete an interview template by its UUID. Cascades to associated questions/sessions.

        :param db: SQLAlchemy database session.
        :param interview_id: Primary UUID of the interview to delete.
        :raises HTTPException: 404 Not Found if record does not exist.
        """
        interview = cls.get_interview(db, interview_id)
        db.delete(interview)
        db.commit()
import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate


class QuestionService:
    """Service layer encapsulating business logic for Question management."""

    @staticmethod
    def _validate_interview_exists(db: Session, interview_id: uuid.UUID) -> Interview:
        """
        Internal helper to verify that a parent interview exists.
        
        :param db: SQLAlchemy database session.
        :param interview_id: UUID of the interview to check.
        :return: The Interview ORM object if found.
        :raises HTTPException: 404 Not Found if the interview does not exist.
        """
        stmt = select(Interview).where(Interview.id == interview_id)
        interview: Optional[Interview] = db.scalar(stmt)
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview with ID '{interview_id}' does not exist.",
            )
        return interview

    @classmethod
    def create_question(cls, db: Session, question_in: QuestionCreate) -> Question:
        """
        Create and persist a new question under a validated interview template.

        :param db: SQLAlchemy database session.
        :param question_in: Validated question creation payload.
        :return: Created Question ORM instance.
        """
        cls._validate_interview_exists(db, question_in.interview_id)

        question = Question(
            interview_id=question_in.interview_id,
            question_text=question_in.question_text.strip(),
            question_type=question_in.question_type.strip(),
            expected_answer=question_in.expected_answer.strip() if question_in.expected_answer else None,
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def get_question(db: Session, question_id: uuid.UUID) -> Question:
        """
        Retrieve a single question by its UUID. Raises 404 if not found.

        :param db: SQLAlchemy database session.
        :param question_id: Primary UUID of the question.
        :return: Question ORM instance.
        :raises HTTPException: 404 Not Found if record does not exist.
        """
        stmt = select(Question).where(Question.id == question_id)
        question: Optional[Question] = db.scalar(stmt)

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID '{question_id}' was not found.",
            )
        return question

    @classmethod
    def get_questions_by_interview(
        cls,
        db: Session,
        interview_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Question]:
        """
        Retrieve all questions belonging to a specific interview template with pagination.

        :param db: SQLAlchemy database session.
        :param interview_id: UUID of the parent interview.
        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :return: List of Question ORM instances ordered by creation timestamp.
        """
        cls._validate_interview_exists(db, interview_id)

        stmt = (
            select(Question)
            .where(Question.interview_id == interview_id)
            .order_by(Question.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    @classmethod
    def update_question(
        cls,
        db: Session,
        question_id: uuid.UUID,
        question_in: QuestionUpdate,
    ) -> Question:
        """
        Update fields of an existing question.

        :param db: SQLAlchemy database session.
        :param question_id: Primary UUID of the question to update.
        :param question_in: Validated payload with fields to update.
        :return: Updated Question ORM instance.
        :raises HTTPException: 404 Not Found if record does not exist.
        """
        question = cls.get_question(db, question_id)

        update_data = question_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if isinstance(value, str):
                setattr(question, field, value.strip())
            else:
                setattr(question, field, value)

        db.commit()
        db.refresh(question)
        return question

    @classmethod
    def delete_question(cls, db: Session, question_id: uuid.UUID) -> None:
        """
        Delete a question by its UUID.

        :param db: SQLAlchemy database session.
        :param question_id: Primary UUID of the question to delete.
        :raises HTTPException: 404 Not Found if record does not exist.
        """
        question = cls.get_question(db, question_id)
        db.delete(question)
        db.commit()
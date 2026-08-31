import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.models.question import Question
from app.schemas.interview import InterviewCreate, InterviewUpdate
from app.services.ai_question_generator import AIQuestionGeneratorService


class InterviewService:
    """Service layer encapsulating business logic for Interview templates."""

    @staticmethod
    def create_interview(db: Session, interview_in: InterviewCreate) -> Interview:
        """Create and persist a new interview template."""
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
        """Retrieve a single interview by its UUID. Raises 404 if not found."""
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
        """Retrieve a paginated list of interviews with optional filters."""
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
        """Update fields of an existing interview template."""
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
        """Delete an interview template by its UUID."""
        interview = cls.get_interview(db, interview_id)
        db.delete(interview)
        db.commit()

    @classmethod
    def generate_and_save_questions(
        cls,
        db: Session,
        interview_id: uuid.UUID,
        count: int = 5,
        additional_context: Optional[str] = None,
    ) -> List[Question]:
        """
        Generate questions automatically using Gemini and persist them under the target interview.

        :param db: SQLAlchemy database session.
        :param interview_id: UUID of the target interview template.
        :param count: Total questions to generate.
        :param additional_context: Optional extra guidance/topics for Gemini.
        :return: List of newly created Question ORM objects.
        """
        interview = cls.get_interview(db, interview_id)

        # 1. Generate questions from Gemini
        ai_questions = AIQuestionGeneratorService.generate_questions(
            title=interview.title,
            role=interview.role,
            difficulty=interview.difficulty,
            count=count,
            additional_context=additional_context,
        )

        # 2. Convert to ORM models and save in PostgreSQL
        new_questions: List[Question] = []
        for item in ai_questions:
            q = Question(
                interview_id=interview.id,
                question_text=item.question_text.strip(),
                question_type=item.question_type.strip(),
                expected_answer=item.expected_answer.strip() if item.expected_answer else None,
            )
            db.add(q)
            new_questions.append(q)

        db.commit()

        # 3. Refresh instances to populate IDs and timestamps
        for q in new_questions:
            db.refresh(q)

        return new_questions
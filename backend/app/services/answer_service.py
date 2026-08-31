import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.question import Question
from app.schemas.answer import AnswerCreate


class AnswerService:
    """Service layer for user-submitted answers."""

    @staticmethod
    def _validate_question_exists(db: Session, question_id: uuid.UUID) -> Question:
        stmt = select(Question).where(Question.id == question_id)
        question: Optional[Question] = db.scalar(stmt)

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID '{question_id}' was not found.",
            )
        return question

    @classmethod
    def submit_answer(
        cls,
        db: Session,
        user_id: uuid.UUID,
        answer_in: AnswerCreate,
    ) -> Answer:
        cls._validate_question_exists(db, answer_in.question_id)

        answer_text = answer_in.answer_text.strip()
        if not answer_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Answer text cannot be empty.",
            )

        answer = Answer(
            user_id=user_id,
            question_id=answer_in.question_id,
            answer_text=answer_text,
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer

    @classmethod
    def get_answers_by_question(
        cls,
        db: Session,
        question_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Answer]:
        cls._validate_question_exists(db, question_id)

        stmt = (
            select(Answer)
            .where(Answer.question_id == question_id)
            .order_by(Answer.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.answer import Answer
from app.models.feedback import Feedback
from app.services.ai_feedback_service import AIFeedbackService


class FeedbackService:
    """Service layer for AI feedback generation and retrieval."""

    @staticmethod
    def _get_answer(db: Session, answer_id: uuid.UUID) -> Answer:
        stmt = (
            select(Answer)
            .options(
                joinedload(Answer.question),
                joinedload(Answer.feedback),
            )
            .where(Answer.id == answer_id)
        )
        answer: Optional[Answer] = db.scalar(stmt)

        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer with ID '{answer_id}' was not found.",
            )
        return answer

    @classmethod
    def generate_feedback(cls, db: Session, answer_id: uuid.UUID) -> Feedback:
        answer = cls._get_answer(db, answer_id)

        if answer.feedback:
            return answer.feedback

        evaluation = AIFeedbackService.evaluate_answer(
            question_text=answer.question.question_text,
            expected_answer=answer.question.expected_answer,
            candidate_answer=answer.answer_text,
        )

        feedback = Feedback(
            answer_id=answer.id,
            score=evaluation.score,
            strengths=evaluation.strengths.strip(),
            weaknesses=evaluation.weaknesses.strip(),
            suggestions=evaluation.suggestions.strip(),
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def get_feedback(db: Session, answer_id: uuid.UUID) -> Feedback:
        stmt = select(Feedback).where(Feedback.answer_id == answer_id)
        feedback: Optional[Feedback] = db.scalar(stmt)

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback for answer ID '{answer_id}' was not found.",
            )
        return feedback

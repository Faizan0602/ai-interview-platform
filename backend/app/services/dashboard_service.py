import uuid
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.feedback import Feedback
from app.models.interview import Interview
from app.schemas.dashboard import DashboardResponse, RecentInterviewResponse


class DashboardService:
    """Service layer for dynamic authenticated dashboard data."""

    @staticmethod
    def get_dashboard(db: Session, user_id: uuid.UUID) -> DashboardResponse:
        total_interviews = db.scalar(select(func.count(Interview.id))) or 0

        total_answers = (
            db.scalar(
                select(func.count(Answer.id)).where(Answer.user_id == user_id)
            )
            or 0
        )

        feedback_stmt = (
            select(func.count(Feedback.id))
            .join(Answer, Feedback.answer_id == Answer.id)
            .where(Answer.user_id == user_id)
        )
        total_feedbacks = db.scalar(feedback_stmt) or 0

        average_score_stmt = (
            select(func.avg(Feedback.score))
            .join(Answer, Feedback.answer_id == Answer.id)
            .where(Answer.user_id == user_id)
        )
        raw_average_score = db.scalar(average_score_stmt)
        average_score = round(float(raw_average_score), 1) if raw_average_score is not None else 0.0

        recent_interviews = DashboardService._get_recent_interviews(db=db)

        return DashboardResponse(
            total_interviews=total_interviews,
            total_answers=total_answers,
            total_feedbacks=total_feedbacks,
            average_score=average_score,
            recent_interviews=[
                RecentInterviewResponse(
                    interview_id=interview.id,
                    title=interview.title,
                    role=interview.role,
                    difficulty=interview.difficulty,
                    created_at=interview.created_at,
                )
                for interview in recent_interviews
            ],
        )

    @staticmethod
    def _get_recent_interviews(db: Session, limit: int = 5) -> List[Interview]:
        stmt = select(Interview).order_by(Interview.created_at.desc()).limit(limit)
        return list(db.scalars(stmt).all())

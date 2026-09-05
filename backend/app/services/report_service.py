import uuid
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.answer import Answer
from app.models.question import Question
from app.schemas.report import InterviewReportResponse, ReportQuestionResponse
from app.services.interview_service import InterviewService


class ReportService:
    """Service layer for dynamic interview report generation."""

    @staticmethod
    def generate_interview_report(
        db: Session,
        interview_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> InterviewReportResponse:
        interview = InterviewService.get_interview(db=db, interview_id=interview_id)

        questions = ReportService._get_questions(db=db, interview_id=interview_id)
        answers_by_question = ReportService._get_latest_answers_by_question(
            db=db,
            user_id=user_id,
            question_ids=[question.id for question in questions],
        )

        report_questions: List[ReportQuestionResponse] = []
        scores: List[int] = []

        for question in questions:
            answer = answers_by_question.get(question.id)
            feedback = answer.feedback if answer else None

            if feedback:
                scores.append(feedback.score)

            report_questions.append(
                ReportQuestionResponse(
                    question_id=question.id,
                    question_text=question.question_text,
                    answer_text=answer.answer_text if answer else None,
                    score=feedback.score if feedback else None,
                    strengths=feedback.strengths if feedback else None,
                    weaknesses=feedback.weaknesses if feedback else None,
                    suggestions=feedback.suggestions if feedback else None,
                )
            )

        answered_questions = sum(1 for question in questions if question.id in answers_by_question)
        feedback_generated = len(scores)
        average_score = round(sum(scores) / feedback_generated, 1) if feedback_generated else 0.0

        return InterviewReportResponse(
            interview_id=interview.id,
            interview_title=interview.title,
            role=interview.role,
            difficulty=interview.difficulty,
            total_questions=len(questions),
            answered_questions=answered_questions,
            feedback_generated=feedback_generated,
            average_score=average_score,
            questions=report_questions,
        )

    @staticmethod
    def _get_questions(db: Session, interview_id: uuid.UUID) -> List[Question]:
        stmt = (
            select(Question)
            .where(Question.interview_id == interview_id)
            .order_by(Question.created_at.asc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def _get_latest_answers_by_question(
        db: Session,
        user_id: uuid.UUID,
        question_ids: List[uuid.UUID],
    ) -> Dict[uuid.UUID, Answer]:
        if not question_ids:
            return {}

        stmt = (
            select(Answer)
            .options(joinedload(Answer.feedback))
            .where(
                Answer.user_id == user_id,
                Answer.question_id.in_(question_ids),
            )
            .order_by(Answer.created_at.desc())
        )

        answers_by_question: Dict[uuid.UUID, Answer] = {}
        for answer in db.scalars(stmt).all():
            answers_by_question.setdefault(answer.question_id, answer)

        return answers_by_question

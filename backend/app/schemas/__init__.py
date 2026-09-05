"""Central schema exports."""
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.schemas.interview import (
    InterviewBase,
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse,
)
from app.schemas.question import (
    QuestionBase,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
)
from app.schemas.answer import AnswerCreate, AnswerResponse
from app.schemas.feedback import FeedbackResponse
from app.schemas.report import InterviewReportResponse, ReportQuestionResponse
from app.schemas.dashboard import DashboardResponse, RecentInterviewResponse
from app.schemas.ai_generator import (
    GeneratedQuestionItem,
    GenerateQuestionsRequest,
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "InterviewBase",
    "InterviewCreate",
    "InterviewUpdate",
    "InterviewResponse",
    "QuestionBase",
    "QuestionCreate",
    "QuestionUpdate",
    "QuestionResponse",
    "AnswerCreate",
    "AnswerResponse",
    "FeedbackResponse",
    "ReportQuestionResponse",
    "InterviewReportResponse",
    "RecentInterviewResponse",
    "DashboardResponse",
    "GeneratedQuestionItem",
    "GenerateQuestionsRequest",
]

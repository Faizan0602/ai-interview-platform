import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class ReportQuestionResponse(BaseModel):
    question_id: uuid.UUID
    question_text: str
    answer_text: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=0, le=10)
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    suggestions: Optional[str] = None


class InterviewReportResponse(BaseModel):
    interview_id: uuid.UUID
    interview_title: str
    role: str
    difficulty: str
    total_questions: int = Field(..., ge=0)
    answered_questions: int = Field(..., ge=0)
    feedback_generated: int = Field(..., ge=0)
    average_score: float = Field(..., ge=0, le=10)
    questions: List[ReportQuestionResponse]

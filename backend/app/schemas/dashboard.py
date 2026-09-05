import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class RecentInterviewResponse(BaseModel):
    interview_id: uuid.UUID
    title: str
    role: str
    difficulty: str
    created_at: datetime


class DashboardResponse(BaseModel):
    total_interviews: int = Field(..., ge=0)
    total_answers: int = Field(..., ge=0)
    total_feedbacks: int = Field(..., ge=0)
    average_score: float = Field(..., ge=0, le=10)
    recent_interviews: List[RecentInterviewResponse]

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class QuestionBase(BaseModel):
    question_text: str = Field(..., min_length=5, max_length=5000)
    question_type: str = Field(default="Technical", min_length=2, max_length=50)
    expected_answer: Optional[str] = Field(default=None, max_length=10000)


class QuestionCreate(QuestionBase):
    interview_id: uuid.UUID


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(default=None, min_length=5, max_length=5000)
    question_type: Optional[str] = Field(default=None, min_length=2, max_length=50)
    expected_answer: Optional[str] = Field(default=None, max_length=10000)


class QuestionResponse(QuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    interview_id: uuid.UUID
    created_at: datetime
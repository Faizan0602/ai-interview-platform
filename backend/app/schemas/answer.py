import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnswerCreate(BaseModel):
    question_id: uuid.UUID
    answer_text: str = Field(..., min_length=1, max_length=20000)


class AnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    question_id: uuid.UUID
    answer_text: str
    created_at: datetime

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    answer_id: uuid.UUID
    score: int = Field(..., ge=0, le=10)
    strengths: str
    weaknesses: str
    suggestions: str
    created_at: datetime

from typing import Optional

from pydantic import BaseModel, Field


class GeneratedQuestionItem(BaseModel):
    question_text: str = Field(..., min_length=5)

    question_type: str = Field(
        default="Technical"
    )

    expected_answer: Optional[str] = None


class GenerateQuestionsRequest(BaseModel):
    count: int = Field(
        default=5,
        ge=1,
        le=10
    )

    additional_context: Optional[str] = None
import logging
from typing import Optional

from fastapi import HTTPException, status
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger("ai_interview_platform.gemini.feedback")


class FeedbackEvaluation(BaseModel):
    score: int = Field(..., ge=0, le=10)
    strengths: str = Field(..., min_length=1)
    weaknesses: str = Field(..., min_length=1)
    suggestions: str = Field(..., min_length=1)


class AIFeedbackService:
    """Gemini-powered answer feedback evaluator."""

    @classmethod
    def _get_client(cls) -> genai.Client:
        if (
            not settings.GEMINI_API_KEY
            or settings.GEMINI_API_KEY.startswith("your-")
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key is not configured.",
            )

        return genai.Client(api_key=settings.GEMINI_API_KEY)

    @classmethod
    def evaluate_answer(
        cls,
        question_text: str,
        expected_answer: Optional[str],
        candidate_answer: str,
    ) -> FeedbackEvaluation:
        client = cls._get_client()

        system_instruction = """
        You are a senior technical interviewer.

        Evaluate the candidate answer against the question and expected answer.

        Requirements:
        - Score from 0 to 10.
        - Be concise but specific.
        - Return strengths, weaknesses, and improvement suggestions.
        """

        prompt = f"""
        Question:
        {question_text}

        Expected Answer / Evaluation Criteria:
        {expected_answer or "No expected answer was provided. Evaluate based on correctness, clarity, and completeness."}

        Candidate Answer:
        {candidate_answer}
        """

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    response_mime_type="application/json",
                    response_schema=FeedbackEvaluation,
                ),
            )

            parsed: FeedbackEvaluation = response.parsed
            if not parsed:
                raise ValueError("Gemini returned empty feedback.")

            return parsed

        except Exception as exc:
            logger.exception("AI feedback generation failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI feedback generation failed: {str(exc)}",
            )

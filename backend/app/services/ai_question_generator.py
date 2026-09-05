import logging
from typing import List, Optional

from fastapi import HTTPException, status
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger("ai_interview_platform.gemini")


class GeneratedQuestionItem(BaseModel):
    question_text: str = Field(..., min_length=5)
    question_type: str
    expected_answer: str = Field(..., min_length=10)


class GeneratedQuestionsResponse(BaseModel):
    questions: List[GeneratedQuestionItem]


class AIQuestionGeneratorService:

    @classmethod
    def _get_client(cls):
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
    def generate_questions(
        cls,
        title: str,
        role: str,
        difficulty: str,
        count: int = 5,
        additional_context: Optional[str] = None,
    ):
        client = cls._get_client()

        system_instruction = """
        You are a Senior Technical Recruiter and Hiring Manager.

        Generate high-quality interview questions.

        Requirements:
        - Mix Technical, System Design, and Behavioral questions.
        - Match the role and difficulty.
        - Provide detailed expected answers.
        - Return exactly the requested number of questions.
        """

        prompt = f"""
        Generate exactly {count} interview questions.

        Title: {title}
        Role: {role}
        Difficulty: {difficulty}
        """

        if additional_context:
            prompt += f"\nAdditional Context: {additional_context}"

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    response_mime_type="application/json",
                    response_schema=GeneratedQuestionsResponse,
                ),
            )

            parsed = response.parsed

            if not parsed:
                raise ValueError("Gemini returned empty response.")

            return parsed.questions[:count]

        except Exception as exc:
            logger.exception("AI question generation failed")

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI generation failed: {str(exc)}",
            )
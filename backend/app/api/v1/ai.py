from fastapi import APIRouter

from app.services.ai_question_generator import (
    AIQuestionGeneratorService,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.get("/test")
def test_ai():

    questions = AIQuestionGeneratorService.generate_questions(
        title="FastAPI Backend Developer",
        role="Backend Engineer",
        difficulty="Medium",
        count=3,
    )

    return questions
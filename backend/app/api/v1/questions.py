import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new interview question",
    description="Creates an interview question linked to an existing interview template. Requires valid JWT authentication.",
)
def create_question(
    question_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionResponse:
    """Create a new interview question."""
    return QuestionService.create_question(db=db, question_in=question_in)


@router.get(
    "/interview/{interview_id}",
    response_model=List[QuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all questions for an interview",
    description="Retrieves all questions belonging to a specific interview template in chronological order.",
)
def get_questions_by_interview(
    interview_id: uuid.UUID,
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=50, ge=1, le=100, description="Pagination limit (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[QuestionResponse]:
    """Retrieve all questions for a specific interview template."""
    return QuestionService.get_questions_by_interview(
        db=db,
        interview_id=interview_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get question by ID",
    description="Retrieves the detailed content of a single interview question by its unique UUID.",
)
def get_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionResponse:
    """Retrieve a question by its unique ID."""
    return QuestionService.get_question(db=db, question_id=question_id)


@router.put(
    "/{question_id}",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update question",
    description="Updates the text, category type, or expected answer of an existing question.",
)
def update_question(
    question_id: uuid.UUID,
    question_in: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionResponse:
    """Update fields on an existing question."""
    return QuestionService.update_question(
        db=db,
        question_id=question_id,
        question_in=question_in,
    )


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete question",
    description="Deletes a question by its unique identifier.",
)
def delete_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an interview question."""
    QuestionService.delete_question(db=db, question_id=question_id)
import uuid
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.answer import AnswerCreate, AnswerResponse
from app.services.answer_service import AnswerService

router = APIRouter(prefix="/answers", tags=["Answers"])


@router.post(
    "",
    response_model=AnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_answer(
    answer_in: AnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnswerResponse:
    return AnswerService.submit_answer(
        db=db,
        user_id=current_user.id,
        answer_in=answer_in,
    )


@router.get(
    "/question/{question_id}",
    response_model=List[AnswerResponse],
    status_code=status.HTTP_200_OK,
)
def get_answers_by_question(
    question_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[AnswerResponse]:
    return AnswerService.get_answers_by_question(
        db=db,
        question_id=question_id,
        skip=skip,
        limit=limit,
    )

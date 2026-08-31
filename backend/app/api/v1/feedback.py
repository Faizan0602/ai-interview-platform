import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.feedback import FeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "/{answer_id}",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_feedback(
    answer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedbackResponse:
    return FeedbackService.generate_feedback(db=db, answer_id=answer_id)


@router.get(
    "/{answer_id}",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
)
def get_feedback(
    answer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedbackResponse:
    return FeedbackService.get_feedback(db=db, answer_id=answer_id)

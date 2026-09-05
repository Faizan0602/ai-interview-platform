import uuid
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.ai_generator import GenerateQuestionsRequest
from app.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewUpdate,
)
from app.schemas.question import QuestionResponse
from app.schemas.report import InterviewReportResponse

from app.services.interview_service import InterviewService
from app.services.report_service import ReportService

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)


# =========================
# CREATE INTERVIEW
# =========================
@router.post(
    "",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview(
    interview_in: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InterviewService.create_interview(
        db=db,
        interview_in=interview_in,
    )


# =========================
# GET ALL INTERVIEWS
# =========================
@router.get(
    "",
    response_model=List[InterviewResponse],
)
def get_all_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InterviewService.get_all_interviews(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        difficulty=difficulty,
    )


# =========================
# GET INTERVIEW REPORT
# =========================
@router.get(
    "/{interview_id}/report",
    response_model=InterviewReportResponse,
    status_code=status.HTTP_200_OK,
)
def get_interview_report(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewReportResponse:
    return ReportService.generate_interview_report(
        db=db,
        interview_id=interview_id,
        user_id=current_user.id,
    )


# =========================
# GET SINGLE INTERVIEW
# =========================
@router.get(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def get_interview(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InterviewService.get_interview(
        db=db,
        interview_id=interview_id,
    )


# =========================
# UPDATE INTERVIEW
# =========================
@router.put(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def update_interview(
    interview_id: uuid.UUID,
    interview_in: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InterviewService.update_interview(
        db=db,
        interview_id=interview_id,
        interview_in=interview_in,
    )


# =========================
# DELETE INTERVIEW
# =========================
@router.delete(
    "/{interview_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_interview(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    InterviewService.delete_interview(
        db=db,
        interview_id=interview_id,
    )


# =========================
# AI QUESTION GENERATION
# =========================
@router.post(
    "/{interview_id}/generate-questions",
    response_model=List[QuestionResponse],
    status_code=status.HTTP_201_CREATED,
)
def generate_questions_for_interview(
    interview_id: uuid.UUID,
    request_body: Optional[GenerateQuestionsRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate interview questions using Gemini
    and save them directly into PostgreSQL.
    """

    count = 5
    additional_context = None

    if request_body:
        count = request_body.count
        additional_context = request_body.additional_context

    return InterviewService.generate_and_save_questions(
        db=db,
        interview_id=interview_id,
        count=count,
        additional_context=additional_context,
    )

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewUpdate,
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post(
    "",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new interview template",
    description="Creates a new interview specification with role, title, and target difficulty.",
)
def create_interview(
    interview_in: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewResponse:
    """Create a new interview."""
    return InterviewService.create_interview(db=db, interview_in=interview_in)


@router.get(
    "",
    response_model=List[InterviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all interview templates",
    description="Retrieves a paginated list of all interview templates with optional filters.",
)
def get_all_interviews(
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=50, ge=1, le=100, description="Pagination limit (max 100)"),
    role: Optional[str] = Query(default=None, description="Filter by job role substring"),
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty level"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[InterviewResponse]:
    """List all interviews with pagination and search filters."""
    return InterviewService.get_all_interviews(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        difficulty=difficulty,
    )


@router.get(
    "/{interview_id}",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get interview by ID",
    description="Retrieves the detailed specification of a single interview by its UUID.",
)
def get_interview(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewResponse:
    """Retrieve an interview by its unique identifier."""
    return InterviewService.get_interview(db=db, interview_id=interview_id)


@router.put(
    "/{interview_id}",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Update interview template",
    description="Updates the title, role, or difficulty of an existing interview template.",
)
def update_interview(
    interview_id: uuid.UUID,
    interview_in: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewResponse:
    """Update fields on an existing interview."""
    return InterviewService.update_interview(
        db=db,
        interview_id=interview_id,
        interview_in=interview_in,
    )


@router.delete(
    "/{interview_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete interview template",
    description="Deletes an interview template and cascades to its associated questions and sessions.",
)
def delete_interview(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an interview template."""
    InterviewService.delete_interview(db=db, interview_id=interview_id)
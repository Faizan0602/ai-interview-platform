import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class InterviewBase(BaseModel):
    """Base interview schema containing common fields."""
    title: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Title of the interview template (e.g. Senior Backend Engineer - Python)",
        examples=["Senior Backend Engineer - Python"],
    )
    role: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Target job position or discipline",
        examples=["Backend Developer"],
    )
    difficulty: str = Field(
        default="Medium",
        min_length=2,
        max_length=50,
        description="Target difficulty level (e.g., Easy, Medium, Hard, Senior)",
        examples=["Medium"],
    )


class InterviewCreate(InterviewBase):
    """Schema for creating a new interview template."""
    pass


class InterviewUpdate(BaseModel):
    """Schema for updating an existing interview template (partial updates allowed)."""
    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=150,
        description="Updated title of the interview template",
    )
    role: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Updated target job position",
    )
    difficulty: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Updated target difficulty level",
    )


class InterviewResponse(InterviewBase):
    """Schema for returning interview details in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique interview UUID identifier")
    created_at: datetime = Field(..., description="Timestamp when the interview was created")
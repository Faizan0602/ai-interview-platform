from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration and environment variable validator."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Required Environment Variables
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string (e.g. postgresql+psycopg2://user:pass@localhost:5432/dbname)",
    )
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Cryptographic secret key for signing tokens and sessions (min 32 chars)",
    )
    GEMINI_API_KEY: str = Field(
        ...,
        min_length=10,
        description="Google Gemini API key for question generation and feedback analysis",
    )

    # Optional / Defaulted App Settings
    PROJECT_NAME: str = "AI Interview Platform API"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure the DATABASE_URL uses the synchronous PostgreSQL driver format."""
        if not v.startswith("postgresql://") and not v.startswith("postgresql+psycopg2://"):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://' or 'postgresql+psycopg2://'"
            )
        # Normalize postgresql:// to postgresql+psycopg2:// for explicit driver resolution in SQLAlchemy 2.x
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v


# Instantiate settings singleton (triggers startup validation)
settings = Settings()
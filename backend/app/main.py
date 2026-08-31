import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.answers import router as answers_router
from app.api.v1.auth import router as auth_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.interviews import router as interviews_router
from app.api.v1.questions import router as questions_router
from app.core.config import settings
from app.db.session import engine
from app.api.v1.ai import router as ai_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ai_interview_platform")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup & shutdown events."""
    logger.info("Initializing %s in [%s] mode...", settings.PROJECT_NAME, settings.ENVIRONMENT)

    # Verify DB connection on startup
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
    except Exception as exc:
        logger.critical("Failed to connect to the database on startup: %s", exc)
        raise RuntimeError(f"Database startup check failed: {exc}") from exc

    yield

    logger.info("Shutting down database connection engine...")
    engine.dispose()
    logger.info("Application shutdown complete.")


# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade backend for the AI Interview Platform.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(interviews_router, prefix=settings.API_V1_STR)
app.include_router(questions_router, prefix=settings.API_V1_STR)
app.include_router(answers_router, prefix=settings.API_V1_STR)
app.include_router(feedback_router, prefix=settings.API_V1_STR)


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health check endpoint",
)
def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy"}

app.include_router(
    ai_router,
    prefix=settings.API_V1_STR
)

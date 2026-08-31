import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ai_interview_platform")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager:
    - Runs startup validations & verifies DB connectivity
    - Runs graceful shutdown routines
    """
    logger.info("Initializing %s in [%s] mode...", settings.PROJECT_NAME, settings.ENVIRONMENT)

    # 1. Verify DB connection on startup
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
    except Exception as exc:
        logger.critical("Failed to connect to the database on startup: %s", exc)
        raise RuntimeError(f"Database startup check failed: {exc}") from exc

    # 2. Validate Gemini API Key configuration
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your-"):
        logger.warning(
            "GEMINI_API_KEY is using a placeholder or default value. AI features may fail."
        )

    yield

    # Teardown logic
    logger.info("Shutting down database connection engine...")
    engine.dispose()
    logger.info("Application shutdown complete.")


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-performance backend API for the AI Interview Platform.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health check endpoint",
    description="Returns the current operational status of the service.",
)
def health_check() -> dict[str, str]:
    """Health check endpoint required by load balancers and container orchestrators."""
    return {"status": "healthy"}
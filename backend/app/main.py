import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.auth import router as auth_router
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
    Application startup & shutdown events.
    """
    logger.info(
        "Initializing %s in [%s] mode...",
        settings.PROJECT_NAME,
        settings.ENVIRONMENT,
    )

    # Verify database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
    except Exception as exc:
        logger.critical("Database connection failed: %s", exc)
        raise RuntimeError(f"Database startup check failed: {exc}") from exc

    yield

    logger.info("Shutting down database connection engine...")
    engine.dispose()
    logger.info("Application shutdown complete.")


# FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Interview Platform Backend API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Routes
app.include_router(
    auth_router,
    prefix=settings.API_V1_STR,
)

# Health Check
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
)
def health_check():
    return {"status": "healthy"}
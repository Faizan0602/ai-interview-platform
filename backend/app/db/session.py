from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Configure synchronous PostgreSQL Engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Health-checks connection before using from pool
    pool_size=10,             # Number of active connections to persist in pool
    max_overflow=20,          # Extra burst connections allowed above pool_size
    echo=settings.DEBUG,      # Echo SQL queries in DEBUG mode
)

# Session factory for synchronous database operations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session per request,
    ensuring proper lifecycle management and cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
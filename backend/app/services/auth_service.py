from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.core.config import settings


class AuthService:
    """Service layer encapsulating user authentication and account management."""

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Fetch a single user by their email address."""
        stmt = select(User).where(User.email == email.lower().strip())
        return db.scalar(stmt)

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> User | None:
        """Fetch a single user by primary UUID."""
        stmt = select(User).where(User.id == user_id)
        return db.scalar(stmt)

    @classmethod
    def register_user(cls, db: Session, user_in: UserCreate) -> UserResponse:
        """Register a new user account with hashed credentials."""
        existing_user = cls.get_user_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists.",
            )

        new_user = User(
            email=user_in.email.lower().strip(),
            full_name=user_in.full_name.strip(),
            hashed_password=hash_password(user_in.password),
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return UserResponse.model_validate(new_user)

    @classmethod
    def authenticate_user(cls, db: Session, credentials: UserLogin) -> Token:
        """Verify user credentials and issue a signed access token."""
        user = cls.get_user_by_email(db, credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated.",
            )

        access_token = create_access_token(subject=str(user.id))
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
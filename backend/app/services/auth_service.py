"""
Authentication service — business logic layer.
Routers stay thin; this is where the actual login/refresh rules live.
"""
import uuid

from sqlalchemy.orm import Session

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenType,
    InvalidTokenError,
)
from app.models.enums import EntityStatus
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthenticationError(Exception):
    """Raised for any login/refresh failure. Message is safe to show the user."""


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate(self, email: str, password: str) -> tuple[str, str, User]:
        """Validate credentials and return (access_token, refresh_token, user)."""
        user = self.user_repo.get_by_email(email)

        # Deliberately identical error for "no such user" and "wrong password" —
        # never let a bad actor use this endpoint to enumerate valid emails.
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("Incorrect email or password.")

        if user.status != EntityStatus.ACTIVE:
            raise AuthenticationError("This account has been deactivated.")

        company_id_str = str(user.company_id) if user.company_id else None
        access = create_access_token(str(user.user_id), company_id_str, user.role.value)
        refresh = create_refresh_token(str(user.user_id), company_id_str, user.role.value)
        return access, refresh, user

    def refresh_access_token(self, refresh_token: str) -> str:
        """Validate a refresh token and issue a brand new access token."""
        try:
            payload = decode_token(refresh_token, TokenType.REFRESH)
        except InvalidTokenError as exc:
            raise AuthenticationError(f"Invalid refresh token: {exc}") from exc

        user = self.user_repo.get_by_id(uuid.UUID(payload["sub"]))
        if user is None or user.status != EntityStatus.ACTIVE:
            raise AuthenticationError("User not found or inactive.")

        company_id_str = str(user.company_id) if user.company_id else None
        return create_access_token(str(user.user_id), company_id_str, user.role.value)

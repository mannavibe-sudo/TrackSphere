"""
Password hashing (bcrypt) and JWT access/refresh token creation & verification.

Uses the `bcrypt` library directly rather than passlib, which has had
compatibility breaks with recent bcrypt releases.
"""
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

import bcrypt
import jwt
from jwt import PyJWTError

from app.core.config import settings


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class InvalidTokenError(Exception):
    """Raised when a JWT is missing, expired, malformed, or of the wrong type."""


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        # Malformed hash in the DB — never crash the login endpoint over it.
        return False


# ---------------------------------------------------------------------------
# JWT tokens
# ---------------------------------------------------------------------------

def _create_token(
    subject: str, company_id: str | None, role: str, token_type: TokenType, expires_delta: timedelta
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,          # user_id
        "company_id": company_id,
        "role": role,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),  # unique id, enables future revocation lists
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str, company_id: str | None, role: str) -> str:
    return _create_token(
        user_id, company_id, role, TokenType.ACCESS,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str, company_id: str | None, role: str) -> str:
    return _create_token(
        user_id, company_id, role, TokenType.REFRESH,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: TokenType) -> dict:
    """Decode and validate a JWT. Raises InvalidTokenError on any problem."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if payload.get("type") != expected_type.value:
        raise InvalidTokenError(
            f"Expected a {expected_type.value} token, got {payload.get('type')}"
        )
    return payload

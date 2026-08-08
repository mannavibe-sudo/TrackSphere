"""
FastAPI dependencies: extract & validate the current user from the JWT,
and enforce role-based access control.

require_role() is the single reusable guard every protected endpoint uses —
centralizing this is what keeps tenant-isolation and RBAC from being
re-implemented (and potentially gotten wrong) in every router.
"""
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token, TokenType, InvalidTokenError
from app.models.enums import UserRole
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=True)


class CurrentUser:
    """Lightweight, request-scoped representation of the authenticated user."""

    def __init__(self, user_id: uuid.UUID, company_id: uuid.UUID | None, role: UserRole):
        self.user_id = user_id
        self.company_id = company_id
        self.role = role

    @property
    def is_super_admin(self) -> bool:
        return self.role == UserRole.SUPER_ADMIN


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    try:
        payload = decode_token(credentials.credentials, TokenType.ACCESS)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload["sub"]
    user = db.get(User, uuid.UUID(user_id))
    if user is None or user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )

    return CurrentUser(user_id=user.user_id, company_id=user.company_id, role=user.role)


def require_role(*allowed_roles: UserRole):
    """
    Usage: Depends(require_role(UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN))
    Super Admin is NOT auto-allowed everywhere — pass it explicitly where
    it should have access, keeping intent visible at each endpoint.
    """

    def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return _check

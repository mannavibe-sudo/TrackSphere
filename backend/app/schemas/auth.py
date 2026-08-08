"""Pydantic request/response schemas for the authentication endpoints."""
import uuid

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    user_id: uuid.UUID
    company_id: uuid.UUID | None
    name: str
    email: EmailStr
    role: UserRole
    status: str

    model_config = {"from_attributes": True}

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole, EntityStatus


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    mobile: str | None = None
    password: str = Field(min_length=8)
    role: UserRole
    # Only used when Super Admin creates a user — Company Admin can only
    # create users within their own company (enforced in the service layer).
    company_id: uuid.UUID | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    mobile: str | None = None
    role: UserRole | None = None
    status: EntityStatus | None = None


class UserManagementOut(BaseModel):
    user_id: uuid.UUID
    company_id: uuid.UUID | None
    name: str
    email: EmailStr
    mobile: str | None
    role: UserRole
    status: EntityStatus
    created_date: datetime

    model_config = {"from_attributes": True}

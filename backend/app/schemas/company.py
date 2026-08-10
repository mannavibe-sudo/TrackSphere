import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.enums import EntityStatus


class CompanyCreate(BaseModel):
    company_name: str
    company_code: str
    gst_number: str | None = None
    address: str | None = None
    contact_person: str | None = None
    contact_number: str | None = None
    email: EmailStr | None = None


class CompanyUpdate(BaseModel):
    company_name: str | None = None
    gst_number: str | None = None
    address: str | None = None
    contact_person: str | None = None
    contact_number: str | None = None
    email: EmailStr | None = None
    status: EntityStatus | None = None


class CompanyOut(BaseModel):
    company_id: uuid.UUID
    company_name: str
    company_code: str
    gst_number: str | None
    address: str | None
    contact_person: str | None
    contact_number: str | None
    email: str | None
    status: EntityStatus
    created_date: datetime
    updated_date: datetime

    model_config = {"from_attributes": True}

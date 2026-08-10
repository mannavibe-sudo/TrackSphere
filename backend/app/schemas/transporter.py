import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import EntityStatus


class TransporterCreate(BaseModel):
    transporter_name: str


class TransporterOut(BaseModel):
    transporter_id: uuid.UUID
    company_id: uuid.UUID
    transporter_name: str
    status: EntityStatus
    created_date: datetime

    model_config = {"from_attributes": True}

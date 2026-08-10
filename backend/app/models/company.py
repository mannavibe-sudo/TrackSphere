"""Company Master model — every tenant on the platform."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Enum as SAEnum, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import EntityStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.record import Record


class Company(Base):
    __tablename__ = "companies"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    gst_number: Mapped[str | None] = mapped_column(String(15))
    address: Mapped[str | None] = mapped_column(Text)
    contact_person: Mapped[str | None] = mapped_column(String(150))
    contact_number: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[EntityStatus] = mapped_column(
        SAEnum(EntityStatus, name="entity_status", native_enum=True, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=EntityStatus.ACTIVE,
        nullable=False,
    )
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="company")
    records: Mapped[list["Record"]] = relationship(back_populates="company")

    def __repr__(self) -> str:
        return f"<Company {self.company_code} - {self.company_name}>"

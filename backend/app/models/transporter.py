"""
Transporter Master — a company-scoped, admin-curated list of transporter
names. Prevents different Data Entry Users from typing the same transporter
under different spellings (free-text mobile numbers stay per-record, since
those genuinely change trip to trip).
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Enum as SAEnum, func, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import EntityStatus

if TYPE_CHECKING:
    from app.models.company import Company


class Transporter(Base):
    __tablename__ = "transporters"
    __table_args__ = (
        UniqueConstraint("company_id", "transporter_name", name="uq_transporter_per_company"),
    )

    transporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False
    )
    transporter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[EntityStatus] = mapped_column(
        SAEnum(EntityStatus, name="entity_status", native_enum=True, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=EntityStatus.ACTIVE,
        nullable=False,
    )
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company: Mapped["Company"] = relationship()

    def __repr__(self) -> str:
        return f"<Transporter {self.transporter_name}>"

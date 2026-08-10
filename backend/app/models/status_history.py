"""Complete lifecycle tracking for a record — one row per status transition."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, Enum as SAEnum, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import RecordStatus

if TYPE_CHECKING:
    from app.models.record import Record


class RecordStatusHistory(Base):
    __tablename__ = "record_status_history"

    history_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("records.record_id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[RecordStatus] = mapped_column(
        SAEnum(RecordStatus, name="record_status", native_enum=True, values_callable=lambda enum_cls: [e.value for e in enum_cls]), nullable=False
    )
    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id")
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    remarks: Mapped[str | None] = mapped_column(Text)

    record: Mapped["Record"] = relationship(back_populates="status_history")

"""
Record model.

Field set generated verbatim from the uploaded Excel (Sheet1, 31 columns,
4 groups). Column names map 1:1 to the Excel headers — see
docs/excel-field-mapping.md for the full original-header -> column mapping.
No field renamed, merged, or removed from what was in the sheet.
"""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import RecordStatus

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User
    from app.models.status_history import RecordStatusHistory
    from app.models.attachment import Attachment
    from app.models.comment import Comment


class Record(Base):
    __tablename__ = "records"

    record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="RESTRICT"), nullable=False
    )

    # ---- Group 1: Loading & Dispatch ----
    loading_location: Mapped[str | None] = mapped_column(String(255))
    truck_number: Mapped[str | None] = mapped_column(String(20))
    driver_mobile: Mapped[str | None] = mapped_column(String(20))
    weight_at_pi_yard_mt: Mapped[float | None] = mapped_column(Numeric(10, 2))
    eway_bill_no: Mapped[str | None] = mapped_column(String(30))
    date_of_dispatch: Mapped[date | None] = mapped_column(Date)
    lr_no: Mapped[str | None] = mapped_column(String(50))
    delivery_chalan: Mapped[str | None] = mapped_column(String(50))
    cost_of_material: Mapped[float | None] = mapped_column(Numeric(12, 2))

    # ---- Group 2: Transportation ----
    transporter_name: Mapped[str | None] = mapped_column(String(255))
    transporter_mobile: Mapped[str | None] = mapped_column(String(20))
    capacity_of_truck_mt: Mapped[float | None] = mapped_column(Numeric(10, 2))
    length_of_truck_ft: Mapped[float | None] = mapped_column(Numeric(10, 2))
    rate_fixed_for_transportation: Mapped[float | None] = mapped_column(Numeric(12, 2))
    advance_paid: Mapped[float | None] = mapped_column(Numeric(12, 2))
    advance_payment_date: Mapped[date | None] = mapped_column(Date)
    advance_paid_to: Mapped[str | None] = mapped_column(String(255))
    final_payment: Mapped[float | None] = mapped_column(Numeric(12, 2))
    total_payment_to_transport: Mapped[float | None] = mapped_column(Numeric(12, 2))

    # ---- Group 3: Delivery & Weight at ITC ----
    truck_entry_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    truck_exit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    weight_at_itc_yard_mt: Mapped[float | None] = mapped_column(Numeric(10, 2))
    wc_number: Mapped[str | None] = mapped_column(String(50))
    weight_loss_mt: Mapped[float | None] = mapped_column(Numeric(10, 2))

    # ---- Group 4: Invoice & GST ----
    invoice_number: Mapped[str | None] = mapped_column(String(50))
    invoice_amount_raised: Mapped[float | None] = mapped_column(Numeric(12, 2))
    amount_raised_date: Mapped[date | None] = mapped_column(Date)
    gst_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    payment_received_date: Mapped[date | None] = mapped_column(Date)
    total_amount_received: Mapped[float | None] = mapped_column(Numeric(12, 2))
    margin_pnl: Mapped[float | None] = mapped_column(Numeric(12, 2))

    # ---- System / tracking fields ----
    status: Mapped[RecordStatus] = mapped_column(
        SAEnum(RecordStatus, name="record_status", native_enum=True),
        default=RecordStatus.DRAFT,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id")
    )
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    company: Mapped["Company"] = relationship(back_populates="records")
    created_by_user: Mapped["User | None"] = relationship(back_populates="records_created")
    status_history: Mapped[list["RecordStatusHistory"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Record {self.lr_no or self.record_id} ({self.status.value})>"

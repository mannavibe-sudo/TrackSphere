"""
Pydantic schemas for Record.

Every business field is Optional because the frontend saves the 4-step form
incrementally (PATCH after each step) — a record can legitimately exist in
the DB with only Step 1's fields filled in while still in `draft` status.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import RecordStatus


class RecordBase(BaseModel):
    # ---- Group 1: Loading & Dispatch ----
    loading_location: str | None = None
    truck_number: str | None = None
    driver_mobile: str | None = None
    weight_at_pi_yard_mt: Decimal | None = None
    eway_bill_no: str | None = None
    date_of_dispatch: date | None = None
    lr_no: str | None = None
    delivery_chalan: str | None = None
    cost_of_material: Decimal | None = None

    # ---- Group 2: Transportation ----
    transporter_name: str | None = None
    transporter_mobile: str | None = None
    capacity_of_truck_mt: Decimal | None = None
    length_of_truck_ft: Decimal | None = None
    rate_fixed_for_transportation: Decimal | None = None
    advance_paid: Decimal | None = None
    advance_payment_date: date | None = None
    advance_paid_to: str | None = None
    final_payment: Decimal | None = None
    total_payment_to_transport: Decimal | None = None

    # ---- Group 3: Delivery & Weight at ITC ----
    truck_entry_date: datetime | None = None
    truck_exit_date: datetime | None = None
    weight_at_itc_yard_mt: Decimal | None = None
    wc_number: str | None = None
    weight_loss_mt: Decimal | None = None

    # ---- Group 4: Invoice & GST ----
    invoice_number: str | None = None
    invoice_amount_raised: Decimal | None = None
    amount_raised_date: date | None = None
    gst_amount: Decimal | None = None
    payment_received_date: date | None = None
    total_amount_received: Decimal | None = None
    margin_pnl: Decimal | None = None


class RecordCreate(RecordBase):
    """Creating a record just opens a draft — company_id comes from the JWT, not the body."""
    pass


class RecordUpdate(RecordBase):
    """Used for every step's autosave PATCH. Same shape as create — all optional."""
    pass


class RecordOut(RecordBase):
    record_id: uuid.UUID
    company_id: uuid.UUID
    status: RecordStatus
    created_by: uuid.UUID | None
    created_date: datetime
    updated_date: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class RecordListItem(BaseModel):
    """Slim shape for list views — avoids sending all 31 fields per row."""
    record_id: uuid.UUID
    lr_no: str | None
    truck_number: str | None
    transporter_name: str | None
    loading_location: str | None
    status: RecordStatus
    invoice_amount_raised: Decimal | None
    date_of_dispatch: date | None

    model_config = {"from_attributes": True}


class RecordListResponse(BaseModel):
    items: list[RecordListItem]
    total: int
    page: int
    page_size: int

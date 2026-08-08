"""
Python enums mirroring the PostgreSQL ENUM types created in schema.sql.
Keep these in sync manually — Alembic migrations manage the DB-side types.
"""
import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    COMPANY_ADMIN = "company_admin"
    DATA_ENTRY_USER = "data_entry_user"


class RecordStatus(str, enum.Enum):
    DRAFT = "draft"
    LOADING = "loading"
    DISPATCHED = "dispatched"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    INVOICE_RAISED = "invoice_raised"
    PAYMENT_RECEIVED = "payment_received"
    CLOSED = "closed"


class EntityStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


# Defines the only legal forward transitions for a record's lifecycle.
# The service layer uses this to reject invalid status jumps
# (e.g. draft -> closed directly).
RECORD_STATUS_FLOW: dict[RecordStatus, RecordStatus | None] = {
    RecordStatus.DRAFT: RecordStatus.LOADING,
    RecordStatus.LOADING: RecordStatus.DISPATCHED,
    RecordStatus.DISPATCHED: RecordStatus.IN_TRANSIT,
    RecordStatus.IN_TRANSIT: RecordStatus.DELIVERED,
    RecordStatus.DELIVERED: RecordStatus.INVOICE_RAISED,
    RecordStatus.INVOICE_RAISED: RecordStatus.PAYMENT_RECEIVED,
    RecordStatus.PAYMENT_RECEIVED: RecordStatus.CLOSED,
    RecordStatus.CLOSED: None,
}

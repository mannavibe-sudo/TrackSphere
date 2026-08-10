"""
Import every model here so Base.metadata sees them all — required for
Alembic's autogenerate to detect the full schema.
"""
from app.models.base import Base
from app.models.company import Company
from app.models.user import User
from app.models.record import Record
from app.models.status_history import RecordStatusHistory
from app.models.attachment import Attachment
from app.models.comment import Comment
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.transporter import Transporter

__all__ = [
    "Base",
    "Company",
    "User",
    "Record",
    "RecordStatusHistory",
    "Attachment",
    "Comment",
    "AuditLog",
    "Notification",
    "Transporter",
]

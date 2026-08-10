"""User model. company_id is NULL only for super_admin (enforced by DB CHECK)."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Enum as SAEnum, func, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import UserRole, EntityStatus

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.record import Record
    from app.models.comment import Comment
    from app.models.notification import Notification


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "(role = 'super_admin' AND company_id IS NULL) OR "
            "(role <> 'super_admin' AND company_id IS NOT NULL)",
            name="chk_super_admin_no_company",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="RESTRICT")
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mobile: Mapped[str | None] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", native_enum=True, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=UserRole.DATA_ENTRY_USER,
        nullable=False,
    )
    status: Mapped[EntityStatus] = mapped_column(
        SAEnum(EntityStatus, name="entity_status", native_enum=True, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=EntityStatus.ACTIVE,
        nullable=False,
    )
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company: Mapped["Company | None"] = relationship(back_populates="users")
    records_created: Mapped[list["Record"]] = relationship(back_populates="created_by_user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")

    @property
    def is_super_admin(self) -> bool:
        return self.role == UserRole.SUPER_ADMIN

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"

"""
Repository layer for Record. This layer does NOT enforce tenant isolation
itself — it trusts the company_id filter passed in by the service layer.
Keeping that responsibility one layer up (in RecordService) means there is
exactly one place in the codebase that decides "who can see what."
"""
import uuid

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.record import Record
from app.schemas.record import RecordCreate, RecordUpdate


class RecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, record_id: uuid.UUID, company_id: uuid.UUID | None) -> Record | None:
        stmt = select(Record).where(
            Record.record_id == record_id, Record.deleted_at.is_(None)
        )
        if company_id is not None:
            stmt = stmt.where(Record.company_id == company_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(
        self,
        company_id: uuid.UUID | None,
        status: str | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Record], int]:
        stmt = select(Record).where(Record.deleted_at.is_(None))
        if company_id is not None:
            stmt = stmt.where(Record.company_id == company_id)
        if status:
            stmt = stmt.where(Record.status == status)
        if search:
            like = f"%{search}%"
            stmt = stmt.where(
                (Record.lr_no.ilike(like))
                | (Record.truck_number.ilike(like))
                | (Record.transporter_name.ilike(like))
                | (Record.invoice_number.ilike(like))
            )

        total = self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar_one()

        stmt = (
            stmt.order_by(Record.created_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def create(self, data: RecordCreate, company_id: uuid.UUID, created_by: uuid.UUID) -> Record:
        record = Record(
            **data.model_dump(exclude_unset=True),
            company_id=company_id,
            created_by=created_by,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: Record, data: RecordUpdate) -> Record:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def soft_delete(self, record: Record) -> None:
        from datetime import datetime, timezone

        record.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

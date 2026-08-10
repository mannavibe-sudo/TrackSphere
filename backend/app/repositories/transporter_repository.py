import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transporter import Transporter
from app.models.enums import EntityStatus


class TransporterRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active(self, company_id: uuid.UUID) -> list[Transporter]:
        stmt = (
            select(Transporter)
            .where(Transporter.company_id == company_id, Transporter.status == EntityStatus.ACTIVE)
            .order_by(Transporter.transporter_name)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_name(self, company_id: uuid.UUID, name: str) -> Transporter | None:
        stmt = select(Transporter).where(
            Transporter.company_id == company_id, Transporter.transporter_name == name
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, company_id: uuid.UUID, name: str) -> Transporter:
        transporter = Transporter(company_id=company_id, transporter_name=name)
        self.db.add(transporter)
        self.db.commit()
        self.db.refresh(transporter)
        return transporter

    def deactivate(self, transporter: Transporter) -> None:
        transporter.status = EntityStatus.INACTIVE
        self.db.commit()

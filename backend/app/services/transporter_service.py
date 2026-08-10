import uuid

from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.models.enums import UserRole
from app.models.transporter import Transporter
from app.repositories.transporter_repository import TransporterRepository


class TransporterPermissionError(Exception):
    pass


class DuplicateTransporterError(Exception):
    pass


class TransporterService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TransporterRepository(db)

    def list_for_company(self, current_user: CurrentUser, company_id: uuid.UUID | None = None) -> list[Transporter]:
        target_company_id = company_id or current_user.company_id
        if target_company_id is None:
            raise TransporterPermissionError("Super Admin must specify a company_id.")
        return self.repo.list_active(target_company_id)

    def create(self, current_user: CurrentUser, name: str) -> Transporter:
        if current_user.role == UserRole.DATA_ENTRY_USER:
            raise TransporterPermissionError(
                "Only a Company Admin or Super Admin can add a transporter."
            )
        if current_user.company_id is None:
            raise TransporterPermissionError("Super Admin must create transporters within a company context.")
        if self.repo.get_by_name(current_user.company_id, name):
            raise DuplicateTransporterError(f"'{name}' is already in the transporter list.")
        return self.repo.create(current_user.company_id, name)

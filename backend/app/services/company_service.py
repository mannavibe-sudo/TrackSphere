import uuid

from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.models.company import Company
from app.repositories.company_repository import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyPermissionError(Exception):
    pass


class CompanyNotFoundError(Exception):
    pass


class DuplicateCompanyCodeError(Exception):
    pass


class CompanyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CompanyRepository(db)

    def _assert_super_admin(self, current_user: CurrentUser) -> None:
        if not current_user.is_super_admin:
            raise CompanyPermissionError("Only Super Admin can manage companies.")

    def list(self, current_user: CurrentUser) -> list[Company]:
        # Company Admin / Data Entry User can see their own company's
        # basic details (e.g. to show the company name in the UI), but
        # only Super Admin sees the full multi-company list.
        if current_user.is_super_admin:
            return self.repo.list()
        if current_user.company_id is None:
            return []
        company = self.repo.get_by_id(current_user.company_id)
        return [company] if company else []

    def get(self, company_id: uuid.UUID, current_user: CurrentUser) -> Company:
        if not current_user.is_super_admin and current_user.company_id != company_id:
            raise CompanyPermissionError("You can only view your own company.")
        company = self.repo.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError("Company not found.")
        return company

    def create(self, data: CompanyCreate, current_user: CurrentUser) -> Company:
        self._assert_super_admin(current_user)
        if self.repo.get_by_code(data.company_code):
            raise DuplicateCompanyCodeError(
                f"Company code '{data.company_code}' is already in use."
            )
        return self.repo.create(data)

    def update(self, company_id: uuid.UUID, data: CompanyUpdate, current_user: CurrentUser) -> Company:
        self._assert_super_admin(current_user)
        company = self.repo.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError("Company not found.")
        return self.repo.update(company, data)

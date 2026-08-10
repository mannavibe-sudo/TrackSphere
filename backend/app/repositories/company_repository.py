import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, company_id: uuid.UUID) -> Company | None:
        return self.db.get(Company, company_id)

    def get_by_code(self, company_code: str) -> Company | None:
        stmt = select(Company).where(Company.company_code == company_code)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(self) -> list[Company]:
        stmt = select(Company).order_by(Company.company_name)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, data: CompanyCreate) -> Company:
        company = Company(**data.model_dump())
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update(self, company: Company, data: CompanyUpdate) -> Company:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)
        self.db.commit()
        self.db.refresh(company)
        return company

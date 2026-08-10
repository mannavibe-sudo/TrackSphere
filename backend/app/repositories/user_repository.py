"""Repository layer for User — the only place that runs raw queries on users."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def list_by_company(self, company_id: uuid.UUID) -> list[User]:
        stmt = select(User).where(User.company_id == company_id).order_by(User.name)
        return list(self.db.execute(stmt).scalars().all())

    def list_all(self) -> list[User]:
        stmt = select(User).order_by(User.name)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, **fields) -> User:
        for key, value in fields.items():
            if value is not None:
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

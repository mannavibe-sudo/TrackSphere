import uuid

from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_management import UserCreate, UserUpdate


class UserPermissionError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class DuplicateEmailError(Exception):
    pass


class UserManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def list(self, current_user: CurrentUser) -> list[User]:
        if current_user.is_super_admin:
            return self.repo.list_all()
        if current_user.company_id is None:
            return []
        return self.repo.list_by_company(current_user.company_id)

    def create(self, data: UserCreate, current_user: CurrentUser) -> User:
        if current_user.role == UserRole.DATA_ENTRY_USER:
            raise UserPermissionError("Only a Company Admin or Super Admin can create users.")

        if current_user.is_super_admin:
            # Super Admin can create a user in any company, or another
            # Super Admin (company_id stays None).
            target_company_id = data.company_id
            if data.role != UserRole.SUPER_ADMIN and target_company_id is None:
                raise UserPermissionError(
                    "company_id is required when creating a Company Admin or Data Entry User."
                )
        else:
            # Company Admin can only create Data Entry Users, only in their own company.
            if data.role != UserRole.DATA_ENTRY_USER:
                raise UserPermissionError(
                    "Company Admin can only create Data Entry Users."
                )
            target_company_id = current_user.company_id

        if self.repo.get_by_email(data.email):
            raise DuplicateEmailError(f"'{data.email}' is already registered.")

        user = User(
            company_id=target_company_id,
            name=data.name,
            email=data.email,
            mobile=data.mobile,
            password_hash=hash_password(data.password),
            role=data.role,
        )
        return self.repo.create(user)

    def update(self, user_id: uuid.UUID, data: UserUpdate, current_user: CurrentUser) -> User:
        if current_user.role == UserRole.DATA_ENTRY_USER:
            raise UserPermissionError("Only a Company Admin or Super Admin can edit users.")

        target = self.repo.get_by_id(user_id)
        if target is None:
            raise UserNotFoundError("User not found.")

        if not current_user.is_super_admin and target.company_id != current_user.company_id:
            raise UserPermissionError("You can only edit users in your own company.")

        return self.repo.update(
            target, name=data.name, mobile=data.mobile, role=data.role, status=data.status
        )

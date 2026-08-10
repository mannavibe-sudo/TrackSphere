"""
Record service — business logic layer.

Key rule (per product requirement): a Data Entry User can freely edit their
own record while it is still `draft`. The moment it's submitted (status
moves past draft), only Company Admin / Super Admin can edit it further.
"""
import uuid

from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.models.enums import RecordStatus, UserRole, RECORD_STATUS_FLOW
from app.models.record import Record
from app.repositories.record_repository import RecordRepository
from app.schemas.record import RecordCreate, RecordUpdate


class RecordPermissionError(Exception):
    """Raised when the current user isn't allowed to do this to this record."""


class RecordNotFoundError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    pass


class RecordService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RecordRepository(db)

    def _scoping_company_id(self, current_user: CurrentUser) -> uuid.UUID | None:
        """Super Admin sees everything (no filter); everyone else is scoped."""
        return None if current_user.is_super_admin else current_user.company_id

    def _assert_can_edit(self, record: Record, current_user: CurrentUser) -> None:
        if current_user.is_super_admin or current_user.role == UserRole.COMPANY_ADMIN:
            return
        # Data Entry User: allowed on their own draft records, OR a
        # submitted record an Admin has explicitly reopened for them.
        if record.status != RecordStatus.DRAFT and not record.edit_unlocked:
            raise RecordPermissionError(
                "This record has been submitted. Ask a Company Admin or "
                "Super Admin to reopen it if you need to make changes."
            )
        if record.created_by != current_user.user_id:
            raise RecordPermissionError("You can only edit records you created.")

    def get(self, record_id: uuid.UUID, current_user: CurrentUser) -> Record:
        record = self.repo.get_by_id(record_id, self._scoping_company_id(current_user))
        if record is None:
            raise RecordNotFoundError("Record not found.")
        return record

    def list(
        self,
        current_user: CurrentUser,
        status: str | None,
        search: str | None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Record], int]:
        # Data Entry Users see only records they created, even within their
        # own company — Company Admin / Super Admin see everyone's.
        own_only = (
            current_user.user_id
            if current_user.role == UserRole.DATA_ENTRY_USER
            else None
        )
        return self.repo.list(
            self._scoping_company_id(current_user),
            status,
            search,
            page,
            page_size,
            created_by=own_only,
        )

    def create_draft(self, data: RecordCreate, current_user: CurrentUser) -> Record:
        company_id = current_user.company_id
        if company_id is None:
            raise RecordPermissionError(
                "Super Admin must create records within a specific company context."
            )
        return self.repo.create(data, company_id, current_user.user_id)

    def update(self, record_id: uuid.UUID, data: RecordUpdate, current_user: CurrentUser) -> Record:
        record = self.get(record_id, current_user)
        self._assert_can_edit(record, current_user)
        return self.repo.update(record, data)

    def submit(self, record_id: uuid.UUID, current_user: CurrentUser) -> Record:
        """Moves a record from draft to the next stage (loading), locking it
        from further edits by the original Data Entry User."""
        record = self.get(record_id, current_user)
        self._assert_can_edit(record, current_user)

        next_status = RECORD_STATUS_FLOW.get(record.status)
        if next_status is None:
            raise InvalidStatusTransitionError(
                f"Record is already at its final status ({record.status.value})."
            )
        record.status = next_status
        record.edit_unlocked = False
        self.db.commit()
        self.db.refresh(record)
        return record

    def advance_status(self, record_id: uuid.UUID, current_user: CurrentUser) -> Record:
        """Advances a record one step further along the lifecycle (used by
        Company Admin / Super Admin from the Records screen)."""
        if current_user.role == UserRole.DATA_ENTRY_USER:
            raise RecordPermissionError(
                "Only a Company Admin or Super Admin can advance a record's status."
            )
        return self.submit(record_id, current_user)

    def soft_delete(self, record_id: uuid.UUID, current_user: CurrentUser) -> None:
        if current_user.role == UserRole.DATA_ENTRY_USER:
            raise RecordPermissionError("Only a Company Admin or Super Admin can delete records.")
        record = self.get(record_id, current_user)
        self.repo.soft_delete(record)

    def reopen(self, record_id: uuid.UUID, current_user: CurrentUser) -> Record:
        """Admin-only: lets the original Data Entry User edit a submitted
        record again, without changing its real lifecycle status."""
        if current_user.role == UserRole.DATA_ENTRY_USER:
            raise RecordPermissionError("Only a Company Admin or Super Admin can reopen a record.")
        record = self.get(record_id, current_user)
        record.edit_unlocked = True
        self.db.commit()
        self.db.refresh(record)
        return record

    def lock(self, record_id: uuid.UUID, current_user: CurrentUser) -> Record:
        """Admin-only: revokes the temporary edit access granted by reopen()."""
        if current_user.role == UserRole.DATA_ENTRY_USER:
            raise RecordPermissionError("Only a Company Admin or Super Admin can lock a record.")
        record = self.get(record_id, current_user)
        record.edit_unlocked = False
        self.db.commit()
        self.db.refresh(record)
        return record

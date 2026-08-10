import uuid

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.user_management import UserCreate, UserUpdate, UserManagementOut
from app.services.user_management_service import (
    UserManagementService,
    UserPermissionError,
    UserNotFoundError,
    DuplicateEmailError,
)

router = APIRouter(prefix="/users", tags=["Users"])


def _service(db: Session = Depends(get_db)) -> UserManagementService:
    return UserManagementService(db)


@router.get("", response_model=list[UserManagementOut])
def list_users(
    current_user: CurrentUser = Depends(get_current_user),
    service: UserManagementService = Depends(_service),
) -> list[UserManagementOut]:
    users = service.list(current_user)
    return [UserManagementOut.model_validate(u) for u in users]


@router.post("", response_model=UserManagementOut, status_code=http_status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserManagementService = Depends(_service),
) -> UserManagementOut:
    try:
        user = service.create(payload, current_user)
    except UserPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UserManagementOut.model_validate(user)


@router.patch("/{user_id}", response_model=UserManagementOut)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserManagementService = Depends(_service),
) -> UserManagementOut:
    try:
        user = service.update(user_id, payload, current_user)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return UserManagementOut.model_validate(user)

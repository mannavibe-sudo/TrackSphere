"""
Record endpoints. Thin — all rules live in RecordService.

Frontend mapping (Module 11):
  - "New Record" button          -> POST /records            (creates draft)
  - Each step's "Save & Continue" -> PATCH /records/{id}       (autosave)
  - Final "Submit Record"         -> POST /records/{id}/submit (draft -> loading)
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.record import (
    RecordCreate,
    RecordUpdate,
    RecordOut,
    RecordListResponse,
    RecordListItem,
)
from app.services.record_service import (
    RecordService,
    RecordNotFoundError,
    RecordPermissionError,
    InvalidStatusTransitionError,
)

router = APIRouter(prefix="/records", tags=["Records"])


def _service(db: Session = Depends(get_db)) -> RecordService:
    return RecordService(db)


@router.post("", response_model=RecordOut, status_code=http_status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: RecordService = Depends(_service),
) -> RecordOut:
    try:
        record = service.create_draft(payload, current_user)
    except RecordPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return RecordOut.model_validate(record)


@router.get("", response_model=RecordListResponse)
def list_records(
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    service: RecordService = Depends(_service),
) -> RecordListResponse:
    items, total = service.list(current_user, status_filter, search, page, page_size)
    return RecordListResponse(
        items=[RecordListItem.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{record_id}", response_model=RecordOut)
def get_record(
    record_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: RecordService = Depends(_service),
) -> RecordOut:
    try:
        record = service.get(record_id, current_user)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RecordOut.model_validate(record)


@router.patch("/{record_id}", response_model=RecordOut)
def update_record(
    record_id: uuid.UUID,
    payload: RecordUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: RecordService = Depends(_service),
) -> RecordOut:
    try:
        record = service.update(record_id, payload, current_user)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RecordPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return RecordOut.model_validate(record)


@router.post("/{record_id}/submit", response_model=RecordOut)
def submit_record(
    record_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: RecordService = Depends(_service),
) -> RecordOut:
    try:
        record = service.submit(record_id, current_user)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RecordPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except InvalidStatusTransitionError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RecordOut.model_validate(record)


@router.post("/{record_id}/advance-status", response_model=RecordOut)
def advance_status(
    record_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: RecordService = Depends(_service),
) -> RecordOut:
    """Company Admin / Super Admin only — moves a record to its next lifecycle stage."""
    try:
        record = service.advance_status(record_id, current_user)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RecordPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except InvalidStatusTransitionError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RecordOut.model_validate(record)


@router.post("/{record_id}/reopen", response_model=RecordOut)
def reopen_record(
    record_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: RecordService = Depends(_service),
) -> RecordOut:
    """Company Admin / Super Admin only — lets the original user edit a
    submitted record again without changing its lifecycle status."""
    try:
        record = service.reopen(record_id, current_user)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RecordPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return RecordOut.model_validate(record)


@router.post("/{record_id}/lock", response_model=RecordOut)
def lock_record(
    record_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: RecordService = Depends(_service),
) -> RecordOut:
    """Company Admin / Super Admin only — revokes a temporary reopen."""
    try:
        record = service.lock(record_id, current_user)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RecordPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return RecordOut.model_validate(record)


@router.delete("/{record_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: RecordService = Depends(_service),
) -> None:
    try:
        service.soft_delete(record_id, current_user)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RecordPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

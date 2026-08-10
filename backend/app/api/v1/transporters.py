"""
Transporter Master endpoints. Populates the "Transporter Name" dropdown in
the record form (Module 11) so every Data Entry User in a company picks
from the same admin-curated list instead of free-typing it.
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.transporter import TransporterCreate, TransporterOut
from app.services.transporter_service import (
    TransporterService,
    TransporterPermissionError,
    DuplicateTransporterError,
)

router = APIRouter(prefix="/transporters", tags=["Transporters"])


def _service(db: Session = Depends(get_db)) -> TransporterService:
    return TransporterService(db)


@router.get("", response_model=list[TransporterOut])
def list_transporters(
    current_user: CurrentUser = Depends(get_current_user),
    service: TransporterService = Depends(_service),
) -> list[TransporterOut]:
    try:
        transporters = service.list_for_company(current_user)
    except TransporterPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return [TransporterOut.model_validate(t) for t in transporters]


@router.post("", response_model=TransporterOut, status_code=http_status.HTTP_201_CREATED)
def create_transporter(
    payload: TransporterCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: TransporterService = Depends(_service),
) -> TransporterOut:
    try:
        transporter = service.create(current_user, payload.transporter_name)
    except TransporterPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except DuplicateTransporterError as exc:
        raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return TransporterOut.model_validate(transporter)

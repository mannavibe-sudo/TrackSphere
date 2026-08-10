import uuid

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut
from app.services.company_service import (
    CompanyService,
    CompanyPermissionError,
    CompanyNotFoundError,
    DuplicateCompanyCodeError,
)

router = APIRouter(prefix="/companies", tags=["Companies"])


def _service(db: Session = Depends(get_db)) -> CompanyService:
    return CompanyService(db)


@router.get("", response_model=list[CompanyOut])
def list_companies(
    current_user: CurrentUser = Depends(get_current_user),
    service: CompanyService = Depends(_service),
) -> list[CompanyOut]:
    companies = service.list(current_user)
    return [CompanyOut.model_validate(c) for c in companies]


@router.post("", response_model=CompanyOut, status_code=http_status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: CompanyService = Depends(_service),
) -> CompanyOut:
    try:
        company = service.create(payload, current_user)
    except CompanyPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except DuplicateCompanyCodeError as exc:
        raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return CompanyOut.model_validate(company)


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: CompanyService = Depends(_service),
) -> CompanyOut:
    try:
        company = service.get(company_id, current_user)
    except CompanyNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CompanyPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return CompanyOut.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: uuid.UUID,
    payload: CompanyUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: CompanyService = Depends(_service),
) -> CompanyOut:
    try:
        company = service.update(company_id, payload, current_user)
    except CompanyNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CompanyPermissionError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return CompanyOut.model_validate(company)

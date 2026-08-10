"""TrackSphere backend entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.records import router as records_router
from app.api.v1.transporters import router as transporters_router
from app.api.v1.companies import router as companies_router
from app.api.v1.users import router as users_router

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(records_router, prefix="/api/v1")
app.include_router(transporters_router, prefix="/api/v1")
app.include_router(companies_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}

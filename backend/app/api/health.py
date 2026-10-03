import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_repository
from app.config import get_settings
from app.errors import STORAGE_ERRORS
from app.repository import InvestigationRepository

VERSION = "0.2.0"

log = logging.getLogger("zuno.health")
router = APIRouter()


@router.get("/health")
def health() -> dict:
    """Liveness: the process is up. Does not touch dependencies."""
    return {"status": "ok", "service": "zuno-backend", "version": VERSION, "environment": get_settings().environment}


@router.get("/health/ready")
def ready(repo: InvestigationRepository = Depends(get_repository)):
    """Readiness: dependencies (Firestore) are reachable."""
    try:
        repo.ping()
        firestore = "ok"
    except STORAGE_ERRORS as exc:
        log.warning("firestore_unreachable", extra={"error_type": type(exc).__name__})
        firestore = "unavailable"
    ok = firestore == "ok"
    return JSONResponse(
        status_code=200 if ok else 503,
        content={"status": "ok" if ok else "degraded", "checks": {"firestore": firestore}},
    )

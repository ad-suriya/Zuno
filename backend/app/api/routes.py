from fastapi import APIRouter, Depends, status

from app.api.deps import get_service
from app.models import AddEvidenceRequest, CreateInvestigationRequest, InvestigationDetail
from app.service import InvestigationService

# NotFoundError and storage errors are mapped to HTTP responses in app/errors.py.
router = APIRouter(prefix="/api/v1")


@router.post("/investigations", response_model=InvestigationDetail, status_code=status.HTTP_201_CREATED)
def create_investigation(body: CreateInvestigationRequest, service: InvestigationService = Depends(get_service)):
    return service.start(body.story, body.language, body.channel)


@router.get("/investigations/{investigation_id}", response_model=InvestigationDetail)
def get_investigation(investigation_id: str, service: InvestigationService = Depends(get_service)):
    return service.detail(investigation_id)


@router.post("/investigations/{investigation_id}/evidence", response_model=InvestigationDetail)
def add_evidence(
    investigation_id: str, body: AddEvidenceRequest, service: InvestigationService = Depends(get_service)
):
    return service.add_evidence(investigation_id, body.content)


@router.post("/investigations/{investigation_id}/assessment", response_model=InvestigationDetail)
def assess_investigation(investigation_id: str, service: InvestigationService = Depends(get_service)):
    return service.run_assessment(investigation_id)

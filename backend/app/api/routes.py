from fastapi import APIRouter, Depends, status

from app.api.deps import get_service
from app.models import (
    AddEvidenceRequest,
    AnswerRequest,
    CreateInvestigationRequest,
    EvidenceKind,
    InvestigationDetail,
)
from app.service import InvestigationService

# NotFoundError, ConflictError, ApiProblem and storage errors are mapped to HTTP responses in app/errors.py.
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
    return service.add_evidence(investigation_id, body.content, EvidenceKind(body.kind))


@router.post("/investigations/{investigation_id}/assessment", response_model=InvestigationDetail)
def assess_investigation(investigation_id: str, service: InvestigationService = Depends(get_service)):
    return service.run_assessment(investigation_id)


# --- Adaptive questions (F06) ---


@router.post("/investigations/{investigation_id}/questions/next", response_model=InvestigationDetail)
def next_question(investigation_id: str, service: InvestigationService = Depends(get_service)):
    """Compute and store the next question; `next_question` is null when Zuno has enough."""
    return service.next_question(investigation_id)


@router.post("/investigations/{investigation_id}/questions/{question_id}/answer", response_model=InvestigationDetail)
def answer_question(
    investigation_id: str, question_id: str, body: AnswerRequest, service: InvestigationService = Depends(get_service)
):
    return service.answer(investigation_id, question_id, body.content)


@router.post("/investigations/{investigation_id}/questions/{question_id}/skip", response_model=InvestigationDetail)
def skip_question(investigation_id: str, question_id: str, service: InvestigationService = Depends(get_service)):
    return service.skip(investigation_id, question_id)


@router.post("/investigations/{investigation_id}/finish", response_model=InvestigationDetail)
def finish_investigation(investigation_id: str, service: InvestigationService = Depends(get_service)):
    """The user has nothing more to add: no more questions."""
    return service.finish(investigation_id)

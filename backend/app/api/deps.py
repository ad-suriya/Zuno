from functools import lru_cache

from app.config import get_settings
from app.repository import InvestigationRepository
from app.service import InvestigationService


@lru_cache
def get_repository() -> InvestigationRepository:
    from app.repository.firestore import FirestoreRepository

    return FirestoreRepository.from_settings(get_settings())


def get_service() -> InvestigationService:
    return InvestigationService(get_repository())

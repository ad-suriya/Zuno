import logging
from functools import lru_cache

from app.config import get_settings
from app.llm.client import FakeClient, GeminiClient, LLMClient
from app.repository import InvestigationRepository
from app.service import InvestigationService
from app.voice.sarvam import RateLimiter, SarvamClient


log = logging.getLogger("zuno.deps")


@lru_cache
def get_repository() -> InvestigationRepository:
    settings = get_settings()
    if settings.repository == "memory" and not settings.on_cloud_run:
        from app.repository.memory import InMemoryRepository

        log.warning("using_in_memory_repository: data is lost on restart (local demo only)")
        return InMemoryRepository()
    from app.repository.firestore import FirestoreRepository

    return FirestoreRepository.from_settings(settings)


@lru_cache
def get_llm() -> LLMClient:
    """Gemini when LLM_ENABLED=true and GEMINI_MODEL is set; otherwise every feature uses its fallback."""
    settings = get_settings()
    if settings.llm_enabled and settings.gemini_model:
        return GeminiClient(settings.google_cloud_project, settings.google_cloud_region, settings.gemini_model)
    return FakeClient()


def get_service() -> InvestigationService:
    return InvestigationService(get_repository(), get_llm())


@lru_cache
def get_voice() -> SarvamClient:
    settings = get_settings()
    return SarvamClient(settings.sarvam_api_key, settings.sarvam_stt_model, settings.sarvam_tts_model)


@lru_cache
def get_rate_limiter() -> RateLimiter:
    return RateLimiter(get_settings().voice_rate_per_minute)

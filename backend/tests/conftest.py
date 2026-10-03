from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_llm, get_repository, get_service
from app.engine.registry import Registry, load_registry
from app.llm.client import FakeClient
from app.main import app
from app.repository.memory import InMemoryRepository
from app.service import InvestigationService

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def repo() -> InMemoryRepository:
    return InMemoryRepository()


@pytest.fixture
def registry() -> Registry:
    """Small, fictional registry so unit tests don't depend on the real SEBI snapshot."""
    return load_registry(FIXTURES / "sebi_test_registry.csv")


@pytest.fixture
def llm() -> FakeClient:
    """Disabled LLM by default: every feature must work on its deterministic fallback."""
    return FakeClient()


@pytest.fixture
def service(repo, llm, registry) -> InvestigationService:
    return InvestigationService(repo, llm, registry)


@pytest.fixture
def client(repo, llm, service):
    app.dependency_overrides[get_service] = lambda: service
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_llm] = lambda: llm
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()

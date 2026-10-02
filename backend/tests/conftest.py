import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_repository, get_service
from app.main import app
from app.repository.memory import InMemoryRepository
from app.service import InvestigationService


@pytest.fixture
def repo() -> InMemoryRepository:
    return InMemoryRepository()


@pytest.fixture
def client(repo: InMemoryRepository):
    app.dependency_overrides[get_service] = lambda: InvestigationService(repo)
    app.dependency_overrides[get_repository] = lambda: repo
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()

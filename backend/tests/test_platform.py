"""Health checks, request IDs and error handling."""

import pytest
from fastapi.testclient import TestClient
from google.api_core.exceptions import ServiceUnavailable

from app.api.deps import get_repository, get_service
from app.main import app
from app.service import InvestigationService


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["service"] == "zuno-backend"


def test_ready_ok(client):
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "checks": {"firestore": "ok"}}


def test_request_id_generated_and_echoed(client):
    assert client.get("/health").headers["X-Request-ID"]
    assert client.get("/health", headers={"X-Request-ID": "abc"}).headers["X-Request-ID"] == "abc"


def test_error_body_includes_request_id(client):
    resp = client.get("/api/v1/investigations/nope", headers={"X-Request-ID": "rid-1"})
    assert resp.json()["error"]["request_id"] == "rid-1"


def test_unknown_route_uses_error_shape(client):
    resp = client.get("/nope")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "HTTP_ERROR"


def test_cors_allows_local_frontend(client):
    resp = client.options(
        "/health",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"


class BrokenRepo:
    def __init__(self, exc: Exception):
        self.exc = exc

    def __getattr__(self, name):
        def fail(*args, **kwargs):
            raise self.exc

        return fail


@pytest.fixture
def broken_client():
    def use(exc: Exception) -> TestClient:
        repo = BrokenRepo(exc)
        app.dependency_overrides[get_repository] = lambda: repo
        app.dependency_overrides[get_service] = lambda: InvestigationService(repo)
        return TestClient(app, raise_server_exceptions=False)

    yield use
    app.dependency_overrides.clear()


def test_ready_degraded_when_firestore_down(broken_client):
    resp = broken_client(ServiceUnavailable("down")).get("/health/ready")
    assert resp.status_code == 503
    assert resp.json()["checks"]["firestore"] == "unavailable"


def test_storage_failure_returns_503(broken_client):
    resp = broken_client(ServiceUnavailable("down")).post("/api/v1/investigations", json={"story": "hi"})
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "STORAGE_UNAVAILABLE"


def test_unexpected_failure_returns_500_without_details(broken_client):
    resp = broken_client(RuntimeError("secret internal detail")).post(
        "/api/v1/investigations", json={"story": "hi"}, headers={"Origin": "http://localhost:3000"}
    )
    assert resp.status_code == 500
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert resp.headers["X-Request-ID"]
    assert resp.json()["error"]["code"] == "INTERNAL_ERROR"
    assert "secret internal detail" not in resp.text

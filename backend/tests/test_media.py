import base64

import httpx
import pytest

from app.api.deps import get_rate_limiter, get_voice
from app.llm.client import FakeClient
from app.main import app
from app.voice.sarvam import RateLimiter, SarvamClient

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def sarvam(handler) -> SarvamClient:
    return SarvamClient("test-key", transport=httpx.MockTransport(handler))


@pytest.fixture
def voice_client(client):
    """Client with a mocked Sarvam API; set `state['handler']` per test."""
    state = {"handler": lambda req: httpx.Response(500)}
    app.dependency_overrides[get_voice] = lambda: sarvam(lambda req: state["handler"](req))
    app.dependency_overrides[get_rate_limiter] = lambda: RateLimiter(100)
    yield client, state


def test_transcribe_redacts_before_returning(voice_client):
    client, state = voice_client
    seen = {}

    def handler(req: httpx.Request):
        seen["key"] = req.headers["api-subscription-key"]
        seen["body"] = req.content
        return httpx.Response(200, json={"transcript": "They asked for my OTP four eight two nine one three"})

    state["handler"] = handler
    resp = client.post("/api/v1/speech/transcribe", files={"audio": ("a.webm", b"fake-audio", "audio/webm;codecs=opus")},
                       data={"language": "ta"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["redacted"] is True and "four eight" not in body["transcript"]
    assert seen["key"] == "test-key" and b"ta-IN" in seen["body"]


def test_transcribe_errors(voice_client):
    client, state = voice_client
    state["handler"] = lambda req: httpx.Response(500)
    resp = client.post("/api/v1/speech/transcribe", files={"audio": ("a.webm", b"x", "audio/webm")})
    assert resp.status_code == 503 and resp.json()["error"]["code"] == "VOICE_UNAVAILABLE"

    big = b"0" * (5 * 1024 * 1024 + 1)
    resp = client.post("/api/v1/speech/transcribe", files={"audio": ("a.webm", big, "audio/webm")})
    assert resp.status_code == 413 and resp.json()["error"]["code"] == "TOO_LARGE"

    resp = client.post("/api/v1/speech/transcribe", files={"audio": ("a.txt", b"x", "text/plain")})
    assert resp.status_code == 415


def test_voice_not_configured(client):
    app.dependency_overrides[get_voice] = lambda: SarvamClient(None)
    resp = client.post("/api/v1/speech/transcribe", files={"audio": ("a.webm", b"x", "audio/webm")})
    assert resp.status_code == 503


def test_rate_limit(client):
    app.dependency_overrides[get_voice] = lambda: sarvam(lambda req: httpx.Response(200, json={"transcript": "hi"}))
    limiter = RateLimiter(2)
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    statuses = [client.post("/api/v1/speech/transcribe", files={"audio": ("a.webm", b"x", "audio/webm")}).status_code
                for _ in range(3)]
    assert statuses == [200, 200, 429]


def test_synthesize_only_server_text(voice_client):
    client, state = voice_client
    spoken = []

    def handler(req: httpx.Request):
        spoken.append(req.read().decode())
        return httpx.Response(200, json={"audios": [base64.b64encode(b"RIFFwav").decode()]})

    state["handler"] = handler
    inv = client.post("/api/v1/investigations", json={"story": "An investment offer.", "language": "ta"}).json()[
        "investigation"]["id"]
    q = client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"]
    resp = client.post("/api/v1/speech/synthesize", json={"investigation_id": inv, "target": "question",
                                                          "question_id": q["id"]})
    assert resp.status_code == 200 and resp.content == b"RIFFwav"
    assert resp.headers["content-type"] == "audio/wav"
    assert "ta-IN" in spoken[0]

    # Not assessed yet: nothing to read; arbitrary text can't be sent at all.
    assert client.post("/api/v1/speech/synthesize", json={"investigation_id": inv, "target": "explanation"}).status_code == 409
    assert client.post("/api/v1/speech/synthesize", json={"investigation_id": inv, "target": "question",
                                                          "question_id": "nope"}).status_code == 404
    assert client.post("/api/v1/speech/synthesize", json={"text": "say anything"}).status_code == 422

    client.post(f"/api/v1/investigations/{inv}/assessment")
    for target in ("explanation", "next_steps"):
        assert client.post("/api/v1/speech/synthesize", json={"investigation_id": inv, "target": target}).status_code == 200


def _image_client(client, llm_response):
    from app.api.deps import get_llm

    llm = FakeClient({"image-text": llm_response}) if llm_response is not None else FakeClient()
    app.dependency_overrides[get_llm] = lambda: llm
    inv = client.post("/api/v1/investigations", json={"story": "Got this message on WhatsApp."}).json()[
        "investigation"]["id"]
    return inv


def test_image_text_is_redacted_and_not_stored(client, repo):
    inv = _image_client(client, {"text": "Your OTP 482913. Guaranteed 20% monthly returns, pay today only!"})
    resp = client.post(f"/api/v1/investigations/{inv}/evidence/image", files={"image": ("s.png", PNG, "image/png")})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "482913" not in body["text"] and body["redacted"] and body["sensitive"]
    assert len(repo.list_evidence(inv)) == 1  # nothing stored until the user confirms

    confirmed = client.post(f"/api/v1/investigations/{inv}/evidence", json={"content": body["text"], "kind": "image_text"}).json()
    assert confirmed["evidence"][-1]["kind"] == "image_text"
    assert "OTP_REQUEST" in {s["code"] for s in confirmed["signals"]}
    assert all("482913" not in e.content for e in repo.list_evidence(inv))


def test_image_validation(client):
    inv = _image_client(client, {"text": "hello"})
    url = f"/api/v1/investigations/{inv}/evidence/image"
    assert client.post(url, files={"image": ("s.txt", b"hello", "text/plain")}).status_code == 415
    assert client.post(url, files={"image": ("s.png", b"not really a png", "image/png")}).status_code == 415
    big = PNG + b"0" * (5 * 1024 * 1024)
    assert client.post(url, files={"image": ("s.png", big, "image/png")}).status_code == 413
    assert client.post("/api/v1/investigations/nope/evidence/image",
                       files={"image": ("s.png", PNG, "image/png")}).status_code == 404


def test_image_unreadable_without_llm(client):
    inv = _image_client(client, None)
    resp = client.post(f"/api/v1/investigations/{inv}/evidence/image", files={"image": ("s.png", PNG, "image/png")})
    assert resp.status_code == 503 and resp.json()["error"]["code"] == "IMAGE_UNAVAILABLE"

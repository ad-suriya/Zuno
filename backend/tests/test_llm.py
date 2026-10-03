import os

import pytest
from pydantic import BaseModel

from app.llm.client import FakeClient, GeminiClient
from app.llm.prompts import load_prompt, prompts_dir, render

PROMPTS = ["extraction", "adaptive-question", "explanation", "image-text"]


class Out(BaseModel):
    text: str


@pytest.mark.parametrize("name", PROMPTS)
def test_every_prompt_loads_with_safety_preamble(name):
    rendered = render(name, {"language": "ta", "evidence": "தமிழ் text"})
    assert rendered.startswith(load_prompt("safety"))
    assert "Never" in rendered or "never" in rendered
    assert "{{input}}" not in rendered
    assert "தமிழ் text" in rendered  # payload is embedded, non-ASCII kept


def test_prompts_dir_is_repo_root():
    assert (prompts_dir() / "safety.md").is_file()


def test_fake_client_validates_and_fails_safe():
    llm = FakeClient({"explanation": {"text": "ok"}})
    assert llm.generate_json("explanation", {}, Out) == Out(text="ok")
    assert FakeClient({"explanation": {"wrong": 1}}).generate_json("explanation", {}, Out) is None
    assert FakeClient({"explanation": "not json"}).generate_json("explanation", {}, Out) is None
    assert FakeClient({"explanation": TimeoutError()}).generate_json("explanation", {}, Out) is None
    assert FakeClient().generate_json("explanation", {}, Out) is None
    assert not FakeClient().enabled


def test_gemini_client_returns_none_on_errors(monkeypatch):
    client = GeminiClient("p", "asia-south1", "model")

    def boom(*args, **kwargs):
        raise TimeoutError("slow")

    monkeypatch.setattr(client, "_call", boom)
    assert client.generate_json("explanation", {}, Out) is None

    monkeypatch.setattr(client, "_call", lambda *a, **k: '{"text": 5}')
    assert client.generate_json("explanation", {}, Out) is None

    monkeypatch.setattr(client, "_call", lambda *a, **k: '{"text": "fine"}')
    assert client.generate_json("explanation", {}, Out) == Out(text="fine")


def test_gemini_client_retries_once(monkeypatch):
    from google.genai import errors

    client = GeminiClient("p", "asia-south1", "model")
    calls = []

    def flaky(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise ConnectionError("blip")
        return '{"text": "second time"}'

    monkeypatch.setattr(client, "_call", flaky)
    assert client.generate_json("explanation", {}, Out) == Out(text="second time")
    assert len(calls) == 2
    assert errors  # imported: the SDK is installed


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("GEMINI_MODEL") or os.environ.get("LLM_LIVE") != "1",
                    reason="live Gemini test: set LLM_LIVE=1, GEMINI_MODEL and ADC credentials")
def test_live_gemini_round_trip():
    import time

    client = GeminiClient(os.environ.get("GOOGLE_CLOUD_PROJECT", ""), os.environ.get("GOOGLE_CLOUD_REGION",
                          "asia-south1"), os.environ["GEMINI_MODEL"])
    start = time.monotonic()
    out = client.generate_json("explanation", {"language": "en", "level": "NEEDS_VERIFICATION",
                                               "level_label": "Needs verification", "reasons": [],
                                               "warning_signals": [], "next_steps": [], "max_words": 60}, Out)
    assert out is not None and out.text
    assert time.monotonic() - start < 10

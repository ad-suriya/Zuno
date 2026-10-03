"""LLM clients (F04, ADR-008).

`generate_json` never raises: on timeout, quota, safety block or schema mismatch it
returns None and the calling feature falls back to deterministic behaviour.
Only redacted text is ever sent. Prompts and responses are never logged; only the
prompt name, latency and outcome are.
"""

import logging
import time
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from app.llm.prompts import render

M = TypeVar("M", bound=BaseModel)
Image = tuple[bytes, str]  # (data, mime type)

log = logging.getLogger("zuno.llm")

TIMEOUT_MS = 10_000


class LLMClient(Protocol):
    enabled: bool

    def generate_json(
        self, prompt_name: str, payload: dict, schema: type[M], images: list[Image] | None = None
    ) -> M | None: ...


def _validate(schema: type[M], data: object) -> M | None:
    try:
        if isinstance(data, (str, bytes)):
            return schema.model_validate_json(data)
        return schema.model_validate(data)
    except ValidationError:
        return None


class FakeClient:
    """Canned responses keyed by prompt name. With no responses it behaves like a disabled LLM.

    A response may be a dict/JSON string, a callable(payload) -> dict, or an Exception to raise
    (to simulate SDK failures in tests).
    """

    def __init__(self, responses: dict[str, object] | None = None):
        self.responses = responses or {}
        self.enabled = bool(self.responses)
        self.calls: list[tuple[str, dict]] = []

    def generate_json(
        self, prompt_name: str, payload: dict, schema: type[M], images: list[Image] | None = None
    ) -> M | None:
        self.calls.append((prompt_name, payload))
        if prompt_name not in self.responses:
            return None
        response = self.responses[prompt_name]
        try:
            render(prompt_name, payload)  # same prompt path as production, so missing prompts fail tests
            if isinstance(response, Exception):
                raise response
            data = response(payload) if callable(response) else response
        except Exception as exc:  # noqa: BLE001 - mirror GeminiClient: never raise to the caller
            log.warning("llm_failed", extra={"prompt": prompt_name, "reason": type(exc).__name__})
            return None
        result = _validate(schema, data)
        if result is None:
            log.warning("llm_failed", extra={"prompt": prompt_name, "reason": "schema_mismatch"})
        return result


class GeminiClient:
    """Gemini on Vertex AI via the official `google-genai` SDK, using Application Default Credentials."""

    enabled = True

    def __init__(self, project: str, location: str, model: str, timeout_ms: int = TIMEOUT_MS):
        self.project = project
        self.location = location
        self.model = model
        self.timeout_ms = timeout_ms
        self._client = None

    def _sdk(self):
        if self._client is None:
            from google import genai
            from google.genai import types

            self._client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location,
                http_options=types.HttpOptions(timeout=self.timeout_ms),
            )
        return self._client

    def _call(self, prompt: str, schema: type[BaseModel], images: list[Image] | None) -> str | None:
        from google.genai import types

        contents: list = [prompt]
        for data, mime in images or []:
            contents.append(types.Part.from_bytes(data=data, mime_type=mime))
        response = self._sdk().models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.2,
            ),
        )
        return response.text

    def generate_json(
        self, prompt_name: str, payload: dict, schema: type[M], images: list[Image] | None = None
    ) -> M | None:
        from google.genai import errors

        start = time.monotonic()
        reason = "ok"
        result: M | None = None
        try:
            prompt = render(prompt_name, payload)
            for attempt in range(2):  # one retry on transient errors
                try:
                    text = self._call(prompt, schema, images)
                    break
                except (errors.ServerError, TimeoutError, ConnectionError) as exc:
                    if attempt == 1:
                        raise
                    log.info("llm_retry", extra={"prompt": prompt_name, "reason": type(exc).__name__})
            if not text:
                reason = "empty_or_blocked"
            else:
                result = _validate(schema, text)
                if result is None:
                    reason = "schema_mismatch"
        except Exception as exc:  # noqa: BLE001 - every LLM failure degrades to the fallback
            reason = type(exc).__name__
        latency_ms = int((time.monotonic() - start) * 1000)
        if result is None:
            log.warning("llm_failed", extra={"prompt": prompt_name, "reason": reason, "latency_ms": latency_ms})
        else:
            log.info("llm_ok", extra={"prompt": prompt_name, "latency_ms": latency_ms})
        return result


def disabled() -> FakeClient:
    return FakeClient()


"""Thin Sarvam client for speech-to-text and text-to-speech (F11, ADR-001, ADR-012).

The API key stays on the server. Audio is processed in memory only: it is never
stored or logged, and neither are transcripts.
API: https://docs.sarvam.ai (STT: POST /speech-to-text, TTS: POST /text-to-speech,
header `api-subscription-key`). Model names are configurable; empty uses Sarvam's default.
"""

import base64
import logging
import threading
import time

import httpx

from app.models import Language

log = logging.getLogger("zuno.voice")

BASE_URL = "https://api.sarvam.ai"
LANGUAGE_CODES = {Language.EN: "en-IN", Language.TA: "ta-IN"}
TIMEOUT_S = 30.0
MAX_TTS_CHARS = 1500  # the lower of the bulbul:v2 / v3 limits


class VoiceUnavailable(Exception):
    """Sarvam is not configured, failed or timed out. The app keeps working by typing."""


class SarvamClient:
    def __init__(self, api_key: str | None, stt_model: str = "", tts_model: str = "",
                 transport: httpx.BaseTransport | None = None):
        self.api_key = api_key
        self.stt_model = stt_model
        self.tts_model = tts_model
        self._transport = transport

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=BASE_URL, timeout=TIMEOUT_S, transport=self._transport,
                            headers={"api-subscription-key": self.api_key or ""})

    def transcribe(self, audio: bytes, content_type: str, language: Language) -> str:
        if not self.configured:
            raise VoiceUnavailable("not_configured")
        data = {"language_code": LANGUAGE_CODES[language]}
        if self.stt_model:
            data["model"] = self.stt_model
        start = time.monotonic()
        try:
            with self._client() as client:
                resp = client.post("/speech-to-text", data=data, files={"file": ("audio", audio, content_type)})
            resp.raise_for_status()
            transcript = resp.json().get("transcript")
        except (httpx.HTTPError, ValueError) as exc:
            log.warning("stt_failed", extra={"reason": type(exc).__name__})
            raise VoiceUnavailable("stt_failed") from exc
        if not isinstance(transcript, str):
            raise VoiceUnavailable("stt_bad_response")
        log.info("stt_ok", extra={"latency_ms": int((time.monotonic() - start) * 1000), "bytes": len(audio)})
        return transcript

    def synthesize(self, text: str, language: Language) -> bytes:
        """Return WAV bytes for server-generated text."""
        if not self.configured:
            raise VoiceUnavailable("not_configured")
        body = {"text": text[:MAX_TTS_CHARS], "language_code": LANGUAGE_CODES[language]}
        if self.tts_model:
            body["model"] = self.tts_model
        start = time.monotonic()
        try:
            with self._client() as client:
                resp = client.post("/text-to-speech", json=body)
            resp.raise_for_status()
            audios = resp.json().get("audios") or []
            audio = base64.b64decode(audios[0])
        except (httpx.HTTPError, ValueError, IndexError, TypeError) as exc:
            log.warning("tts_failed", extra={"reason": type(exc).__name__})
            raise VoiceUnavailable("tts_failed") from exc
        log.info("tts_ok", extra={"latency_ms": int((time.monotonic() - start) * 1000)})
        return audio


class RateLimiter:
    """In-memory token bucket per client IP, to protect the Sarvam quota. Per instance, which is
    enough for a demo; a shared limit would need Firestore or Redis."""

    def __init__(self, per_minute: int):
        self.capacity = max(1, per_minute)
        self.rate = self.capacity / 60.0
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            tokens, last = self._buckets.get(key, (float(self.capacity), now))
            tokens = min(self.capacity, tokens + (now - last) * self.rate)
            if tokens < 1:
                self._buckets[key] = (tokens, now)
                return False
            self._buckets[key] = (tokens - 1, now)
            return True

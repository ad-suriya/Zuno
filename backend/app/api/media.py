"""Voice (F11) and screenshot (F13) endpoints.

Audio and images are processed in memory and discarded: never written to Firestore,
Cloud Storage or logs (ADR-012). Transcribed text is redacted before it is returned,
and nothing becomes evidence until the user confirms the text and submits it.
"""

import re

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.api.deps import get_llm, get_rate_limiter, get_service, get_voice
from app.engine.safety import detect_hard_signals, redact
from app.errors import ApiProblem
from app.i18n import STEP_TEXT
from app.llm.client import LLMClient
from app.models import (
    ImageTextResponse,
    Language,
    SynthesizeRequest,
    TranscriptResponse,
)
from app.repository import NotFoundError
from app.service import InvestigationService
from app.voice.sarvam import RateLimiter, SarvamClient, VoiceUnavailable

router = APIRouter(prefix="/api/v1")

MAX_AUDIO_BYTES = 5 * 1024 * 1024  # ~60 s of compressed speech; the browser also stops recording at 60 s
MAX_IMAGE_BYTES = 5 * 1024 * 1024
AUDIO_TYPES = {"audio/webm", "audio/ogg", "audio/wav", "audio/x-wav", "audio/wave", "audio/mpeg", "audio/mp3",
               "audio/mp4", "audio/m4a", "audio/x-m4a", "audio/aac", "audio/flac"}
IMAGE_MAGIC = {"image/png": b"\x89PNG\r\n\x1a\n", "image/jpeg": b"\xff\xd8\xff"}
IMAGE_PROMPT = "image-text"
# Text that suggests the screenshot shows a banking app, OTP SMS or card: ask the user to crop it.
_BANKING_SCREEN = re.compile(
    r"\bavailable\s+balance\b|\baccount\s+(?:no|number)\b|\bifsc\b|\bvalid\s+thru\b|\bdebit\s+card\b|\bcredit\s+card\b"
    r"|\bdo\s+not\s+share\s+(?:this|the)\s+(?:otp|code)\b|\bverification\s+code\b",
    re.IGNORECASE,
)


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[0].strip() or (request.client.host if request.client else "unknown")


def _limit(request: Request, limiter: RateLimiter) -> None:
    if not limiter.allow(_client_key(request)):
        raise ApiProblem(429, "RATE_LIMITED", "Too many voice requests. Please wait a minute, or type instead.")


async def _read_limited(upload: UploadFile, limit: int) -> bytes:
    data = await upload.read(limit + 1)
    if len(data) > limit:
        raise ApiProblem(413, "TOO_LARGE", f"The file is too large (max {limit // (1024 * 1024)} MB).")
    if not data:
        raise ApiProblem(422, "VALIDATION_ERROR", "The file is empty.")
    return data


def _base_type(content_type: str | None) -> str:
    return (content_type or "").split(";")[0].strip().lower()


# --- Voice (F11) ---


@router.post("/speech/transcribe", response_model=TranscriptResponse)
async def transcribe(
    request: Request,
    audio: UploadFile = File(...),
    language: Language = Form(Language.EN),
    voice: SarvamClient = Depends(get_voice),
    limiter: RateLimiter = Depends(get_rate_limiter),
):
    content_type = _base_type(audio.content_type)
    if content_type not in AUDIO_TYPES:
        raise ApiProblem(415, "UNSUPPORTED_MEDIA", "Please record audio in a supported format.")
    data = await _read_limited(audio, MAX_AUDIO_BYTES)
    _limit(request, limiter)
    try:
        transcript = voice.transcribe(data, content_type, language)
    except VoiceUnavailable:
        raise ApiProblem(503, "VOICE_UNAVAILABLE", "Voice is not available right now. Please type instead.")
    finally:
        del data  # never kept beyond the request
    text, was_redacted = redact(transcript)
    return TranscriptResponse(transcript=text, redacted=was_redacted)


@router.post("/speech/synthesize")
def synthesize(
    request: Request,
    body: SynthesizeRequest,
    service: InvestigationService = Depends(get_service),
    voice: SarvamClient = Depends(get_voice),
    limiter: RateLimiter = Depends(get_rate_limiter),
):
    """Speak server-generated text only (a question, the explanation or the next steps)."""
    detail = service.detail(body.investigation_id)
    language = detail.investigation.language
    assessment = detail.investigation.assessment
    if body.target == "question":
        question = next((q for q in detail.questions if q.id == body.question_id), None)
        if question is None:
            raise NotFoundError(body.question_id or "", "Question")
        text = question.text
    elif assessment is None:
        raise ApiProblem(409, "CONFLICT", "This investigation has not been assessed yet.")
    elif body.target == "explanation":
        text = assessment.explanation.text if assessment.explanation else ""
    else:
        text = " ".join(STEP_TEXT[language][c] for c in assessment.next_steps if c in STEP_TEXT[language])
    if not text:
        raise ApiProblem(409, "CONFLICT", "There is nothing to read aloud yet.")
    _limit(request, limiter)
    try:
        audio = voice.synthesize(text, language)
    except VoiceUnavailable:
        raise ApiProblem(503, "VOICE_UNAVAILABLE", "Voice is not available right now.")
    return Response(content=audio, media_type="audio/wav", headers={"Cache-Control": "no-store"})


# --- Screenshot evidence (F13) ---


class ImageTextOutput(BaseModel):
    text: str


@router.post("/investigations/{investigation_id}/evidence/image", response_model=ImageTextResponse)
async def image_text(
    investigation_id: str,
    image: UploadFile = File(...),
    service: InvestigationService = Depends(get_service),
    llm: LLMClient = Depends(get_llm),
):
    """Read the message text in a screenshot. Returns redacted text for the user to confirm; stores nothing."""
    service.repo.get_investigation(investigation_id)  # 404 for unknown investigations
    content_type = _base_type(image.content_type)
    if content_type not in IMAGE_MAGIC:
        raise ApiProblem(415, "UNSUPPORTED_MEDIA", "Please upload a PNG or JPEG screenshot.")
    data = await _read_limited(image, MAX_IMAGE_BYTES)
    if not data.startswith(IMAGE_MAGIC[content_type]):
        raise ApiProblem(415, "UNSUPPORTED_MEDIA", "Please upload a PNG or JPEG screenshot.")
    out = llm.generate_json(IMAGE_PROMPT, {"instruction": "Transcribe the visible message text."}, ImageTextOutput,
                            images=[(data, content_type)]) if llm.enabled else None
    del data  # never kept beyond the request
    if out is None or not out.text.strip():
        raise ApiProblem(503, "IMAGE_UNAVAILABLE", "We couldn't read the image. Please type the message instead.")
    text, was_redacted = redact(out.text.strip())
    sensitive = bool(detect_hard_signals(out.text)) or bool(_BANKING_SCREEN.search(out.text))
    return ImageTextResponse(text=text, redacted=was_redacted, sensitive=sensitive)

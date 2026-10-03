"""Domain models. These are the API contract the frontend mirrors."""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

# Investigations and everything under them expire after this (PRIVACY.md, Firestore TTL on `expires_at`).
RETENTION = timedelta(days=7)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return uuid4().hex


def expiry() -> datetime:
    return utcnow() + RETENTION


class Language(str, Enum):
    EN = "en"
    TA = "ta"


class Channel(str, Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    CALL = "call"
    SOCIAL = "social"
    EMAIL = "email"
    IN_PERSON = "in_person"
    REFERRAL = "referral"
    OTHER = "other"
    UNKNOWN = "unknown"


class AssessmentLevel(str, Enum):
    LOW_CONCERN = "LOW_CONCERN"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    HIGH_CONCERN = "HIGH_CONCERN"


class SignalKind(str, Enum):
    WARNING = "WARNING"
    REASSURING = "REASSURING"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SignalSource(str, Enum):
    """Where a signal came from, so every finding is traceable (AI_BEHAVIOR.md)."""

    RULE = "RULE"  # deterministic rule applied to user-provided text
    VERIFIED_SOURCE = "VERIFIED_SOURCE"  # derived from a verification record


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class SourceTier(int, Enum):
    OFFICIAL_REGULATOR = 1
    OFFICIAL_ENTITY = 2
    REPUTABLE_SECONDARY = 3
    USER_PROVIDED = 4


class EvidenceKind(str, Enum):
    STORY = "story"
    TEXT = "text"  # pasted message, transcript, etc.
    ANSWER = "answer"  # answer to an adaptive question (F06)
    IMAGE_TEXT = "image_text"  # text read from a screenshot and confirmed by the user (F13)


class Unknown(str, Enum):
    """Fixed vocabulary of missing facts, so question selection stays deterministic (F05, F06)."""

    ENTITY_NAME = "ENTITY_NAME"
    REGISTRATION_NUMBER = "REGISTRATION_NUMBER"
    PAYMENT_RECIPIENT = "PAYMENT_RECIPIENT"
    AMOUNT = "AMOUNT"
    RETURN_CLAIM = "RETURN_CLAIM"
    CONTACT_CHANNEL = "CONTACT_CHANNEL"
    DOCUMENTATION = "DOCUMENTATION"
    PRODUCT_SOLD = "PRODUCT_SOLD"


class Evidence(BaseModel):
    id: str = Field(default_factory=new_id)
    kind: EvidenceKind
    content: str  # always stored redacted
    redacted: bool = False
    created_at: datetime = Field(default_factory=utcnow)


class Signal(BaseModel):
    id: str = Field(default_factory=new_id)
    kind: SignalKind
    code: str
    severity: Severity
    source: SignalSource
    evidence_id: str | None = None
    verification_id: str | None = None
    matched_text: str | None = None
    explanation: str
    created_at: datetime = Field(default_factory=utcnow)


class VerificationRecord(BaseModel):
    """Written only by the verification engine, never directly by API clients."""

    id: str = Field(default_factory=new_id)
    # Stable machine code for the outcome (e.g. REG_NAME_MATCH) + values, so clients can localize it.
    code: str = ""
    params: dict[str, str] = Field(default_factory=dict)
    claim: str
    source: str
    source_tier: SourceTier
    status: VerificationStatus
    evidence: str
    explanation: str
    material: bool = True  # does this claim matter for the assessment?
    checked_at: datetime = Field(default_factory=utcnow)


class AssessmentReason(BaseModel):
    rule: str
    explanation: str
    signal_ids: list[str] = Field(default_factory=list)
    verification_ids: list[str] = Field(default_factory=list)


class Explanation(BaseModel):
    """Plain-language explanation of the rules-decided level (F07). Never decides anything."""

    language: Language
    text: str
    source: Literal["llm", "template"]
    generated_at: datetime = Field(default_factory=utcnow)


class Assessment(BaseModel):
    level: AssessmentLevel
    reasons: list[AssessmentReason]
    next_steps: list[str] = Field(default_factory=list)  # step codes, localized by clients (F02)
    explanation: Explanation | None = None
    assessed_at: datetime = Field(default_factory=utcnow)


# --- Extracted facts (F05). Facts are claims to check, never verdicts. ---

EntityType = Literal["company", "person", "app", "website", "phone", "upi_id", "registration_number", "other"]
ClaimCategory = Literal["registration", "returns", "identity", "payment", "documentation", "product", "other"]


class Entity(BaseModel):
    type: EntityType
    value: str
    evidence_id: str


class Claim(BaseModel):
    text: str
    category: ClaimCategory
    evidence_id: str
    quote: str | None = None  # exact substring of the evidence, if any


class Facts(BaseModel):
    offer_type: str | None = None
    entities: list[Entity] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    money: list[str] = Field(default_factory=list)
    requests: list[str] = Field(default_factory=list)
    unknowns: list[Unknown] = Field(default_factory=list)  # computed in code, never trusted from the LLM
    updated_at: datetime = Field(default_factory=utcnow)


# --- Adaptive questions (F06) ---


class QuestionStatus(str, Enum):
    ASKED = "asked"
    ANSWERED = "answered"
    SKIPPED = "skipped"


class Question(BaseModel):
    id: str = Field(default_factory=new_id)
    text: str
    objective: str
    target_unknown: Unknown | None = None
    priority: Literal["high", "medium", "low"] = "medium"
    reasoning_source: str
    source: Literal["llm", "template"]
    status: QuestionStatus = QuestionStatus.ASKED
    answer_evidence_id: str | None = None
    asked_at: datetime = Field(default_factory=utcnow)


class Investigation(BaseModel):
    id: str = Field(default_factory=new_id)
    language: Language = Language.EN
    channel: Channel = Channel.UNKNOWN
    assessment: Assessment | None = None
    finished: bool = False  # the user pressed "Finish"; no more questions
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    expires_at: datetime = Field(default_factory=expiry)


class InvestigationDetail(BaseModel):
    investigation: Investigation
    evidence: list[Evidence]
    signals: list[Signal]
    verifications: list[VerificationRecord]
    facts: Facts | None = None
    questions: list[Question] = Field(default_factory=list)
    next_question: Question | None = None  # the question waiting for an answer, if any


# --- Request bodies ---


class CreateInvestigationRequest(BaseModel):
    story: str = Field(min_length=1, max_length=10_000)
    language: Language = Language.EN
    channel: Channel = Channel.UNKNOWN


class AddEvidenceRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)
    # "image_text" when the user confirmed text read from a screenshot (F13).
    kind: Literal["text", "image_text"] = "text"


class AnswerRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2_000)


class SynthesizeRequest(BaseModel):
    """Only server-generated text can be spoken, so the endpoint is not an open TTS proxy (F11)."""

    investigation_id: str
    target: Literal["question", "explanation", "next_steps"]
    question_id: str | None = None


class TranscriptResponse(BaseModel):
    transcript: str  # redacted
    redacted: bool


class ImageTextResponse(BaseModel):
    text: str  # redacted; nothing is stored until the user confirms it as evidence
    redacted: bool
    sensitive: bool  # looks like a banking app / OTP SMS / card: ask the user to crop it

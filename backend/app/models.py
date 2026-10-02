"""Domain models. These are the API contract the frontend mirrors."""

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return uuid4().hex


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


class Assessment(BaseModel):
    level: AssessmentLevel
    reasons: list[AssessmentReason]
    next_steps: list[str] = Field(default_factory=list)  # step codes (engine/next_steps.py)
    assessed_at: datetime = Field(default_factory=utcnow)


class Investigation(BaseModel):
    id: str = Field(default_factory=new_id)
    language: Language = Language.EN
    channel: Channel = Channel.UNKNOWN
    assessment: Assessment | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class InvestigationDetail(BaseModel):
    investigation: Investigation
    evidence: list[Evidence]
    signals: list[Signal]
    verifications: list[VerificationRecord]


# --- Request bodies ---


class CreateInvestigationRequest(BaseModel):
    story: str = Field(min_length=1, max_length=10_000)
    language: Language = Language.EN
    channel: Channel = Channel.UNKNOWN


class AddEvidenceRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)

"""Deterministic question ranker (F06, ADR-009).

The LLM may propose questions; this module decides. It can veto any candidate,
including templates, so no edit anywhere can make Zuno ask for a credential.

1. Veto: credential/OTP/PIN/password mentions (hard safety rules), investment advice,
   or sensitive identity/banking data (Aadhaar, PAN, account numbers...).
2. Dedupe: drop candidates for unknowns already resolved or already asked, and repeats.
3. Score: safety relevance > information gain > answerability > priority.
4. Tie-break by a fixed unknown order, then text, so the result is reproducible.
"""

import re
from dataclasses import dataclass

from app.engine.safety import detect_hard_signals
from app.models import Question, Unknown

UNKNOWN_ORDER: tuple[Unknown, ...] = (
    Unknown.ENTITY_NAME,
    Unknown.REGISTRATION_NUMBER,
    Unknown.PAYMENT_RECIPIENT,
    Unknown.PRODUCT_SOLD,
    Unknown.AMOUNT,
    Unknown.RETURN_CLAIM,
    Unknown.DOCUMENTATION,
    Unknown.CONTACT_CHANNEL,
)
# Unknowns that unlock verification come first.
SAFETY_WEIGHT: dict[Unknown | None, float] = {
    Unknown.ENTITY_NAME: 3.0,
    Unknown.REGISTRATION_NUMBER: 3.0,
    Unknown.PAYMENT_RECIPIENT: 3.0,
    Unknown.PRODUCT_SOLD: 2.0,
    Unknown.AMOUNT: 2.0,
    Unknown.RETURN_CLAIM: 1.5,
    Unknown.DOCUMENTATION: 1.0,
    Unknown.CONTACT_CHANNEL: 0.5,
    None: 0.5,
}
PRIORITY_WEIGHT = {"high": 0.3, "medium": 0.15, "low": 0.0}

_ADVICE = re.compile(
    r"\b(?:should|must|better|want\s+to)\s+(?:you\s+|i\s+|we\s+)?(?:buy|sell|hold|invest)\b"
    r"|\b(?:buy|sell|hold)\s+(?:this|these|that|the|some|more)?\s*(?:stocks?|shares?|units?|crypto|coins?|tokens?)\b"
    r"|\binvest\s+more\b|\bput\s+(?:in\s+)?more\s+money\b|\bprice\s+(?:will|target)\b"
    r"|(?:பங்கு|ஷேர்).{0,12}(?:வாங்க|விற்க)|இன்னும்\s*முதலீடு",
    re.IGNORECASE,
)
_SENSITIVE = re.compile(
    r"\baadha?ar\b|\bpan\s*(?:card|number|no)\b|\baccount\s+(?:number|no\.?)\b|\bifsc\b|\bdate\s+of\s+birth\b"
    r"|\bscreenshot\s+of\s+(?:your\s+)?(?:bank|banking|upi|payment)\b|\bcard\b.{0,15}\b(?:number|details|photo)\b"
    r"|\bpassport\b|\bselfie\b|ஆதார்|பான்\s*கார்டு|கணக்கு\s*எண்",
    re.IGNORECASE,
)
MAX_LENGTH = 300


@dataclass(frozen=True)
class Candidate:
    text: str
    objective: str
    target_unknown: Unknown | None
    priority: str
    reasoning_source: str
    source: str  # "llm" | "template"


def veto_reason(text: str) -> str | None:
    """Why a question must never be shown, or None if it is allowed."""
    if not text.strip() or len(text) > MAX_LENGTH:
        return "empty_or_too_long"
    if detect_hard_signals(text):
        return "credential_mention"
    if _ADVICE.search(text):
        return "investment_advice"
    if _SENSITIVE.search(text):
        return "sensitive_data"
    return None


def _norm(text: str) -> str:
    return re.sub(r"\W+", " ", text).strip().casefold()


def score(c: Candidate, boosts: dict[Unknown, float]) -> float:
    answerability = 0.5 if len(c.text) <= 140 else 0.25 if len(c.text) <= 220 else 0.0
    gain = boosts.get(c.target_unknown, 0.0) if c.target_unknown else 0.0
    return SAFETY_WEIGHT[c.target_unknown] + gain + answerability + PRIORITY_WEIGHT.get(c.priority, 0.0)


def rank(
    candidates: list[Candidate],
    *,
    open_unknowns: set[Unknown],
    asked: list[Question],
    boosts: dict[Unknown, float] | None = None,
) -> Candidate | None:
    """Pick the single best allowed candidate, or None."""
    boosts = boosts or {}
    asked_targets = {q.target_unknown for q in asked if q.target_unknown}
    asked_texts = {_norm(q.text) for q in asked}
    allowed = [
        c for c in candidates
        if veto_reason(c.text) is None
        and _norm(c.text) not in asked_texts
        and (c.target_unknown is None or (c.target_unknown in open_unknowns and c.target_unknown not in asked_targets))
    ]
    if not allowed:
        return None

    def key(c: Candidate) -> tuple:
        order = UNKNOWN_ORDER.index(c.target_unknown) if c.target_unknown else len(UNKNOWN_ORDER)
        return (-score(c, boosts), order, 0 if c.source == "llm" else 1, c.text)

    return sorted(allowed, key=key)[0]

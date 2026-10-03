"""Reassuring signals (F09, ADR-011): what looks right, shown next to what looks wrong.

They are derived from verification records and structured facts, never from flattering
wording alone, and they never change the level: `assess()` only counts WARNING signals,
and only tier 1-2 verification can move toward LOW CONCERN (ADR-006).
"""

import re

from app.engine.registry import MATCH_THRESHOLD, name_similarity, name_tokens
from app.models import (
    Facts,
    Question,
    QuestionStatus,
    Severity,
    Signal,
    SignalKind,
    SignalSource,
    SourceTier,
    Unknown,
    VerificationRecord,
    VerificationStatus,
)

# Below these stated rates a return claim is not flagged (mirrors red_flags._RATE_THRESHOLDS).
_RATE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_PERIOD_LIMITS = (
    (re.compile(r"day|daily|தினம|நாள்", re.IGNORECASE), 0.5),
    (re.compile(r"week|வாரம்", re.IGNORECASE), 1.0),
    (re.compile(r"month|மாத|maasam|masam", re.IGNORECASE), 3.0),
    (re.compile(r"year|annum|annual|p\.?\s?a|வருட|ஆண்டு", re.IGNORECASE), 36.0),
)
_GUARANTEE = re.compile(r"guarant|assured|sure|உத்தரவாத|கண்டிப்பா|kandippa", re.IGNORECASE)
RETURN_WARNINGS = {"GUARANTEED_RETURNS", "UNREALISTIC_RETURN_RATE", "DOUBLING_MONEY"}


def _signal(code: str, explanation: str, evidence_id: str | None = None, verification_id: str | None = None,
            matched: str | None = None) -> Signal:
    return Signal(kind=SignalKind.REASSURING, code=code, severity=Severity.LOW, source=(
        SignalSource.VERIFIED_SOURCE if verification_id else SignalSource.RULE
    ), evidence_id=evidence_id, verification_id=verification_id, matched_text=matched, explanation=explanation)


def _realistic(quote: str) -> bool:
    m = _RATE.search(quote)
    if not m or _GUARANTEE.search(quote):
        return False
    for period, limit in _PERIOD_LIMITS:
        if period.search(quote):
            return float(m.group(1)) < limit
    return False  # no period stated: can't judge


def reassuring_signals(facts: Facts | None, verifications: list[VerificationRecord], questions: list[Question],
                       warning_codes: set[str]) -> list[Signal]:
    signals: list[Signal] = []
    verified = [v for v in verifications
                if v.status == VerificationStatus.VERIFIED and v.source_tier == SourceTier.OFFICIAL_REGULATOR]
    for v in verified[:1]:
        signals.append(_signal(
            "REGISTRATION_VERIFIED",
            "The registration was found on SEBI's official register.",
            verification_id=v.id,
        ))
    if facts is None:
        return signals

    payment_question_answered = any(
        q.status == QuestionStatus.ANSWERED and q.target_unknown in (Unknown.AMOUNT, Unknown.PAYMENT_RECIPIENT)
        for q in questions
    )
    if payment_question_answered and not facts.money and "PAYMENT" not in facts.requests:
        signals.append(_signal("NO_UPFRONT_PAYMENT", "No upfront payment has been asked for so far."))

    if not warning_codes & RETURN_WARNINGS:
        for c in facts.claims:
            if c.category == "returns" and c.quote and _realistic(c.quote):
                signals.append(_signal(
                    "REALISTIC_RETURN_CLAIM",
                    "The return mentioned is in a normal range and is not described as guaranteed.",
                    evidence_id=c.evidence_id, matched=c.quote,
                ))
                break

    registered = [name_tokens(v.params.get("registered_name", "")) for v in verified]
    for e in facts.entities:
        if e.type != "upi_id" or not registered:
            continue
        handle = name_tokens(re.sub(r"[@._-]", " ", e.value))
        if any(name_similarity(handle, r) >= MATCH_THRESHOLD for r in registered):
            signals.append(_signal(
                "OFFICIAL_CHANNEL_PAYMENT",
                "The payment account appears to be in the registered firm's name.",
                evidence_id=e.evidence_id, matched=e.value,
            ))
            break
    return signals

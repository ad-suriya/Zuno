"""Adaptive question selection (docs/ADAPTIVE_ENGINE.md).

Pure and deterministic: no database, network or LLM calls. Given the evidence
text collected so far, it returns the single most useful next question, or
None when questioning should stop. An LLM may later reword the question
(docs/AI_BEHAVIOR.md) but never decides whether to ask it.
"""

from __future__ import annotations

import re
from collections.abc import Collection, Sequence
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict


class NextQuestion(BaseModel):
    """One question, with the four fields required by docs/AI_BEHAVIOR.md."""

    model_config = ConfigDict(frozen=True)

    code: str
    text: str
    objective: str
    expected_information: str
    priority: float
    reasoning: str


# Selection factors from docs/ADAPTIVE_ENGINE.md. Evidence already available
# and redundancy are applied as filters, not weights.
W_SAFETY = 0.35
W_GAIN = 0.30
W_ANSWERABLE = 0.20

DEFAULT_MAX_QUESTIONS = 5

# Questions must never ask for any of these (docs/SAFETY.md).
FORBIDDEN_TERMS = re.compile(
    r"\b(password|passcode|otp|pin|cvv|credentials?)s?\b", re.IGNORECASE
)


@dataclass(frozen=True)
class _Candidate:
    code: str
    text: str
    objective: str
    expected_information: str
    safety: float  # 0-1: how much the answer matters for protecting the user
    gain: float  # 0-1: how much the answer reduces uncertainty
    answerable: float  # 0-1: how likely the user can answer it
    known: re.Pattern[str]  # matches when the evidence already covers it


_CANDIDATES: tuple[_Candidate, ...] = (
    _Candidate(
        code="ENTITY",
        text="What is the exact company or organization name?",
        objective="Identify who is making the offer so it can be checked.",
        expected_information="Company, organization or person name.",
        safety=0.6,
        gain=1.0,
        answerable=0.9,
        known=re.compile(
            r"\b(?:pvt\.?\s*ltd|private\s+limited|ltd|llp)\b"
            r"|\b(?:company|firm|platform|broker|advisor|app|group)\s+"
            r"(?:is\s+)?(?:called|named)\s+\w+",
            re.IGNORECASE,
        ),
    ),
    _Candidate(
        code="PAYMENT_RECIPIENT",
        text=(
            "Who were you asked to send money to? "
            "Please share the name or UPI ID shown to you."
        ),
        objective="Find out where the money would go before any payment.",
        expected_information="Recipient name, UPI ID or account holder.",
        safety=0.9,
        gain=0.6,
        answerable=0.7,
        known=re.compile(
            r"\b(?:upi\s*id|account\s*(?:no|number)|ifsc|beneficiary)\b"
            r"|\b[\w.\-]{2,}@[a-z]{2,}\b",
            re.IGNORECASE,
        ),
    ),
    _Candidate(
        code="REGISTRATION",
        text=(
            "Did they give you any registration number, "
            "such as a SEBI registration number?"
        ),
        objective="Get a number that can be checked against official records.",
        expected_information="Registration or licence number.",
        safety=0.7,
        gain=0.8,
        answerable=0.5,
        known=re.compile(
            r"\bin[zhapbm]\d{9}\b"
            r"|\b[lu]\d{5}[a-z]{2}\d{4}[a-z]{3}\d{6}\b"
            r"|\breg(?:istration)?\.?\s*(?:no\.?|number)\s*[:\-]?\s*\w+",
            re.IGNORECASE,
        ),
    ),
    _Candidate(
        code="DOCUMENTATION",
        text="Did they share any document, certificate or official website?",
        objective="Collect material that can be checked or compared.",
        expected_information="Documents, certificates or a website address.",
        safety=0.4,
        gain=0.5,
        answerable=0.6,
        known=re.compile(
            r"\b(?:documents?|brochure|pdf|certificate|agreement|contract|website)\b"
            r"|www\.|https?://",
            re.IGNORECASE,
        ),
    ),
)


def _score(c: _Candidate) -> float:
    return W_SAFETY * c.safety + W_GAIN * c.gain + W_ANSWERABLE * c.answerable


def known_slots(evidence_texts: Sequence[str]) -> set[str]:
    """Codes of questions the evidence already answers."""
    text = "\n".join(evidence_texts)
    return {c.code for c in _CANDIDATES if c.known.search(text)}


def next_question(
    evidence_texts: Sequence[str],
    *,
    asked_codes: Collection[str] = (),
    assessment_is_stable: bool = False,
    user_finished: bool = False,
    max_questions: int = DEFAULT_MAX_QUESTIONS,
) -> NextQuestion | None:
    """Return the single most useful next question, or None to stop."""
    if user_finished or assessment_is_stable:
        return None
    if len(asked_codes) >= max_questions:
        return None

    skip = known_slots(evidence_texts) | set(asked_codes)
    remaining = [
        c
        for c in _CANDIDATES
        if c.code not in skip and not FORBIDDEN_TERMS.search(c.text)
    ]
    if not remaining:
        return None

    best = min(remaining, key=lambda c: (-_score(c), c.code))
    return NextQuestion(
        code=best.code,
        text=best.text,
        objective=best.objective,
        expected_information=best.expected_information,
        priority=round(_score(best), 3),
        reasoning=(
            f"Not yet known. Safety relevance {best.safety}, information gain "
            f"{best.gain}, user answerability {best.answerable} "
            "(docs/ADAPTIVE_ENGINE.md)."
        ),
    )

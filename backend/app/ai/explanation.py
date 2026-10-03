"""Explanation layer (F07): a short, calm explanation of the rules-decided result.

The LLM explains; it never decides. A deterministic output guard rejects any LLM text
that names a different level, uses banned phrases, asks for credentials or is too long
for voice; the template explanation is used instead.
"""

import re

from pydantic import BaseModel

from app.ai.questions import in_language
from app.i18n import LEVEL_LABEL, LEVEL_SENTENCE, PHRASES, REASON_TEXT, SIGNAL_SHORT, STEP_TEXT
from app.llm.client import LLMClient
from app.models import (
    Assessment,
    Explanation,
    Language,
    Severity,
    Signal,
    SignalKind,
    VerificationRecord,
)

PROMPT = "explanation"
MAX_WORDS = 120
SEVERITY_ORDER = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]

_BANNED = re.compile(
    r"definitely\s+(?:a\s+)?(?:scam|fraud)|100\s*%\s*(?:a\s+)?(?:fraud|scam|safe)|guaranteed\s+safe|completely\s+safe"
    r"|\b(?:buy|sell)\b|\binvest\s+in\b|நிச்சயமாக\s*மோசடி|கண்டிப்பாக\s*மோசடி|100\s*%\s*மோசடி",
    re.IGNORECASE,
)
# Asking the user for a credential (mentioning one, e.g. "never share your OTP", is fine).
_ASKS_CREDENTIAL = re.compile(
    r"\b(?:share|send|tell|give|enter|type|provide)\s+(?:us\s+|me\s+|zuno\s+)?(?:your|the)\s+"
    r"(?:otp|pin|upi\s*pin|password|cvv|card\s+number)"
    r"|(?:OTP|PIN|பாஸ்வேர்டு|கடவுச்சொல்).{0,20}(?:சொல்லுங்கள்|அனுப்புங்கள்|பகிருங்கள்|கொடுங்கள்|டைப்\s*செய்யுங்கள்)",
    re.IGNORECASE,
)

_NEGATED = re.compile(r"\b(?:never|not|don'?t|no\s+one|nobody|should\s+not|shouldn'?t)\b\W*(?:\w+\W+){0,2}$",
                      re.IGNORECASE)


def _asks_for_credential(text: str) -> bool:
    """True if the text asks for a credential; "never share your OTP" is advice, not a request."""
    return any(not _NEGATED.search(text[max(0, m.start() - 25): m.start()]) for m in _ASKS_CREDENTIAL.finditer(text))


class ExplanationOutput(BaseModel):
    text: str


def guard(text: str, assessment: Assessment, language: Language) -> str | None:
    """Why the LLM text must be rejected, or None if it may be shown."""
    if not text.strip():
        return "empty"
    lowered = text.casefold()
    for lang in LEVEL_LABEL:
        for level, label in LEVEL_LABEL[lang].items():
            if level != assessment.level and label.casefold() in lowered:
                return "different_level"
    if _BANNED.search(text):
        return "banned_phrase"
    if _asks_for_credential(text):
        return "asks_for_credential"
    if len(text.split()) > MAX_WORDS:
        return "too_long"
    if not in_language(text, language):
        return "wrong_language"
    return None


def template_explanation(assessment: Assessment, signals: list[Signal], language: Language) -> str:
    """Built from the reasons, top 3 warning signals and first 2 next steps."""
    parts = [LEVEL_SENTENCE[language][assessment.level]]
    reasons = REASON_TEXT[language]
    parts += [reasons[r.rule] for r in assessment.reasons[:2] if r.rule in reasons]
    warnings = sorted((s for s in signals if s.kind == SignalKind.WARNING), key=lambda s: SEVERITY_ORDER.index(s.severity))
    short = SIGNAL_SHORT[language]
    items = [short[s.code] for s in warnings if s.code in short][:3]
    if items:
        parts.append(PHRASES[language]["warning_signs"].format(items="; ".join(items)))
    steps = [STEP_TEXT[language][c] for c in assessment.next_steps[:2] if c in STEP_TEXT[language]]
    if steps:
        parts.append(PHRASES[language]["next"].format(steps=" ".join(steps)))
    return " ".join(parts)


def explain(llm: LLMClient, assessment: Assessment, signals: list[Signal], verifications: list[VerificationRecord],
            language: Language) -> Explanation:
    if llm.enabled:
        payload = {
            "language": language.value,
            "level": assessment.level.value,
            "level_label": LEVEL_LABEL[language][assessment.level],
            "reasons": [r.explanation for r in assessment.reasons],
            "warning_signals": [
                {"code": s.code, "explanation": s.explanation, "matched_text": s.matched_text}
                for s in signals if s.kind == SignalKind.WARNING
            ],
            "reassuring_signals": [s.explanation for s in signals if s.kind == SignalKind.REASSURING],
            "verifications": [{"claim": v.claim, "status": v.status.value, "explanation": v.explanation}
                              for v in verifications if v.material],
            "next_steps": [STEP_TEXT[language][c] for c in assessment.next_steps if c in STEP_TEXT[language]],
            "max_words": MAX_WORDS,
        }
        out = llm.generate_json(PROMPT, payload, ExplanationOutput)
        if out is not None and guard(out.text, assessment, language) is None:
            return Explanation(language=language, text=out.text.strip(), source="llm")
    return Explanation(language=language, text=template_explanation(assessment, signals, language), source="template")

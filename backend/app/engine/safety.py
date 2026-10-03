"""Deterministic safety rules: credential redaction and hard safety signals.

These run on every piece of user text before it is stored or sent to an LLM.
Hard safety signals are decided here, never by the LLM (SAFETY.md, ADR-002).

Note: Python's \\b is unreliable around Tamil combining marks, so Tamil
alternatives are matched without word boundaries.
"""

import re
from dataclasses import dataclass

from app.models import Severity

REDACTED = "[REDACTED]"

_KEYWORDS = (
    r"(?:\b(?:otp|one[\s-]?time[\s-]?password|upi[\s-]*pin|m-?pin|atm\s*pin|pin|passcode|password|cvv)\b"
    r"|ஓடிபி|கடவுச்சொல்|பின்\s*(?:எண்|நம்பர்))"
)
# A 4-8 digit code shortly after an OTP / PIN / password keyword ("482913", "4 8 2 9 1 3", "4829-13").
_CODE_AFTER_KEYWORD = re.compile(
    rf"({_KEYWORDS}[^\d\n]{{0,25}}?)(\d(?:[\s-]?\d){{3,7}})(?!\d)",
    re.IGNORECASE,
)
# Spoken codes as transcribed by speech-to-text: "my OTP is four eight two nine one three" (English/Tamil).
_DIGIT_WORD = (
    r"(?:zero|oh|one|two|three|four|five|six|seven|eight|nine|\d"
    r"|பூஜ்ஜியம்|சைபர்|ஒன்று|ஒண்ணு|இரண்டு|ரெண்டு|மூன்று|மூணு|நான்கு|நாலு|ஐந்து|அஞ்சு|ஆறு|ஏழு|எட்டு|ஒன்பது)"
)
_SPOKEN_CODE = re.compile(
    rf"({_KEYWORDS}[^\n]{{0,25}}?)(?<!\w)({_DIGIT_WORD}(?:[\s,.-]+{_DIGIT_WORD}){{3,7}})(?!\w)",
    re.IGNORECASE,
)
# "password is hunter2", "password: hunter2"
_PASSWORD_VALUE = re.compile(
    r"((?:\bpassword\b|\bpasscode\b|கடவுச்சொல்)\s*(?:is|:|=|-)\s*)(\S+)",
    re.IGNORECASE,
)
# 13-19 digit card numbers, optionally separated by spaces or dashes.
_CARD_NUMBER = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


def redact(text: str) -> tuple[str, bool]:
    """Remove credentials a user may have pasted by mistake (PRIVACY.md)."""
    out = _PASSWORD_VALUE.sub(lambda m: m.group(1) + REDACTED, text)
    out = _CODE_AFTER_KEYWORD.sub(lambda m: m.group(1) + REDACTED, out)
    out = _SPOKEN_CODE.sub(lambda m: m.group(1) + REDACTED, out)
    out = _CARD_NUMBER.sub(REDACTED, out)
    return out, out != text


@dataclass(frozen=True)
class Rule:
    code: str
    severity: Severity
    pattern: re.Pattern[str]
    explanation: str
    # Skip matches that are negated ("no joining fee", "returns are not guaranteed").
    # Hard safety rules are never negatable: "never share your OTP" still flags, erring on caution.
    negatable: bool = False


def _p(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.IGNORECASE)


HARD_SAFETY_RULES: tuple[Rule, ...] = (
    Rule(
        "OTP_REQUEST",
        Severity.CRITICAL,
        _p(r"\botp\b|one[\s-]?time[\s-]?password|ஓடிபி"),
        "An OTP is mentioned. Genuine investment platforms, banks and regulators never ask you to share an OTP.",
    ),
    Rule(
        "UPI_PIN_REQUEST",
        Severity.CRITICAL,
        _p(r"\bupi[\s-]*pin\b|\bm-?pin\b|\batm\s*pin\b|\benter\s+(?:your\s+|the\s+)?pin\b|பின்\s*(?:எண்|நம்பர்)"),
        "A PIN is mentioned. You never need to enter a UPI PIN to receive money, and no one should ask for it.",
    ),
    Rule(
        "PASSWORD_REQUEST",
        Severity.CRITICAL,
        _p(r"(?<!time\s)(?<!time-)\bpassword\b|\bpasscode\b|கடவுச்சொல்"),
        "A password is mentioned. No genuine opportunity requires your password.",
    ),
    Rule(
        "CREDENTIAL_REQUEST",
        Severity.CRITICAL,
        _p(
            r"\bcvv\b|\bcard\s+(?:number|details)\b|\bnet\s*banking\s+(?:login|id|details|credentials)\b"
            r"|\b(?:demat|trading|broker)\s+(?:login|credentials|account\s+details)\b"
        ),
        "Bank, card or trading-account credentials are mentioned. These should never be shared with anyone.",
    ),
    Rule(
        "REMOTE_ACCESS_REQUEST",
        Severity.CRITICAL,
        _p(r"\banydesk\b|\bteam\s?viewer\b|\bquick\s?support\b|\brustdesk\b|\bairdroid\b|\bscreen[\s-]?shar(?:e|ing)\b|\bremote\s+access\b"),
        "Remote access or screen sharing is mentioned. This can give someone control of your phone or bank apps.",
    ),
)


def detect_hard_signals(text: str) -> list[tuple[Rule, str]]:
    """Return (rule, matched_text) for each hard safety rule that fires."""
    hits = []
    for rule in HARD_SAFETY_RULES:
        m = rule.pattern.search(text)
        if m:
            hits.append((rule, m.group(0)))
    return hits

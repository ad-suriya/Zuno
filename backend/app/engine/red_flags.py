"""Deterministic warning-signal rules applied to user-provided text.

These catch common patterns in the wording of an offer. They are warning
signals, not verdicts: the assessment engine decides how they combine.
Recruitment or joining fees alone are MEDIUM, because MLM != fraud (SAFETY.md).
"""

import re

from app.engine.safety import Rule, _p
from app.models import Severity

RED_FLAG_RULES: tuple[Rule, ...] = (
    Rule(
        "GUARANTEED_RETURNS",
        Severity.HIGH,
        _p(
            r"\b(?:guarantee[ds]?|assured)\s+(?:\S+\s+){0,3}?(?:returns?|profits?|income|payouts?)\b"
            r"|\b(?:returns?|profits?|income)\s+(?:is\s+|are\s+)?(?:guaranteed|assured)\b"
            r"|\b(?:guarantee[ds]?|assured)\s+\d+(?:\.\d+)?\s*%"
            r"|\brisk[\s-]?free\b|\b(?:no|zero)\s+risk\b|உத்தரவாத"
        ),
        "Returns are described as guaranteed or risk-free. Real investments carry risk, and SEBI-registered "
        "entities are not allowed to guarantee returns.",
    ),
    Rule(
        "DOUBLING_MONEY",
        Severity.HIGH,
        _p(r"\bdoubl(?:e|es|ed|ing)\s+(?:your\s+|the\s+)?(?:money|investment|amount)\b|\bmoney\s+doubl|இரட்டிப்பு"),
        "The offer promises to double money, which is a common pattern in fraudulent schemes.",
    ),
    Rule(
        "WITHDRAWAL_FEE",
        Severity.HIGH,
        _p(r"\b(?:pay|deposit|send)\b.{0,40}\b(?:to|before|for)\s+(?:withdraw|withdrawal|release|unlock)"),
        "You are asked to pay before you can withdraw your own money. This is a common pattern in fraudulent schemes.",
    ),
    Rule(
        "APK_INSTALL",
        Severity.MEDIUM,
        _p(r"\.apk\b|\bapk\s+(?:file|link)\b|\binstall\s+(?:this|the|our)\s+apk\b"),
        "You are asked to install an app from outside the Play Store / App Store.",
    ),
    Rule(
        "SURE_SHOT_TIP",
        Severity.MEDIUM,
        _p(r"\bsure[\s-]?shot\b|\binsider\s+(?:tips?|info|information|news)\b|\b100\s*%\s*(?:sure|profit|accuracy)\b|\bjackpot\s+(?:stock|call|tip)"),
        "The offer claims certain or insider knowledge about market moves. No one can know this reliably.",
    ),
    Rule(
        "URGENCY_PRESSURE",
        Severity.MEDIUM,
        _p(
            r"\b(?:only|valid)\s+today\b|\btoday\s+only\b|\blimited\s+(?:slots?|seats?|time|period)\b"
            r"|\bact\s+(?:now|fast)\b|\blast\s+chance\b|\bhurry\b|\bwithin\s+\d+\s+(?:minutes?|mins?|hours?|hrs?)\b|அவசரம்"
        ),
        "You are being pressured to act quickly. Pressure to decide fast leaves no time to verify.",
    ),
    Rule(
        "RECRUITMENT_DEPENDENCE",
        Severity.MEDIUM,
        _p(
            r"\brecruit|\bdownline\b|\b(?:refer|bring|add|join)\s+(?:\d+|your\s+friends|friends|people|members)\b"
        ),
        "Earnings seem to depend on bringing in other people. This needs a closer look at whether real "
        "products or services are sold.",
    ),
    Rule(
        "ENTRY_FEE",
        Severity.MEDIUM,
        _p(r"\b(?:registration|joining|activation|membership|entry)\s+(?:fees?|charges?|amount)\b"),
        "An upfront fee is required to join. Check what the fee is for and whether it is refundable.",
    ),
    Rule(
        "SECRECY",
        Severity.MEDIUM,
        _p(r"\b(?:don'?t|do\s+not)\s+tell\s+(?:anyone|anybody|your\s+family)\b|\bkeep\s+(?:it|this)\s+(?:secret|confidential)\b"),
        "You are asked to keep this secret. Genuine opportunities do not need secrecy from your family.",
    ),
)

# "5% per month", "2% daily", "10 % weekly returns"
_RATE = re.compile(
    r"(\d+(?:\.\d+)?)\s*%\s*(?:(?:returns?|profits?|interest)\s+)?"
    r"(?:(?:per|a|every|each|/)\s*(day|week|month)|(daily|weekly|monthly))",
    re.IGNORECASE,
)
# Thresholds above which a stated return is flagged as unrealistic.
_RATE_THRESHOLDS = {"day": 0.5, "week": 1.0, "month": 3.0}
_PERIOD = {"daily": "day", "weekly": "week", "monthly": "month"}

UNREALISTIC_RETURN_EXPLANATION = (
    "The promised return rate is far above what regulated investments normally offer."
)


def detect_red_flags(text: str) -> list[tuple[Rule, str]]:
    """Return (rule, matched_text) for each warning rule that fires."""
    hits = []
    for rule in RED_FLAG_RULES:
        m = rule.pattern.search(text)
        if m:
            hits.append((rule, m.group(0)))
    for m in _RATE.finditer(text):
        period = (m.group(2) or _PERIOD[m.group(3).lower()]).lower()
        if float(m.group(1)) >= _RATE_THRESHOLDS[period]:
            rule = Rule("UNREALISTIC_RETURN_RATE", Severity.HIGH, _RATE, UNREALISTIC_RETURN_EXPLANATION)
            hits.append((rule, m.group(0)))
            break
    return hits

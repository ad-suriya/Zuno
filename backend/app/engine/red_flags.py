"""Deterministic warning-signal rules applied to user-provided text.

These catch common patterns in the wording of an offer. They are warning
signals, not verdicts: the assessment engine decides how they combine.
Recruitment or joining fees alone are MEDIUM, because MLM != fraud (SAFETY.md).

Each rule has English, Tamil-script and Tanglish (Tamil in Latin script) variants (F10).
Tamil script alternatives avoid \\b (see the note in safety.py). Negated matches
("no joining fee", "returns are not guaranteed") are skipped.
"""

import re

from app.engine.safety import Rule, _p
from app.models import Severity

RED_FLAG_RULES: tuple[Rule, ...] = (
    Rule(
        "GUARANTEED_RETURNS",
        Severity.HIGH,
        _p(
            r"\b(?:guarantee[ds]?|assured)\s+(?:\S+\s+){0,3}?(?:returns?|profits?|income|payouts?|labam)\b"
            r"|\b(?:returns?|profits?|income)\s+(?:is\s+|are\s+)?(?:guaranteed|assured)\b"
            r"|\b(?:guarantee[ds]?|assured)\s+\d+(?:\.\d+)?\s*%"
            r"|\brisk[\s-]?free\b|\b(?:no|zero)\s+risk\b|\bkandippa\s+(?:profit|labam|return)"
            r"|\bnashtam\s+(?:illa|illai|varaadhu|varathu)\b"
            r"|உத்தரவாத|கண்டிப்பா(?:க)?\s*(?:லாபம்|வருமானம்)|நஷ்டம்\s*(?:இல்லை|வராது)|ரிஸ்க்\s*இல்லை"
        ),
        "Returns are described as guaranteed or risk-free. Real investments carry risk, and SEBI-registered "
        "entities are not allowed to guarantee returns.",
        negatable=True,
    ),
    Rule(
        "DOUBLING_MONEY",
        Severity.HIGH,
        _p(
            r"\bdoubl(?:e|es|ed|ing)\s+(?:your\s+|the\s+)?(?:money|investment|amount)\b|\bmoney\s+doubl"
            r"|\bdouble\s+aa?gum\b|\brendu\s+madang|இரட்டிப்பு|இரண்டு\s*மடங்கு|ரெண்டு\s*மடங்கு"
        ),
        "The offer promises to double money, which is a common pattern in fraudulent schemes.",
        negatable=True,
    ),
    Rule(
        "WITHDRAWAL_FEE",
        Severity.HIGH,
        _p(
            r"\b(?:pay|deposit|send)\b.{0,40}\b(?:to|before|for)\s+(?:withdraw|withdrawal|release|unlock)"
            r"|\bwithdraw(?:al)?\b.{0,30}\b(?:pay|deposit|kattanum|kattunga)\b.{0,25}\b(?:tax|fee|charges?|first)\b"
            r"|\bwithdraw\s+panna.{0,30}kat"
            r"|(?:எடுக்க|எடுப்பதற்கு|திரும்பப்\s*பெற|வித்ட்ரா).{0,30}(?:கட்ட|செலுத்த|வரி|கட்டணம்)"
        ),
        "You are asked to pay before you can withdraw your own money. This is a common pattern in fraudulent schemes.",
        negatable=True,
    ),
    Rule(
        "APK_INSTALL",
        Severity.MEDIUM,
        _p(r"\.apk\b|\bapk\s+(?:file|link)\b|\binstall\s+(?:this|the|our)\s+apk\b|ஏபிகே"),
        "You are asked to install an app from outside the Play Store / App Store.",
        negatable=True,
    ),
    Rule(
        "SURE_SHOT_TIP",
        Severity.MEDIUM,
        _p(
            r"\bsure[\s-]?shot\b|\binsider\s+(?:tips?|info|information|news)\b|\b100\s*%\s*(?:sure|profit|accuracy)\b"
            r"|\bjackpot\s+(?:stock|call|tip)|ஷ்யூர்\s*ஷாட்|உள்\s*தகவல்|100\s*%\s*(?:உறுதி|லாபம்)"
        ),
        "The offer claims certain or insider knowledge about market moves. No one can know this reliably.",
        negatable=True,
    ),
    Rule(
        "URGENCY_PRESSURE",
        Severity.MEDIUM,
        _p(
            r"\b(?:only|valid)\s+today\b|\btoday\s+only\b|\blimited\s+(?:slots?|seats?|time|period)\b"
            r"|\bact\s+(?:now|fast)\b|\blast\s+chance\b|\bhurry\b|\bwithin\s+\d+\s+(?:minutes?|mins?|hours?|hrs?)\b"
            r"|\binn?(?:i|ai)ku\s+(?:mattum|matum)\b|\budane\s+(?:pay|kattunga|anuppunga|join)"
            r"|அவசரம்|இன்று\s*மட்டும்|இன்னைக்கு\s*மட்டும்|உடனே\s*(?:கட்ட|செலுத்த|அனுப்ப|சேர)|கடைசி\s*வாய்ப்பு"
        ),
        "You are being pressured to act quickly. Pressure to decide fast leaves no time to verify.",
        negatable=True,
    ),
    Rule(
        "RECRUITMENT_DEPENDENCE",
        Severity.MEDIUM,
        _p(
            r"\brecruit|\bdownline\b"
            r"|\b(?:refer|bring|add|join)(?:ing)?\s+(?:\d+|your\s+friends|friends|people|members|more\s+people)\b"
            r"|\b(?:aal|aala|members?|friends?)(?:-?a)?\s+(?:serkanum|serthaa|serthal|sethaa)"
            r"|(?:ஆட்களை|ஆட்கள்|உறுப்பினர்களை|நண்பர்களை)\s*சேர்"
        ),
        "Earnings seem to depend on bringing in other people. This needs a closer look at whether real "
        "products or services are sold.",
        negatable=True,
    ),
    Rule(
        "ENTRY_FEE",
        Severity.MEDIUM,
        _p(
            r"\b(?:registration|joining|activation|membership|entry)\s+(?:fees?|charges?|amount)\b"
            r"|(?:சேர்க்கை|பதிவு|உறுப்பினர்|இணைப்பு)\s*(?:கட்டணம்|தொகை)"
        ),
        "An upfront fee is required to join. Check what the fee is for and whether it is refundable.",
        negatable=True,
    ),
    Rule(
        "SECRECY",
        Severity.MEDIUM,
        _p(
            r"\b(?:don'?t|do\s+not)\s+tell\s+(?:anyone|anybody|your\s+family)\b|\bkeep\s+(?:it|this)\s+(?:secret|confidential)\b"
            r"|\byaar\s*kitt?a(?:yum)?\s+(?:sollatheenga|sollaadheenga|solla\s+vendam)|\bragasiyam"
            r"|யாரிடமும்\s*(?:சொல்ல|கூற)|ரகசியமாக?\s*வை"
        ),
        "You are asked to keep this secret. Genuine opportunities do not need secrecy from your family.",
    ),
)

# "no guaranteed returns", "it is not risk free", "don't need any joining fee". English only.
_NEGATION_BEFORE = re.compile(
    r"\b(?:no|not|never|without|don'?t|doesn'?t|didn'?t|isn'?t|aren'?t|wasn'?t|can'?t|cannot|won'?t|nothing)\b"
    r"(?:\s+\S+){0,2}\s*$",
    re.IGNORECASE,
)


def _first_match(rule: Rule, text: str) -> str | None:
    for m in rule.pattern.finditer(text):
        if rule.negatable and _NEGATION_BEFORE.search(text[max(0, m.start() - 30): m.start()]):
            continue
        return m.group(0)
    return None


# "5% per month", "2% daily", "10 % weekly returns", "monthly 20%", "மாதம் 20%", "maasam 20%".
_PERIOD_WORD = (
    r"(?:per|a|every|each|/)\s*(?:day|week|month)|daily|weekly|monthly"
    r"|தினமும்|தினசரி|நாளொன்றுக்கு|நாளுக்கு|வாரம்|வாரத்திற்கு|மாதம்|மாதத்திற்கு|மாதா\s*மாதம்"
    r"|maasam|masam|maasathuku|dhinamum|dinamum|vaaram"
)
_RATE_AFTER = re.compile(
    rf"(\d+(?:\.\d+)?)\s*%\s*(?:(?:returns?|profits?|interest|லாபம்|வட்டி)\s*)?({_PERIOD_WORD})",
    re.IGNORECASE,
)
_RATE_BEFORE = re.compile(
    rf"({_PERIOD_WORD})\s*(?:(?:returns?|profits?|interest|லாபம்|வருமானம்|vaddi)\s*)?(\d+(?:\.\d+)?)\s*%",
    re.IGNORECASE,
)
# Thresholds above which a stated return is flagged as unrealistic.
_RATE_THRESHOLDS = {"day": 0.5, "week": 1.0, "month": 3.0}
_PERIOD_KEYS = (
    ("day", re.compile(r"day|daily|தின|நாள|dhinam|dinam", re.IGNORECASE)),
    ("week", re.compile(r"week|வார|vaaram", re.IGNORECASE)),
    ("month", re.compile(r"month|மாத|maas|mas", re.IGNORECASE)),
)


def _period(word: str) -> str:
    for key, pattern in _PERIOD_KEYS:
        if pattern.search(word):
            return key
    return "month"


def _rates(text: str):
    for m in _RATE_AFTER.finditer(text):
        yield float(m.group(1)), _period(m.group(2)), m.group(0)
    for m in _RATE_BEFORE.finditer(text):
        yield float(m.group(2)), _period(m.group(1)), m.group(0)

UNREALISTIC_RETURN_EXPLANATION = (
    "The promised return rate is far above what regulated investments normally offer."
)
UNREALISTIC_RETURN_RULE = Rule("UNREALISTIC_RETURN_RATE", Severity.HIGH, _RATE_AFTER, UNREALISTIC_RETURN_EXPLANATION)


def detect_red_flags(text: str) -> list[tuple[Rule, str]]:
    """Return (rule, matched_text) for each warning rule that fires."""
    hits = []
    for rule in RED_FLAG_RULES:
        matched = _first_match(rule, text)
        if matched is not None:
            hits.append((rule, matched))
    for rate, period, matched in _rates(text):
        if rate >= _RATE_THRESHOLDS[period]:
            hits.append((UNREALISTIC_RETURN_RULE, matched))
            break
    return hits

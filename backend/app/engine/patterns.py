"""Deterministic fact extractors (F05). They work without the LLM and are always merged in.

They extract facts to check, never verdicts: nothing here creates a Signal.
Tamil script has no reliable \\b, so Tamil alternatives avoid word boundaries.
"""

import re
from dataclasses import dataclass

# SEBI registration numbers: "IN" + category letter + 9 digits, e.g. INA000017523 (investment adviser),
# INH000011431 (research analyst), INZ000284836 (stock broker; INB/INF are older broker formats),
# INM000012801 (merchant banker), INP000001234 (portfolio manager).
REG_NO_PREFIXES = {
    "INA": "Investment Adviser",
    "INH": "Research Analyst",
    "INZ": "Stock Broker",
    "INB": "Stock Broker",
    "INF": "Stock Broker",
    "INM": "Merchant Banker",
    "INP": "Portfolio Manager",
}
# Candidates allow spaces/dashes and a wrong digit count, so malformed numbers can be explained (F08).
_REG_CANDIDATE = re.compile(r"(?<![A-Za-z0-9])IN\s?-?\s?([A-Z])\s?-?\s?(\d{4,12})(?!\d)", re.IGNORECASE)

_UPI = re.compile(r"(?<![\w.@-])([\w.-]{2,64}@[A-Za-z][A-Za-z0-9]{1,30})(?![\w@-]|\.[A-Za-z])")
_PHONE = re.compile(r"(?<![\w+])(?:\+91[\s-]?|91[\s-]|0)?([6-9]\d{4}[\s-]?\d{5})(?!\d)")
_URL = re.compile(
    r"(?<![@\w.])(?:https?://[^\s<>\"']+|www\.[^\s<>\"']+|[a-z0-9-]+\.(?:com|in|co\.in|net|org|app|xyz|io|live|club|"
    r"online|site|info|vip|top)(?:/[^\s<>\"']*)?)(?![\w@])",
    re.IGNORECASE,
)
_AMOUNT = re.compile(
    r"(?:₹|\brs\.?|\binr\b|ரூ\.?)\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:k\b|l\b|lakhs?\b|lacs?\b|crores?\b|cr\b|லட்சம்|கோடி))?"
    r"|\b\d[\d,]*(?:\.\d+)?\s?(?:lakhs?|lacs?|crores?|rupees)\b"
    r"|\d[\d,]*(?:\.\d+)?\s?(?:ரூபாய்|லட்சம்|கோடி)",
    re.IGNORECASE,
)
# "20% monthly", "2% daily returns", "monthly 20%", Tamil "மாதம் 20%".
_PERIOD_WORDS = (
    r"(?:per\s+(?:day|week|month|year|annum)|a\s+(?:day|week|month|year)|daily|weekly|monthly|yearly|annually|p\.?\s?a\.?"
    r"|every\s+(?:day|week|month)|மாதம்|மாதத்திற்கு|தினமும்|நாளொன்றுக்கு|வாரம்|வருடம்|ஆண்டுக்கு|maasam|masam)"
)
_RETURN = re.compile(
    rf"\d+(?:\.\d+)?\s*%\s*(?:(?:returns?|profits?|interest|லாபம்|வட்டி)\s*)?{_PERIOD_WORDS}"
    rf"|{_PERIOD_WORDS}\s*\d+(?:\.\d+)?\s*%"
    r"|\d+(?:\.\d+)?\s*%\s*(?:returns?|profits?|interest|லாபம்|வருமானம்)"
    r"|\bdoubl(?:e|es|ed|ing)\s+(?:your\s+|the\s+)?(?:money|investment|amount)\b|இரட்டிப்பு",
    re.IGNORECASE,
)
_REGISTRATION_CLAIM = re.compile(
    r"\bsebi[\s-]*(?:registered|regd|reg\b|registration|approved|certified|licen[sc]ed)"
    r"|\bregistered\s+(?:with|under|by)\s+sebi\b|செபி|SEBI\s*(?:பதிவு|அங்கீகார)",
    re.IGNORECASE,
)
_DOCUMENTATION = re.compile(
    r"\b(?:agreement|contract|invoice|receipt|bill|terms\s+and\s+conditions|brochure|offer\s+letter)\b"
    r"|ஒப்பந்தம்|ரசீது|இன்வாய்ஸ்",
    re.IGNORECASE,
)
_PAYMENT_REQUEST = re.compile(
    r"\b(?:pay|paid|send|sent|deposit|transfer|invest)\b|கட்ட|செலுத்த|அனுப்ப|katt?an?um|anupp",
    re.IGNORECASE,
)
# Company-like names: capitalised words ending in a common business suffix. Case-sensitive on purpose.
_COMPANY = re.compile(
    r"\b((?:[A-Z0-9][\w&'.-]*\s+){1,5}(?:Private\s+Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|LLP|Advisors?|Advisers?|"
    r"Advisory|Capital|Securities|Investments?|Wealth|Finance|Financial\s+Services|Research|Broking|Fintech|"
    r"Markets?|Trading|Ventures|Holdings)\b\.?)"
)
_QUOTED_NAME = re.compile(r"(?:company|firm|from|called|named|by)\s+[\"'“‘]([^\"'”’\n]{3,60})[\"'”’]", re.IGNORECASE)
# Leading words that are sentence glue, not part of a name ("The", "From", ...).
_NAME_STOPWORDS = {"the", "a", "an", "from", "with", "by", "at", "of", "for", "and", "my", "our", "their", "his", "her",
                   "this", "that", "called", "named", "company", "firm", "in", "on", "to", "is", "was"}

_OFFER_TYPES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("mlm", re.compile(r"\bmlm\b|multi[\s-]?level|network\s+marketing|direct\s+selling|downline|joining\s+fee"
                       r"|\brecruit|add\s+members|நெட்வொர்க்|உறுப்பினர்", re.IGNORECASE)),
    ("crypto", re.compile(r"\bcrypto|bitcoin|\busdt\b|\btoken\b|blockchain|கிரிப்டோ", re.IGNORECASE)),
    ("loan", re.compile(r"\bloan\b|கடன்", re.IGNORECASE)),
    ("job", re.compile(r"\bpart[\s-]?time\b|\bjob\b|\btask\b|work\s+from\s+home|வேலை", re.IGNORECASE)),
    ("trading_tips", re.compile(r"\btips?\b|\bcalls?\b.*\b(?:stock|share|nifty)|telegram\s+group|\bintraday\b"
                                r"|\bf&o\b|options|டிப்ஸ்", re.IGNORECASE)),
    ("advisory", re.compile(r"\badvis[oe]r|advisory|research\s+analyst|ஆலோசக", re.IGNORECASE)),
    ("investment", re.compile(r"\binvest|\breturns?\b|\bprofit|\bscheme\b|\bplan\b|\bstocks?\b|\bshares?\b|\btrading\b"
                              r"|முதலீடு|லாபம்", re.IGNORECASE)),
)

# Offer types for which SEBI registration is the relevant check (F08).
SEBI_OFFER_TYPES = {"investment", "trading_tips", "advisory", "crypto"}


@dataclass(frozen=True)
class RegNo:
    value: str  # normalised, e.g. "INA000017523"
    raw: str  # as written in the evidence
    well_formed: bool


def find_reg_numbers(text: str) -> list[RegNo]:
    out: dict[str, RegNo] = {}
    for m in _REG_CANDIDATE.finditer(text):
        letter, digits = m.group(1).upper(), m.group(2)
        value = f"IN{letter}{digits}"
        out.setdefault(value, RegNo(value, m.group(0), len(digits) == 9 and f"IN{letter}" in REG_NO_PREFIXES))
    return list(out.values())


def _all(pattern: re.Pattern[str], text: str, group: int = 0) -> list[str]:
    seen: dict[str, None] = {}
    for m in pattern.finditer(text):
        seen.setdefault(m.group(group).strip(" .,;:"), None)
    return [v for v in seen if v]


def find_upi_ids(text: str) -> list[str]:
    return _all(_UPI, text, 1)


def find_phones(text: str) -> list[str]:
    return _all(_PHONE, text, 0)


def find_urls(text: str) -> list[str]:
    return _all(_URL, text)


def find_amounts(text: str) -> list[str]:
    return _all(_AMOUNT, text)


def find_return_claims(text: str) -> list[str]:
    return _all(_RETURN, text)


def find_registration_claims(text: str) -> list[str]:
    return _all(_REGISTRATION_CLAIM, text)


def find_documentation(text: str) -> list[str]:
    return _all(_DOCUMENTATION, text)


def mentions_payment(text: str) -> bool:
    return bool(_PAYMENT_REQUEST.search(text))


def _trim_name(name: str) -> str:
    words = name.split()
    while words and words[0].lower().strip(".,") in _NAME_STOPWORDS:
        words = words[1:]
    return " ".join(words).strip(" .,;:")


def find_company_names(text: str) -> list[str]:
    names: dict[str, None] = {}
    for m in _COMPANY.finditer(text):
        name = _trim_name(m.group(1))
        if len(name.split()) >= 2:
            names.setdefault(name, None)
    for m in _QUOTED_NAME.finditer(text):
        name = _trim_name(m.group(1))
        if name:
            names.setdefault(name, None)
    return list(names)


def guess_offer_type(text: str) -> str | None:
    for offer_type, pattern in _OFFER_TYPES:
        if pattern.search(text):
            return offer_type
    return None

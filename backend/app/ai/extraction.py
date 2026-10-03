"""Claim & entity extraction (F05).

redact → store evidence → rules → extract(evidence, previous facts) → merge → save facts

Extraction never judges: it creates no Signals and never feeds `assess()` directly.
LLM output is data to validate: any entity whose value, or claim whose quote, is not
present in the (redacted) evidence text is dropped (grounding check). Deterministic
regex extractors always run, so facts exist even with the LLM disabled.
"""

import re

from pydantic import BaseModel, Field

from app.engine import patterns
from app.llm.client import LLMClient
from app.models import (
    Channel,
    Claim,
    ClaimCategory,
    Entity,
    EntityType,
    Evidence,
    Facts,
    Language,
    Question,
    Unknown,
    utcnow,
)

PROMPT = "extraction"
OFFER_TYPES = {"investment", "trading_tips", "advisory", "loan", "job", "mlm", "crypto", "other"}
REQUEST_CODES = {"PAYMENT", "APP_INSTALL", "OTP", "PIN", "PASSWORD", "BANK_DETAILS", "REMOTE_ACCESS", "RECRUIT_OTHERS"}
# Signal codes that tell us what the user was asked for (read-only use of rule output).
_SIGNAL_REQUESTS = {
    "OTP_REQUEST": "OTP",
    "UPI_PIN_REQUEST": "PIN",
    "PASSWORD_REQUEST": "PASSWORD",
    "CREDENTIAL_REQUEST": "BANK_DETAILS",
    "REMOTE_ACCESS_REQUEST": "REMOTE_ACCESS",
    "APK_INSTALL": "APP_INSTALL",
    "RECRUITMENT_DEPENDENCE": "RECRUIT_OTHERS",
    "WITHDRAWAL_FEE": "PAYMENT",
    "ENTRY_FEE": "PAYMENT",
}
_DONT_KNOW = re.compile(
    r"\b(?:don'?t|do\s+not)\s+know\b|\bnot\s+sure\b|\bno\s+idea\b|\bdunno\b|தெரியாது|தெரியவில்லை|theriya",
    re.IGNORECASE,
)
_ANSWER_CATEGORY: dict[Unknown, ClaimCategory] = {
    Unknown.ENTITY_NAME: "identity",
    Unknown.REGISTRATION_NUMBER: "registration",
    Unknown.PAYMENT_RECIPIENT: "payment",
    Unknown.AMOUNT: "payment",
    Unknown.RETURN_CLAIM: "returns",
    Unknown.CONTACT_CHANNEL: "other",
    Unknown.DOCUMENTATION: "documentation",
    Unknown.PRODUCT_SOLD: "product",
}
_ANSWER_LABEL: dict[Unknown, str] = {
    Unknown.ENTITY_NAME: "Name given",
    Unknown.REGISTRATION_NUMBER: "Registration details",
    Unknown.PAYMENT_RECIPIENT: "Payment goes to",
    Unknown.AMOUNT: "Amount",
    Unknown.RETURN_CLAIM: "Promised return",
    Unknown.CONTACT_CHANNEL: "First contact",
    Unknown.DOCUMENTATION: "Documents",
    Unknown.PRODUCT_SOLD: "Product sold",
}
MAX_ANSWER_QUOTE = 200
MAX_NAME_LEN = 80


# --- LLM output schema (validated; never trusted as-is) ---


class LLMEntity(BaseModel):
    type: EntityType
    value: str


class LLMClaim(BaseModel):
    text: str
    category: ClaimCategory
    quote: str | None = None


class ExtractionOutput(BaseModel):
    offer_type: str | None = None
    entities: list[LLMEntity] = Field(default_factory=list)
    claims: list[LLMClaim] = Field(default_factory=list)
    money: list[str] = Field(default_factory=list)
    requests: list[str] = Field(default_factory=list)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _grounded(value: str, evidence_text: str) -> bool:
    v = _norm(value)
    return bool(v) and v in _norm(evidence_text)


def _digits_grounded(value: str, evidence_text: str) -> bool:
    runs = re.findall(r"\d+", value.replace(",", ""))
    plain = evidence_text.replace(",", "")
    return bool(runs) and all(r in plain for r in runs)


def pattern_facts(evidence: Evidence, signal_codes: set[str] | None = None) -> Facts:
    """Regex-only facts for one evidence item (works without the LLM)."""
    text, eid = evidence.content, evidence.id
    entities = [Entity(type="registration_number", value=r.value, evidence_id=eid) for r in patterns.find_reg_numbers(text)]
    entities += [Entity(type="upi_id", value=v, evidence_id=eid) for v in patterns.find_upi_ids(text)]
    entities += [Entity(type="phone", value=v, evidence_id=eid) for v in patterns.find_phones(text)]
    entities += [Entity(type="website", value=v, evidence_id=eid) for v in patterns.find_urls(text)]
    entities += [Entity(type="company", value=v, evidence_id=eid) for v in patterns.find_company_names(text)]

    claims = [Claim(text=f"Promised return: {q}", category="returns", evidence_id=eid, quote=q)
              for q in patterns.find_return_claims(text)]
    claims += [Claim(text="Says they are SEBI registered", category="registration", evidence_id=eid, quote=q)
               for q in patterns.find_registration_claims(text)[:1]]
    claims += [Claim(text=f"Mentions documentation: {q}", category="documentation", evidence_id=eid, quote=q)
               for q in patterns.find_documentation(text)[:1]]

    requests = {code for sig, code in _SIGNAL_REQUESTS.items() if sig in (signal_codes or set())}
    if patterns.mentions_payment(text):
        requests.add("PAYMENT")
    return Facts(
        offer_type=patterns.guess_offer_type(text),
        entities=entities,
        claims=claims,
        money=patterns.find_amounts(text),
        requests=sorted(requests),
    )


def answer_facts(question: Question, evidence: Evidence) -> Facts:
    """Interpret an answer by the question's target unknown. Deterministic and grounded by construction."""
    answer = evidence.content.strip()
    if not question.target_unknown or not answer or _DONT_KNOW.search(answer):
        return Facts()
    target = question.target_unknown
    entities: list[Entity] = []
    if target == Unknown.ENTITY_NAME and len(answer) <= MAX_NAME_LEN and not patterns.find_reg_numbers(answer):
        entities.append(Entity(type="company", value=answer.strip(" .,;:\"'“”"), evidence_id=evidence.id))
    quote = answer if len(answer) <= MAX_ANSWER_QUOTE else None
    claims = (
        [Claim(text=f"{_ANSWER_LABEL[target]}: {answer}", category=_ANSWER_CATEGORY[target], evidence_id=evidence.id,
               quote=quote)]
        # A name answer is already an entity; registration answers are handled by the regex extractor.
        if quote and target != Unknown.REGISTRATION_NUMBER and not entities
        else []
    )
    return Facts(entities=entities, claims=claims)


def llm_facts(llm: LLMClient, evidence: Evidence, previous: Facts | None, language: Language) -> Facts:
    """LLM extraction with the deterministic grounding check. Empty Facts on any failure."""
    if not llm.enabled:
        return Facts()
    payload = {
        "language": language.value,
        "evidence": evidence.content,
        "known_facts": {
            "offer_type": previous.offer_type if previous else None,
            "entities": [{"type": e.type, "value": e.value} for e in (previous.entities if previous else [])],
            "claims": [c.text for c in (previous.claims if previous else [])],
        },
    }
    out = llm.generate_json(PROMPT, payload, ExtractionOutput)
    if out is None:
        return Facts()
    text, eid = evidence.content, evidence.id
    offer = (out.offer_type or "").strip().lower().replace(" ", "_")
    return Facts(
        offer_type=offer if offer in OFFER_TYPES else None,
        entities=[Entity(type=e.type, value=e.value.strip(), evidence_id=eid)
                  for e in out.entities if _grounded(e.value, text)],
        claims=[Claim(text=c.text.strip(), category=c.category, evidence_id=eid, quote=c.quote)
                for c in out.claims if c.quote and _grounded(c.quote, text) and c.text.strip()],
        money=[m.strip() for m in out.money if _digits_grounded(m, text)],
        requests=sorted({r.strip().upper() for r in out.requests} & REQUEST_CODES),
    )


def merge(previous: Facts | None, *new: Facts) -> Facts:
    """Union by (type, value) for entities and by normalized text for claims; earliest item wins."""
    merged = previous.model_copy(deep=True) if previous else Facts()
    seen_entities = {(e.type, _norm(e.value)) for e in merged.entities}
    seen_claims = {_norm(c.text) for c in merged.claims}
    for facts in new:
        if facts.offer_type and not merged.offer_type:
            merged.offer_type = facts.offer_type
        for e in facts.entities:
            key = (e.type, _norm(e.value))
            if key not in seen_entities:
                seen_entities.add(key)
                merged.entities.append(e)
        for c in facts.claims:
            if _norm(c.text) not in seen_claims:
                seen_claims.add(_norm(c.text))
                merged.claims.append(c)
        merged.money += [m for m in facts.money if _norm(m) not in {_norm(x) for x in merged.money}]
        merged.requests = sorted(set(merged.requests) | set(facts.requests))
    merged.updated_at = utcnow()
    return merged


def compute_unknowns(facts: Facts, channel: Channel) -> list[Unknown]:
    """Fixed vocabulary minus what is present. Computed in code, never taken from the LLM."""
    types = {e.type for e in facts.entities}
    categories = {c.category for c in facts.claims}
    present = {
        Unknown.ENTITY_NAME: bool(types & {"company", "person", "app", "website"}),
        Unknown.REGISTRATION_NUMBER: "registration_number" in types,
        Unknown.PAYMENT_RECIPIENT: "upi_id" in types or "payment" in categories,
        Unknown.AMOUNT: bool(facts.money),
        Unknown.RETURN_CLAIM: "returns" in categories,
        Unknown.CONTACT_CHANNEL: channel != Channel.UNKNOWN,
        Unknown.DOCUMENTATION: "documentation" in categories,
        Unknown.PRODUCT_SOLD: "product" in categories,
    }
    return [u for u in Unknown if not present[u]]


def facts_changed(before: Facts | None, after: Facts) -> bool:
    if before is None:
        return bool(after.entities or after.claims or after.money)
    return (
        len(after.entities) != len(before.entities)
        or len(after.claims) != len(before.claims)
        or len(after.money) != len(before.money)
    )

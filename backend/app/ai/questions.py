"""Adaptive questions (F06): the LLM proposes, the deterministic ranker selects (ADR-009).

Template questions for every unknown are always candidates, so the full flow works with
the LLM disabled. Stop conditions live in the service (they need the whole investigation).
"""

import re
from typing import Literal

from pydantic import BaseModel, Field

from app.engine.patterns import SEBI_OFFER_TYPES
from app.engine.question_ranker import Candidate, rank
from app.i18n import QUESTION_OBJECTIVE, QUESTION_TEMPLATES
from app.llm.client import LLMClient
from app.models import (
    Facts,
    Language,
    Question,
    Signal,
    SignalKind,
    Unknown,
    VerificationRecord,
)

PROMPT = "adaptive-question"
MLM_CODES = {"RECRUITMENT_DEPENDENCE", "ENTRY_FEE"}
NON_SEBI = {"mlm", "job", "loan"}
_TAMIL = re.compile(r"[\u0B80-\u0BFF]")


def in_language(text: str, language: Language) -> bool:
    """Cheap script check so an LLM question in the wrong language is never shown."""
    has_tamil = bool(_TAMIL.search(text))
    return has_tamil if language == Language.TA else not has_tamil


class LLMQuestion(BaseModel):
    question: str
    objective: str = ""
    expected_information: str = ""
    priority: Literal["high", "medium", "low"] = "medium"
    reasoning_source: str = ""
    target_unknown: Unknown | None = None


class QuestionsOutput(BaseModel):
    candidates: list[LLMQuestion] = Field(default_factory=list)


def relevant_unknowns(facts: Facts, signals: list[Signal]) -> set[Unknown]:
    """Unknowns worth asking about for this kind of offer."""
    codes = {s.code for s in signals if s.kind == SignalKind.WARNING}
    mlm_like = facts.offer_type == "mlm" or bool(codes & MLM_CODES)
    claims_registration = any(c.category == "registration" for c in facts.claims)
    relevant = set(facts.unknowns)
    if not mlm_like:
        relevant.discard(Unknown.PRODUCT_SOLD)
    if facts.offer_type in NON_SEBI and not claims_registration:
        relevant.discard(Unknown.REGISTRATION_NUMBER)
    return relevant


def information_gain(facts: Facts, signals: list[Signal], verifications: list[VerificationRecord]) -> dict[Unknown, float]:
    """Context that makes a particular unknown more valuable right now."""
    codes = {s.code for s in signals if s.kind == SignalKind.WARNING}
    boosts: dict[Unknown, float] = {}
    if any(c.category == "registration" for c in facts.claims):
        boosts[Unknown.REGISTRATION_NUMBER] = 2.0  # they claimed SEBI registration: get the number
    if any(v.code == "REG_NO_NAME" for v in verifications):
        boosts[Unknown.ENTITY_NAME] = 2.0  # number is registered: whose name were they using?
    if facts.offer_type == "mlm" or codes & MLM_CODES:
        boosts[Unknown.PRODUCT_SOLD] = 2.0
    if "PAYMENT" in facts.requests:
        boosts[Unknown.PAYMENT_RECIPIENT] = boosts.get(Unknown.PAYMENT_RECIPIENT, 0) + 0.25
    if facts.offer_type in SEBI_OFFER_TYPES:
        boosts[Unknown.ENTITY_NAME] = boosts.get(Unknown.ENTITY_NAME, 0) + 0.5
    return boosts


def template_candidates(unknowns: set[Unknown], language: Language) -> list[Candidate]:
    templates = QUESTION_TEMPLATES[language]
    return [
        Candidate(
            text=templates[u],
            objective=QUESTION_OBJECTIVE[u],
            target_unknown=u,
            priority="high" if u in (Unknown.ENTITY_NAME, Unknown.REGISTRATION_NUMBER, Unknown.PAYMENT_RECIPIENT)
            else "medium",
            reasoning_source=f"Missing fact: {u.value}",
            source="template",
        )
        for u in unknowns
    ]


def llm_candidates(llm: LLMClient, *, language: Language, facts: Facts, unknowns: set[Unknown], signals: list[Signal],
                   verifications: list[VerificationRecord], asked: list[Question]) -> list[Candidate]:
    if not llm.enabled or not unknowns:
        return []
    payload = {
        "language": language.value,
        "offer_type": facts.offer_type,
        "entities": [{"type": e.type, "value": e.value} for e in facts.entities],
        "claims": [c.text for c in facts.claims],
        "money": facts.money,
        "warning_signals": sorted({s.code for s in signals if s.kind == SignalKind.WARNING}),
        "verifications": [{"claim": v.claim, "status": v.status.value} for v in verifications],
        "unknowns": sorted(u.value for u in unknowns),
        "unknowns_vocabulary": [u.value for u in Unknown],
        "already_asked": [q.text for q in asked],
    }
    out = llm.generate_json(PROMPT, payload, QuestionsOutput)
    if out is None:
        return []
    return [
        Candidate(
            text=c.question.strip(),
            objective=c.objective.strip() or (QUESTION_OBJECTIVE[c.target_unknown] if c.target_unknown else ""),
            target_unknown=c.target_unknown,
            priority=c.priority,
            reasoning_source=c.reasoning_source.strip() or "LLM proposal",
            source="llm",
        )
        for c in out.candidates[:5]
        if in_language(c.question, language)
    ]


def choose_next(llm: LLMClient, *, language: Language, facts: Facts, signals: list[Signal],
                verifications: list[VerificationRecord], asked: list[Question]) -> Question | None:
    open_unknowns = relevant_unknowns(facts, signals) - {q.target_unknown for q in asked if q.target_unknown}
    if not open_unknowns:
        return None
    candidates = llm_candidates(llm, language=language, facts=facts, unknowns=open_unknowns, signals=signals,
                                verifications=verifications, asked=asked)
    candidates += template_candidates(open_unknowns, language)
    best = rank(candidates, open_unknowns=open_unknowns, asked=asked,
                boosts=information_gain(facts, signals, verifications))
    if best is None:
        return None
    return Question(
        text=best.text,
        objective=best.objective,
        target_unknown=best.target_unknown,
        priority=best.priority,  # type: ignore[arg-type]
        reasoning_source=best.reasoning_source,
        source=best.source,  # type: ignore[arg-type]
    )

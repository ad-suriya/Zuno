"""Investigation workflow.

Ingest (story, extra evidence, answers):
    redact → store evidence → deterministic rules → signals
          → extract facts (regex + grounded LLM) → merge → verify against SEBI snapshot
Questions:   stop conditions → LLM proposes / templates → deterministic ranker picks one
Assessment:  assess() (rules decide the level) → next_steps() → explain() (LLM or template)

LLMs interpret; deterministic rules decide (ADR-002, ADR-006). Every LLM step has a fallback.
"""

import logging

from app.ai.explanation import explain
from app.ai.extraction import answer_facts, compute_unknowns, llm_facts, merge, pattern_facts
from app.ai.questions import choose_next
from app.engine.assessment import assess
from app.engine.next_steps import next_steps
from app.engine.reassuring import reassuring_signals
from app.engine.red_flags import detect_red_flags
from app.engine.registry import Registry, get_registry
from app.engine.safety import detect_hard_signals, redact
from app.engine.verification import verify
from app.llm.client import LLMClient, disabled
from app.models import (
    Channel,
    Evidence,
    EvidenceKind,
    Facts,
    Investigation,
    InvestigationDetail,
    Language,
    Question,
    QuestionStatus,
    Severity,
    Signal,
    SignalKind,
    SignalSource,
    VerificationRecord,
)
from app.repository import ConflictError, InvestigationRepository, NotFoundError

# Log IDs and event names only, never user content (PRIVACY.md).
log = logging.getLogger("zuno.investigation")

MAX_QUESTIONS = 5
STABLE_AFTER = 2  # stop when this many answers in a row added nothing new


def _signals_for(evidence: Evidence, already: set[str]) -> list[Signal]:
    """Run all deterministic rules on one evidence item, skipping codes already recorded."""
    hits = detect_hard_signals(evidence.content) + detect_red_flags(evidence.content)
    signals = []
    for rule, matched in hits:
        if rule.code in already:
            continue
        already.add(rule.code)
        signals.append(
            Signal(
                kind=SignalKind.WARNING,
                code=rule.code,
                severity=rule.severity,
                source=SignalSource.RULE,
                evidence_id=evidence.id,
                matched_text=matched,
                explanation=rule.explanation,
            )
        )
    return signals


def _verification_key(r: VerificationRecord) -> tuple:
    return (r.code, r.status, tuple(sorted(r.params.items())))


class InvestigationService:
    def __init__(self, repo: InvestigationRepository, llm: LLMClient | None = None, registry: Registry | None = None):
        self.repo = repo
        self.llm = llm or disabled()
        self.registry = registry if registry is not None else get_registry()

    # --- ingest ---

    def _sync_verifications(self, investigation_id: str, facts: Facts) -> list[VerificationRecord]:
        """Recompute verification from the current facts; keep IDs of unchanged records stable."""
        existing = self.repo.list_verifications(investigation_id)
        by_key = {_verification_key(r): r for r in existing}
        records = [by_key.get(_verification_key(r), r) for r in verify(facts, self.registry)]
        if {r.id for r in records} != {r.id for r in existing}:
            self.repo.replace_verifications(investigation_id, records)
        return records

    def _ingest(self, investigation: Investigation, kind: EvidenceKind, raw: str,
                question: Question | None = None) -> Evidence:
        inv_id = investigation.id
        content, was_redacted = redact(raw)
        evidence = Evidence(kind=kind, content=content, redacted=was_redacted)
        self.repo.add_evidence(inv_id, evidence)

        known = {s.code for s in self.repo.list_signals(inv_id)}
        signals = _signals_for(evidence, known)
        self.repo.add_signals(inv_id, signals)

        if question is not None:
            question.status = QuestionStatus.ANSWERED
            question.answer_evidence_id = evidence.id
            self.repo.update_question(inv_id, question)

        previous = self.repo.get_facts(inv_id)
        parts = [pattern_facts(evidence, known)]
        if question is not None:
            parts.append(answer_facts(question, evidence))
        parts.append(llm_facts(self.llm, evidence, previous, investigation.language))
        facts = merge(previous, *parts)
        facts.unknowns = compute_unknowns(facts, investigation.channel)
        self.repo.save_facts(inv_id, facts)
        records = self._sync_verifications(inv_id, facts)

        log.info(
            "evidence_ingested",
            extra={
                "investigation_id": inv_id,
                "evidence_id": evidence.id,
                "kind": kind.value,
                "redacted": was_redacted,
                "signal_codes": [s.code for s in signals],
                "verification_codes": [r.code for r in records],
            },
        )
        return evidence

    def start(self, story: str, language: Language, channel: Channel) -> InvestigationDetail:
        investigation = Investigation(language=language, channel=channel)
        self.repo.create_investigation(investigation)
        log.info("investigation_created", extra={"investigation_id": investigation.id})
        self._ingest(investigation, EvidenceKind.STORY, story)
        return self.detail(investigation.id)

    def add_evidence(self, investigation_id: str, content: str,
                     kind: EvidenceKind = EvidenceKind.TEXT) -> InvestigationDetail:
        investigation = self.repo.get_investigation(investigation_id)  # raises NotFoundError
        self._ingest(investigation, kind, content)
        return self.detail(investigation_id)

    # --- adaptive questions (F06) ---

    def _question(self, investigation_id: str, question_id: str) -> Question:
        for q in self.repo.list_questions(investigation_id):
            if q.id == question_id:
                return q
        raise NotFoundError(question_id, "Question")

    def answer(self, investigation_id: str, question_id: str, content: str) -> InvestigationDetail:
        investigation = self.repo.get_investigation(investigation_id)
        question = self._question(investigation_id, question_id)
        if question.status != QuestionStatus.ASKED:
            raise ConflictError("This question was already answered or skipped.")
        self._ingest(investigation, EvidenceKind.ANSWER, content, question=question)
        log.info("question_answered", extra={"investigation_id": investigation_id, "question_id": question_id})
        return self.detail(investigation_id)

    def skip(self, investigation_id: str, question_id: str) -> InvestigationDetail:
        question = self._question(investigation_id, question_id)
        if question.status != QuestionStatus.ASKED:
            raise ConflictError("This question was already answered or skipped.")
        question.status = QuestionStatus.SKIPPED
        self.repo.update_question(investigation_id, question)
        log.info("question_skipped", extra={"investigation_id": investigation_id, "question_id": question_id})
        return self.detail(investigation_id)

    def finish(self, investigation_id: str) -> InvestigationDetail:
        for q in self.repo.list_questions(investigation_id):
            if q.status == QuestionStatus.ASKED:
                q.status = QuestionStatus.SKIPPED
                self.repo.update_question(investigation_id, q)
        self.repo.set_finished(investigation_id)
        log.info("investigation_finished", extra={"investigation_id": investigation_id})
        return self.detail(investigation_id)

    def _added_information(self, q: Question, signals: list[Signal], facts: Facts | None) -> bool:
        if q.status != QuestionStatus.ANSWERED or not q.answer_evidence_id:
            return False
        eid = q.answer_evidence_id
        if any(s.evidence_id == eid for s in signals):
            return True
        return bool(facts) and any(x.evidence_id == eid for x in [*facts.entities, *facts.claims])

    def stop_reason(self, investigation: Investigation, signals: list[Signal], questions: list[Question],
                    facts: Facts | None) -> str | None:
        """Why no further question should be asked, or None (docs/ADAPTIVE_ENGINE.md)."""
        if investigation.finished:
            return "user_finished"
        if any(s.kind == SignalKind.WARNING and s.severity == Severity.CRITICAL for s in signals):
            return "critical_signal"  # show HIGH + safety steps now; don't keep questioning
        if len(questions) >= MAX_QUESTIONS:
            return "max_questions"
        closed = [q for q in questions if q.status != QuestionStatus.ASKED]
        if len(closed) >= STABLE_AFTER and not any(
            self._added_information(q, signals, facts) for q in closed[-STABLE_AFTER:]
        ):
            return "assessment_stable"
        if facts is None:
            return "no_facts"
        return None

    def next_question(self, investigation_id: str) -> InvestigationDetail:
        investigation = self.repo.get_investigation(investigation_id)
        questions = self.repo.list_questions(investigation_id)
        if any(q.status == QuestionStatus.ASKED for q in questions):
            return self.detail(investigation_id)  # idempotent: the pending question is still open
        signals = self.repo.list_signals(investigation_id)
        facts = self.repo.get_facts(investigation_id)
        reason = self.stop_reason(investigation, signals, questions, facts)
        question = None
        if reason is None and facts is not None:
            question = choose_next(self.llm, language=investigation.language, facts=facts, signals=signals,
                                   verifications=self.repo.list_verifications(investigation_id), asked=questions)
            reason = None if question else "no_useful_question"
        if question is not None:
            self.repo.add_question(investigation_id, question)
        log.info(
            "next_question",
            extra={
                "investigation_id": investigation_id,
                "question_id": question.id if question else None,
                "target_unknown": question.target_unknown.value if question and question.target_unknown else None,
                "source": question.source if question else None,
                "stop_reason": reason,
            },
        )
        return self.detail(investigation_id)

    # --- assessment ---

    def _all_signals(self, investigation_id: str, verifications: list[VerificationRecord] | None = None,
                     questions: list[Question] | None = None, facts: Facts | None = None) -> list[Signal]:
        """Stored warning signals + reassuring signals derived from the current state (F09).

        Reassuring signals are recomputed rather than stored, so they always match the current
        verification records. Their IDs are stable per code.
        """
        stored = self.repo.list_signals(investigation_id)
        verifications = verifications if verifications is not None else self.repo.list_verifications(investigation_id)
        questions = questions if questions is not None else self.repo.list_questions(investigation_id)
        facts = facts if facts is not None else self.repo.get_facts(investigation_id)
        warning_codes = {s.code for s in stored if s.kind == SignalKind.WARNING}
        reassuring = reassuring_signals(facts, verifications, questions, warning_codes)
        for s in reassuring:
            s.id = f"reassuring-{s.code.lower()}"
        return stored + reassuring

    def run_assessment(self, investigation_id: str) -> InvestigationDetail:
        investigation = self.repo.get_investigation(investigation_id)
        verifications = self.repo.list_verifications(investigation_id)
        signals = self._all_signals(investigation_id, verifications=verifications)
        assessment = assess(signals, verifications)
        assessment.next_steps = next_steps(assessment, signals)
        assessment.explanation = explain(self.llm, assessment, signals, verifications, investigation.language)
        self.repo.save_assessment(investigation_id, assessment)
        log.info(
            "investigation_assessed",
            extra={
                "investigation_id": investigation_id,
                "level": assessment.level.value,
                "explanation_source": assessment.explanation.source,
            },
        )
        return self.detail(investigation_id)

    def detail(self, investigation_id: str) -> InvestigationDetail:
        investigation = self.repo.get_investigation(investigation_id)
        verifications = self.repo.list_verifications(investigation_id)
        questions = self.repo.list_questions(investigation_id)
        facts = self.repo.get_facts(investigation_id)
        pending = [q for q in questions if q.status == QuestionStatus.ASKED]
        return InvestigationDetail(
            investigation=investigation,
            evidence=self.repo.list_evidence(investigation_id),
            signals=self._all_signals(investigation_id, verifications, questions, facts),
            verifications=verifications,
            facts=facts,
            questions=questions,
            next_question=pending[-1] if pending else None,
        )

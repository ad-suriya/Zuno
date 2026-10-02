"""Investigation workflow: redact → store evidence → run deterministic rules → assess."""

import logging

from app.engine.assessment import assess
from app.engine.next_steps import next_steps
from app.engine.red_flags import detect_red_flags
from app.engine.safety import detect_hard_signals, redact
from app.models import (
    Channel,
    Evidence,
    EvidenceKind,
    Investigation,
    InvestigationDetail,
    Language,
    Signal,
    SignalKind,
    SignalSource,
)
from app.repository import InvestigationRepository

# Log IDs and event names only, never user content (PRIVACY.md).
log = logging.getLogger("zuno.investigation")


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


class InvestigationService:
    def __init__(self, repo: InvestigationRepository):
        self.repo = repo

    def _ingest(self, investigation_id: str, kind: EvidenceKind, raw: str) -> Evidence:
        content, was_redacted = redact(raw)
        evidence = Evidence(kind=kind, content=content, redacted=was_redacted)
        self.repo.add_evidence(investigation_id, evidence)
        known = {s.code for s in self.repo.list_signals(investigation_id)}
        signals = _signals_for(evidence, known)
        self.repo.add_signals(investigation_id, signals)
        log.info(
            "evidence_ingested",
            extra={
                "investigation_id": investigation_id,
                "evidence_id": evidence.id,
                "redacted": was_redacted,
                "signal_codes": [s.code for s in signals],
            },
        )
        return evidence

    def start(self, story: str, language: Language, channel: Channel) -> InvestigationDetail:
        investigation = Investigation(language=language, channel=channel)
        self.repo.create_investigation(investigation)
        log.info("investigation_created", extra={"investigation_id": investigation.id})
        self._ingest(investigation.id, EvidenceKind.STORY, story)
        return self.detail(investigation.id)

    def add_evidence(self, investigation_id: str, content: str) -> InvestigationDetail:
        self.repo.get_investigation(investigation_id)  # raises NotFoundError
        self._ingest(investigation_id, EvidenceKind.TEXT, content)
        return self.detail(investigation_id)

    def run_assessment(self, investigation_id: str) -> InvestigationDetail:
        signals = self.repo.list_signals(investigation_id)
        verifications = self.repo.list_verifications(investigation_id)
        assessment = assess(signals, verifications)
        assessment.next_steps = next_steps(assessment, signals, verifications)
        self.repo.save_assessment(investigation_id, assessment)
        log.info(
            "investigation_assessed",
            extra={"investigation_id": investigation_id, "level": assessment.level.value},
        )
        return self.detail(investigation_id)

    def detail(self, investigation_id: str) -> InvestigationDetail:
        return InvestigationDetail(
            investigation=self.repo.get_investigation(investigation_id),
            evidence=self.repo.list_evidence(investigation_id),
            signals=self.repo.list_signals(investigation_id),
            verifications=self.repo.list_verifications(investigation_id),
        )

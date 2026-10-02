"""Storage interface for investigations.

Firestore layout (ADR-005):

    investigations/{investigation_id}
        evidence/{evidence_id}
        signals/{signal_id}
        verifications/{verification_id}
"""

from typing import Protocol

from app.models import Assessment, Evidence, Investigation, Signal, VerificationRecord


class NotFoundError(Exception):
    pass


class InvestigationRepository(Protocol):
    def ping(self) -> None:
        """Raise if storage is unreachable. Used by the readiness check."""
        ...

    def create_investigation(self, investigation: Investigation) -> None: ...
    def get_investigation(self, investigation_id: str) -> Investigation: ...
    def save_assessment(self, investigation_id: str, assessment: Assessment) -> Investigation: ...

    def add_evidence(self, investigation_id: str, evidence: Evidence) -> None: ...
    def list_evidence(self, investigation_id: str) -> list[Evidence]: ...

    def add_signals(self, investigation_id: str, signals: list[Signal]) -> None: ...
    def list_signals(self, investigation_id: str) -> list[Signal]: ...

    def add_verification(self, investigation_id: str, record: VerificationRecord) -> None: ...
    def list_verifications(self, investigation_id: str) -> list[VerificationRecord]: ...

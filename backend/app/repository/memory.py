"""In-memory repository used by tests. Not a persistent store; the app uses Firestore."""

from app.models import Assessment, Evidence, Facts, Investigation, Question, Signal, VerificationRecord, utcnow
from app.repository.base import NotFoundError


class InMemoryRepository:
    def __init__(self) -> None:
        self._investigations: dict[str, Investigation] = {}
        self._evidence: dict[str, list[Evidence]] = {}
        self._signals: dict[str, list[Signal]] = {}
        self._verifications: dict[str, list[VerificationRecord]] = {}
        self._facts: dict[str, Facts] = {}
        self._questions: dict[str, list[Question]] = {}

    def _require(self, investigation_id: str) -> Investigation:
        if investigation_id not in self._investigations:
            raise NotFoundError(investigation_id)
        return self._investigations[investigation_id]

    def ping(self) -> None:
        return None

    def create_investigation(self, investigation: Investigation) -> None:
        self._investigations[investigation.id] = investigation.model_copy(deep=True)
        self._evidence[investigation.id] = []
        self._signals[investigation.id] = []
        self._verifications[investigation.id] = []
        self._questions[investigation.id] = []

    def get_investigation(self, investigation_id: str) -> Investigation:
        return self._require(investigation_id).model_copy(deep=True)

    def save_assessment(self, investigation_id: str, assessment: Assessment) -> Investigation:
        inv = self._require(investigation_id)
        self._investigations[investigation_id] = inv.model_copy(
            update={"assessment": assessment, "updated_at": utcnow()}
        )
        return self.get_investigation(investigation_id)

    def set_finished(self, investigation_id: str) -> None:
        inv = self._require(investigation_id)
        self._investigations[investigation_id] = inv.model_copy(update={"finished": True, "updated_at": utcnow()})

    def save_facts(self, investigation_id: str, facts: Facts) -> None:
        self._require(investigation_id)
        self._facts[investigation_id] = facts.model_copy(deep=True)

    def get_facts(self, investigation_id: str) -> Facts | None:
        self._require(investigation_id)
        facts = self._facts.get(investigation_id)
        return facts.model_copy(deep=True) if facts else None

    def add_evidence(self, investigation_id: str, evidence: Evidence) -> None:
        self._require(investigation_id)
        self._evidence[investigation_id].append(evidence)

    def list_evidence(self, investigation_id: str) -> list[Evidence]:
        self._require(investigation_id)
        return list(self._evidence[investigation_id])

    def add_signals(self, investigation_id: str, signals: list[Signal]) -> None:
        self._require(investigation_id)
        self._signals[investigation_id].extend(signals)

    def list_signals(self, investigation_id: str) -> list[Signal]:
        self._require(investigation_id)
        return list(self._signals[investigation_id])

    def add_verification(self, investigation_id: str, record: VerificationRecord) -> None:
        self._require(investigation_id)
        self._verifications[investigation_id].append(record)

    def list_verifications(self, investigation_id: str) -> list[VerificationRecord]:
        self._require(investigation_id)
        return list(self._verifications[investigation_id])

    def replace_verifications(self, investigation_id: str, records: list[VerificationRecord]) -> None:
        self._require(investigation_id)
        self._verifications[investigation_id] = list(records)

    def add_question(self, investigation_id: str, question: Question) -> None:
        self._require(investigation_id)
        self._questions[investigation_id].append(question.model_copy(deep=True))

    def update_question(self, investigation_id: str, question: Question) -> None:
        self._require(investigation_id)
        items = self._questions[investigation_id]
        for i, q in enumerate(items):
            if q.id == question.id:
                items[i] = question.model_copy(deep=True)
                return
        raise NotFoundError(question.id, "Question")

    def list_questions(self, investigation_id: str) -> list[Question]:
        self._require(investigation_id)
        return [q.model_copy(deep=True) for q in self._questions[investigation_id]]

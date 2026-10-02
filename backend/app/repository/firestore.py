"""Firestore-backed repository. Locally, set FIRESTORE_EMULATOR_HOST to use the emulator."""

from enum import Enum
from typing import Any, TypeVar

from google.cloud import firestore
from pydantic import BaseModel

from app.config import Settings
from app.models import Assessment, Evidence, Investigation, Signal, VerificationRecord, utcnow
from app.repository.base import NotFoundError

INVESTIGATIONS = "investigations"
EVIDENCE = "evidence"
SIGNALS = "signals"
VERIFICATIONS = "verifications"

M = TypeVar("M", bound=BaseModel)


def _encode(value: Any) -> Any:
    # Keep datetimes native (Firestore timestamps, usable for TTL); flatten enums to plain values.
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: _encode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_encode(v) for v in value]
    return value


def _to_doc(model: BaseModel, exclude_id: bool = True) -> dict:
    return _encode(model.model_dump(mode="python", exclude={"id"} if exclude_id else None))


class FirestoreRepository:
    def __init__(self, client: firestore.Client):
        self._db = client

    @classmethod
    def from_settings(cls, settings: Settings) -> "FirestoreRepository":
        client = firestore.Client(project=settings.google_cloud_project, database=settings.firestore_database)
        return cls(client)

    def _inv(self, investigation_id: str) -> firestore.DocumentReference:
        return self._db.collection(INVESTIGATIONS).document(investigation_id)

    def _require(self, investigation_id: str) -> firestore.DocumentReference:
        ref = self._inv(investigation_id)
        if not ref.get().exists:
            raise NotFoundError(investigation_id)
        return ref

    def _list(self, investigation_id: str, sub: str, model: type[M], order_by: str) -> list[M]:
        ref = self._require(investigation_id)
        docs = ref.collection(sub).order_by(order_by).stream()
        return [model.model_validate({**d.to_dict(), "id": d.id}) for d in docs]

    def ping(self) -> None:
        # Reading a missing document is cheap and proves connectivity + credentials.
        self._db.collection("_health").document("ping").get(timeout=3)

    def create_investigation(self, investigation: Investigation) -> None:
        self._inv(investigation.id).set(_to_doc(investigation))

    def get_investigation(self, investigation_id: str) -> Investigation:
        snap = self._inv(investigation_id).get()
        if not snap.exists:
            raise NotFoundError(investigation_id)
        return Investigation.model_validate({**snap.to_dict(), "id": snap.id})

    def save_assessment(self, investigation_id: str, assessment: Assessment) -> Investigation:
        ref = self._require(investigation_id)
        ref.update({"assessment": _to_doc(assessment, exclude_id=False), "updated_at": utcnow()})
        return self.get_investigation(investigation_id)

    def add_evidence(self, investigation_id: str, evidence: Evidence) -> None:
        ref = self._require(investigation_id)
        ref.collection(EVIDENCE).document(evidence.id).set(_to_doc(evidence))
        ref.update({"updated_at": utcnow()})

    def list_evidence(self, investigation_id: str) -> list[Evidence]:
        return self._list(investigation_id, EVIDENCE, Evidence, "created_at")

    def add_signals(self, investigation_id: str, signals: list[Signal]) -> None:
        if not signals:
            return
        ref = self._require(investigation_id)
        batch = self._db.batch()
        for s in signals:
            batch.set(ref.collection(SIGNALS).document(s.id), _to_doc(s))
        batch.commit()

    def list_signals(self, investigation_id: str) -> list[Signal]:
        return self._list(investigation_id, SIGNALS, Signal, "created_at")

    def add_verification(self, investigation_id: str, record: VerificationRecord) -> None:
        ref = self._require(investigation_id)
        ref.collection(VERIFICATIONS).document(record.id).set(_to_doc(record))

    def list_verifications(self, investigation_id: str) -> list[VerificationRecord]:
        return self._list(investigation_id, VERIFICATIONS, VerificationRecord, "checked_at")

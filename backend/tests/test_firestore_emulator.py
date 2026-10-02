"""Round-trip against the Firestore emulator. Skipped unless the emulator is reachable.

    gcloud emulators firestore start --host-port=localhost:8080
    FIRESTORE_EMULATOR_HOST=localhost:8080 pytest tests/test_firestore_emulator.py
"""

import os
import socket

import pytest

from app.models import (
    AssessmentLevel,
    Channel,
    Investigation,
    Language,
    SourceTier,
    VerificationRecord,
    VerificationStatus,
)
from app.service import InvestigationService


def _emulator_up() -> bool:
    host = os.environ.get("FIRESTORE_EMULATOR_HOST")
    if not host:
        return False
    name, _, port = host.partition(":")
    try:
        socket.create_connection((name, int(port or 8080)), timeout=0.5).close()
        return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(not _emulator_up(), reason="Firestore emulator not running")


@pytest.fixture
def fs_repo():
    from google.cloud import firestore

    from app.repository.firestore import FirestoreRepository

    return FirestoreRepository(firestore.Client(project="zuno-test"))


def test_round_trip(fs_repo):
    service = InvestigationService(fs_repo)
    detail = service.start("Guaranteed 20% monthly. Share the OTP 123456.", Language.TA, Channel.TELEGRAM)
    inv_id = detail.investigation.id
    assert "123456" not in detail.evidence[0].content
    assert {"OTP_REQUEST", "GUARANTEED_RETURNS"} <= {s.code for s in detail.signals}

    fs_repo.add_verification(
        inv_id,
        VerificationRecord(
            claim="c", source="s", source_tier=SourceTier.OFFICIAL_REGULATOR,
            status=VerificationStatus.NOT_VERIFIED, evidence="e", explanation="x",
        ),
    )
    detail = service.run_assessment(inv_id)
    assert detail.investigation.assessment.level == AssessmentLevel.HIGH_CONCERN
    assert detail.investigation.language == Language.TA
    assert detail.verifications[0].status == VerificationStatus.NOT_VERIFIED


def test_missing_investigation(fs_repo):
    from app.repository import NotFoundError

    with pytest.raises(NotFoundError):
        fs_repo.get_investigation(Investigation().id)

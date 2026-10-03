"""Demo scenarios (F03) as regression tests, against the real SEBI snapshot.

Protects the rules the demo depends on: MLM != fraud, NOT VERIFIED != FRAUD, and that
every outcome level stays reachable. One source of truth: tests/scenarios/scenarios.json
(the frontend copy in frontend/src/lib/scenarios.json must match it).
"""

import json
from pathlib import Path

import pytest

from app.engine.registry import get_registry
from app.llm.client import FakeClient
from app.models import AssessmentLevel, Channel, Language
from app.repository.memory import InMemoryRepository
from app.service import InvestigationService

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tests" / "scenarios" / "scenarios.json"
FRONTEND_COPY = ROOT / "frontend" / "src" / "lib" / "scenarios.json"
SCENARIOS = json.loads(SOURCE.read_text(encoding="utf-8"))


def test_frontend_copy_matches_source():
    assert json.loads(FRONTEND_COPY.read_text(encoding="utf-8")) == SCENARIOS, (
        "Copy tests/scenarios/scenarios.json to frontend/src/lib/scenarios.json")


def test_every_level_is_reachable():
    assert {s["expected_level"] for s in SCENARIOS} == {level.value for level in AssessmentLevel}


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario_level(scenario):
    registry = get_registry()
    assert registry.available, "backend/data/sebi_registry.csv is missing; run make refresh-sebi"
    service = InvestigationService(InMemoryRepository(), FakeClient(), registry)
    detail = service.start(scenario["story"], Language(scenario["language"]), Channel(scenario["channel"]))
    inv_id = detail.investigation.id
    for follow_up in scenario["follow_ups"]:
        service.add_evidence(inv_id, follow_up)
    result = service.run_assessment(inv_id)
    assessment = result.investigation.assessment
    assert assessment.level.value == scenario["expected_level"], [r.rule for r in assessment.reasons]
    assert 2 <= len(assessment.next_steps) <= 6
    assert assessment.explanation and assessment.explanation.language.value == scenario["language"]


def test_mlm_is_never_high_concern():
    mlm = next(s for s in SCENARIOS if s["id"] == "mlm")
    service = InvestigationService(InMemoryRepository(), FakeClient(), get_registry())
    inv = service.start(mlm["story"], Language.EN, Channel.REFERRAL).investigation.id
    for _ in range(3):  # more MLM-style evidence still stays below HIGH
        service.add_evidence(inv, "Bring 5 friends and pay the registration fee to unlock your income.")
    assert service.run_assessment(inv).investigation.assessment.level != AssessmentLevel.HIGH_CONCERN


def test_registered_advisor_shows_registration_verified():
    advisor = next(s for s in SCENARIOS if s["id"] == "registered_advisor")
    service = InvestigationService(InMemoryRepository(), FakeClient(), get_registry())
    inv = service.start(advisor["story"], Language.EN, Channel.CALL).investigation.id
    detail = service.run_assessment(inv)
    assert "REGISTRATION_VERIFIED" in {s.code for s in detail.signals}
    assert detail.verifications[0].code == "REG_NAME_MATCH"


def test_unknown_but_well_formed_number_is_not_fraud():
    service = InvestigationService(InMemoryRepository(), FakeClient(), get_registry())
    inv = service.start("Sunrise Growth Capital gave SEBI number INA999999999.", Language.EN, Channel.CALL)
    detail = service.run_assessment(inv.investigation.id)
    assert detail.verifications[0].status.value == "NOT_VERIFIED"
    assert detail.investigation.assessment.level == AssessmentLevel.NEEDS_VERIFICATION

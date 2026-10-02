"""F03 demo scenarios double as regression tests, so the demo cannot silently break."""

import json
from pathlib import Path

import pytest

from app.models import AssessmentLevel, Channel, Language
from app.repository.memory import InMemoryRepository
from app.service import InvestigationService

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_PATH = ROOT / "tests" / "scenarios" / "scenarios.json"
FRONTEND_COPY = ROOT / "frontend" / "src" / "lib" / "scenarios.json"
SCENARIOS = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario_level(scenario):
    service = InvestigationService(InMemoryRepository())
    detail = service.start(scenario["story"], Language(scenario["language"]), Channel(scenario["channel"]))
    for follow_up in scenario["follow_ups"]:
        service.add_evidence(detail.investigation.id, follow_up)
    detail = service.run_assessment(detail.investigation.id)
    assert detail.investigation.assessment.level == AssessmentLevel(scenario["expected_level"])
    assert 2 <= len(detail.investigation.assessment.next_steps) <= 6


def test_mlm_is_never_high_concern():
    mlm = next(s for s in SCENARIOS if s["id"] == "mlm")
    assert mlm["expected_level"] != "HIGH_CONCERN"


def test_frontend_copy_in_sync():
    """The frontend can't import files outside its project, so it keeps a copy. Keep them identical."""
    assert json.loads(FRONTEND_COPY.read_text(encoding="utf-8")) == SCENARIOS, (
        "Run: cp tests/scenarios/scenarios.json frontend/src/lib/scenarios.json"
    )

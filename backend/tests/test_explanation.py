import pytest

from app.ai.explanation import MAX_WORDS, explain, guard, template_explanation
from app.i18n import LEVEL_LABEL
from app.llm.client import FakeClient
from app.models import Assessment, AssessmentLevel, AssessmentReason, Language

HIGH = Assessment(level=AssessmentLevel.HIGH_CONCERN,
                  reasons=[AssessmentReason(rule="CRITICAL_SAFETY_SIGNAL", explanation="x")],
                  next_steps=["NEVER_SHARE_CREDENTIALS", "IF_SHARED_CALL_BANK", "REPORT_IF_LOST"])


def llm_says(text):
    return FakeClient({"explanation": {"text": text}})


@pytest.mark.parametrize("text,reason", [
    ("Low concern. This looks fine.", "different_level"),
    ("குறைந்த கவலை.", "different_level"),
    ("High concern. This is definitely a scam.", "banned_phrase"),
    ("High concern. You should sell your shares.", "banned_phrase"),
    ("High concern. Please share your OTP with us to continue.", "asks_for_credential"),
    ("High concern. " + "word " * MAX_WORDS, "too_long"),
    ("அதிக கவலை", "wrong_language"),
])
def test_guard_rejects(text, reason):
    assert guard(text, HIGH, Language.EN) == reason


def test_guard_allows_mentioning_otp_safely():
    assert guard("High concern. Never share your OTP with anyone.", HIGH, Language.EN) is None


def test_contradicting_llm_text_falls_back_to_template():
    out = explain(llm_says("Low concern: nothing to worry about."), HIGH, [], [], Language.EN)
    assert out.source == "template"
    assert out.text.startswith("Our assessment: High concern")


def test_valid_llm_text_is_used():
    out = explain(llm_says("High concern, based on what you shared: someone asked for an OTP. Never share it."),
                  HIGH, [], [], Language.EN)
    assert out.source == "llm"


def test_disabled_llm_gives_template_in_tamil():
    out = explain(FakeClient(), HIGH, [], [], Language.TA)
    assert out.source == "template" and out.language == Language.TA
    assert LEVEL_LABEL[Language.TA][AssessmentLevel.HIGH_CONCERN] in out.text


@pytest.mark.parametrize("language", list(Language))
@pytest.mark.parametrize("level", list(AssessmentLevel))
def test_template_never_names_another_level(language, level):
    a = Assessment(level=level, reasons=[], next_steps=["DO_NOT_PAY_YET", "REPORT_IF_LOST"])
    text = template_explanation(a, [], language)
    for other, label in LEVEL_LABEL[language].items():
        assert (label in text) == (other == level)
    assert len(text.split()) <= MAX_WORDS

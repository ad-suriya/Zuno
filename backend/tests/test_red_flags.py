import pytest

from app.engine.red_flags import detect_red_flags
from app.models import Severity


def flags(text: str) -> dict[str, Severity]:
    return {rule.code: rule.severity for rule, _ in detect_red_flags(text)}


@pytest.mark.parametrize(
    "text, code",
    [
        ("Guaranteed 20% monthly returns", "GUARANTEED_RETURNS"),
        ("returns are guaranteed", "GUARANTEED_RETURNS"),
        ("Guaranteed 20% monthly.", "GUARANTEED_RETURNS"),
        ("completely risk-free", "GUARANTEED_RETURNS"),
        ("we will double your money in 30 days", "DOUBLING_MONEY"),
        ("pay 18% tax to withdraw your profit", "WITHDRAWAL_FEE"),
        ("download our app from this link: trade.apk", "APK_INSTALL"),
        ("sure shot intraday call", "SURE_SHOT_TIP"),
        ("offer valid today only, limited slots", "URGENCY_PRESSURE"),
        ("you earn when you recruit people", "RECRUITMENT_DEPENDENCE"),
        ("joining fee of ₹5000", "ENTRY_FEE"),
        ("don't tell anyone about this", "SECRECY"),
        ("பணம் இரட்டிப்பு ஆகும்", "DOUBLING_MONEY"),
    ],
)
def test_red_flags_detected(text, code):
    assert code in flags(text)


@pytest.mark.parametrize(
    "text",
    ["20% monthly", "2% per day", "5 % a week", "10% returns per month"],
)
def test_unrealistic_rate_flagged(text):
    assert flags(text).get("UNREALISTIC_RETURN_RATE") == Severity.HIGH


@pytest.mark.parametrize("text", ["1% per month", "0.2% daily", "12% per year", "7% interest"])
def test_realistic_rate_not_flagged(text):
    assert "UNREALISTIC_RETURN_RATE" not in flags(text)


def test_mlm_patterns_are_medium_only():
    result = flags("joining fee ₹2000, and you earn when you refer friends who buy our products")
    assert result == {"ENTRY_FEE": Severity.MEDIUM, "RECRUITMENT_DEPENDENCE": Severity.MEDIUM}


def test_fixed_deposit_story_not_flagged():
    assert flags("I opened a fixed deposit at my bank branch at 7% per year") == {}

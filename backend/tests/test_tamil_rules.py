"""Tamil and Tanglish variants for every red-flag rule (F10), plus negation handling."""

import pytest

from app.engine.red_flags import detect_red_flags
from app.engine.safety import redact


def codes(text):
    return {r.code for r, _ in detect_red_flags(text)}


@pytest.mark.parametrize("text,code", [
    ("மாதம் 20% லாபம் உத்தரவாதம்", "GUARANTEED_RETURNS"),
    ("கண்டிப்பா லாபம் வரும்", "GUARANTEED_RETURNS"),
    ("kandippa profit varum, nashtam illa", "GUARANTEED_RETURNS"),
    ("guarantee labam", "GUARANTEED_RETURNS"),
    ("உங்கள் பணம் இரண்டு மடங்கு ஆகும்", "DOUBLING_MONEY"),
    ("panam double aagum", "DOUBLING_MONEY"),
    ("பணத்தை எடுக்க 10% வரி கட்ட வேண்டும்", "WITHDRAWAL_FEE"),
    ("withdraw panna 10% tax kattanum", "WITHDRAWAL_FEE"),
    ("ஷ்யூர் ஷாட் டிப்ஸ்", "SURE_SHOT_TIP"),
    ("இன்று மட்டும் சலுகை", "URGENCY_PRESSURE"),
    ("inniku mattum offer", "URGENCY_PRESSURE"),
    ("நண்பர்களை சேர்த்தால் வருமானம்", "RECRUITMENT_DEPENDENCE"),
    ("friends-a serkanum", "RECRUITMENT_DEPENDENCE"),
    ("சேர்க்கை கட்டணம் ₹5000", "ENTRY_FEE"),
    ("யாரிடமும் சொல்ல வேண்டாம்", "SECRECY"),
    ("yaar kittayum sollatheenga", "SECRECY"),
    ("மாதம் 20% லாபம்", "UNREALISTIC_RETURN_RATE"),
    ("maasam 15% varum", "UNREALISTIC_RETURN_RATE"),
    ("monthly 20% returns", "UNREALISTIC_RETURN_RATE"),
    ("தினமும் 2% லாபம்", "UNREALISTIC_RETURN_RATE"),
])
def test_tamil_and_tanglish_variants(text, code):
    assert code in codes(text)


@pytest.mark.parametrize("text", [
    "நான் ஒரு வங்கியில் சேமிப்பு கணக்கு வைத்திருக்கிறேன். என் மகன் கல்லூரியில் படிக்கிறான்.",
    "இன்று வானிலை நன்றாக இருக்கிறது.",
    "Naan oru mutual fund pathi kekka vandhen.",
])
def test_no_false_positives_on_neutral_text(text):
    assert codes(text) == set()


@pytest.mark.parametrize("text", [
    "There are no guaranteed returns.",
    "They said it is not risk free.",
    "There is no joining fee.",
    "Take your time, no hurry.",
    "You don't need to recruit anyone.",
])
def test_negated_phrases_do_not_fire(text):
    assert codes(text) == set()


def test_positive_still_fires_after_negated_mention():
    assert "GUARANTEED_RETURNS" in codes("No hidden charges and guaranteed returns of 10%.")


def test_redacts_spoken_and_spaced_codes():
    for text in ("my OTP is four eight two nine one three", "OTP 4 8 2 9 1 3", "ஓடிபி நான்கு எட்டு இரண்டு ஒன்பது"):
        out, changed = redact(text)
        assert changed and "[REDACTED]" in out
    assert redact("I have one two three friends")[1] is False

from app.engine.questions import (
    FORBIDDEN_TERMS,
    _CANDIDATES,
    known_slots,
    next_question,
)

SPEC_STORY = (
    "Someone on Telegram promised me guaranteed 20% monthly return "
    "on an investment opportunity and asked for 25,000 rupees."
)


def test_spec_example_asks_for_entity_first():
    q = next_question([SPEC_STORY])
    assert q is not None
    assert q.code == "ENTITY"
    assert q.text == "What is the exact company or organization name?"


def test_question_has_required_fields():
    q = next_question([SPEC_STORY])
    assert q.objective and q.expected_information and q.reasoning
    assert q.priority > 0


def test_known_entity_is_skipped():
    story = SPEC_STORY + " The company is called Alpha Wealth Pvt Ltd."
    assert "ENTITY" in known_slots([story])
    q = next_question([story])
    assert q is not None and q.code != "ENTITY"


def test_limited_time_offer_is_not_an_entity():
    assert "ENTITY" not in known_slots(["Limited time offer, join now"])


def test_registration_number_detected():
    assert "REGISTRATION" in known_slots(["Their SEBI number is INZ000123456"])
    assert "REGISTRATION" not in known_slots(["They say they are SEBI registered"])


def test_payment_recipient_detected():
    assert "PAYMENT_RECIPIENT" in known_slots(["Pay to rahul123@okaxis"])


def test_documentation_detected():
    assert "DOCUMENTATION" in known_slots(["He sent a brochure on WhatsApp"])


def test_never_repeats_and_exhausts():
    asked: list[str] = []
    while True:
        q = next_question([SPEC_STORY], asked_codes=asked)
        if q is None:
            break
        assert q.code not in asked
        asked.append(q.code)
    assert asked == ["ENTITY", "PAYMENT_RECIPIENT", "REGISTRATION", "DOCUMENTATION"]


def test_stop_conditions():
    assert next_question([SPEC_STORY], assessment_is_stable=True) is None
    assert next_question([SPEC_STORY], user_finished=True) is None
    assert next_question([SPEC_STORY], asked_codes=["A", "B"], max_questions=2) is None


def test_all_known_returns_none():
    story = (
        "Alpha Wealth Pvt Ltd, SEBI INZ000123456, pay to alpha@okaxis, "
        "see their brochure"
    )
    assert next_question([story]) is None


def test_no_question_asks_for_credentials():
    for c in _CANDIDATES:
        assert not FORBIDDEN_TERMS.search(c.text), c.code

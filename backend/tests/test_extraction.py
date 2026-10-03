from app.ai.extraction import answer_facts, compute_unknowns, llm_facts, merge, pattern_facts
from app.llm.client import FakeClient
from app.models import Channel, Evidence, EvidenceKind, Language, Question, Unknown

STORY = ("Rahul from Alpha Wealth Advisors said SEBI registered, reg no INA000000001, guaranteed 20% monthly "
         "returns. Pay ₹25,000 to alpha.wealth@ybl today.")


def ev(text: str) -> Evidence:
    return Evidence(kind=EvidenceKind.STORY, content=text)


def test_pattern_facts_without_llm():
    facts = pattern_facts(ev(STORY))
    values = {(e.type, e.value) for e in facts.entities}
    assert ("registration_number", "INA000000001") in values
    assert ("upi_id", "alpha.wealth@ybl") in values
    assert ("company", "Alpha Wealth Advisors") in values
    assert {c.category for c in facts.claims} >= {"returns", "registration"}
    assert facts.money == ["₹25,000"]
    assert "PAYMENT" in facts.requests


def test_llm_grounding_drops_invented_entities_and_claims():
    llm = FakeClient({"extraction": {
        "offer_type": "Trading Tips",
        "entities": [{"type": "company", "value": "alpha wealth  advisors"},  # case/space-insensitive: kept
                     {"type": "company", "value": "Invented Capital Ltd"}],  # not in text: dropped
        "claims": [{"text": "Guaranteed returns", "category": "returns", "quote": "guaranteed 20% monthly returns"},
                   {"text": "Made up", "category": "other", "quote": "this is not in the text"},
                   {"text": "No quote", "category": "other", "quote": None}],
        "money": ["₹25,000", "₹99,999"],
        "requests": ["payment", "TELEPATHY"],
    }})
    facts = llm_facts(llm, ev(STORY), None, Language.EN)
    assert [e.value for e in facts.entities] == ["alpha wealth  advisors"]
    assert [c.text for c in facts.claims] == ["Guaranteed returns"]
    assert facts.money == ["₹25,000"]
    assert facts.requests == ["PAYMENT"]
    assert facts.offer_type == "trading_tips"


def test_llm_failure_or_disabled_gives_empty_facts():
    assert llm_facts(FakeClient(), ev(STORY), None, Language.EN).entities == []
    assert llm_facts(FakeClient({"extraction": {"bad": "shape", "entities": "x"}}), ev(STORY), None, Language.EN).entities == []


def test_merge_dedupes_and_keeps_first():
    a = pattern_facts(ev(STORY))
    b = pattern_facts(ev("Again: pay ₹25,000 to alpha.wealth@ybl"))
    merged = merge(a, b)
    assert [e.value for e in merged.entities].count("alpha.wealth@ybl") == 1
    assert merged.money == ["₹25,000"]


def test_unknowns_computed_in_code():
    facts = pattern_facts(ev(STORY))
    unknowns = compute_unknowns(facts, Channel.TELEGRAM)
    assert Unknown.ENTITY_NAME not in unknowns
    assert Unknown.REGISTRATION_NUMBER not in unknowns
    assert Unknown.PAYMENT_RECIPIENT not in unknowns
    assert Unknown.DOCUMENTATION in unknowns
    assert Unknown.CONTACT_CHANNEL not in unknowns
    assert Unknown.CONTACT_CHANNEL in compute_unknowns(facts, Channel.UNKNOWN)


def test_answer_interpreted_by_target_unknown():
    q = Question(text="name?", objective="", target_unknown=Unknown.ENTITY_NAME, reasoning_source="", source="template")
    facts = answer_facts(q, Evidence(kind=EvidenceKind.ANSWER, content="Sunrise Growth Capital"))
    assert [(e.type, e.value) for e in facts.entities] == [("company", "Sunrise Growth Capital")]
    assert answer_facts(q, Evidence(kind=EvidenceKind.ANSWER, content="I don't know")).entities == []
    assert answer_facts(q, Evidence(kind=EvidenceKind.ANSWER, content="தெரியாது")).claims == []

    q2 = q.model_copy(update={"target_unknown": Unknown.DOCUMENTATION})
    facts2 = answer_facts(q2, Evidence(kind=EvidenceKind.ANSWER, content="No, nothing in writing"))
    assert facts2.claims[0].category == "documentation"


def test_tamil_story_extraction():
    facts = pattern_facts(ev("டெலிகிராம் குழுவில் மாதம் 20% லாபம் உத்தரவாதம் என்றார்கள். இன்று மட்டும் ₹25,000 கட்ட வேண்டும்."))
    assert facts.money == ["₹25,000"]
    assert any(c.category == "returns" for c in facts.claims)
    assert "PAYMENT" in facts.requests

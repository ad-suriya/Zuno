from app.ai.questions import choose_next, template_candidates
from app.engine.question_ranker import Candidate, rank, veto_reason
from app.i18n import QUESTION_TEMPLATES
from app.llm.client import FakeClient
from app.models import Facts, Language, Question, Unknown

TELEGRAM = "Telegram group admin: guaranteed 20% monthly returns, pay ₹25,000 today only."


def cand(text, target=Unknown.ENTITY_NAME, source="llm", priority="high"):
    return Candidate(text=text, objective="", target_unknown=target, priority=priority, reasoning_source="",
                     source=source)


def test_veto_credentials_advice_and_sensitive_data():
    assert veto_reason("Can you share the OTP you received?") == "credential_mention"
    assert veto_reason("Please share your UPI PIN so we can check") == "credential_mention"
    assert veto_reason("What is your net banking login?") == "credential_mention"
    assert veto_reason("உங்கள் ஓடிபி என்ன?") == "credential_mention"
    assert veto_reason("Should you buy this stock?") == "investment_advice"
    assert veto_reason("Maybe invest more to recover?") == "investment_advice"
    assert veto_reason("What is your Aadhaar number?") == "sensitive_data"
    assert veto_reason("Send a screenshot of your bank app") == "sensitive_data"
    assert veto_reason("What is the exact company name?") is None


def test_every_template_passes_the_veto():
    for lang, templates in QUESTION_TEMPLATES.items():
        assert set(templates) == set(Unknown), lang
        for text in templates.values():
            assert veto_reason(text) is None, text


def test_ranker_vetoes_and_is_deterministic():
    candidates = [cand("Share the OTP please", Unknown.REGISTRATION_NUMBER, priority="high"),
                  cand("What is the company name?"), *template_candidates(set(Unknown), Language.EN)]
    open_unknowns = set(Unknown)
    first = rank(candidates, open_unknowns=open_unknowns, asked=[])
    assert first == rank(list(reversed(candidates)), open_unknowns=open_unknowns, asked=[])
    assert "OTP" not in first.text
    assert first.target_unknown == Unknown.ENTITY_NAME


def test_ranker_dedupes_asked_and_resolved():
    asked = [Question(text="What is the company name?", objective="", target_unknown=Unknown.ENTITY_NAME,
                      reasoning_source="", source="llm")]
    best = rank([cand("What is the company name?"), cand("Who runs it?", Unknown.ENTITY_NAME),
                 cand("Registration number?", Unknown.REGISTRATION_NUMBER)],
                open_unknowns={Unknown.ENTITY_NAME, Unknown.REGISTRATION_NUMBER}, asked=asked)
    assert best.target_unknown == Unknown.REGISTRATION_NUMBER
    assert rank([cand("Amount?", Unknown.AMOUNT)], open_unknowns={Unknown.ENTITY_NAME}, asked=[]) is None


def test_registration_claim_boosts_registration_question(client):
    body = client.post("/api/v1/investigations", json={"story": "They said they are SEBI registered advisers.",
                                                       "channel": "whatsapp"}).json()
    inv = body["investigation"]["id"]
    q = client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"]
    assert q["target_unknown"] == "REGISTRATION_NUMBER"


def test_telegram_example_asks_entity_or_registration_first(client):
    inv = client.post("/api/v1/investigations", json={"story": TELEGRAM, "channel": "telegram"}).json()[
        "investigation"]["id"]
    q = client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"]
    assert q["target_unknown"] in ("ENTITY_NAME", "REGISTRATION_NUMBER")
    assert q["text"] == "What is the exact name of the company or organization behind this offer?"
    assert q["source"] == "template"


def test_full_flow_without_llm_never_repeats_and_stops_at_five(client):
    inv = client.post("/api/v1/investigations", json={"story": "Someone offered me an investment plan.",
                                                      "channel": "unknown"}).json()["investigation"]["id"]
    seen = []
    answers = iter(["Sunrise Growth Capital", "INA000000099", "To a person's UPI ID sunrise@ybl", "₹50,000",
                    "3% per month", "Yes an agreement"])
    for _ in range(10):
        q = client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"]
        if q is None:
            break
        assert q["text"] not in seen
        seen.append(q["text"])
        resp = client.post(f"/api/v1/investigations/{inv}/questions/{q['id']}/answer", json={"content": next(answers)})
        assert resp.status_code == 200, resp.text
    assert len(seen) == 5
    detail = client.get(f"/api/v1/investigations/{inv}").json()
    assert all(q["status"] == "answered" for q in detail["questions"])
    assert {e["kind"] for e in detail["evidence"]} == {"story", "answer"}
    assert detail["next_question"] is None


def test_critical_signal_stops_questions(client):
    inv = client.post("/api/v1/investigations", json={"story": "They asked me for the OTP to unlock profits."}).json()[
        "investigation"]["id"]
    assert client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"] is None


def test_skip_finish_and_conflicts(client):
    inv = client.post("/api/v1/investigations", json={"story": "An investment offer on WhatsApp."}).json()[
        "investigation"]["id"]
    q = client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"]
    # idempotent while a question is pending
    assert client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"]["id"] == q["id"]
    assert client.post(f"/api/v1/investigations/{inv}/questions/{q['id']}/skip").json()["questions"][0]["status"] == "skipped"
    again = client.post(f"/api/v1/investigations/{inv}/questions/{q['id']}/answer", json={"content": "x"})
    assert again.status_code == 409 and again.json()["error"]["code"] == "CONFLICT"
    assert client.post(f"/api/v1/investigations/{inv}/questions/nope/skip").json()["error"]["message"] == (
        "Question not found.")
    q2 = client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"]
    assert q2["target_unknown"] != q["target_unknown"]
    body = client.post(f"/api/v1/investigations/{inv}/finish").json()
    assert body["investigation"]["finished"] is True and body["next_question"] is None
    assert client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"] is None


def test_two_unhelpful_answers_stop_questions(client):
    inv = client.post("/api/v1/investigations", json={"story": "An investment offer on WhatsApp."}).json()[
        "investigation"]["id"]
    for _ in range(2):
        q = client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"]
        client.post(f"/api/v1/investigations/{inv}/questions/{q['id']}/answer", json={"content": "I don't know"})
    assert client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"] is None


def test_llm_candidates_are_used_but_vetoed_when_unsafe():
    facts = Facts(unknowns=[Unknown.ENTITY_NAME, Unknown.REGISTRATION_NUMBER], offer_type="investment")
    unsafe = FakeClient({"adaptive-question": {"candidates": [
        {"question": "Please tell me the OTP you got", "priority": "high", "target_unknown": "REGISTRATION_NUMBER"}]}})
    q = choose_next(unsafe, language=Language.EN, facts=facts, signals=[], verifications=[], asked=[])
    assert q.source == "template" and "OTP" not in q.text

    good = FakeClient({"adaptive-question": {"candidates": [
        {"question": "Which company did the caller say they work for?", "priority": "high",
         "target_unknown": "ENTITY_NAME", "reasoning_source": "entity missing"}]}})
    q = choose_next(good, language=Language.EN, facts=facts, signals=[], verifications=[], asked=[])
    assert q.source == "llm" and q.target_unknown == Unknown.ENTITY_NAME

    wrong_lang = FakeClient({"adaptive-question": {"candidates": [
        {"question": "Which company?", "priority": "high", "target_unknown": "ENTITY_NAME"}]}})
    q = choose_next(wrong_lang, language=Language.TA, facts=facts, signals=[], verifications=[], asked=[])
    assert q.source == "template" and q.text == QUESTION_TEMPLATES[Language.TA][Unknown.ENTITY_NAME]

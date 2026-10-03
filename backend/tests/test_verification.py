from datetime import date

from app.engine.registry import load_registry, name_similarity, name_tokens
from app.engine.verification import verify
from app.models import Claim, Entity, Facts, VerificationStatus


def facts(*entities, claims=(), offer_type="advisory"):
    return Facts(offer_type=offer_type, entities=[Entity(type=t, value=v, evidence_id="e") for t, v in entities],
                 claims=[Claim(text=t, category=c, evidence_id="e") for t, c in claims])


def one(registry, f):
    [record] = verify(f, registry, today=date(2026, 10, 3))
    return record


def test_name_normalisation():
    assert name_tokens("Test Wealth Advisors Pvt. Ltd.") == name_tokens("TEST WEALTH ADVISORS PRIVATE LIMITED")
    assert name_similarity(name_tokens("Marina"), name_tokens("Marina Broking Limited")) >= 0.8
    assert name_similarity(name_tokens("Capital"), name_tokens("Sunrise Capital")) < 0.8  # generic word alone


def test_reg_found_name_matches_verified(registry):
    r = one(registry, facts(("registration_number", "INA000000001"), ("company", "Test Wealth Advisors Pvt Ltd")))
    assert (r.status, r.source_tier, r.code) == (VerificationStatus.VERIFIED, 1, "REG_NAME_MATCH")
    assert r.material and "does not confirm the person contacting you" in r.explanation
    assert r.params["registered_name"] == "Test Wealth Advisors Private Limited"


def test_reg_found_name_clearly_different_contradicted(registry):
    r = one(registry, facts(("registration_number", "INA000000001"), ("company", "Sunrise Growth Capital")))
    assert (r.status, r.code) == (VerificationStatus.CONTRADICTED, "REG_NAME_MISMATCH")


def test_reg_expired_contradicted(registry):
    r = one(registry, facts(("registration_number", "INA000000002"), ("company", "Expired Advisory Services")))
    assert (r.status, r.code) == (VerificationStatus.CONTRADICTED, "REG_EXPIRED")


def test_well_formed_not_in_snapshot_is_only_not_verified(registry):
    r = one(registry, facts(("registration_number", "INA000000999"), ("company", "Anything Ltd")))
    assert (r.status, r.source_tier, r.code) == (VerificationStatus.NOT_VERIFIED, 1, "REG_NOT_FOUND")
    assert "doesn't mean it's fake" in r.explanation


def test_malformed_number(registry):
    r = one(registry, facts(("registration_number", "INA12345")))
    assert (r.status, r.source_tier, r.code) == (VerificationStatus.NOT_VERIFIED, 4, "REG_MALFORMED")


def test_category_not_in_snapshot(registry):
    r = one(registry, facts(("registration_number", "INP000000005")))
    assert (r.status, r.code) == (VerificationStatus.NOT_VERIFIED, "REG_CATEGORY_NOT_COVERED")


def test_registered_number_without_a_name_asks_for_it(registry):
    r = one(registry, facts(("registration_number", "INH000000003"), ("person", "Ravi")))
    assert (r.status, r.code) == (VerificationStatus.UNKNOWN, "REG_NO_NAME")


def test_claim_without_number_is_unknown(registry):
    r = one(registry, facts(claims=[("SEBI registered", "registration")]))
    assert (r.status, r.code) == (VerificationStatus.UNKNOWN, "REGISTRATION_CLAIM_NO_NUMBER")


def test_name_only_match_and_trade_name(registry):
    assert one(registry, facts(("company", "Kaveri Research"))).status == VerificationStatus.VERIFIED
    assert one(registry, facts(("company", "Marina Trade"))).code == "NAME_FOUND"
    assert one(registry, facts(("company", "Unknown Galaxy Capital"))).code == "NAME_NOT_FOUND"


def test_mlm_not_applicable(registry):
    r = one(registry, facts(("company", "Herbal Life Network"), offer_type="mlm"))
    assert (r.status, r.material) == (VerificationStatus.NOT_APPLICABLE, False)


def test_missing_snapshot_never_contradicts(tmp_path):
    empty = load_registry(tmp_path / "missing.csv")
    [r] = verify(facts(("registration_number", "INA000000001"), ("company", "X")), empty)
    assert r.status == VerificationStatus.NOT_VERIFIED


def test_verified_plus_otp_is_still_high(client):
    body = client.post("/api/v1/investigations", json={
        "story": "Test Wealth Advisors Pvt Ltd, SEBI reg INA000000001, asked me to share the OTP."}).json()
    assert body["verifications"][0]["status"] == "VERIFIED"
    inv = body["investigation"]["id"]
    assert client.post(f"/api/v1/investigations/{inv}/assessment").json()["investigation"]["assessment"]["level"] == (
        "HIGH_CONCERN")


def test_registered_advisor_reaches_low_concern(client):
    inv = client.post("/api/v1/investigations", json={
        "story": "An adviser from Test Wealth Advisors Private Limited gave SEBI registration number INA000000001. "
                 "There are no guaranteed returns and the fee is paid by invoice to the company."}).json()[
        "investigation"]["id"]
    body = client.post(f"/api/v1/investigations/{inv}/assessment").json()
    assert body["investigation"]["assessment"]["level"] == "LOW_CONCERN"
    assert "REGISTRATION_VERIFIED" in {s["code"] for s in body["signals"] if s["kind"] == "REASSURING"}


def test_answering_the_name_resolves_reg_no_name(client):
    body = client.post("/api/v1/investigations", json={"story": "He gave reg no INH000000003 on a call."}).json()
    inv = body["investigation"]["id"]
    assert body["verifications"][0]["code"] == "REG_NO_NAME"
    q = client.post(f"/api/v1/investigations/{inv}/questions/next").json()["next_question"]
    assert q["target_unknown"] == "ENTITY_NAME"
    body = client.post(f"/api/v1/investigations/{inv}/questions/{q['id']}/answer",
                       json={"content": "Some Other Capital Pvt Ltd"}).json()
    assert [v["code"] for v in body["verifications"]] == ["REG_NAME_MISMATCH"]
    assessed = client.post(f"/api/v1/investigations/{inv}/assessment").json()
    assert assessed["investigation"]["assessment"]["level"] == "HIGH_CONCERN"

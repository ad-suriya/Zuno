from app.models import SourceTier, VerificationRecord, VerificationStatus

SCAM_STORY = (
    "A Telegram group admin said guaranteed 20% monthly returns if I invest ₹25000. "
    "He asked me to share the OTP 482913 to activate my account."
)


def create(client, story=SCAM_STORY, **extra):
    resp = client.post("/api/v1/investigations", json={"story": story, **extra})
    assert resp.status_code == 201, resp.text
    return resp.json()




def test_create_redacts_and_detects_signals(client):
    body = create(client, language="ta", channel="telegram")
    assert body["investigation"]["language"] == "ta"
    assert body["investigation"]["channel"] == "telegram"
    [story] = body["evidence"]
    assert story["kind"] == "story"
    assert story["redacted"] is True
    assert "482913" not in story["content"]
    codes = {s["code"] for s in body["signals"]}
    assert {"OTP_REQUEST", "GUARANTEED_RETURNS", "UNREALISTIC_RETURN_RATE"} <= codes
    assert all(s["evidence_id"] == story["id"] for s in body["signals"])
    assert body["investigation"]["assessment"] is None


def test_redacted_secret_never_stored(client, repo):
    body = create(client)
    stored = repo.list_evidence(body["investigation"]["id"])
    assert all("482913" not in e.content for e in stored)


def test_assessment_flow(client):
    inv_id = create(client)["investigation"]["id"]
    body = client.post(f"/api/v1/investigations/{inv_id}/assessment").json()
    assert body["investigation"]["assessment"]["level"] == "HIGH_CONCERN"
    assert client.get(f"/api/v1/investigations/{inv_id}").json()["investigation"]["assessment"]["level"] == (
        "HIGH_CONCERN"
    )


def test_evidence_adds_new_signals_without_duplicates(client):
    inv_id = create(client, story="A friend told me about an investment plan.")["investigation"]["id"]
    assert client.post(f"/api/v1/investigations/{inv_id}/assessment").json()["investigation"]["assessment"][
        "level"
    ] == "NEEDS_VERIFICATION"

    for _ in range(2):
        body = client.post(
            f"/api/v1/investigations/{inv_id}/evidence", json={"content": "Only today! Install AnyDesk."}
        ).json()
    codes = [s["code"] for s in body["signals"]]
    assert sorted(codes) == ["REMOTE_ACCESS_REQUEST", "URGENCY_PRESSURE"]
    assert len(body["evidence"]) == 3


def test_low_concern_requires_trusted_verification(client, repo):
    inv_id = create(client, story="My bank's relationship manager suggested a SEBI-registered mutual fund.")[
        "investigation"
    ]["id"]
    repo.add_verification(
        inv_id,
        VerificationRecord(
            claim="Mutual fund is SEBI registered", source="SEBI register",
            source_tier=SourceTier.OFFICIAL_REGULATOR, status=VerificationStatus.VERIFIED,
            evidence="Registration found", explanation="Listed on sebi.gov.in",
        ),
    )
    body = client.post(f"/api/v1/investigations/{inv_id}/assessment").json()
    assert body["investigation"]["assessment"]["level"] == "LOW_CONCERN"
    assert len(body["verifications"]) == 1


def test_unknown_investigation_404(client):
    for resp in (
        client.get("/api/v1/investigations/nope"),
        client.post("/api/v1/investigations/nope/evidence", json={"content": "x"}),
        client.post("/api/v1/investigations/nope/assessment"),
    ):
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"


def test_validation(client):
    assert client.post("/api/v1/investigations", json={"story": ""}).status_code == 422
    resp = client.post("/api/v1/investigations", json={"story": "my OTP 123456", "language": "fr"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "language" in resp.json()["error"]["message"]
    assert "123456" not in resp.text  # submitted values are not echoed back


def test_clients_cannot_write_verifications(client):
    inv_id = create(client)["investigation"]["id"]
    resp = client.post(f"/api/v1/investigations/{inv_id}/verifications", json={"status": "VERIFIED"})
    assert resp.status_code in (404, 405)

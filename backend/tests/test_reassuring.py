from app.engine.assessment import assess
from app.engine.reassuring import reassuring_signals
from app.models import (
    Claim,
    Entity,
    Facts,
    Question,
    QuestionStatus,
    Severity,
    Signal,
    SignalKind,
    SignalSource,
    SourceTier,
    Unknown,
    VerificationRecord,
    VerificationStatus,
)

VERIFIED = VerificationRecord(code="REG_NAME_MATCH", params={"registered_name": "Kaveri Research Private Limited"},
                              claim="c", source="SEBI", source_tier=SourceTier.OFFICIAL_REGULATOR,
                              status=VerificationStatus.VERIFIED, evidence="e", explanation="x")


def test_registration_verified_signal():
    [s] = reassuring_signals(None, [VERIFIED], [], set())
    assert (s.code, s.kind, s.source, s.verification_id) == (
        "REGISTRATION_VERIFIED", SignalKind.REASSURING, SignalSource.VERIFIED_SOURCE, VERIFIED.id)


def test_realistic_return_only_without_return_warnings():
    facts = Facts(claims=[Claim(text="r", category="returns", evidence_id="e", quote="1% per month")])
    assert [s.code for s in reassuring_signals(facts, [], [], set())] == ["REALISTIC_RETURN_CLAIM"]
    assert reassuring_signals(facts, [], [], {"GUARANTEED_RETURNS"}) == []
    guaranteed = Facts(claims=[Claim(text="r", category="returns", evidence_id="e", quote="assured 1% per month")])
    assert reassuring_signals(guaranteed, [], [], set()) == []


def test_no_upfront_payment_needs_an_answered_payment_question():
    facts = Facts()
    q = Question(text="q", objective="", target_unknown=Unknown.AMOUNT, reasoning_source="", source="template",
                 status=QuestionStatus.ANSWERED)
    assert [s.code for s in reassuring_signals(facts, [], [q], set())] == ["NO_UPFRONT_PAYMENT"]
    assert reassuring_signals(facts, [], [], set()) == []
    assert reassuring_signals(Facts(money=["₹5,000"]), [], [q], set()) == []


def test_official_channel_payment():
    facts = Facts(entities=[Entity(type="upi_id", value="kaveri.research@icici", evidence_id="e")])
    codes = [s.code for s in reassuring_signals(facts, [VERIFIED], [], set())]
    assert codes == ["REGISTRATION_VERIFIED", "OFFICIAL_CHANNEL_PAYMENT"]


def test_reassuring_signals_never_change_the_level():
    warning = Signal(kind=SignalKind.WARNING, code="GUARANTEED_RETURNS", severity=Severity.HIGH,
                     source=SignalSource.RULE, explanation="x")
    many_reassuring = [Signal(kind=SignalKind.REASSURING, code=f"R{i}", severity=Severity.LOW,
                              source=SignalSource.RULE, explanation="x") for i in range(5)]
    for signals, verifications in ([[warning], []], [[], []], [[warning], [VERIFIED]], [[], [VERIFIED]]):
        assert assess(signals, verifications).level == assess(signals + many_reassuring, verifications).level

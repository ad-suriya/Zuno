from app.engine.assessment import assess
from app.models import (
    AssessmentLevel,
    Severity,
    Signal,
    SignalKind,
    SignalSource,
    SourceTier,
    VerificationRecord,
    VerificationStatus,
)


def warning(code: str, severity: Severity) -> Signal:
    return Signal(
        kind=SignalKind.WARNING, code=code, severity=severity, source=SignalSource.RULE, explanation="x"
    )


def record(status: VerificationStatus, tier: SourceTier = SourceTier.OFFICIAL_REGULATOR, material=True):
    return VerificationRecord(
        claim="SEBI registered", source="SEBI register", source_tier=tier, status=status,
        evidence="lookup", explanation="x", material=material,
    )


def rules(assessment) -> set[str]:
    return {r.rule for r in assessment.reasons}


def test_critical_signal_is_high_concern_even_with_verified_entity():
    a = assess([warning("OTP_REQUEST", Severity.CRITICAL)], [record(VerificationStatus.VERIFIED)])
    assert a.level == AssessmentLevel.HIGH_CONCERN
    assert {"CRITICAL_SAFETY_SIGNAL", "VERIFIED_CLAIMS"} <= rules(a)


def test_contradicted_material_claim_is_high_concern():
    a = assess([], [record(VerificationStatus.CONTRADICTED)])
    assert a.level == AssessmentLevel.HIGH_CONCERN
    assert "CONTRADICTED_CLAIM" in rules(a)


def test_two_distinct_high_warnings_is_high_concern():
    a = assess(
        [warning("GUARANTEED_RETURNS", Severity.HIGH), warning("UNREALISTIC_RETURN_RATE", Severity.HIGH)], []
    )
    assert a.level == AssessmentLevel.HIGH_CONCERN


def test_one_high_warning_needs_verification():
    a = assess([warning("GUARANTEED_RETURNS", Severity.HIGH)], [])
    assert a.level == AssessmentLevel.NEEDS_VERIFICATION


def test_same_high_code_twice_is_not_multiple():
    s = warning("GUARANTEED_RETURNS", Severity.HIGH)
    assert assess([s, s.model_copy(update={"id": "other"})], []).level == AssessmentLevel.NEEDS_VERIFICATION


def test_not_verified_is_never_high_concern():
    a = assess([], [record(VerificationStatus.NOT_VERIFIED), record(VerificationStatus.UNKNOWN)])
    assert a.level == AssessmentLevel.NEEDS_VERIFICATION
    assert "UNVERIFIED_CLAIMS" in rules(a)


def test_mlm_signals_alone_need_verification_not_high():
    a = assess(
        [warning("RECRUITMENT_DEPENDENCE", Severity.MEDIUM), warning("ENTRY_FEE", Severity.MEDIUM)], []
    )
    assert a.level == AssessmentLevel.NEEDS_VERIFICATION


def test_no_evidence_is_not_low_concern():
    a = assess([], [])
    assert a.level == AssessmentLevel.NEEDS_VERIFICATION
    assert "NO_TRUSTED_VERIFICATION" in rules(a)


def test_user_provided_verification_does_not_give_low_concern():
    a = assess([], [record(VerificationStatus.VERIFIED, tier=SourceTier.USER_PROVIDED)])
    assert a.level == AssessmentLevel.NEEDS_VERIFICATION


def test_trusted_verification_without_warnings_is_low_concern():
    a = assess([], [record(VerificationStatus.VERIFIED)])
    assert a.level == AssessmentLevel.LOW_CONCERN
    assert rules(a) == {"NO_MAJOR_WARNINGS", "VERIFIED_CLAIMS"}


def test_non_material_contradiction_ignored():
    a = assess([], [record(VerificationStatus.VERIFIED), record(VerificationStatus.CONTRADICTED, material=False)])
    assert a.level == AssessmentLevel.LOW_CONCERN


def test_every_reason_is_traceable():
    a = assess(
        [warning("OTP_REQUEST", Severity.CRITICAL), warning("URGENCY_PRESSURE", Severity.MEDIUM)],
        [record(VerificationStatus.CONTRADICTED)],
    )
    for reason in a.reasons:
        assert reason.signal_ids or reason.verification_ids

from app.engine.assessment import assess
from app.engine.next_steps import MAX_STEPS, next_steps
from app.models import (
    Severity,
    Signal,
    SignalKind,
    SignalSource,
    SourceTier,
    VerificationRecord,
    VerificationStatus,
)


def _signal(code: str, severity: Severity) -> Signal:
    return Signal(kind=SignalKind.WARNING, code=code, severity=severity, source=SignalSource.RULE, explanation="x")


def _steps(signals, verifications=()):
    verifications = list(verifications)
    return next_steps(assess(signals, verifications), signals, verifications)


def test_otp_puts_credential_steps_first():
    steps = _steps([_signal("URGENCY_PRESSURE", Severity.MEDIUM), _signal("OTP_REQUEST", Severity.CRITICAL)])
    assert steps[:2] == ["NEVER_SHARE_CREDENTIALS", "IF_SHARED_CALL_BANK"]
    assert steps[-1] == "REPORT_IF_LOST"


def test_no_signals_still_checks_and_reports():
    steps = _steps([])
    assert "CHECK_SEBI_REGISTER" in steps
    assert "REPORT_IF_LOST" in steps


def test_remote_access_and_apk():
    steps = _steps([_signal("REMOTE_ACCESS_REQUEST", Severity.CRITICAL), _signal("APK_INSTALL", Severity.MEDIUM)])
    assert "UNINSTALL_REMOTE_APP" in steps
    assert "DO_NOT_INSTALL_APK" in steps
    assert "IF_SHARED_CALL_BANK" not in steps  # remote access is not a credential


def test_mlm_asks_what_is_sold():
    steps = _steps([_signal("ENTRY_FEE", Severity.MEDIUM), _signal("RECRUITMENT_DEPENDENCE", Severity.MEDIUM)])
    assert steps.count("ASK_WHAT_IS_SOLD") == 1


def test_verified_low_concern_has_two_steps():
    record = VerificationRecord(
        claim="reg no",
        source="SEBI",
        source_tier=SourceTier.OFFICIAL_REGULATOR,
        status=VerificationStatus.VERIFIED,
        evidence="match",
        explanation="x",
    )
    steps = _steps([], [record])
    assert steps == ["CONTACT_VIA_OFFICIAL_DETAILS", "REPORT_IF_LOST"]


def test_capped_stable_and_unique():
    signals = [
        _signal("OTP_REQUEST", Severity.CRITICAL),
        _signal("REMOTE_ACCESS_REQUEST", Severity.CRITICAL),
        _signal("APK_INSTALL", Severity.MEDIUM),
        _signal("ENTRY_FEE", Severity.MEDIUM),
        _signal("URGENCY_PRESSURE", Severity.MEDIUM),
    ]
    steps = _steps(signals)
    assert 2 <= len(steps) <= MAX_STEPS
    assert len(steps) == len(set(steps))
    assert steps[0] == "NEVER_SHARE_CREDENTIALS"
    assert steps[-1] == "REPORT_IF_LOST"
    assert steps == _steps(list(reversed(signals)))

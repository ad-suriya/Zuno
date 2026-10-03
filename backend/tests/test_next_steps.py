from app.engine.assessment import assess
from app.engine.next_steps import MAX_STEPS, next_steps
from app.engine.red_flags import detect_red_flags
from app.engine.safety import detect_hard_signals
from app.models import Signal, SignalKind, SignalSource


def _signals(text: str) -> list[Signal]:
    return [
        Signal(kind=SignalKind.WARNING, code=r.code, severity=r.severity, source=SignalSource.RULE,
               explanation=r.explanation)
        for r, _ in detect_hard_signals(text) + detect_red_flags(text)
    ]


def _steps(text: str) -> list[str]:
    signals = _signals(text)
    return next_steps(assess(signals, []), signals)


def test_otp_story_puts_credential_steps_first():
    steps = _steps("Caller from SEBI KYC says my account will be frozen and asks for the OTP sent to me.")
    assert steps[:2] == ["NEVER_SHARE_CREDENTIALS", "IF_SHARED_CALL_BANK"]
    assert steps[-1] == "REPORT_IF_LOST"


def test_no_signals_still_gives_checks():
    steps = _steps("A friend told me about an investment plan.")
    assert "CHECK_SEBI_REGISTER" in steps and "DO_NOT_PAY_YET" in steps
    assert steps[-1] == "REPORT_IF_LOST"


def test_order_is_stable_without_duplicates_and_bounded():
    text = ("Share the OTP and UPI PIN, install AnyDesk and this .apk, pay the joining fee and recruit 3 friends, "
            "only today!")
    first, second = _steps(text), _steps(text)
    assert first == second
    assert len(first) == len(set(first))
    assert 2 <= len(first) <= MAX_STEPS
    assert first[-1] == "REPORT_IF_LOST"


def test_signal_specific_steps():
    assert "UNINSTALL_REMOTE_APP" in _steps("Install AnyDesk so I can help you.")
    assert "DO_NOT_INSTALL_APK" in _steps("Download the trading.apk file.")
    assert "ASK_WHAT_IS_SOLD" in _steps("Pay the joining fee and recruit people.")
    assert "TAKE_YOUR_TIME" in _steps("Offer valid today only.")


def test_low_concern_steps():
    from app.models import Assessment, AssessmentLevel

    steps = next_steps(Assessment(level=AssessmentLevel.LOW_CONCERN, reasons=[]), [])
    assert steps == ["CONTACT_VIA_OFFICIAL_DETAILS", "REPORT_IF_LOST"]


def test_steps_never_give_advice():
    from app.i18n import STEP_TEXT

    for texts in STEP_TEXT.values():
        for text in texts.values():
            lowered = text.lower()
            assert "scam" not in lowered and " buy " not in f" {lowered} " and " sell " not in f" {lowered} "

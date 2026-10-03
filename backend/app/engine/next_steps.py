"""Safe next steps (F02). Chosen deterministically from the level and signals, never by the LLM.

Steps are codes, not text, so the frontend and voice can localize them
(`app/i18n.py` STEP_TEXT, `frontend/src/lib/i18n.ts`). No step recommends buying,
selling or a specific product, and none says "this is a scam".
"""

from app.models import Assessment, AssessmentLevel, Severity, Signal, SignalKind

CREDENTIAL_CODES = {"OTP_REQUEST", "UPI_PIN_REQUEST", "PASSWORD_REQUEST", "CREDENTIAL_REQUEST"}
MAX_STEPS = 6
LAST_STEP = "REPORT_IF_LOST"


def next_steps(assessment: Assessment, signals: list[Signal]) -> list[str]:
    """Return ordered step codes, e.g. ["DO_NOT_PAY_YET", "CHECK_SEBI_REGISTER", "REPORT_IF_LOST"]."""
    warnings = [s for s in signals if s.kind == SignalKind.WARNING]
    codes = {s.code for s in warnings}
    unsure = assessment.level in (AssessmentLevel.HIGH_CONCERN, AssessmentLevel.NEEDS_VERIFICATION)

    candidates: list[tuple[bool, str]] = [
        # Credential steps always come first when a critical signal exists.
        (any(s.severity == Severity.CRITICAL for s in warnings), "NEVER_SHARE_CREDENTIALS"),
        (bool(codes & CREDENTIAL_CODES), "IF_SHARED_CALL_BANK"),
        ("REMOTE_ACCESS_REQUEST" in codes, "UNINSTALL_REMOTE_APP"),
        ("APK_INSTALL" in codes, "DO_NOT_INSTALL_APK"),
        (unsure, "DO_NOT_PAY_YET"),
        (unsure, "CHECK_SEBI_REGISTER"),
        (bool(codes & {"RECRUITMENT_DEPENDENCE", "ENTRY_FEE"}), "ASK_WHAT_IS_SOLD"),
        ("URGENCY_PRESSURE" in codes, "TAKE_YOUR_TIME"),
        (assessment.level == AssessmentLevel.LOW_CONCERN, "CONTACT_VIA_OFFICIAL_DETAILS"),
    ]
    steps = [code for applies, code in candidates if applies]
    return steps[: MAX_STEPS - 1] + [LAST_STEP]

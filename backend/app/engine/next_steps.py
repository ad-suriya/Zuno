"""Deterministic safe next steps (F02).

Steps are codes, not text, so the frontend and voice can localize them. They are
chosen from the assessment level, signal codes and verification statuses only,
never by the LLM. No step recommends buying, selling, or a product or broker.
"""

from app.models import (
    Assessment,
    AssessmentLevel,
    Severity,
    Signal,
    SignalKind,
    VerificationRecord,
    VerificationStatus,
)

CREDENTIAL_CODES = {"OTP_REQUEST", "UPI_PIN_REQUEST", "PASSWORD_REQUEST", "CREDENTIAL_REQUEST"}
MAX_STEPS = 6

# Fixed display order. Credential protection always comes first.
ORDER = (
    "NEVER_SHARE_CREDENTIALS",
    "IF_SHARED_CALL_BANK",
    "UNINSTALL_REMOTE_APP",
    "DO_NOT_INSTALL_APK",
    "DO_NOT_PAY_YET",
    "CHECK_SEBI_REGISTER",
    "ASK_WHAT_IS_SOLD",
    "TAKE_YOUR_TIME",
    "CONTACT_VIA_OFFICIAL_DETAILS",
    "REPORT_IF_LOST",
)


def next_steps(
    assessment: Assessment, signals: list[Signal], verifications: list[VerificationRecord]
) -> list[str]:
    warnings = [s for s in signals if s.kind == SignalKind.WARNING]
    codes = {s.code for s in warnings}
    chosen: set[str] = {"REPORT_IF_LOST"}

    if any(s.severity == Severity.CRITICAL for s in warnings):
        chosen.add("NEVER_SHARE_CREDENTIALS")
    if codes & CREDENTIAL_CODES:
        chosen.add("IF_SHARED_CALL_BANK")
    if "REMOTE_ACCESS_REQUEST" in codes:
        chosen.add("UNINSTALL_REMOTE_APP")
    if "APK_INSTALL" in codes:
        chosen.add("DO_NOT_INSTALL_APK")
    if assessment.level in (AssessmentLevel.HIGH_CONCERN, AssessmentLevel.NEEDS_VERIFICATION):
        chosen.update({"DO_NOT_PAY_YET", "CHECK_SEBI_REGISTER"})
    if codes & {"RECRUITMENT_DEPENDENCE", "ENTRY_FEE"}:
        chosen.add("ASK_WHAT_IS_SOLD")
    if "URGENCY_PRESSURE" in codes:
        chosen.add("TAKE_YOUR_TIME")
    # A verified entity does not prove the contact represents it (VERIFICATION.md, F08).
    if any(v.status == VerificationStatus.VERIFIED for v in verifications):
        chosen.add("CONTACT_VIA_OFFICIAL_DETAILS")

    ordered = [code for code in ORDER if code in chosen]
    if len(ordered) > MAX_STEPS:
        ordered = ordered[: MAX_STEPS - 1] + ["REPORT_IF_LOST"]
    return ordered

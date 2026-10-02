"""Deterministic assessment engine (ADR-002, ADR-006).

Maps warning signals and verification records to one of three levels.
The LLM never decides the level; it only explains it afterwards.
"""

from app.models import (
    Assessment,
    AssessmentLevel,
    AssessmentReason,
    Severity,
    Signal,
    SignalKind,
    SourceTier,
    VerificationRecord,
    VerificationStatus,
)

TRUSTED_TIERS = (SourceTier.OFFICIAL_REGULATOR, SourceTier.OFFICIAL_ENTITY)
UNRESOLVED = (VerificationStatus.NOT_VERIFIED, VerificationStatus.UNKNOWN)


def assess(signals: list[Signal], verifications: list[VerificationRecord]) -> Assessment:
    warnings = [s for s in signals if s.kind == SignalKind.WARNING]
    critical = [s for s in warnings if s.severity == Severity.CRITICAL]
    high = [s for s in warnings if s.severity == Severity.HIGH]
    material = [v for v in verifications if v.material]
    contradicted = [v for v in material if v.status == VerificationStatus.CONTRADICTED]
    unresolved = [v for v in material if v.status in UNRESOLVED]
    trusted_verified = [
        v for v in material if v.status == VerificationStatus.VERIFIED and v.source_tier in TRUSTED_TIERS
    ]

    high_reasons: list[AssessmentReason] = []
    if critical:
        high_reasons.append(
            AssessmentReason(
                rule="CRITICAL_SAFETY_SIGNAL",
                explanation="A request for an OTP, PIN, password, credentials or remote access was found.",
                signal_ids=[s.id for s in critical],
            )
        )
    if contradicted:
        high_reasons.append(
            AssessmentReason(
                rule="CONTRADICTED_CLAIM",
                explanation="A claim made to you was contradicted by a trusted source.",
                verification_ids=[v.id for v in contradicted],
            )
        )
    if len({s.code for s in high}) >= 2:
        high_reasons.append(
            AssessmentReason(
                rule="MULTIPLE_SIGNIFICANT_WARNINGS",
                explanation="Several significant warning signals are present together.",
                signal_ids=[s.id for s in high],
            )
        )

    verified_reason = (
        [
            AssessmentReason(
                rule="VERIFIED_CLAIMS",
                explanation="Some claims were confirmed by trusted sources. This confirms the named entity exists; "
                "it does not prove that the person who contacted you represents it.",
                verification_ids=[v.id for v in trusted_verified],
            )
        ]
        if trusted_verified
        else []
    )

    if high_reasons:
        return Assessment(level=AssessmentLevel.HIGH_CONCERN, reasons=high_reasons + verified_reason)

    needs_reasons: list[AssessmentReason] = []
    if warnings:
        needs_reasons.append(
            AssessmentReason(
                rule="WARNING_SIGNALS_PRESENT",
                explanation="Some warning signals were found that should be checked before acting.",
                signal_ids=[s.id for s in warnings],
            )
        )
    if unresolved:
        needs_reasons.append(
            AssessmentReason(
                rule="UNVERIFIED_CLAIMS",
                explanation="Important claims could not be verified. This does not mean they are false.",
                verification_ids=[v.id for v in unresolved],
            )
        )
    if not trusted_verified:
        needs_reasons.append(
            AssessmentReason(
                rule="NO_TRUSTED_VERIFICATION",
                explanation="Nothing has been confirmed by an official source yet. Important information is missing.",
            )
        )

    if needs_reasons:
        return Assessment(level=AssessmentLevel.NEEDS_VERIFICATION, reasons=needs_reasons + verified_reason)

    return Assessment(
        level=AssessmentLevel.LOW_CONCERN,
        reasons=[
            AssessmentReason(
                rule="NO_MAJOR_WARNINGS",
                explanation="No major warning signals were identified from the information available.",
            ),
            *verified_reason,
        ],
    )

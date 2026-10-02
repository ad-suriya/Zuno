# Architecture Decisions

## ADR-001: Use Sarvam for voice

Decision:
Use Sarvam for Indic speech-to-text and text-to-speech.

Reason:
Bharat-first voice interaction is a core product feature.

---

## ADR-002: Do not use LLM as final safety classifier

Decision:
Use deterministic rules + structured evidence.

Reason:
Safety-critical conclusions should be explainable and predictable.

---

## ADR-003: GCP

Decision:
Use Cloud Run + Firestore + Cloud Storage.

Reason:
Simple deployment architecture suitable for prototype and future deployment.

---

## ADR-004: Assessment labels

Decision:
Use LOW CONCERN / NEEDS VERIFICATION / HIGH CONCERN.

Reason:
Avoid unsupported numerical fraud probabilities.

---

## ADR-005: Database is GCP Firestore

Decision:
Use GCP Firestore (Native mode) as the primary database. Do not use PostgreSQL or Cloud SQL.

Reason:
Serverless, GCP-native and has a free tier: no instance to provision or connection pool to manage from Cloud Run.
An investigation maps naturally to a document with subcollections (evidence, claims, questions, verifications).
Local development uses the Firestore emulator.

Trade-off:
No SQL joins or ad-hoc relational queries. Model data around the investigation document and
denormalize where needed. Verification records must still store claim, source, timestamp,
result, evidence and explanation (see VERIFICATION.md).

---

## ADR-006: Deterministic assessment rules

Decision:
The assessment level is computed by `backend/app/engine/assessment.py` from warning signals and
verification records:

- HIGH CONCERN if any of: a CRITICAL signal; a material claim CONTRADICTED; two or more distinct
  HIGH-severity warning signals.
- Otherwise NEEDS VERIFICATION if any of: any warning signal; a material claim NOT_VERIFIED or
  UNKNOWN; no material claim VERIFIED by a tier 1-2 source.
- Otherwise LOW CONCERN.

Every reason cites the signal or verification IDs it depends on.

Reason:
Keeps the level predictable and explainable. NOT_VERIFIED can never reach HIGH CONCERN on its own.
LOW CONCERN requires positive verification from an official source, so an empty investigation is
NEEDS VERIFICATION ("important information is missing"), not LOW CONCERN. A verified entity never
cancels a critical signal, because impersonation of registered entities is common.

---

## ADR-007: Verification records are written only by the backend

Decision:
The API exposes no endpoint for clients to create or edit verification records. Only the
verification engine (server-side) writes them.

Reason:
Prevents invented or client-supplied verification results.

---

## ADR-008: Calm, accessible design system

Decision:
UI follows `design-system/MASTER.md`: warm stone neutrals, one sea-blue accent, Noto Sans +
Noto Sans Tamil, flat surfaces, and three reserved assessment colour families (green / amber /
red) that are always paired with an icon and text label.

Reason:
Users are often anxious, on low-end phones, and reading in Tamil. A calm public-service look
builds trust without alarm; Noto covers every Indic script we may add with matched metrics.
Assessment colours are never used alone, so the level is readable in greyscale and by screen
readers, and HIGH CONCERN never reads as a "fraud" verdict.

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

## ADR-008: Gemini via Vertex AI, structured output, deterministic fallback

Decision:
All LLM calls go through `backend/app/llm/client.py`, using the official `google-genai` SDK against
Vertex AI (Application Default Credentials, no API key). Every call requests JSON validated against a
Pydantic schema. Prompts are loaded from `prompts/`, always prefixed with `prompts/safety.md`.
`generate_json` never raises: timeouts, quota errors, safety blocks and schema mismatches return `None`
and the feature falls back to deterministic behaviour. `LLM_ENABLED=false` (the default) disables the
LLM entirely.

Reason:
The demo must never break on an LLM error, and LLM output is data to validate, not instructions.

Consequences:
Only redacted text is sent. Prompts and responses are never logged (prompt name, latency, outcome only).
The backend image is built from the repo root so it contains `prompts/`.

---

## ADR-009: LLM proposes questions; a deterministic ranker selects

Decision:
`ai/questions.py` collects candidate questions from the LLM (when enabled) plus one template per open
unknown. `engine/question_ranker.py` vetoes any candidate that mentions credentials (hard safety rules),
gives investment advice or asks for identity/banking data; drops candidates for resolved or already-asked
unknowns; and scores the rest (safety relevance > information gain > answerability > priority) with a
fixed tie-break. Stop conditions (critical signal, 5 questions, user finished, two answers with no new
information, nothing useful left) live in the service.

Reason:
The LLM can phrase good questions, but which question is shown, and that it is safe, must be predictable.

---

## ADR-010: SEBI verification from a dated offline snapshot; "not found" = NOT_VERIFIED

Decision:
`scripts/refresh_sebi.py` downloads SEBI's public lists of Investment Advisers, Research Analysts and
Stock Brokers into `backend/data/sebi_registry.csv` (with snapshot date and source URL per row).
`engine/verification.py` checks registration numbers and names against it. A well-formed number missing
from the snapshot is NOT_VERIFIED, never CONTRADICTED. CONTRADICTED requires positive evidence: the
number belongs to a clearly different company, or the registration has expired.
Verification is recomputed from the current facts after every evidence item; unchanged records keep
their IDs.

Reason:
No live scraping during a request (latency, availability, load on sebi.gov.in). The snapshot can be
stale, so absence must never be treated as fraud.

---

## ADR-011: Reassuring signals are shown but never lower the level

Decision:
`engine/reassuring.py` derives REASSURING signals (REGISTRATION_VERIFIED, NO_UPFRONT_PAYMENT,
REALISTIC_RETURN_CLAIM, OFFICIAL_CHANNEL_PAYMENT) from verification records and structured facts only.
They are computed on read rather than stored, so they always match the current verification state.
`assess()` ignores them; only tier 1-2 verification can move toward LOW CONCERN (ADR-006).

Reason:
Balanced evidence helps users, but positive wording is easy for a scammer to fake.

---

## ADR-012: Uploaded audio and images are processed in memory, not persisted

Decision:
Voice (`/speech/transcribe`) and screenshots (`/investigations/{id}/evidence/image`) are processed in
memory and discarded. They return redacted text that the user reviews; only the confirmed text is
submitted as evidence through the normal ingest path. Text-to-speech only speaks server-generated text
(a stored question, the explanation or the next steps), never arbitrary input. Voice requests are rate
limited per client IP.

Reason:
Screenshots and recordings can contain OTPs, account numbers or other people's data. Not storing them
removes that risk and the need for Cloud Storage in the MVP.

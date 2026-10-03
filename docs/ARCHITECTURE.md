# Architecture

```
User
 ↓
Next.js frontend
 ↓
FastAPI backend
 ↓
Investigation engine
 ├── Evidence processor
 ├── NLP extraction
 ├── Adaptive question engine
 ├── Red-flag engine
 ├── Positive-signal engine
 └── Verification engine
 ↓
Assessment engine
 ↓
Explanation layer
```

## Backend layout (`backend/app/`)

| Module | Role |
|---|---|
| `engine/safety.py` | Credential redaction (typed, spaced and spoken codes) + hard safety signals |
| `engine/red_flags.py` | Deterministic warning rules (English, Tamil, Tanglish; negation-aware) |
| `engine/patterns.py` | Regex fact extractors: SEBI reg nos, UPI IDs, phones, URLs, ₹ amounts, return claims, company names |
| `engine/registry.py` | SEBI snapshot loader + name matching (`backend/data/sebi_registry.csv`) |
| `engine/verification.py` | Deterministic SEBI verification (ADR-010) |
| `engine/reassuring.py` | Reassuring signals, never affect the level (ADR-011) |
| `engine/assessment.py` | Rules-based assessment (ADR-006) |
| `engine/next_steps.py` | Safe next-step codes from level + signals (F02) |
| `engine/question_ranker.py` | Veto / dedupe / score question candidates (ADR-009) |
| `llm/` | Prompt loading (`prompts/`) and the fail-safe Gemini client (ADR-008) |
| `ai/extraction.py` | Facts: regex + grounded LLM extraction + answer interpretation (F05) |
| `ai/questions.py` | Candidate questions: LLM + templates (F06) |
| `ai/explanation.py` | Explanation with output guard and template fallback (F07) |
| `voice/sarvam.py` | Sarvam STT/TTS client + per-IP rate limiter (F11) |
| `i18n.py` | Backend-generated text per language (question/explanation templates, steps) |
| `service.py` | Workflow (below) |
| `repository/firestore.py` | Firestore persistence (`repository/memory.py` for tests and `REPOSITORY=memory` local demos) |
| `api/routes.py`, `api/media.py` | HTTP API |

### Flow

```
ingest (story / added message / answer / confirmed screenshot text):
  redact → store evidence → rules (hard safety + red flags) → signals
         → facts = merge(previous, regex facts, answer facts, grounded LLM facts) → unknowns
         → verify(facts, SEBI snapshot) → replace changed verification records
next question:
  stop conditions → candidates (LLM + templates) → ranker veto/dedupe/score → store question
assessment:
  signals (+ derived reassuring) + verifications → assess() → next_steps() → explain()
```

All user text is redacted before it is stored, logged or sent to an LLM. Logs carry IDs and
codes only. LLMs never decide the level, the verification status or which question is shown.

## API (`/api/v1`)

| Method | Path | Purpose |
|---|---|---|
| POST | `/investigations` | Start from the user's story (`story`, `language`, `channel`) |
| GET | `/investigations/{id}` | Investigation + evidence + signals + verifications + facts + questions |
| POST | `/investigations/{id}/evidence` | Add text evidence (`content`, `kind`: `text` or `image_text`) |
| POST | `/investigations/{id}/assessment` | Run the deterministic assessment + next steps + explanation |
| POST | `/investigations/{id}/questions/next` | Compute and store the next question (`next_question` null = done) |
| POST | `/investigations/{id}/questions/{qid}/answer` | Answer (`content`), ingested as evidence kind `answer` |
| POST | `/investigations/{id}/questions/{qid}/skip` | Skip a question |
| POST | `/investigations/{id}/finish` | User is done; no more questions |
| POST | `/investigations/{id}/evidence/image` | Screenshot → redacted text to confirm (nothing stored) |
| POST | `/speech/transcribe` | Audio (multipart, ≤ 5 MB) → redacted transcript (nothing stored) |
| POST | `/speech/synthesize` | Speak a stored question / the explanation / the next steps (WAV) |

Outside `/api/v1`: `GET /health` (liveness, no dependencies) and
`GET /health/ready` (readiness; 503 if Firestore is unreachable).

Investigation endpoints return `InvestigationDetail` (see `backend/app/models.py`, mirrored in
`frontend/src/lib/types.ts`). There is no endpoint for writing verification records (ADR-007).

## Firestore layout

```
investigations/{investigation_id}        language, channel, assessment, finished, facts, created_at, updated_at, expires_at
  evidence/{evidence_id}                 kind, content (redacted), redacted, created_at, expires_at
  signals/{signal_id}                    kind, code, severity, source, evidence_id, matched_text, explanation, expires_at
  verifications/{verification_id}        code, params, claim, source, source_tier, status, evidence, explanation, material, checked_at, expires_at
  questions/{question_id}                text, objective, target_unknown, priority, source, status, answer_evidence_id, asked_at, expires_at
```

Every document has `expires_at` (created + 7 days). A Firestore TTL policy on each collection group
deletes expired documents (PRIVACY.md); `scripts/deploy.sh setup` creates the policies.
Reassuring signals are derived on read and not stored (ADR-011).

## Errors

Every error response has the same shape, which the frontend's `ApiError` mirrors
(`frontend/src/lib/api.ts`):

```json
{"error": {"code": "NOT_FOUND", "message": "Investigation not found.", "request_id": "..."}}
```

| Code | Status | When |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Bad request body (field names only; submitted values are never echoed) |
| `NOT_FOUND` | 404 | Unknown investigation or question |
| `CONFLICT` | 409 | E.g. answering a question that was already answered or skipped |
| `TOO_LARGE` | 413 | Audio or image over 5 MB |
| `UNSUPPORTED_MEDIA` | 415 | Not a supported audio format / not a PNG or JPEG |
| `RATE_LIMITED` | 429 | Too many voice requests from one client |
| `VOICE_UNAVAILABLE` | 503 | Sarvam not configured or failing (users can still type) |
| `IMAGE_UNAVAILABLE` | 503 | LLM disabled or could not read the screenshot |
| `HTTP_ERROR` | 4xx | Other HTTP errors (e.g. unknown route) |
| `STORAGE_UNAVAILABLE` | 503 | Firestore unreachable or credentials missing |
| `INTERNAL_ERROR` | 500 | Anything else; details are logged, not returned |

Every response carries an `X-Request-ID` header (echoed if the client sends one),
which is also written to logs so a user-reported reference can be traced.
The frontend adds `NETWORK_ERROR` and `TIMEOUT` for failures before a response arrives.

## Logging

On Cloud Run (`K_SERVICE` set), logs are one JSON object per line on stdout, which
Cloud Logging parses into severity and fields. Locally they are plain text.

## Configuration and secrets

| Where | File |
|---|---|
| Backend, local | `.env` (from `.env.example`), loaded by `make backend` |
| Frontend, local | `frontend/.env.local` (from `frontend/.env.example`) |
| Backend, Cloud Run | Service env vars; API keys via `--set-secrets` from Secret Manager |

Key backend settings: `LLM_ENABLED` + `GEMINI_MODEL` (Gemini on Vertex AI, ADR-008),
`SARVAM_API_KEY` (voice), `PROMPTS_DIR` and `SEBI_REGISTRY_PATH` (set in the Docker image),
`REPOSITORY=memory` (local demo without the emulator; ignored on Cloud Run).

The backend reads configuration only from environment variables (`backend/app/config.py`),
so the same code runs locally and on Cloud Run. `backend/Dockerfile` builds the Cloud Run
image from the repo root (so `prompts/` and `backend/data/` are included); `frontend/Dockerfile`
builds the Next.js standalone server. `NEXT_PUBLIC_*` values are baked into the browser bundle, so never put secrets there.

## External services

| Service | Role |
|---|---|
| Sarvam | STT / Indic language / TTS |
| Gemini / Vertex AI | NLP / reasoning / explanation |
| SEBI + trusted sources | Verification |
| GCP | Deployment |

## GCP

Deployed with `scripts/deploy.sh` (README "Deploying"):

| Service | Use |
|---|---|
| Cloud Run `zuno-backend` | FastAPI; runs as service account `zuno-backend` (`datastore.user`, `aiplatform.user`, `secretmanager.secretAccessor`) |
| Cloud Run `zuno-frontend` | Next.js standalone server; `NEXT_PUBLIC_API_BASE_URL` baked in at build time |
| Firestore (Native, `asia-south1`) | Primary database, TTL on `expires_at` |
| Vertex AI | Gemini (when `LLM_ENABLED=true`) |
| Secret Manager | `SARVAM_API_KEY` → `--set-secrets` |
| Artifact Registry `zuno` + Cloud Build | Images |
| Cloud Logging | Application logs (JSON, IDs and codes only) |

Cloud Storage is not used: uploaded audio and screenshots are never stored (ADR-012).

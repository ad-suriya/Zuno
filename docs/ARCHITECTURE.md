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
| `engine/safety.py` | Credential redaction + hard safety signals |
| `engine/red_flags.py` | Deterministic warning-signal rules |
| `engine/assessment.py` | Rules-based assessment (ADR-006) |
| `engine/next_steps.py` | Rules-chosen safe next steps, returned as codes (F02) |
| `service.py` | Workflow: redact → store evidence → run rules → assess |
| `repository/firestore.py` | Firestore persistence |
| `api/routes.py` | HTTP API |

All user text is redacted before it is stored or logged. Logs carry IDs and
signal codes only.

## API (`/api/v1`)

| Method | Path | Purpose |
|---|---|---|
| POST | `/investigations` | Start from the user's story (`story`, `language`, `channel`) |
| GET | `/investigations/{id}` | Investigation + evidence + signals + verifications |
| POST | `/investigations/{id}/evidence` | Add text evidence (`content`) |
| POST | `/investigations/{id}/assessment` | Run the deterministic assessment and its `next_steps` codes |

Outside `/api/v1`: `GET /health` (liveness, no dependencies) and
`GET /health/ready` (readiness; 503 if Firestore is unreachable).

Every endpoint returns `InvestigationDetail` (see `backend/app/models.py`).
There is no endpoint for writing verification records (ADR-007).

## Firestore layout

```
investigations/{investigation_id}        language, channel, assessment, created_at, updated_at
  evidence/{evidence_id}                 kind, content (redacted), redacted, created_at
  signals/{signal_id}                    kind, code, severity, source, evidence_id, matched_text, explanation
  verifications/{verification_id}        claim, source, source_tier, status, evidence, explanation, material, checked_at
```

Timestamps are stored as native Firestore timestamps so a TTL policy can
enforce evidence retention (PRIVACY.md).

## Errors

Every error response has the same shape, which the frontend's `ApiError` mirrors
(`frontend/src/lib/api.ts`):

```json
{"error": {"code": "NOT_FOUND", "message": "Investigation not found.", "request_id": "..."}}
```

| Code | Status | When |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Bad request body (field names only; submitted values are never echoed) |
| `NOT_FOUND` | 404 | Unknown investigation |
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

The backend reads configuration only from environment variables (`backend/app/config.py`),
so the same code runs locally and on Cloud Run. `backend/Dockerfile` builds the Cloud Run
image. `NEXT_PUBLIC_*` values are baked into the browser bundle, so never put secrets there.

## External services

| Service | Role |
|---|---|
| Sarvam | STT / Indic language / TTS |
| Gemini / Vertex AI | NLP / reasoning / explanation |
| SEBI + trusted sources | Verification |
| GCP | Deployment |

## GCP

| Service | Use |
|---|---|
| Cloud Run | Backend |
| Firestore | Primary database (Native mode) |
| Cloud Storage | Temporary evidence |
| Secret Manager | API keys |
| Cloud Logging | Application logs |

# Zuno

> Know before you act.

Zuno is a voice-first financial opportunity verification
assistant designed for Indian investors.

## The problem

Indian users receive financial offers through WhatsApp, Telegram, calls,
social media, and people they know. Many don't know which claims matter,
what to check, or where to check it, and they find out only after the
money is gone.

## How it works

User story
→ Evidence
→ Adaptive questions
→ Verification
→ Assessment
→ Safe next step

## Features

- Voice-first interaction
- Indic languages (English + Tamil MVP)
- Adaptive investigation
- Evidence extraction
- Trusted-source verification
- Explainable assessment
- Privacy-first design

## Tech Stack

- Next.js
- FastAPI
- GCP Firestore
- Sarvam AI
- Gemini / Vertex AI
- Google Cloud

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Running locally

Prerequisites: Python 3.12+, Node 20+, and for the Firestore emulator the `gcloud` CLI + Java 21+.

```bash
gcloud components install cloud-firestore-emulator
make setup        # creates .env, frontend/.env.local, backend venv, npm install
```

Then, in three terminals:

```bash
make emulator     # Firestore emulator on localhost:8080
make backend      # FastAPI on http://localhost:8000 (docs at /docs)
make frontend     # Next.js on http://localhost:3000
```

No `gcloud`? Use `make backend-memory` instead of `make emulator` + `make backend`: data stays in
the backend process and is lost on restart (local demos only; ignored on Cloud Run).

Everything works without API keys: with `LLM_ENABLED=false` (default) extraction, questions and
explanations use deterministic fallbacks, and without `SARVAM_API_KEY` users type instead of speaking.
To turn them on, set in `.env`:

| Feature | Settings |
|---|---|
| Gemini (extraction, questions, explanations, screenshots) | `LLM_ENABLED=true`, `GEMINI_MODEL=<current fast Gemini model on Vertex AI>`, `GOOGLE_CLOUD_PROJECT`, and `gcloud auth application-default login` |
| Voice (Sarvam) | `SARVAM_API_KEY` |

Checks:

```bash
make test         # backend tests (incl. emulator round-trip) + frontend lint/typecheck
make smoke        # end-to-end checks against the running stack
cd backend && LLM_LIVE=1 .venv/bin/python -m pytest -m live   # optional: real Gemini call
```

The SEBI register snapshot (`backend/data/sebi_registry.csv`) is refreshed with `make refresh-sebi`.

## Deploying (GCP Cloud Run)

Needs the `gcloud` CLI, logged in, and a GCP project with billing.

```bash
export PROJECT=<your-gcp-project-id>          # REGION defaults to asia-south1
make deploy-setup      # once: APIs, Firestore (Native) + TTL, Artifact Registry, service account, SARVAM_API_KEY secret
make deploy-backend    # build (Cloud Build) + deploy zuno-backend
make deploy-frontend   # build with the backend URL baked in + deploy zuno-frontend, then set backend CORS
API_BASE_URL=<backend url> WEB_BASE_URL=<frontend url> make smoke
```

Options (env vars): `LLM_ENABLED=true GEMINI_MODEL=...` to enable Gemini, `MIN_INSTANCES=1` during the
demo window to avoid cold starts. `LLM_ENABLED` can be switched off instantly on stage with
`gcloud run services update zuno-backend --update-env-vars LLM_ENABLED=false`.
Add a billing budget alert in the Cloud Console. Secrets live only in Secret Manager.

## Adding a language

1. `frontend/src/lib/i18n.ts`: add a dictionary (typecheck fails until every key is translated).
2. `backend/app/i18n.py`: add level labels, reasons, signal phrases, steps and question templates.
3. `backend/app/models.py` `Language` + `voice/sarvam.py` `LANGUAGE_CODES` + `frontend/src/lib/types.ts`.
4. `backend/app/engine/red_flags.py` / `safety.py`: add script and transliterated variants, with tests.

## Repository layout

| Path | Contents |
|---|---|
| `frontend/` | Next.js + TypeScript + Tailwind |
| `backend/` | FastAPI + Pydantic, Firestore repository, deterministic rules, SEBI snapshot (`data/`) |
| `prompts/` | LLM prompts, loaded by `backend/app/llm/prompts.py` |
| `docs/` | Product, safety and architecture docs |
| `tests/` | End-to-end smoke test and demo scenarios; unit tests live in `backend/tests/` |
| `scripts/` | SEBI snapshot refresh, Cloud Run deployment |

## Safety

Zuno does not provide investment advice, predict prices, or recommend
buying, selling, or holding any security. It never asks for OTPs,
passwords, UPI PINs, or bank/trading credentials. See
[docs/SAFETY.md](docs/SAFETY.md).

## Team

Caffeine Overflow — SANGYAN hackathon.

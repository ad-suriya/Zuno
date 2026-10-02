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

Prerequisites: Python 3.12+, Node 20+, `gcloud` CLI, and Java 21+ (for the Firestore emulator).

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

Checks:

```bash
make test         # backend tests (incl. emulator round-trip) + frontend lint/typecheck
make smoke        # end-to-end checks against the running stack
```

## Repository layout

| Path | Contents |
|---|---|
| `frontend/` | Next.js + TypeScript + Tailwind |
| `backend/` | FastAPI + Pydantic, Firestore repository, deterministic rules |
| `prompts/` | LLM prompts (not used yet) |
| `docs/` | Product, safety and architecture docs |
| `tests/` | End-to-end smoke test; unit tests live in `backend/tests/` |

## Safety

Zuno does not provide investment advice, predict prices, or recommend
buying, selling, or holding any security. It never asks for OTPs,
passwords, UPI PINs, or bank/trading credentials. See
[docs/SAFETY.md](docs/SAFETY.md).

## Team

Caffeine Overflow — SANGYAN hackathon.

# Zuno Development Context

Before making changes, read `CONTEXT.md`, this file, and the relevant files in `docs/`.

## Product

Zuno is a voice-first, native-language financial opportunity
verification assistant for Indian users.

## Core principle

Zuno investigates. It does not make investment decisions for users.

## Never

- Give buy/sell/hold recommendations.
- Predict stock prices.
- Ask for OTPs.
- Ask for passwords.
- Ask for UPI PINs.
- Ask for bank credentials.
- Ask for broker credentials.
- Automatically label something as fraud without sufficient evidence.
- Treat "could not verify" as "fraud".
- Treat every MLM as fraudulent.

## Assessment levels

- LOW CONCERN
- NEEDS VERIFICATION
- HIGH CONCERN

Do not replace these with numeric scam scores (see `docs/DECISIONS.md` ADR-004).

## AI principle

LLMs interpret information.
Deterministic rules control safety-critical decisions.

## Languages

MVP:
- English
- Tamil

Architecture should allow additional Indian languages.

## Voice

Sarvam handles Indic speech/language processing.

## Infrastructure

GCP:
- Cloud Run
- Firestore (primary database, Native mode)
- Cloud Storage
- Secret Manager

## Frontend

Next.js + TypeScript + Tailwind.

## Backend

FastAPI + Python. Database is GCP Firestore; use the Firestore emulator locally.

## Prompts

LLM prompts live in `prompts/`, not inline in source code. The backend loads them from there.

## Development rules

- Do not introduce unnecessary dependencies.
- Do not rewrite working modules without reason.
- Keep frontend and backend contracts synchronized.
- Never commit secrets.
- Update documentation when architecture changes.
- Record important architecture/product decisions in `docs/DECISIONS.md`.

## Reference docs

| File | Covers |
|---|---|
| `docs/PRODUCT.md` | What Zuno is and is not |
| `docs/SAFETY.md` | Prohibitions, uncertainty language, hard safety signals |
| `docs/AI_BEHAVIOR.md` | What the LLM may and may not decide |
| `docs/ARCHITECTURE.md` | System components and GCP layout |
| `docs/ADAPTIVE_ENGINE.md` | How the next question is chosen |
| `docs/VERIFICATION.md` | Source tiers and verification states |
| `docs/PRIVACY.md` | Data handling rules |
| `docs/DECISIONS.md` | Architecture decision records |
| `docs/plan/PLAN.md` | Build plan: feature index, phases, effort; one plan file per feature |

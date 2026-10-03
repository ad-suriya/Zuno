# Zuno Build Plan

This is the index. Each feature has its own plan file in this folder with
goal, design, tasks, tests and acceptance criteria.

## Where we are (as of 2026-10-04)

All features F01–F13 are implemented. With `LLM_ENABLED=false` every AI feature runs on its
deterministic fallback; 199 backend tests pass (incl. the F03 scenarios against the real SEBI snapshot),
frontend lint + typecheck + production build pass, and `make smoke` passes against a local stack.

Still needs people or credentials (not doable from code alone):

- Native-speaker review of all Tamil copy (frontend `i18n.ts`, backend `i18n.py`, Tamil scenario).
- Gemini: set `LLM_ENABLED=true` + `GEMINI_MODEL` with ADC credentials, run the live test
  (`LLM_LIVE=1 pytest -m live`) and review LLM questions/explanations on the F03 scenarios.
- Sarvam: set `SARVAM_API_KEY` and try a real Tamil recording end to end.
- Deployment: run `scripts/deploy.sh setup|all` against a GCP project, then `make smoke` on the URLs.
- Firestore emulator round-trip tests (`gcloud` was not available while building).

## Effort scale

| Effort | Meaning |
|---|---|
| Low | ≤ 2 hours, one person, no new dependencies |
| Medium | ½ – 1 day, may add one dependency or endpoint |
| High | 2+ days, external service/data, or cross-cutting |

## Features

| ID | Feature | Effort | Depends on | Phase | Status |
|---|---|---|---|---|---|
| F01 | [Evidence loop & trail UI](01-evidence-trail-ui.md) | Low | — | 1 | Done |
| F02 | [Safe next steps](02-safe-next-steps.md) | Low | — | 1 | Done |
| F03 | [Demo scenarios](03-demo-scenarios.md) | Low | — | 1 | Done |
| F04 | [LLM foundation (Gemini)](04-llm-foundation.md) | Medium | — | 2 | Done (live Gemini test pending) |
| F05 | [Claim & entity extraction](05-extraction.md) | Medium | F04 | 2 | Done (live Gemini test pending) |
| F06 | [Adaptive questions](06-adaptive-questions.md) | Medium–High | F05 (fallback works without) | 2 | Done |
| F07 | [Explanation layer](07-explanation.md) | Medium | F04, F02 | 2 | Done |
| F08 | [SEBI verification](08-verification-sebi.md) | High | F05 | 3 | Done |
| F09 | [Reassuring signals](09-reassuring-signals.md) | Low–Medium | F08 | 3 | Done |
| F10 | [Tamil localization](10-tamil-localization.md) | Medium | F01, F02 | 4 | Done (native-speaker review pending) |
| F11 | [Voice (Sarvam)](11-voice-sarvam.md) | High | F06, F10 | 4 | Done (untested with a real Sarvam key) |
| F12 | [Deployment (GCP)](12-deployment.md) | Medium | — (repeat after F04, F11) | 0 → 5 | Done (scripts); not yet deployed |
| F13 | [Screenshot evidence](13-screenshot-evidence.md) | High | F04 | Stretch | Done (live Gemini test pending) |

## Phases

| Phase | Goal | Features | Demo after this phase |
|---|---|---|---|
| 0 | Deploy the skeleton early | F12 (basic) | Public URL runs today's rules-only checker |
| 1 | Demo-ready text loop | F01, F02, F03 | Paste story → add messages → explainable result + safe steps |
| 2 | Investigate, don't classify | F04, F05, F06, F07 | Zuno asks the next useful question and explains the result |
| 3 | Trusted verification | F08, F09 | Registration number checked against SEBI; LOW / CONTRADICTED reachable |
| 4 | Bharat-first | F10, F11 | Full flow in Tamil, by voice |
| 5 | Ship | F12 (full), smoke tests, demo rehearsal | Stable hosted demo |
| Stretch | Richer evidence | F13 | Upload a WhatsApp screenshot |

Why this order: voice and Tamil look good on stage, but without the adaptive
loop (F06) and at least one real verification (F08), Zuno is just a regex
checker. Deploy early (Phase 0) so cloud problems don't surface on demo day.

## Critical path

```
F04 LLM ──► F05 Extraction ──► F06 Adaptive questions ──► F11 Voice
                    │                      ▲
                    └──► F08 SEBI ──► F09  │
F01, F02, F03 (parallel, no deps) ─────────┘
F10 Tamil (parallel once F01/F02 strings exist)
F12 Deploy (Phase 0, then redeploy after each phase)
```

Suggested split for a 3–4 person team:

- **Backend / AI:** F04 → F05 → F06 (backend) → F07
- **Verification:** F08 → F09
- **Frontend:** F01 → F02 → F03 → F06 (UI) → F10
- **Voice / infra:** F12 → F11 → F13

## Rules that apply to every feature

1. **Safety first.** LLMs interpret; deterministic rules decide the level (ADR-002, ADR-006).
   No feature may let LLM output change the assessment level directly.
2. **Every LLM call has a fallback.** If Gemini fails or is disabled, the feature degrades
   to deterministic behaviour; the demo must never break on an LLM error.
3. **Redact before anything leaves the service.** All user text, transcripts and OCR text
   go through `redact()` before storage, logging, or LLM calls.
4. **Contract sync.** Any change to `backend/app/models.py` updates
   `frontend/src/lib/types.ts` in the same commit.
5. **Prompts live in `prompts/`**, never inline.
6. **No new dependency without a reason** written in the feature's plan.
7. **Tests.** Every feature adds backend tests; safety-relevant logic needs negative tests
   (e.g. "never asks for an OTP").
8. **Docs.** Update `docs/ARCHITECTURE.md` for new endpoints/collections; add ADRs for decisions.

## Definition of done (per feature)

- [ ] Acceptance criteria in the feature plan pass
- [ ] `make test` green (backend tests + frontend lint + typecheck)
- [ ] `make smoke` green against the local stack
- [ ] Contract synced (`models.py` ↔ `types.ts`)
- [ ] Docs / ADR updated
- [ ] Status column above updated

## New ADRs (recorded in `docs/DECISIONS.md`)

| ADR | Decision | Feature |
|---|---|---|
| ADR-008 | Gemini via Vertex AI, structured JSON output, deterministic fallback | F04 |
| ADR-009 | LLM proposes questions; deterministic ranker selects and filters | F06 |
| ADR-010 | SEBI verification from a dated offline snapshot; "not found" = NOT_VERIFIED | F08 |
| ADR-011 | Reassuring signals are shown but never lower the level | F09 |
| ADR-012 | Uploaded audio/images are processed in memory, not persisted | F11, F13 |

# F01: Evidence loop & trail UI

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Low | 1 | — | frontend only |

## Goal

Turn the one-shot form into an investigation: after the first result, the user can
add more evidence (a forwarded message, what the caller said) and see the
assessment update. Show *which text triggered which signal*, so the result is
explainable.

## Current state

- `POST /investigations/{id}/evidence` and `api.addEvidence()` exist; no UI calls them.
- `AssessmentResult` lists signals but not the evidence they came from.
- `Signal.evidence_id` and `AssessmentReason.signal_ids` already link everything.

## Design

### Frontend

- `StoryForm` keeps the `investigationId` after the first submit.
- New `AddEvidenceForm` component under the result:
  "Add another message or detail" textarea → `api.addEvidence(id, content)` → `api.assess(id)`.
- New `EvidenceTrail` component:
  - One card per evidence item (story first), content shown redacted, `[REDACTED]` styled.
  - Under each card, the signals whose `evidence_id` matches, using the existing severity chips.
- In the assessment card, each reason shows a count / anchor link to the signals it cites.
- "Start a new check" button resets state.
- Keep the investigation ID in the URL (`?id=`), and load it with `api.getInvestigation` on
  refresh. The ID is a random hex; no PII.

### Backend

No changes.

## Tasks

- [ ] Lift investigation state so both forms share it
- [ ] `AddEvidenceForm` with busy/error states (reuse `ApiError` rendering)
- [ ] `EvidenceTrail` component grouping signals by `evidence_id`
- [ ] Link reasons → signals
- [ ] `?id=` URL persistence + reload via `getInvestigation`
- [ ] "Start a new check" reset

## Safety & privacy

- Repeat "Do not type any OTP, PIN, password or card number" above the add-evidence box.
- Show the existing redaction notice whenever any evidence item has `redacted: true`.

## Tests

- `make test` (lint + typecheck).
- Manual: story with no signals → add "pay ₹2000 to withdraw" → level changes from
  NEEDS VERIFICATION to show the WITHDRAWAL_FEE signal linked to the second item.
- Extend `tests/smoke.sh`: add evidence to an investigation and re-assess.

## Acceptance criteria

- User can add ≥ 2 extra evidence items and the assessment refreshes each time.
- Every displayed signal shows the evidence item it came from.
- Refreshing the page with `?id=` restores the investigation.

## Out of scope

Adaptive questions (F06), file/image upload (F13).

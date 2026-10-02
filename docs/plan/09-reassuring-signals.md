# F09: Reassuring signals

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Low–Medium | 3 | F08 | backend engine, frontend |

## Goal

Show balanced evidence: what looks *right* as well as what looks wrong.
`SignalKind.REASSURING` already exists in the model but nothing produces it.

## Decision (ADR-011)

Reassuring signals are **displayed but never change the level**. Only tier 1–2
verification can move toward LOW CONCERN (ADR-006). Reason: positive wording in a
message is easy for a scammer to fake.

## Signals

All signals are derived from verification records or structured facts, never from
flattering wording alone.

| Code | Source | Trigger |
|---|---|---|
| `REGISTRATION_VERIFIED` | VERIFIED_SOURCE | F08 VERIFIED record, tier 1 |
| `NO_UPFRONT_PAYMENT` | RULE | Facts show no money requested, after ≥ 1 answered question about payment |
| `REALISTIC_RETURN_CLAIM` | RULE | Return claim present and below the unrealistic thresholds, with no "guaranteed" wording |
| `OFFICIAL_CHANNEL_PAYMENT` | RULE | Payment recipient matches the verified entity name (requires F08) |

## Design

- `engine/reassuring.py` → `list[Signal]` with `kind=REASSURING`, `severity=LOW`.
- `assess()` already ignores non-WARNING signals for the level; add a test that pins this.
- UI: green "What looks right" list, shown after warnings, with the caveat
  "These don't make an offer safe on their own."

## Tasks

- [ ] `engine/reassuring.py` + wiring
- [ ] Test: reassuring signals never change the level
- [ ] UI section
- [ ] ADR-011; update `SAFETY.md` signals tables

## Acceptance criteria

- `registered_advisor` shows `REGISTRATION_VERIFIED`.
- Adding reassuring signals to any F03 scenario leaves its level unchanged.

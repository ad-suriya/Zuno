# F03: Demo scenarios

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Low | 1 | — | frontend, backend tests |

## Goal

One-click realistic stories that show the full range of outcomes, and the same
stories used as regression tests so the demo can't silently break.

## Scenarios

| ID | Story (short) | Expected today | Expected after F08 |
|---|---|---|---|
| `otp_kyc` | "Caller from 'SEBI KYC' says account will be frozen, asks for the OTP sent to me" | HIGH (CRITICAL) | HIGH |
| `telegram_tips` | "Telegram group, sure-shot tips, guaranteed 20% monthly, pay ₹25,000 today only" | HIGH (2× HIGH) | HIGH |
| `withdraw_fee` | "Trading app shows profit ₹1.2L, must pay 10% tax before withdrawal" | NEEDS VERIFICATION | NEEDS VERIFICATION / HIGH |
| `mlm` | "Friend's network: ₹5,000 joining fee, earn by adding members, sells health products" | NEEDS VERIFICATION (never HIGH) | NEEDS VERIFICATION |
| `registered_advisor` | "Advisor gave SEBI reg no INA000XXXXXX, no guaranteed returns, fee by invoice" | NEEDS VERIFICATION | LOW CONCERN (if number verifies) |
| `fake_reg_number` | Same as above but the number belongs to a different entity | NEEDS VERIFICATION | HIGH (CONTRADICTED) |
| `tamil_story` | Tamil version of `telegram_tips` | HIGH | HIGH |

Use a real registration number from the SEBI snapshot (F08) for `registered_advisor`
once the snapshot exists.

## Design

- `tests/scenarios/scenarios.json`: `{id, language, channel, story, follow_ups[], expected_level}`.
- Backend test `test_scenarios.py` runs each through the in-memory service and asserts
  `expected_level`. This test protects the MLM ≠ fraud and NOT VERIFIED ≠ FRAUD rules.
- Frontend: "Try an example" chips above the textarea fill story + channel + language.
  The frontend imports the same JSON (copy at build or a small `src/lib/scenarios.ts`;
  keep one source of truth).

## Tasks

- [ ] Write scenarios JSON (realistic wording, Indian context, ₹ amounts)
- [ ] `test_scenarios.py`
- [ ] Example chips in `StoryForm`
- [ ] Tamil scenario reviewed by a native speaker

## Acceptance criteria

- `make test` runs all scenarios.
- Demo presenter can reach each outcome level in one click.
- `mlm` never returns HIGH CONCERN.

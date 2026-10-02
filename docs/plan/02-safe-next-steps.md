# F02: Safe next steps

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Low | 1 | — | backend engine, models, frontend |

## Goal

Every result ends with concrete, safe actions ("Know before you act"). The steps
are chosen deterministically from the level and the signals, never by the LLM.

## Design

### Backend

New `backend/app/engine/next_steps.py`:

```python
def next_steps(assessment: Assessment, signals: list[Signal]) -> list[str]:
    """Return ordered step codes, e.g. ["DO_NOT_PAY_YET", "CHECK_SEBI_REGISTER"]."""
```

Steps are **codes**, not text, so the frontend (F10) and voice (F11) can localize them.

| Trigger | Step code | English text (frontend) |
|---|---|---|
| any CRITICAL signal | `NEVER_SHARE_CREDENTIALS` | Never share an OTP, PIN or password with anyone, including people claiming to be from a bank or SEBI. |
| OTP/PIN/credential signal | `IF_SHARED_CALL_BANK` | If you already shared one, call your bank now and block the card/UPI. |
| REMOTE_ACCESS_REQUEST | `UNINSTALL_REMOTE_APP` | Uninstall the screen-sharing app and do not reinstall it on request. |
| APK_INSTALL | `DO_NOT_INSTALL_APK` | Do not install apps from links. Use only the Play Store / App Store. |
| HIGH or NEEDS VERIFICATION | `DO_NOT_PAY_YET` | Do not send money until the checks below are done. |
| HIGH or NEEDS VERIFICATION | `CHECK_SEBI_REGISTER` | Ask for the SEBI registration number and check it on sebi.gov.in. |
| RECRUITMENT_DEPENDENCE / ENTRY_FEE | `ASK_WHAT_IS_SOLD` | Ask what product is sold and whether the fee is refundable, in writing. |
| URGENCY_PRESSURE | `TAKE_YOUR_TIME` | A genuine offer will still be there tomorrow. Talk to someone you trust. |
| always | `REPORT_IF_LOST` | If you lost money, report at cybercrime.gov.in or call 1930. |

- Add `next_steps: list[str]` to `Assessment` in `models.py` (stored with the assessment).
- Compute it in `InvestigationService.run_assessment` after `assess()`.

### Frontend

- `types.ts`: add `next_steps: string[]` to `Assessment`.
- `NextSteps` component under the assessment card; a `STEP_TEXT` map keyed by code
  (becomes the i18n dictionary in F10). An unknown code is not rendered.

## Tasks

- [ ] `engine/next_steps.py` + model field
- [ ] Wire into `run_assessment`
- [ ] Sync `types.ts`
- [ ] `NextSteps` component + text map
- [ ] Update `docs/ARCHITECTURE.md` module table

## Safety

- No step may recommend buying, selling, or a specific product/broker.
- Steps must not imply "this is a scam"; they describe checks and protections.

## Tests

`backend/tests/test_next_steps.py`:
- OTP story → includes `NEVER_SHARE_CREDENTIALS` and `IF_SHARED_CALL_BANK`, first in order.
- No signals → includes `CHECK_SEBI_REGISTER`, `REPORT_IF_LOST`.
- Order is stable; no duplicates.

## Acceptance criteria

- Every assessed investigation shows 2–6 next steps.
- A CRITICAL signal always puts credential steps first.

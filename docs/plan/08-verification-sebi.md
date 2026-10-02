# F08: SEBI verification

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| High | 3 | F05 | backend engine, data, scripts, frontend |

## Goal

Check the claims that matter (registration number, entity name) against an
official Tier-1 source and write `VerificationRecord`s. This is the only way
an investigation can reach **LOW CONCERN** or **CONTRADICTED**, and the main
"trusted-source verification" claim in the pitch.

## Design

### Data source (ADR-010)

- SEBI publishes lists of registered intermediaries (investment advisers, research analysts,
  stock brokers, portfolio managers, and others) on sebi.gov.in.
- Use a **dated offline snapshot**, not live scraping during a request:
  `scripts/refresh_sebi.py` downloads the relevant category lists and normalizes them to
  `backend/data/sebi_registry.csv` (`reg_no, name, category, valid_till, snapshot_date`).
- Start with **Investment Advisers + Research Analysts + Stock Brokers** (the categories most
  impersonated in tip/advisory scams).
- Check SEBI's terms of use; keep the source URL and snapshot date in every record.

### Verifier (`engine/verification.py`, deterministic)

Input: `Facts` (registration numbers, entity names, registration claims).

| Situation | Status | Tier | Material |
|---|---|---|---|
| Reg no found, name matches the claimed entity | VERIFIED | 1 | yes |
| Reg no found, **name clearly different** | CONTRADICTED | 1 | yes |
| Reg no found but registration expired (`valid_till` passed) | CONTRADICTED | 1 | yes |
| Reg no well-formed, **not in snapshot** | NOT_VERIFIED | 1 | yes |
| Reg no malformed | NOT_VERIFIED (explain format) | 4 | yes |
| User says "SEBI registered" but gives no number | UNKNOWN → F06 asks for the number | — | yes |
| Name only, fuzzy match ≥ threshold | VERIFIED *(entity exists)* | 1 | yes |
| Offer type is MLM / product selling | NOT_APPLICABLE for SEBI | — | no |

Key rules:
- **Not found ≠ fraud.** The snapshot can be stale, so "not found" is NOT_VERIFIED. It can never
  be CONTRADICTED on its own (ADR-006 then keeps it at NEEDS VERIFICATION).
- A VERIFIED entity never cancels a CRITICAL signal (impersonation is common). This is
  already enforced in `assess()`.
- Explanation always notes: "This confirms the entity is registered; it does not confirm the
  person contacting you represents it. Contact them only via details listed on SEBI's site."
- Name matching: normalize (case, punctuation, "Pvt Ltd" / "Private Limited"), token-set
  similarity; threshold tuned on test cases; ambiguous → NOT_VERIFIED, not VERIFIED.

### Flow

After extraction in `_ingest`: `verify(facts, existing_verifications)` → new records
(skip claims already checked) → `repo.add_verification`. Records are written server-side
only (ADR-007). Optionally derive a `VERIFIED_SOURCE` signal for CONTRADICTED results.

### Frontend

"What we checked" section: claim → source (SEBI register, snapshot date) → status chip →
explanation. Use different wording for NOT_VERIFIED ("We couldn't find this. That doesn't mean
it's fake.") and CONTRADICTED.

## Tasks

- [ ] Confirm SEBI list URLs, formats, and reg-no patterns per category
- [ ] `scripts/refresh_sebi.py` + committed snapshot CSV (small) with a date
- [ ] Registry loader (in-memory index by reg no + normalized name)
- [ ] `engine/verification.py` with the status table above
- [ ] Service wiring after extraction
- [ ] "What we checked" UI
- [ ] ADR-010; update `VERIFICATION.md`, `ARCHITECTURE.md`
- [ ] Update F03 `registered_advisor` / `fake_reg_number` scenarios with real snapshot data

## Stretch

- RBI NBFC list (loan / deposit offers).
- SEBI's lists of unregistered or debarred entities, as a CONTRADICTED source.
- Check whether a URL domain matches the registered entity's website (tier 2).

## Tests

- Each row of the status table has a test.
- Stale snapshot: well-formed unknown number → NOT_VERIFIED, level stays NEEDS VERIFICATION.
- Verified + OTP request → still HIGH CONCERN.
- `registered_advisor` with no warnings → LOW CONCERN.

## Acceptance criteria

- LOW CONCERN and CONTRADICTED → HIGH CONCERN are reachable in the demo.
- Every verification record stores claim, source, tier, status, evidence, explanation,
  timestamp (`VERIFICATION.md`).
- No verification depends on the LLM.

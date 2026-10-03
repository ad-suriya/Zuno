# Verification

## Source priority

| Tier | Source |
|---|---|
| 1 | Official regulator/government sources |
| 2 | Official company/entity sources |
| 3 | Reputable secondary sources |
| 4 | User-provided claims |

## Important distinction

NOT VERIFIED != FRAUD

CONTRADICTED is stronger than NOT VERIFIED.

## Verification states

- VERIFIED
- NOT_VERIFIED
- CONTRADICTED
- UNKNOWN
- NOT_APPLICABLE

## Verification record

Every verification should store:

- claim
- source
- timestamp
- result
- evidence
- explanation

## Implementation (F08, ADR-010)

Source: SEBI's public lists of registered intermediaries (Investment Advisers, Research Analysts,
Stock Brokers), saved as a dated snapshot in `backend/data/sebi_registry.csv` by
`scripts/refresh_sebi.py` (`make refresh-sebi`). Each row keeps the snapshot date and source URL.

| Situation | Status | Tier | Code |
|---|---|---|---|
| Number found, name matches the company named | VERIFIED | 1 | `REG_NAME_MATCH` |
| Number found, clearly different company | CONTRADICTED | 1 | `REG_NAME_MISMATCH` |
| Number found, registration expired | CONTRADICTED | 1 | `REG_EXPIRED` |
| Number found, name similar but unclear | NOT_VERIFIED | 1 | `REG_NAME_UNCLEAR` |
| Number found, no company name yet (Zuno asks for it) | UNKNOWN | 1 | `REG_NO_NAME` |
| Well-formed number not in snapshot | NOT_VERIFIED | 1 | `REG_NOT_FOUND` |
| Category not in the snapshot (e.g. INP) | NOT_VERIFIED | 1 | `REG_CATEGORY_NOT_COVERED` |
| Malformed number | NOT_VERIFIED | 4 | `REG_MALFORMED` |
| "SEBI registered" claimed, no number | UNKNOWN | 4 | `REGISTRATION_CLAIM_NO_NUMBER` |
| Company name found (no number given) | VERIFIED | 1 | `NAME_FOUND` |
| Company name not found, investment-type offer | NOT_VERIFIED | 1 | `NAME_NOT_FOUND` |
| MLM / job / loan offer | NOT_APPLICABLE (not material) | — | `SEBI_NOT_APPLICABLE` |

Names are normalised (case, punctuation, "Pvt Ltd" / "Private Limited", honorifics) and compared by
token-set similarity; generic words like "Capital" or "Wealth" alone never match.
A verified entity only proves the entity exists, not that the person contacting the user represents it.
Records carry `code` + `params` so clients can show them in the user's language.

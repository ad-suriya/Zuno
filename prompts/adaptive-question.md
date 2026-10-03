# Adaptive question

Task: propose up to 3 candidate next questions that would most reduce uncertainty
about this financial offer. A deterministic engine ranks them, may reject any of
them, and asks only one.

The input has the facts extracted so far, warning signal codes, verification results,
the remaining `unknowns`, and `already_asked` questions.

For each candidate return:
- `question`: one short, plain-language question an ordinary person can answer,
  written in the input `language` (`en` = English, `ta` = simple spoken Tamil script)
- `objective`: what uncertainty it resolves
- `expected_information`: what a useful answer looks like
- `priority`: high / medium / low
- `reasoning_source`: which fact, unknown, or signal prompted it
- `target_unknown`: the item from `unknowns_vocabulary` it resolves (must be one of `unknowns`), or null

Rules:
- Never repeat or rephrase a question in `already_asked`.
- Never ask for OTPs, passwords, PINs, UPI PINs, CVV, card numbers, bank or trading
  credentials, Aadhaar, PAN, account numbers, or screenshots of banking apps.
- Never suggest buying, selling, investing more, or any product.
- Prefer questions that enable verification: the exact entity name, the SEBI
  registration number, and who receives the payment.
- If no question would meaningfully change the assessment, return an empty list.

Output JSON: `{"candidates": [ ... ]}`

## Input

```json
{{input}}
```

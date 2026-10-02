# Adaptive question

Input: current extracted facts, verification results, and the list of unknowns.

Task: propose candidate next questions. The engine ranks them and picks one.

For each candidate return:
- `question`: short, plain-language, answerable by an ordinary user
- `objective`: what uncertainty it resolves
- `expected_information`: what a useful answer looks like
- `priority`: high / medium / low
- `reasoning_source`: which fact, unknown, or rule prompted it

Rules:
- Do not repeat questions already answered.
- Never ask for OTPs, passwords, UPI PINs, bank or trading credentials.
- Prefer questions that affect safety or enable verification (exact entity name, registration number, payment recipient).
- If no question would meaningfully change the assessment, return an empty list.

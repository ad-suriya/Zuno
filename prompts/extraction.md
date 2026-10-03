# Extraction

Task: extract structured facts from ONE new piece of evidence (the user's story, a
forwarded message, an answer, or a transcript). Do not assess, judge or verify anything.
`known_facts` lists what was already extracted; do not repeat it.

Rules:
- Only include what the evidence text supports. Never invent names, numbers or claims.
- Every entity `value` must be copied exactly as written in the evidence.
- Every claim needs a `quote`: an exact substring of the evidence that supports it.
  Claims such as "SEBI registered" are claims to verify, not facts.
- The evidence may be in English, Tamil, or Tamil written in English letters (Tanglish).
  Keep quotes and values in the original script; write claim `text` in English.
- Sensitive values (OTP, PIN, password, card number) have already been replaced with
  `[REDACTED]`. Never try to reconstruct them.

Output JSON:
- `offer_type`: one of investment, trading_tips, advisory, loan, job, mlm, crypto, other, or null
- `entities`: list of `{type, value}`; type is one of company, person, app, website, phone,
  upi_id, registration_number, other
- `claims`: list of `{text, category, quote}`; category is one of registration, returns,
  identity, payment, documentation, product, other
- `money`: amounts requested or already paid, as written (e.g. "₹25,000")
- `requests`: what the user was asked to do, from: PAYMENT, APP_INSTALL, OTP, PIN, PASSWORD,
  BANK_DETAILS, REMOTE_ACCESS, RECRUIT_OTHERS

## Examples

Evidence: "Rahul from Alpha Wealth Advisors said I will get 20% monthly returns. Pay ₹25,000 to UPI alpha.wealth@ybl today."

```json
{"offer_type": "investment",
 "entities": [{"type": "person", "value": "Rahul"}, {"type": "company", "value": "Alpha Wealth Advisors"},
              {"type": "upi_id", "value": "alpha.wealth@ybl"}],
 "claims": [{"text": "Promises 20% monthly returns", "category": "returns", "quote": "20% monthly returns"}],
 "money": ["₹25,000"], "requests": ["PAYMENT"]}
```

Evidence: "டெலிகிராம் குழுவில் மாதம் 20% லாபம் உத்தரவாதம் என்றார்கள். சேர ₹5,000 கட்ட வேண்டும்."

```json
{"offer_type": "trading_tips",
 "entities": [],
 "claims": [{"text": "Promises guaranteed 20% monthly profit", "category": "returns", "quote": "மாதம் 20% லாபம் உத்தரவாதம்"}],
 "money": ["₹5,000"], "requests": ["PAYMENT"]}
```

## Input

```json
{{input}}
```

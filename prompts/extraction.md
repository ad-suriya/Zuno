# Extraction

Input: the user's story (text or transcript) and any evidence collected so far.

Task: extract structured facts. Do not assess or judge.

Return JSON with:
- `channel`: how the offer reached the user (whatsapp, telegram, call, social, email, in_person, referral, other, unknown)
- `offer_type`: e.g. investment, trading tip, loan, job, MLM, crypto, other
- `entities`: named companies, people, apps, websites, phone numbers, UPI IDs, registration numbers
- `claims`: each claim made to the user, quoted or paraphrased, e.g. "20% monthly return", "SEBI registered"
- `money`: amounts requested or already paid, and to whom
- `requests`: anything asked of the user (payment, app install, OTP, PIN, remote access, recruiting others)
- `unknowns`: important facts not yet stated

Only include what the input supports. Use `null` or empty lists when absent.

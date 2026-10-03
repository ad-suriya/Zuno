# Privacy

Draft — refine as the data model is built.

## Principles

- Collect only what the investigation needs.
- Never collect OTPs, passwords, UPI PINs, bank or trading credentials.
- Never request SMS inbox access.

## Evidence handling

- Audio recordings and screenshots are **not stored** anywhere (ADR-012). They are processed in
  memory, turned into redacted text, and discarded. Only text the user reviews and confirms is saved.
- Investigations and everything under them carry `expires_at` (7 days); a Firestore TTL policy
  deletes them after that.
- If a user shares credentials or PINs by mistake, they are redacted before storage, logging, or any
  LLM call: typed codes ("OTP 482913"), spaced codes ("4 8 2 9 1 3"), spoken codes in English or
  Tamil ("four eight two nine…", "நான்கு எட்டு…"), passwords and card numbers.
- Only redacted text is sent to Gemini (ADR-008) or returned from voice/screenshot endpoints.

## Logging

- Do not log raw audio, full transcripts, or personal identifiers to Cloud Logging.
- LLM prompts and responses are never logged; only the prompt name, latency and outcome.
- Log investigation IDs and events, not content.

## Secrets

- API keys live in Secret Manager, never in the repo.

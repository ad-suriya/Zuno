# Privacy

Draft — refine as the data model is built.

## Principles

- Collect only what the investigation needs.
- Never collect OTPs, passwords, UPI PINs, bank or trading credentials.
- Never request SMS inbox access.

## Evidence handling

- Uploaded evidence (screenshots, audio, documents) is stored in Cloud Storage as temporary data.
- Temporary evidence should have a defined retention period and be deleted after it.
- If a user shares credentials or PINs by mistake, redact them before storage and logging.

## Logging

- Do not log raw audio, full transcripts, or personal identifiers to Cloud Logging.
- Log investigation IDs and events, not content.

## Secrets

- API keys live in Secret Manager, never in the repo.

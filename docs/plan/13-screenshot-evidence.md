# F13: Screenshot evidence (stretch)

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| High | Stretch | F04 | backend endpoint, LLM vision, frontend upload |

## Goal

Most offers arrive as WhatsApp/Telegram messages. Let the user upload a
screenshot instead of retyping it; the text becomes normal evidence.

## Design

- `POST /api/v1/investigations/{id}/evidence/image`: multipart, PNG/JPEG, ≤ 5 MB, 1 image per call.
- Gemini multimodal (via F04 client) with a new `prompts/image-text.md`: "Transcribe the visible
  message text. Do not interpret." The output is text only.
- Text → `redact()` → `_ingest` as `EvidenceKind.IMAGE_TEXT`. Everything downstream
  (rules, extraction, questions) is unchanged.
- **The image is not stored** (ADR-012). It's processed in memory and discarded. This avoids
  storing screenshots that may contain OTPs, account numbers, or other people's data, and
  means Cloud Storage isn't needed for the MVP.
- If the image appears to show a banking app, OTP SMS or card, show the user a warning to
  remove/crop it (`detect_hard_signals` on the transcribed text).

## Tasks

- [ ] Endpoint + size/type validation
- [ ] Prompt + vision call via F04 client (fallback: "couldn't read the image, please type it")
- [ ] `EvidenceKind.IMAGE_TEXT` + `types.ts`
- [ ] Upload button + "Is this the text?" confirm step in the UI
- [ ] `PRIVACY.md` update

## Tests

- Mocked vision output containing "OTP 482913" → stored as `[REDACTED]`, OTP signal fires.
- Non-image upload → 415; oversized → 413.

## Acceptance criteria

- A WhatsApp screenshot from the F03 Telegram scenario gives the same assessment as the typed text.
- No image bytes are persisted anywhere.

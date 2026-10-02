# F11: Voice (Sarvam)

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| High | 4 | F06, F10 | backend proxy endpoints, frontend audio, config/secrets |

## Goal

Voice-first: the user speaks their story and answers in Tamil or English, and
hears Zuno's questions and explanation (ADR-001).

## Design

### Backend proxy (the key never reaches the browser)

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/v1/speech/transcribe` | multipart audio (≤ 60 s, ≤ 5 MB), `language` | `{transcript}` (**redacted**) |
| POST | `/api/v1/speech/synthesize` | `{text, language}` | audio bytes |

- `backend/app/voice/sarvam.py`: thin `httpx` client for Sarvam STT and TTS. Confirm the
  current model names, language codes (`ta-IN`, `en-IN`) and limits in Sarvam's docs at build time.
- `SARVAM_API_KEY` from env (Secret Manager on Cloud Run; already in `.env.example`).
- Transcripts go through `redact()` **before** being returned. The user then confirms/edits
  the transcript and submits it as text, so the existing ingest path is unchanged.
- Audio is processed in memory and never written to Firestore/GCS or logged (ADR-012).
- Synthesize only server-generated text (questions, explanation, next steps), never arbitrary
  input. This prevents the endpoint becoming an open TTS proxy.
- Rate limit per IP (simple in-memory token bucket) to protect the API key quota.

### Dependencies

- `python-multipart` (FastAPI needs it for `UploadFile`).
- `httpx` (already used by TestClient; promote it to a runtime dependency).

### Frontend

- Mic button on story and answer inputs: `MediaRecorder` → upload → transcript fills the
  textarea for review ("Is this what you said?").
- 🔊 button on each Zuno question and on the explanation; auto-play the next question after
  an answer, with a toggle.
- Graceful fallback: no mic permission / unsupported browser / Sarvam error → keep typing;
  show a short message.

## Tasks

- [ ] Verify Sarvam API contract (STT, TTS, languages, max duration) with a spike script
- [ ] `voice/sarvam.py` + config + secret wiring
- [ ] Two endpoints + size/duration limits + rate limit
- [ ] Redaction on transcripts
- [ ] Mic recorder component + transcript confirm step
- [ ] Playback component
- [ ] ADR-012; `ARCHITECTURE.md`, `PRIVACY.md` (audio retention = none)

## Safety & privacy

- A spoken OTP ("my OTP is four five six…") may be transcribed as words: extend `redact()` to
  handle digit words in English/Tamil, or at minimum flag them. Add tests.
- Never log transcripts or audio.

## Tests

- Sarvam client mocked: transcribe → redacted transcript; error → 503 `VOICE_UNAVAILABLE`.
- Oversized audio → 413.
- Synthesize rejects text not produced by the server (e.g. requires a question id / investigation id).

## Acceptance criteria

- Tamil spoken story → correct transcript → same assessment as the typed version.
- Questions play aloud in the investigation's language.
- With Sarvam down, the app still works by typing.

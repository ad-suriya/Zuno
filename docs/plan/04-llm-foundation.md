# F04: LLM foundation (Gemini / Vertex AI)

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Medium | 2 | — | backend, prompts, config, Dockerfile |

## Goal

One small, testable LLM layer that every AI feature (F05, F06, F07, F13) uses:
loads prompts from `prompts/`, always prepends the safety preamble, returns
validated structured output, and fails safe.

## Design

### Module layout

```
backend/app/llm/
  __init__.py
  prompts.py     # load prompts/*.md, cache, prepend prompts/safety.md
  client.py      # LLMClient protocol + GeminiClient + FakeClient
backend/app/ai/  # feature code that uses the client (F05 extraction, F06 questions, F07 explanation)
```

```python
class LLMClient(Protocol):
    def generate_json(self, prompt_name: str, payload: dict, schema: type[M]) -> M | None: ...
```

- `GeminiClient` uses Vertex AI in `GOOGLE_CLOUD_REGION` with model `GEMINI_MODEL`,
  JSON response mode with a response schema built from the Pydantic model.
- Returns `None` (never raises to the caller) on timeout, quota, safety block, or
  schema-validation failure; logs `llm_failed` with prompt name + reason only.
- `FakeClient` returns canned responses keyed by prompt name; used in tests and when
  `LLM_ENABLED=false`.
- Timeout ~10 s per call; one retry on transient errors.

### Config (`config.py`, `.env.example`)

| Var | Default | Notes |
|---|---|---|
| `LLM_ENABLED` | `false` locally | If false, every feature uses its deterministic fallback |
| `GEMINI_MODEL` | (set per env) | Pick the current fast Gemini model on Vertex AI at build time |
| `GOOGLE_CLOUD_REGION` | `asia-south1` | Check that the model is available in this region; else use a nearby one |

Auth: Application Default Credentials (`gcloud auth application-default login` locally;
the Cloud Run service account in prod). No API key in the repo.

### Dependency

Add `google-genai` (official Google Gen AI SDK, supports Vertex AI). Reason: the only
supported client for Gemini on Vertex; no other LLM libraries (no LangChain).

### Prompt loading & packaging

- Prompts live at repo-root `prompts/`. The backend Docker build context is `backend/`,
  so **the image currently can't see them.** Fix: build from the repo root
  (`docker build -f backend/Dockerfile .`) and `COPY prompts ./prompts`, and read the
  path from `PROMPTS_DIR` (default: repo-root relative).
- Each prompt file gets a fenced `Input`/`Output` section the loader fills with the
  JSON payload. Keep the markdown human-readable.

### Wiring

- `api/deps.py`: `get_llm()` (lru_cache) → `GeminiClient` or `FakeClient` from settings.
- `InvestigationService(repo, llm)`.

## Tasks

- [ ] `llm/prompts.py` with safety preamble always prepended
- [ ] `llm/client.py`: protocol, Gemini, Fake
- [ ] Settings + `.env.example` + `requirements.txt`
- [ ] Dockerfile / build-context fix for `prompts/`
- [ ] Inject into service via `deps.py`
- [ ] ADR-008 in `docs/DECISIONS.md`; update `ARCHITECTURE.md`, README ("prompts not used yet")

## Safety & privacy

- Only **redacted** text is ever sent (callers pass `Evidence.content`, which is stored redacted).
- Never log prompts or responses; log prompt name, latency, success/failure.
- LLM output is data to validate, not instructions to follow.

## Tests

- `test_llm_prompts.py`: every prompt loads; safety preamble is present in every rendered prompt.
- `test_llm_client.py`: invalid JSON / schema mismatch → `None`; timeout → `None`.
- One opt-in live test (`@pytest.mark.live`, skipped by default) that calls Gemini.

## Acceptance criteria

- With `LLM_ENABLED=false`, all existing tests pass unchanged.
- With credentials set, the live test returns a validated object in < 10 s.
- Backend image builds and contains `prompts/`.

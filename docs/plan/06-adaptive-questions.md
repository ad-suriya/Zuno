# F06: Adaptive questions (core differentiator)

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Medium–High | 2 | F05 (has a no-LLM fallback) | backend engine + API, prompts, frontend |

## Goal

After the story, Zuno asks **the single most useful next question**, takes the
answer as new evidence, re-runs rules, and repeats until it has enough or the
user finishes. This is "investigate, don't blindly classify" (`docs/ADAPTIVE_ENGINE.md`).

## Design

### Split of responsibility (ADR-009)

- **LLM proposes** candidate questions (`prompts/adaptive-question.md`).
- **Deterministic ranker selects** one, and can veto any candidate.
- **Template fallback**: if the LLM is off or returns nothing, pick from fixed
  templates keyed by `Facts.unknowns`, e.g.
  `REGISTRATION_NUMBER` → "Did they give you a SEBI registration number? If yes, please type it."

### Model

```python
class Question(BaseModel):
    id: str
    text: str
    objective: str               # which unknown it resolves
    target_unknown: str | None   # from the F05 vocabulary
    priority: Literal["high", "medium", "low"]
    reasoning_source: str
    source: Literal["llm", "template"]
    status: Literal["asked", "answered", "skipped"]
    answer_evidence_id: str | None
    asked_at: datetime
```

Firestore: `investigations/{id}/questions/{question_id}`.
`InvestigationDetail` gains `questions: list[Question]` and `next_question: Question | None`.

### Ranker (`engine/question_ranker.py`, deterministic)

1. **Veto:** drop any candidate where `detect_hard_signals(text)` fires (no question can
   mention OTP/PIN/password/credentials) or matches an advice pattern (buy/sell/invest more).
2. **Dedupe:** drop candidates targeting an unknown that's already answered or asked.
3. **Score:** safety relevance (unknowns that unlock verification first:
   `REGISTRATION_NUMBER`, `ENTITY_NAME`, `PAYMENT_RECIPIENT`) > information gain >
   answerability (short questions preferred) > priority.
4. Tie-break by fixed unknown order, so the result is deterministic and testable.

### Stop conditions

Return `next_question = null` when any holds:
- a CRITICAL signal exists (show HIGH + safety steps immediately; don't keep questioning),
- no unknowns remain that affect verification,
- 5 questions asked,
- the user pressed "Finish",
- the last 2 answers produced no new facts or signals (assessment stable).

### API

| Method | Path | Purpose |
|---|---|---|
| POST | `/investigations/{id}/questions/next` | Compute + store the next question (or null) |
| POST | `/investigations/{id}/questions/{qid}/answer` | `{content}` → ingested as evidence kind `answer`, question marked answered |
| POST | `/investigations/{id}/questions/{qid}/skip` | User doesn't know / won't answer |

Answers go through the same `_ingest` (redact → rules → extraction). Add
`EvidenceKind.ANSWER`.

### Frontend

Chat-style `Investigation` view replacing the single form after submit:
story bubble → Zuno question → answer box ("I don't know" / "Skip" / "Finish") →
live assessment card on the side (desktop) or below (mobile). F01's
evidence trail shows answers as evidence items.

## Tasks

- [ ] `Question` model, repo methods (memory + Firestore), `types.ts`
- [ ] Template bank for every unknown (EN; TA in F10)
- [ ] `engine/question_ranker.py` with veto/dedupe/score
- [ ] `ai/questions.py`: LLM candidates → ranker; fallback to templates
- [ ] Stop conditions
- [ ] 3 endpoints + service methods
- [ ] Chat UI with skip/finish
- [ ] Update `prompts/adaptive-question.md` (pass unknowns vocabulary + asked questions)
- [ ] ADR-009; `ADAPTIVE_ENGINE.md` + `ARCHITECTURE.md` updates

## Safety

- The veto runs on **every** question shown, including templates, so a template edit
  can't introduce a credential request.
- Questions never ask for ID documents, Aadhaar, PAN, account numbers or screenshots of
  banking apps.

## Tests

- Ranker: candidate containing "OTP" is vetoed; "share your UPI PIN" vetoed.
- Ranker is deterministic for identical input.
- Story with a CRITICAL signal → `next_question` is null.
- Telegram scenario → first question targets `ENTITY_NAME` or `REGISTRATION_NUMBER`.
- After 5 questions → null.
- LLM disabled → template questions still flow end-to-end.

## Acceptance criteria

- Example from `ADAPTIVE_ENGINE.md` ("Telegram, 20% monthly, ₹25,000") yields
  "What is the exact company or organization name?" (or the registration-number question) first.
- No question ever repeats within one investigation.
- Full flow works with `LLM_ENABLED=false`.

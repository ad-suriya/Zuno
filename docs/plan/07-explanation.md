# F07: Explanation layer

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Medium | 2 | F04, F02 | backend, prompts/explanation.md, frontend |

## Goal

A short, calm, plain-language explanation of the **rules-decided** result in the
user's language, suitable for reading aloud (F11). The LLM explains; it never
decides.

## Design

### Model

```python
class Explanation(BaseModel):
    language: Language
    text: str
    source: Literal["llm", "template"]
    generated_at: datetime
```

Store on `Assessment.explanation`.

### Flow

`run_assessment` → `assess()` → `next_steps()` → `explain(assessment, signals, verifications, facts, language)`.

### Output guard (deterministic)

Reject the LLM text and use the template if any of these hold:
- It names a different level than `assessment.level` (check for the other two labels in EN/TA).
- It contains banned phrases: "definitely a scam", "100% fraud", "buy", "sell", "invest in",
  "guaranteed safe", or asks for OTP/PIN/password (`detect_hard_signals`).
- It's longer than ~120 words (it needs to work as voice output).

### Template fallback

Built from `AssessmentReason.explanation` + top 3 signals + first 2 next steps. This is
what the UI shows today, made into sentences.

### Frontend

The explanation paragraph sits at the top of the assessment card. The reasons and signals
stay below it as the "show your work" trail.

## Tasks

- [ ] `Explanation` model + `types.ts`
- [ ] `ai/explanation.py` + output guard + template fallback
- [ ] Update `prompts/explanation.md` (input JSON shape, word limit, language)
- [ ] Render in `AssessmentResult`

## Tests

- FakeClient returns text saying "low concern" for a HIGH assessment → template used.
- Text containing "definitely a scam" → template used.
- LLM disabled → template text, correct language.

## Acceptance criteria

- The explanation never contradicts the displayed level.
- Every claim in the explanation traces to a reason, signal or verification
  (manual review on F03 scenarios).

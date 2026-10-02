# F10: Tamil localization

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Medium | 4 (UI strings can start in Phase 1) | F01, F02 | frontend, backend rules, prompts |

## Goal

A Tamil-speaking user can complete the whole flow in Tamil: UI, questions,
signals, next steps, and explanation. The architecture should make adding a
third language a data change, not a code change.

## Current state

- `Language` enum supports `en` / `ta`; the dropdown exists.
- All UI and rule explanation text is English.
- Some Tamil keywords exist in safety and red-flag regexes (OTP, password, PIN, guaranteed,
  double, urgency).

## Design

### Frontend strings

- `frontend/src/lib/i18n.ts`: `messages: Record<Language, Record<Key, string>>` and a `t(key)` hook.
  No i18n library needed at this size (no new dependency).
- Keys cover UI labels, level labels/summaries, **signal codes**, **reason rules**,
  **next-step codes** (F02), verification status wording (F08).
- Signal and reason explanations are rendered from codes on the frontend, so the backend
  keeps English `explanation` fields for logs/API consumers.
- The UI language follows the investigation `language`, with a toggle in the header.

### Backend

- Question templates (F06) and explanation templates (F07) keyed by language.
- LLM prompts receive `language` and must answer in it; F07's output guard checks the
  Tamil level labels too.
- Rules: add Tamil and **Tanglish** (Tamil in Latin script) variants for each red-flag rule,
  e.g. "double aagum", "guarantee return", "kandippa profit", "inniku mattum".
  Tamil script: no `\b` (see the note in `safety.py`).

### Review

All Tamil copy reviewed by a native speaker on the team. Plain register, not formal/literary.

## Tasks

- [ ] `i18n.ts` + English dictionary extracted from current components
- [ ] Tamil dictionary (UI, levels, signals, reasons, steps)
- [ ] Header language toggle
- [ ] Tamil + Tanglish regex variants with tests per rule
- [ ] Tamil question/explanation templates
- [ ] Native-speaker review pass
- [ ] `docs/` note on how to add a language

## Tests

- Every key exists in both dictionaries (unit test / typecheck via `satisfies`).
- `test_red_flags.py`: Tamil and Tanglish cases for each rule; no false positives on a
  neutral Tamil sentence.

## Acceptance criteria

- `tamil_story` (F03) goes end-to-end with no English shown except brand names.
- Adding a language needs only dictionary + templates + regex variants.

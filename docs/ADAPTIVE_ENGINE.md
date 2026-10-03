# Adaptive Evidence Engine

## Goal

Ask the single most useful next question.

## Example

Known:
- Telegram
- investment opportunity
- 20% monthly return
- guaranteed
- ₹25,000 requested

Unknown:
- entity
- registration
- payment recipient
- documentation

Next question:

"What is the exact company or organization name?"

## Question selection factors

1. Safety relevance
2. Information gain
3. User answerability
4. Evidence already available
5. Redundancy

## Stop conditions

Stop asking questions when:
- enough evidence exists
- assessment is stable
- remaining uncertainty cannot reasonably be resolved
- user chooses to finish

## Never

Do not ask for:
- passwords
- OTPs
- UPI PIN
- bank credentials
- trading credentials

## Implementation (F06, ADR-009)

- Unknowns come from a fixed vocabulary (`ENTITY_NAME`, `REGISTRATION_NUMBER`, `PAYMENT_RECIPIENT`,
  `AMOUNT`, `RETURN_CLAIM`, `CONTACT_CHANNEL`, `DOCUMENTATION`, `PRODUCT_SOLD`), computed in code from
  the extracted facts.
- Candidates: the LLM proposes up to 3 (`prompts/adaptive-question.md`); a template exists for every
  unknown in every language (`backend/app/i18n.py`), so the loop works with the LLM off.
- The ranker (`engine/question_ranker.py`) vetoes unsafe candidates, removes asked/resolved unknowns,
  and scores: unknowns that unlock verification first, boosted by context (e.g. a "SEBI registered"
  claim makes the registration number most valuable; MLM signals make "what is sold" valuable).
- Answers are ingested as evidence, so they go through redaction, rules, extraction and verification.
  An answer to the name question becomes a company entity that is checked against SEBI.
- Stop: critical signal, 5 questions, user pressed Finish, the last 2 answers added nothing, or no
  useful question remains.

# F05: Claim & entity extraction

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Medium | 2 | F04 | backend, prompts/extraction.md, models, frontend (display) |

## Goal

Turn free-form stories into structured facts (entities, claims, money, requests,
unknowns). These facts drive adaptive questions (F06) and verification (F08).
Extraction **does not judge**: it never creates signals or changes the level.

## Design

### Model (`models.py`)

```python
class Entity(BaseModel):
    type: Literal["company", "person", "app", "website", "phone", "upi_id", "registration_number", "other"]
    value: str
    evidence_id: str

class Claim(BaseModel):
    text: str            # e.g. "SEBI registered", "20% monthly return"
    category: Literal["registration", "returns", "identity", "payment", "other"]
    evidence_id: str
    quote: str | None    # exact substring of the evidence, if any

class Facts(BaseModel):
    offer_type: str | None
    entities: list[Entity] = []
    claims: list[Claim] = []
    money: list[str] = []
    requests: list[str] = []
    unknowns: list[str] = []   # from a fixed vocabulary, see below
    updated_at: datetime
```

`unknowns` uses a fixed vocabulary so F06 can reason deterministically:
`ENTITY_NAME`, `REGISTRATION_NUMBER`, `PAYMENT_RECIPIENT`, `AMOUNT`, `RETURN_CLAIM`,
`CONTACT_CHANNEL`, `DOCUMENTATION`, `PRODUCT_SOLD`.

Store `facts` on the investigation document (one doc, merged after each evidence item;
Firestore-friendly, ADR-005). Add `facts: Facts | None` to `InvestigationDetail`.

### Flow (`service._ingest`)

```
redact → store evidence → rules → signals → extract(evidence, previous facts) → merge → save facts
```

- Merge: union by (type, value); claims de-duplicated by normalized text.
- **Grounding check (deterministic):** drop any entity whose `value` doesn't appear in the
  redacted evidence text (case/space-insensitive), and any claim whose `quote` isn't a
  substring. This stops invented entities.
- **Deterministic pre-extraction** (works without LLM): regex for SEBI registration
  numbers (`IN[AHZ]\d{9}`-style prefixes; confirm the formats against SEBI), UPI IDs
  (`name@bank`), Indian phone numbers, URLs, ₹ amounts. Regex results are always merged in.
- `unknowns` = fixed vocabulary minus what is present (computed in code, not trusted from LLM).

### Prompt

Update `prompts/extraction.md` to the schema above; include 2 few-shot examples
(one English, one Tamil).

### Frontend

"What we understood" panel: entities and claims as chips, so the user can spot mistakes.

## Tasks

- [ ] Models + `types.ts`
- [ ] `engine/patterns.py` deterministic extractors + tests
- [ ] `ai/extraction.py`: LLM call + grounding check + merge
- [ ] Service wiring; fallback = regex only
- [ ] Firestore: store/merge `facts`
- [ ] Prompt update with few-shots
- [ ] "What we understood" panel
- [ ] `ARCHITECTURE.md` (Firestore layout, flow)

## Safety

- Claims like "SEBI registered" are recorded as **claims to verify**, never as facts.
- Extraction output never creates `Signal`s and never feeds `assess()` directly.

## Tests

- Regex extractors: registration number, UPI, phone, ₹ amounts, URL.
- Grounding: FakeClient returns an entity not present in text → dropped.
- LLM disabled → regex facts still present; unknowns computed.

## Acceptance criteria

- For the F03 scenarios, the entity name, registration number (if any), amount and
  return claim are extracted correctly in English and Tamil.
- No extracted entity is absent from the evidence text.

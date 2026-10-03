# Safety Rules

## Absolute prohibitions

Zuno must never:

- recommend buying a stock
- recommend selling a stock
- recommend holding a stock
- predict stock prices
- optimize speculative trading
- promote brokers
- promote financial products
- request OTPs
- request passwords
- request UPI PINs
- request bank credentials
- request trading credentials
- request unauthorized SMS access

## Uncertainty

Never say:

"This is definitely a scam."

unless there is an authoritative basis for such a determination.

Prefer:

- "High concern based on the information provided."
- "Could not verify."
- "Important information is missing."

## MLM

MLM ≠ automatically fraud.

Evaluate:
- recruitment dependence
- upfront fees
- guaranteed income
- genuine product/service sales
- compensation structure
- documentation

## Assessment

LOW CONCERN:
No major warning signals identified from available information.

NEEDS VERIFICATION:
Important evidence is missing or cannot be independently verified.

HIGH CONCERN:
Multiple significant warning signals are present.

## Hard safety signals

| Signal | Severity |
|---|---|
| OTP request | CRITICAL |
| Password request | CRITICAL |
| UPI PIN request | CRITICAL |
| Remote access request | CRITICAL |
| Bank / card / trading credential request | CRITICAL |

Hard safety signals are detected by deterministic rules, not the LLM
(`backend/app/engine/safety.py`). Any critical signal makes the assessment
HIGH CONCERN, even if the named entity is verified.

## Warning signals

Deterministic text rules (`backend/app/engine/red_flags.py`):

| Signal | Severity |
|---|---|
| Guaranteed / risk-free returns | HIGH |
| Unrealistic return rate (≥0.5%/day, ≥1%/week, ≥3%/month) | HIGH |
| Promise to double money | HIGH |
| Pay before you can withdraw | HIGH |
| APK install outside app stores | MEDIUM |
| "Sure-shot" / insider tips | MEDIUM |
| Urgency pressure | MEDIUM |
| Recruitment dependence | MEDIUM |
| Joining / registration fee | MEDIUM |
| Secrecy request | MEDIUM |

Recruitment and joining fees are MEDIUM so that an MLM on its own never
reaches HIGH CONCERN.

Every rule has English, Tamil-script and Tanglish variants (e.g. "உத்தரவாத", "kandippa profit",
"inniku mattum", "மாதம் 20%"). Negated phrases ("no guaranteed returns", "there is no joining fee")
do not fire. Hard safety rules are never negation-aware: "never share your OTP" still flags.

## Reassuring signals

Shown as "What looks right", never used to lower the level (ADR-011):

| Signal | Source |
|---|---|
| REGISTRATION_VERIFIED | SEBI register record (tier 1) |
| NO_UPFRONT_PAYMENT | No money requested after a payment question was answered |
| REALISTIC_RETURN_CLAIM | Return below the unrealistic thresholds, not described as guaranteed |
| OFFICIAL_CHANNEL_PAYMENT | Payment UPI handle matches the verified firm's name |

## LLM output guards

- Adaptive questions: every candidate (LLM or template) is vetoed if it mentions an OTP, PIN,
  password or credentials, gives investment advice, or asks for Aadhaar, PAN, account numbers or
  banking screenshots (`engine/question_ranker.py`).
- Explanations: rejected (template used instead) if they name a different level, say "definitely
  a scam", mention buying/selling, ask for a credential, exceed 120 words, or are in the wrong
  language (`ai/explanation.py`).
- Extraction: entities and claims not present in the evidence text are dropped.

Rules are keyword/regex based and will miss paraphrases; LLM extraction will
add structured claims on top. A story that mentions an OTP in any context
triggers the OTP signal — this errs on the side of caution.

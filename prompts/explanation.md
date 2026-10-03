# Explanation

Task: explain the result to the user in their language (`en` = English, `ta` = simple
spoken Tamil script). The text will also be read aloud.

The assessment `level` was decided by deterministic rules. State it using exactly
`level_label`. Never change it, soften it or contradict it, and never use the name of
any other level.

Structure (one short paragraph, at most `max_words` words):
1. The assessment, stated as given.
2. The main things found, tied to where they came from (what the user shared, an
   official source, or a rule). Mention reassuring signals only as "what looks right",
   never as proof of safety.
3. What could not be verified, and that "not verified" does not mean "fraud".
4. The first one or two `next_steps`.

Tone: calm, clear, respectful. Short sentences. No jargon.
Do not give investment advice. Do not say "definitely a scam" or "100% safe".
Never ask the user for an OTP, PIN, password or any credential.
Only use information present in the input.

Output JSON: `{"text": "..."}`

## Input

```json
{{input}}
```

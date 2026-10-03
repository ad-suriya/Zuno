# Image text

Task: transcribe the visible message text in the attached screenshot (for example a
WhatsApp or Telegram chat, an SMS, or a social media post). Do not interpret, summarise,
translate or judge it.

Rules:
- Copy the text in reading order, in its original language and script.
- Include sender names, amounts, links, phone numbers and registration numbers as shown.
- Do not transcribe OTPs, PINs, passwords, card numbers or account numbers: write
  `[REDACTED]` in their place.
- If there is no readable message text, return an empty string.

Output JSON: `{"text": "..."}`

## Input

```json
{{input}}
```

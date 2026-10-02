# Zuno Design System — MASTER

Source of truth for how Zuno looks and behaves. Page-specific deviations go in
`design-system/pages/<page>.md` and override this file for that page only.

## 1. Design intent

Zuno is used by someone who has just received a message or call about money and is
unsure. They may be on a low-end Android phone, on a slow connection, reading in Tamil,
and new to financial vocabulary.

The UI must feel like a **calm, careful investigator**, not an alarm system and not a
trading app.

| We are | We are not |
|---|---|
| Calm, plain, patient | Alarming, flashing, red-everywhere |
| Explainable (show *why*) | A score, a gauge, a verdict stamp |
| Evidence-first | Chat-bubble novelty |
| Trustworthy like a public-service form | Flashy like a fintech/crypto app |

Style: **Accessible flat with soft surfaces**. Flat colour, 1px borders, very light
shadows on cards only, 10–12px radius. No gradients, glassmorphism, neon, or dark-by-default.

## 2. Colour tokens

Base palette is Tailwind `stone` (warm neutral, already in use). One accent (deep
sea-blue) for links, focus and secondary actions. Assessment colours are reserved: never
use them for decoration.

### Light (default)

| Token | Value | Use | Contrast |
|---|---|---|---|
| `--bg` | `#fafaf9` stone-50 | Page background | — |
| `--surface` | `#ffffff` | Cards, inputs | — |
| `--surface-muted` | `#f5f5f4` stone-100 | Evidence quotes, secondary panels | — |
| `--fg` | `#1c1917` stone-900 | Body text, headings | 16.7:1 on bg |
| `--fg-muted` | `#57534e` stone-600 | Helper text, meta | 7.3:1 on bg |
| `--border` | `#e7e5e4` stone-200 | Dividers, card outlines (decorative) | — |
| `--border-strong` | `#78716c` stone-500 | Input borders, controls | ≥3:1 on bg |
| `--primary` | `#1c1917` stone-900 | Primary button bg | — |
| `--on-primary` | `#ffffff` | Primary button text | 17.5:1 |
| `--accent` | `#0f5f8a` | Links, focus ring, secondary buttons | 6.7:1 on bg |
| `--on-accent` | `#ffffff` | Text on accent | 6.9:1 |

### Assessment & severity (light)

| Level | Background | Border / icon | Text | Text contrast |
|---|---|---|---|---|
| LOW CONCERN | `#ecfdf5` | `#047857` | `#065f46` | 7.3:1 |
| NEEDS VERIFICATION | `#fffbeb` | `#b45309` | `#78350f` | 8.8:1 |
| HIGH CONCERN | `#fef2f2` | `#b91c1c` | `#7f1d1d` | 9.2:1 |
| CRITICAL signal chip | `#b91c1c` solid | — | `#ffffff` | 6.5:1 |

Severity chips (HIGH / MEDIUM / LOW signals) reuse the same three families: HIGH → red,
MEDIUM → amber, LOW → stone (neutral, not green: a low-severity *warning* is still a warning).

### Dark (`prefers-color-scheme: dark`)

| Token | Value | Contrast |
|---|---|---|
| `--bg` | `#1c1917` | — |
| `--surface` | `#292524` | — |
| `--surface-muted` | `#211e1c` | — |
| `--fg` | `#f5f5f4` | 16.0:1 |
| `--fg-muted` | `#a8a29e` | 6.9:1 |
| `--border` | `#44403c` | — |
| `--border-strong` | `#78716c` | 3.7:1 |
| `--primary` / `--on-primary` | `#f5f5f4` / `#1c1917` | — |
| `--accent` | `#7dd3fc` | 10.5:1 |
| LOW | bg `#052e22`, text `#6ee7b7` | 9.7:1 |
| VERIFY | bg `#3a2508`, text `#fcd34d` | 10.1:1 |
| HIGH | bg `#3b0d0d`, text `#fca5a5` | 8.9:1 |

### Tailwind v4 implementation (`src/app/globals.css`)

```css
@import "tailwindcss";

:root {
  --bg: #fafaf9; --surface: #ffffff; --surface-muted: #f5f5f4;
  --fg: #1c1917; --fg-muted: #57534e;
  --border: #e7e5e4; --border-strong: #78716c;
  --primary: #1c1917; --on-primary: #ffffff;
  --accent: #0f5f8a; --on-accent: #ffffff;
  --low-bg: #ecfdf5; --low-line: #047857; --low-fg: #065f46;
  --verify-bg: #fffbeb; --verify-line: #b45309; --verify-fg: #78350f;
  --high-bg: #fef2f2; --high-line: #b91c1c; --high-fg: #7f1d1d;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1c1917; --surface: #292524; --surface-muted: #211e1c;
    --fg: #f5f5f4; --fg-muted: #a8a29e;
    --border: #44403c; --border-strong: #78716c;
    --primary: #f5f5f4; --on-primary: #1c1917;
    --accent: #7dd3fc; --on-accent: #1c1917;
    --low-bg: #052e22; --low-line: #34d399; --low-fg: #6ee7b7;
    --verify-bg: #3a2508; --verify-line: #f59e0b; --verify-fg: #fcd34d;
    --high-bg: #3b0d0d; --high-line: #f87171; --high-fg: #fca5a5;
  }
}

@theme inline {
  --font-sans: var(--font-noto-sans), var(--font-noto-sans-tamil), system-ui, sans-serif;
  --color-bg: var(--bg); --color-surface: var(--surface); --color-surface-muted: var(--surface-muted);
  --color-fg: var(--fg); --color-fg-muted: var(--fg-muted);
  --color-border: var(--border); --color-border-strong: var(--border-strong);
  --color-primary: var(--primary); --color-on-primary: var(--on-primary);
  --color-accent: var(--accent); --color-on-accent: var(--on-accent);
  --color-low-bg: var(--low-bg); --color-low-line: var(--low-line); --color-low-fg: var(--low-fg);
  --color-verify-bg: var(--verify-bg); --color-verify-line: var(--verify-line); --color-verify-fg: var(--verify-fg);
  --color-high-bg: var(--high-bg); --color-high-line: var(--high-line); --color-high-fg: var(--high-fg);
}

body { background: var(--bg); color: var(--fg); font-family: var(--font-sans); }
```

Components use semantic classes (`bg-surface`, `text-fg-muted`, `border-high-line`), not
raw `stone-*` / `red-*` / hex.

## 3. Typography

**Noto Sans + Noto Sans Tamil** (already loaded via `next/font` in `layout.tsx`). Chosen
because one family covers Latin, Tamil, and every other Indic script we may add
(Noto Sans Devanagari, Telugu, Kannada, …) with matched metrics. Do not introduce a
Latin-only display font (e.g. Lexend, Inter): Tamil text would fall back and the two
scripts would look mismatched side by side.

Display voice: the same Noto family at **width 75 (condensed), weight 800**, via the
`font-display` utility in `globals.css` (fonts load with `axes: ["wdth"]`). Used only for
the page headline, the assessment level and the wordmark. Condensed heavy type reads as a
stamp on a case file and fits longer Tamil strings in a phone-width line.
Utility face: **Noto Sans Mono**, only for check references and note numbers.

| Role | Size / line-height | Weight |
|---|---|---|
| Display (assessment level) | 36–48px / 1.05, `font-display`, uppercase (English only) | 800 |
| H1 page title | 48–72px / 1.05, `font-display` | 800 |
| H2 section | 18px / 1.4 | 600 |
| Body | 16px / 1.6 | 400 |
| Body (Tamil) | 16px / **1.75** | 400 |
| Label | 14px / 1.4 | 500 |
| Meta / helper | 14px / 1.5 | 400 |

Rules:
- Never below 14px; body never below 16px (iOS zoom, Tier-2/3 readability).
- Tamil line-height is taller: set `:lang(ta) { line-height: 1.75 }`. Tamil words are long;
  never `truncate` Tamil text, let it wrap. Budget ~30% more width than English for buttons.
- No ALL CAPS for Tamil; for English, assessment labels may be uppercase with `tracking-wide`.
- Max reading width `max-w-prose` (~65ch) for explanations.
- Use `tabular-nums` for money amounts and percentages (₹2,000, 3%/month).

## 4. Spacing, radius, elevation

- 4px base. Use Tailwind `1 2 3 4 6 8 12` (4–48px). Section gap 32px, card padding 16px
  (mobile) / 24px (≥640px).
- Radius: inputs/buttons `rounded-lg` (8px), cards `rounded-xl` (12px), chips `rounded-full`.
- Elevation: one level only — cards `shadow-sm` + `border`. No stacked shadows.
- Layout: single column, `max-w-2xl mx-auto px-4`. Zuno is a guided flow, not a dashboard;
  no sidebars or multi-column grids.

## 5. Components

### Assessment banner (most important component)

```
┌───────────────────────────────────────────┐
│ [icon]  NEEDS VERIFICATION                │  ← icon + text label, never colour alone
│         Important information is missing. │  ← one-line plain-language meaning
│                                           │
│ Why: • Return of 3%/month is unrealistic  │  ← reasons, each linked to its evidence
│      • Company not found on SEBI register │
└───────────────────────────────────────────┘
```

- 1.5px border all round in `*-line`, background `*-bg`, text `*-fg`, `rounded-2xl`. (Not a 4px left stripe: that reads as a template.)
- Icons (Phosphor, `regular` weight): LOW → `ShieldCheck`, VERIFY → `MagnifyingGlass`
  (it is a *to-do*, not a warning), HIGH → `WarningOctagon`.
- `role="status"` + `aria-live="polite"` so screen readers hear level changes when
  evidence is added.
- Wording comes from `SAFETY.md`. Never "Scam", "Fraud", "Safe", "Guaranteed safe",
  a percentage, or a score/gauge (ADR-004). LOW CONCERN is not "safe".
- HIGH CONCERN is serious but not hysterical: no pulsing, no full-screen red, no siren
  icons. Pair it immediately with the safe next steps.

### Annotated message (signature element)

The user's own text is shown back with each phrase that triggered a signal marked:
severity-tinted background, 2px underline in the severity line colour, and a superscript
note number. Notes below the text are numbered **in reading order**, each with a numbered
badge, severity icon + word, explanation, and "Show in message" back-link. Assessment
reasons cite note numbers (`[2]`). This is the explainable trail made visible; keep every
signal traceable to the words that caused it. Implemented in `AssessmentResult.tsx`.

### Signal chip

`[icon] Guaranteed returns · HIGH` — rounded-full, 14px label, severity colour family,
icon + text. Tappable when it links to evidence (≥44px tall hit area via padding).

### Evidence card

- `bg-surface border rounded-xl`. Quoted user text in `bg-surface-muted` with a 2px
  left rule, font unchanged (no monospace, no italics for Tamil).
- Highlight the phrase that triggered a signal with `<mark>` in the signal's `*-bg` +
  underline in `*-line` (works in greyscale).
- `[REDACTED]` renders as a stone-200 pill with a `LockSimple` icon and visible text
  "hidden for your safety".

### Buttons

| Variant | Style | Use |
|---|---|---|
| Primary | `bg-primary text-on-primary` | One per screen: "Check this offer", "Add evidence" |
| Secondary | `border border-border-strong bg-surface` | "Start a new check" |
| Link | `text-accent underline-offset-4 hover:underline` | Source links (SEBI, RBI) |

- Height ≥ 48px (`min-h-12 px-5`), full-width on mobile.
- Busy: disable + spinner + label change ("Checking…"); never a frozen button.
- Focus: `focus-visible:outline-2 outline-offset-2 outline-accent` on every control.

### Text inputs (story / evidence)

- Visible `<label>` above; helper text below; `min-h-32` textarea, 16px text.
- Safety notice sits **above** the field, always visible, with `ShieldWarning` icon:
  "Never type an OTP, PIN, password or card number." Not a placeholder, not a tooltip.
- Errors below the field, `text-high-fg` + icon, with a recovery action ("Try again").
- Mic button (Sarvam, F11): 48×48, `aria-label` in the current language, clear
  recording state (icon + "Listening…" text + stop button), not colour alone.

### Adaptive question (F06)

One question per card, never a long form. Show why it is asked ("This helps check
whether the company is registered"). Always offer "I don't know" as a first-class answer:
missing knowledge must not feel like failure.

### Safe next steps (F02)

Numbered list, each step a verb ("Search the company on the SEBI website"), official
links with `ArrowSquareOut` icon and domain shown (`sebi.gov.in`) so users learn to
recognise real domains. Helpline 1930 shown as a `tel:` link button.

## 6. Icons

Phosphor (`@phosphor-icons/react`), `regular` weight, 20px inline / 24px standalone.
No emoji as icons (including ✅ ⚠️ 🚩 in the UI; emoji in user-pasted evidence is shown as-is).
Add the dependency only when the first component needs it.

## 7. Motion

Subtle only. 150–200ms `ease-out` for state changes (banner colour change, card
appearance). New evidence card: fade + 8px rise, 200ms. No scroll-triggered animation,
no GSAP, no looping animation except the busy spinner. Wrap all in
`motion-safe:`; under reduced motion, changes are instant.

## 8. Language & content

- English and Tamil MVP; every user-facing string goes through the i18n layer (F10).
  Layout must survive Tamil strings ~1.3–1.6× longer.
- Set `lang` on `<html>` and on any mixed-language block (`<span lang="ta">`).
- Plain language, short sentences, second person. Explain terms on first use
  ("SEBI — the government body that registers investment advisers").
- Numbers: Indian grouping (`₹1,00,000`) via `Intl.NumberFormat('en-IN')`.

## 9. Accessibility checklist (blocking)

- [ ] Text ≥ 4.5:1, controls/borders ≥ 3:1, in light **and** dark
- [ ] Assessment level and severity always have icon + text, not colour alone
- [ ] Every input has a visible label; errors are announced (`role="alert"`)
- [ ] All interactive targets ≥ 44×44px, ≥ 8px apart
- [ ] Visible focus ring on every control; tab order = visual order
- [ ] Works at 360px width (common low-end Android) with no horizontal scroll
- [ ] Usable at 200% browser zoom
- [ ] `prefers-reduced-motion` respected
- [ ] Loading > 300ms shows progress; network errors show retry

## 10. Anti-patterns (do not ship)

- Risk meters, gauges, percentages, traffic-light-only dots, "scam score"
- The words "Scam", "Fraud", "Safe" as a verdict
- Red-dominant screens, shaking/pulsing alerts, alarm sounds
- Placeholder-only inputs; safety warning hidden in a tooltip
- Stock tickers, candlestick charts, green-up/red-down finance styling
- Any field that looks like it accepts an OTP, PIN or password
- Dark-by-default "crypto" aesthetic, gradients, glassmorphism
- Truncated Tamil text

"use client";

import { CircleNotchIcon, ShieldWarningIcon } from "@phosphor-icons/react/ssr";
import { useRef, useState } from "react";

import { ErrorNotice } from "@/components/ErrorNotice";
import { api, ApiError, toApiError } from "@/lib/api";
import { SCENARIOS, type Scenario } from "@/lib/scenarios";
import type { Channel, InvestigationDetail, Language } from "@/lib/types";

const CHANNELS: { value: Channel; label: string }[] = [
  { value: "whatsapp", label: "WhatsApp" },
  { value: "telegram", label: "Telegram" },
  { value: "call", label: "Phone call" },
  { value: "social", label: "Social media" },
  { value: "email", label: "Email" },
  { value: "referral", label: "Friend or relative" },
  { value: "in_person", label: "In person" },
  { value: "other", label: "Other" },
  { value: "unknown", label: "Not sure" },
];

const LANGUAGES: { value: Language; label: string; lang: string }[] = [
  { value: "en", label: "English", lang: "en" },
  { value: "ta", label: "தமிழ்", lang: "ta" },
];

// Visually a chip, semantically a radio: the input stays in the tab order and drives the style via `peer`.
const CHIP =
  "flex min-h-11 cursor-pointer items-center rounded-full border border-border-strong bg-surface px-4 text-sm " +
  "transition-colors duration-150 peer-checked:border-primary peer-checked:bg-primary peer-checked:text-on-primary " +
  "peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-accent hover:bg-surface-muted";

/** The start of a check: the user's story, how it reached them, and its language. */
export function StoryForm({ onCreated }: { onCreated: (detail: InvestigationDetail) => void }) {
  const [story, setStory] = useState("");
  const [channel, setChannel] = useState<Channel>("unknown");
  const [language, setLanguage] = useState<Language>("en");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const storyRef = useRef<HTMLTextAreaElement>(null);

  async function check() {
    setBusy(true);
    setError(null);
    try {
      const created = await api.createInvestigation({ story, channel, language });
      onCreated(await api.assess(created.investigation.id));
    } catch (err) {
      setError(toApiError(err));
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    check();
  }

  // F03: fill the form from a demo scenario; the user still presses "Check this offer".
  function fillExample(scenario: Scenario) {
    setStory(scenario.story);
    setChannel(scenario.channel);
    setLanguage(scenario.language);
    storyRef.current?.focus();
  }

  return (
    <div className="space-y-12">
      <div>
        <h1 className="font-display text-5xl text-balance sm:text-7xl">Check the offer before you pay.</h1>
        <p className="mt-4 max-w-prose text-lg text-fg-muted">
          Tell Zuno what you were offered. It marks the parts that need checking and explains why.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-8">
        <div>
          <label htmlFor="story" className="block text-lg font-semibold">
            What happened?
          </label>
          <p id="story-help" className="mt-1 text-fg-muted">
            In your own words: who contacted you, what they promised, and what they asked you to do. You can paste the
            message you received.
          </p>
          <p className="mt-4 flex gap-2 rounded-lg bg-surface-muted p-3 text-sm font-medium">
            <ShieldWarningIcon size={20} className="shrink-0 text-high-line" aria-hidden />
            Never type an OTP, PIN, password or card number. Zuno will never ask for them.
          </p>
          <textarea
            ref={storyRef}
            id="story"
            aria-describedby="story-help"
            value={story}
            onChange={(e) => setStory(e.target.value)}
            rows={6}
            maxLength={10_000}
            required
            lang={language}
            className="mt-3 block min-h-36 w-full rounded-lg border border-border-strong bg-surface p-3 text-base focus:border-accent"
            placeholder="A Telegram group admin said I will get guaranteed 20% monthly returns if I invest ₹25,000…"
          />
        </div>

        <fieldset>
          <legend className="text-lg font-semibold">How did the offer reach you?</legend>
          <div className="mt-3 flex flex-wrap gap-2">
            {CHANNELS.map((c) => (
              <label key={c.value}>
                <input
                  type="radio"
                  name="channel"
                  value={c.value}
                  checked={channel === c.value}
                  onChange={() => setChannel(c.value)}
                  className="peer sr-only"
                />
                <span className={CHIP}>{c.label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend className="text-lg font-semibold">Your message is in</legend>
          <div className="mt-3 flex flex-wrap gap-2">
            {LANGUAGES.map((l) => (
              <label key={l.value}>
                <input
                  type="radio"
                  name="language"
                  value={l.value}
                  checked={language === l.value}
                  onChange={() => setLanguage(l.value)}
                  className="peer sr-only"
                />
                <span lang={l.lang} className={CHIP}>
                  {l.label}
                </span>
              </label>
            ))}
          </div>
        </fieldset>

        <button
          type="submit"
          disabled={busy || !story.trim()}
          className="flex min-h-12 w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-primary px-6 font-semibold text-on-primary transition-opacity duration-150 hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
        >
          {busy && <CircleNotchIcon size={20} className="motion-safe:animate-spin" aria-hidden />}
          {busy ? "Checking…" : "Check this offer"}
        </button>
      </form>

      {error && <ErrorNotice error={error} onRetry={check} busy={busy} />}

      <section aria-labelledby="examples-heading" className="border-t border-dashed border-border-strong pt-6">
        <h2 id="examples-heading" className="font-semibold">
          No message to check? Try an example
        </h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {SCENARIOS.map((s) => (
            <button
              key={s.id}
              type="button"
              lang={s.language}
              onClick={() => fillExample(s)}
              className="min-h-11 cursor-pointer rounded-full bg-surface-muted px-4 text-sm transition-colors duration-150 hover:bg-border"
            >
              {s.label}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}

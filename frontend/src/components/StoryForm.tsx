"use client";

import { useState } from "react";

import { useI18n } from "@/components/I18nProvider";
import { VoiceInput } from "@/components/Voice";
import type { MessageKey } from "@/lib/i18n";
import { SCENARIOS } from "@/lib/scenarios";
import type { Channel, Language } from "@/lib/types";

const CHANNELS: Channel[] = ["unknown", "whatsapp", "telegram", "call", "social", "email", "referral", "in_person", "other"];

export function StoryForm({
  busy,
  onSubmit,
}: {
  busy: boolean;
  onSubmit: (story: string, channel: Channel, language: Language) => void;
}) {
  const { t, language, setLanguage } = useI18n();
  const [story, setStory] = useState("");
  const [channel, setChannel] = useState<Channel>("unknown");

  function applyExample(id: string) {
    const scenario = SCENARIOS.find((s) => s.id === id);
    if (!scenario) return;
    setStory(scenario.story);
    setChannel(scenario.channel);
    setLanguage(scenario.language);
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(story, channel, language);
      }}
      className="space-y-4"
    >
      <div>
        <p className="text-xs font-medium text-stone-600">{t("story.examples")}</p>
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {SCENARIOS.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => applyExample(s.id)}
              className="rounded-full border border-stone-300 bg-white px-3 py-1 text-xs text-stone-700 hover:border-stone-500 hover:text-stone-900"
            >
              {s.title[language]}
            </button>
          ))}
        </div>
      </div>

      <label className="block">
        <span className="text-sm font-medium text-stone-900">{t("story.label")}</span>
        <span className="block text-sm text-stone-600">{t("story.help")}</span>
        <textarea
          value={story}
          onChange={(e) => setStory(e.target.value)}
          rows={5}
          maxLength={10_000}
          required
          className="mt-2 w-full rounded-md border border-stone-300 bg-white p-3 text-base text-stone-900 focus:border-stone-900 focus:outline-none"
          placeholder={t("story.placeholder")}
        />
      </label>
      <VoiceInput language={language} disabled={busy} onTranscript={(text) => setStory((s) => (s ? `${s} ${text}` : text))} />

      <label className="block text-sm text-stone-900">
        {t("story.channel")}
        <select
          value={channel}
          onChange={(e) => setChannel(e.target.value as Channel)}
          className="mt-1 block rounded-md border border-stone-300 bg-white p-2"
        >
          {CHANNELS.map((c) => (
            <option key={c} value={c}>
              {t(`channel.${c}` as MessageKey)}
            </option>
          ))}
        </select>
      </label>

      <p className="text-sm text-stone-600">{t("safety.no_secrets")}</p>

      <button
        type="submit"
        disabled={busy || !story.trim()}
        className="rounded-md bg-stone-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-stone-700 disabled:cursor-not-allowed disabled:bg-stone-400"
      >
        {busy ? t("story.checking") : t("story.submit")}
      </button>
    </form>
  );
}

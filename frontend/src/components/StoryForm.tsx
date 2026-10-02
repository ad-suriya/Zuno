"use client";

import { useState } from "react";

import { AssessmentResult } from "@/components/AssessmentResult";
import { api, ApiError } from "@/lib/api";
import type { Channel, InvestigationDetail, Language } from "@/lib/types";

const CHANNELS: { value: Channel; label: string }[] = [
  { value: "unknown", label: "Not sure" },
  { value: "whatsapp", label: "WhatsApp" },
  { value: "telegram", label: "Telegram" },
  { value: "call", label: "Phone call" },
  { value: "social", label: "Social media" },
  { value: "email", label: "Email" },
  { value: "referral", label: "Friend or relative" },
  { value: "in_person", label: "In person" },
  { value: "other", label: "Other" },
];

export function StoryForm() {
  const [story, setStory] = useState("");
  const [channel, setChannel] = useState<Channel>("unknown");
  const [language, setLanguage] = useState<Language>("en");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [detail, setDetail] = useState<InvestigationDetail | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const created = await api.createInvestigation({ story, channel, language });
      setDetail(await api.assess(created.investigation.id));
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError("UNKNOWN", "Something went wrong.", null));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={onSubmit} className="space-y-4">
        <label className="block">
          <span className="text-sm font-medium text-stone-900">What happened?</span>
          <span className="block text-sm text-stone-600">
            Tell us about the offer in your own words: who contacted you, what they promised, and what they asked for.
          </span>
          <textarea
            value={story}
            onChange={(e) => setStory(e.target.value)}
            rows={5}
            maxLength={10_000}
            required
            className="mt-2 w-full rounded-md border border-stone-300 bg-white p-3 text-base text-stone-900 focus:border-stone-900 focus:outline-none"
            placeholder="A Telegram group admin said I will get guaranteed 20% monthly returns if I invest ₹25,000…"
          />
        </label>

        <div className="flex flex-wrap gap-4">
          <label className="text-sm text-stone-900">
            How were you approached?
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value as Channel)}
              className="mt-1 block rounded-md border border-stone-300 bg-white p-2"
            >
              {CHANNELS.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-stone-900">
            Language
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as Language)}
              className="mt-1 block rounded-md border border-stone-300 bg-white p-2"
            >
              <option value="en">English</option>
              <option value="ta">தமிழ் (Tamil)</option>
            </select>
          </label>
        </div>

        <p className="text-sm text-stone-600">Do not type any OTP, PIN, password or card number.</p>

        <button
          type="submit"
          disabled={busy || !story.trim()}
          className="rounded-md bg-stone-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-stone-700 disabled:cursor-not-allowed disabled:bg-stone-400"
        >
          {busy ? "Checking…" : "Check this offer"}
        </button>
      </form>

      {error && (
        <div role="alert" className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-900">
          <p>{error.message}</p>
          {error.requestId && <p className="mt-1 font-mono text-xs text-red-700">Reference: {error.requestId}</p>}
        </div>
      )}

      {detail && <AssessmentResult detail={detail} />}
    </div>
  );
}

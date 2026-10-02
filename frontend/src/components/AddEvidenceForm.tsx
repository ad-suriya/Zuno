"use client";

import { CircleNotchIcon, ShieldWarningIcon } from "@phosphor-icons/react/ssr";
import { useState } from "react";

import { ErrorNotice } from "@/components/ErrorNotice";
import { api, ApiError, toApiError } from "@/lib/api";
import type { InvestigationDetail, Language } from "@/lib/types";

/** F01: add another message or detail, then re-run the assessment. */
export function AddEvidenceForm({
  investigationId,
  language,
  onUpdated,
}: {
  investigationId: string;
  language: Language;
  onUpdated: (detail: InvestigationDetail) => void;
}) {
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  async function add() {
    setBusy(true);
    setError(null);
    try {
      await api.addEvidence(investigationId, content);
      onUpdated(await api.assess(investigationId));
      setContent("");
    } catch (err) {
      setError(toApiError(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="add-heading" className="rounded-xl border border-border bg-surface p-5 sm:p-6">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          add();
        }}
        className="space-y-3"
      >
        <label htmlFor="evidence" id="add-heading" className="block text-xl font-semibold">
          Add another message or detail
        </label>
        <p id="evidence-help" className="text-fg-muted">
          Paste a forwarded message, or write what the caller said. Zuno checks it and updates the result.
        </p>
        <p className="flex gap-2 rounded-lg bg-surface-muted p-3 text-sm font-medium">
          <ShieldWarningIcon size={20} className="shrink-0 text-high-line" aria-hidden />
          Never type an OTP, PIN, password or card number.
        </p>
        <textarea
          id="evidence"
          aria-describedby="evidence-help"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={4}
          maxLength={10_000}
          required
          lang={language}
          className="block min-h-28 w-full rounded-lg border border-border-strong bg-surface p-3 text-base focus:border-accent"
        />
        <button
          type="submit"
          disabled={busy || !content.trim()}
          className="flex min-h-12 w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-primary px-6 font-semibold text-on-primary transition-opacity duration-150 hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
        >
          {busy && <CircleNotchIcon size={20} className="motion-safe:animate-spin" aria-hidden />}
          {busy ? "Checking…" : "Add and check again"}
        </button>
      </form>
      {error && (
        <div className="mt-4">
          <ErrorNotice error={error} onRetry={add} busy={busy} />
        </div>
      )}
    </section>
  );
}

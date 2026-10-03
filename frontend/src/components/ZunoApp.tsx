"use client";

import { useCallback, useEffect, useState } from "react";

import { BackendStatus } from "@/components/BackendStatus";
import { ErrorNotice } from "@/components/ErrorNotice";
import { LanguageToggle, useI18n } from "@/components/I18nProvider";
import { type Actions, InvestigationView } from "@/components/InvestigationView";
import { StoryForm } from "@/components/StoryForm";
import { api } from "@/lib/api";
import type { Channel, InvestigationDetail, Language } from "@/lib/types";

// The investigation ID (random hex, no PII) is kept in the URL so a refresh restores it (F01).
function setUrlId(id: string | null) {
  const url = new URL(window.location.href);
  if (id) url.searchParams.set("id", id);
  else url.searchParams.delete("id");
  window.history.replaceState(null, "", url);
}

export function ZunoApp() {
  const { t, setLanguage } = useI18n();
  const [detail, setDetail] = useState<InvestigationDetail | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  const run = useCallback(async (work: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await work();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }, []);

  /** Re-assess, then ask for the next question. Each step updates the view as soon as it returns. */
  const refresh = useCallback(async (id: string) => {
    setDetail(await api.assess(id));
    setDetail(await api.nextQuestion(id));
  }, []);

  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get("id");
    if (!id) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    run(async () => {
      try {
        const loaded = await api.getInvestigation(id);
        setLanguage(loaded.investigation.language);
        setDetail(loaded);
      } catch (err) {
        setUrlId(null);
        throw err;
      }
    });
  }, [run, setLanguage]);

  const start = (story: string, channel: Channel, language: Language) =>
    run(async () => {
      const created = await api.createInvestigation({ story, channel, language });
      setDetail(created);
      setUrlId(created.investigation.id);
      await refresh(created.investigation.id);
    });

  const id = detail?.investigation.id ?? "";
  const actions: Actions = {
    answer: (question, content) =>
      run(async () => {
        setDetail(await api.answer(id, question.id, content));
        await refresh(id);
      }),
    skip: (question) =>
      run(async () => {
        setDetail(await api.skip(id, question.id));
        await refresh(id);
      }),
    finish: () =>
      run(async () => {
        await api.finish(id);
        setDetail(await api.assess(id));
      }),
    addEvidence: (content, kind) =>
      run(async () => {
        setDetail(await api.addEvidence(id, content, kind));
        await refresh(id);
      }),
  };

  function reset() {
    setDetail(null);
    setError(null);
    setUrlId(null);
  }

  return (
    <main className={`mx-auto w-full flex-1 px-4 py-10 sm:py-14 ${detail ? "max-w-6xl" : "max-w-2xl"}`}>
      <header className="mb-8 space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-3xl font-semibold tracking-tight text-stone-900">Zuno</h1>
          <div className="flex items-center gap-2">
            {detail && (
              <button
                type="button"
                onClick={reset}
                className="rounded-md border border-stone-300 bg-white px-3 py-1.5 text-sm text-stone-800 hover:bg-stone-100"
              >
                {t("inv.new")}
              </button>
            )}
            <LanguageToggle />
          </div>
        </div>
        <p className="text-stone-700">{t("app.tagline")}</p>
        <BackendStatus />
      </header>

      <div className="space-y-6">
        <ErrorNotice error={error} />
        {detail ? (
          <InvestigationView detail={detail} busy={busy} actions={actions} />
        ) : (
          <StoryForm busy={busy} onSubmit={start} />
        )}
      </div>

      <footer className="mt-12 border-t border-stone-200 pt-4 text-xs text-stone-500">{t("app.footer")}</footer>
    </main>
  );
}

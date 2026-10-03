"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { LANGUAGES, type MessageKey, translate } from "@/lib/i18n";
import type { Language } from "@/lib/types";

const STORAGE_KEY = "zuno.language";

interface I18n {
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: MessageKey, vars?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18n | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>("en");

  useEffect(() => {
    // Restore the last choice after hydration (the server always renders English first).
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      // eslint-disable-next-line react-hooks/set-state-in-effect
      if (saved === "en" || saved === "ta") setLanguageState(saved);
    } catch {
      // Storage can be unavailable (private mode); English is fine.
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const setLanguage = useCallback((next: Language) => {
    setLanguageState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // ignore
    }
  }, []);

  const value = useMemo<I18n>(
    () => ({ language, setLanguage, t: (key, vars) => translate(language, key, vars) }),
    [language, setLanguage],
  );
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18n {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used inside <I18nProvider>");
  return ctx;
}

export function LanguageToggle() {
  const { language, setLanguage, t } = useI18n();
  return (
    <div role="group" aria-label={t("lang.label")} className="inline-flex rounded-md border border-stone-300 bg-white p-0.5">
      {LANGUAGES.map((l) => (
        <button
          key={l.value}
          type="button"
          onClick={() => setLanguage(l.value)}
          aria-pressed={language === l.value}
          className={`rounded px-3 py-1 text-sm ${
            language === l.value ? "bg-stone-900 text-white" : "text-stone-700 hover:bg-stone-100"
          }`}
        >
          {l.label}
        </button>
      ))}
    </div>
  );
}

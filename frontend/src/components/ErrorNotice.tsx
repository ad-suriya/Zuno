"use client";

import { useCallback } from "react";

import { useI18n } from "@/components/I18nProvider";
import { ApiError } from "@/lib/api";
import { hasKey } from "@/lib/i18n";

/** Localized message for an API error code; falls back to the server's (English) message. */
export function useErrorText() {
  const { t, language } = useI18n();
  return useCallback(
    (err: unknown): string => {
      if (err instanceof ApiError) {
        const key = `error.${err.code}`;
        if (hasKey(key)) return t(key);
        return language === "en" ? err.message : t("error.generic");
      }
      return t("error.generic");
    },
    [t, language],
  );
}

export function ErrorNotice({ error }: { error: unknown }) {
  const { t } = useI18n();
  const text = useErrorText();
  if (!error) return null;
  const requestId = error instanceof ApiError ? error.requestId : null;
  return (
    <div role="alert" className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-900">
      <p>{text(error)}</p>
      {requestId && <p className="mt-1 font-mono text-xs text-red-700">{t("error.reference", { id: requestId })}</p>}
    </div>
  );
}

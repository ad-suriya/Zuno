"use client";

import { SEVERITY_ORDER, SeverityChip, useSignalText } from "@/components/AssessmentResult";
import { useI18n } from "@/components/I18nProvider";
import type { MessageKey } from "@/lib/i18n";
import type { InvestigationDetail } from "@/lib/types";

/** One card per evidence item (story first), with the warning signals each one triggered (F01). */
export function EvidenceTrail({ detail }: { detail: InvestigationDetail }) {
  const { t } = useI18n();
  const signalText = useSignalText();

  return (
    <section>
      <h2 className="text-sm font-semibold text-stone-900">{t("result.trail")}</h2>
      <ol className="mt-2 space-y-3">
        {detail.evidence.map((e) => {
          const signals = detail.signals
            .filter((s) => s.kind === "WARNING" && s.evidence_id === e.id)
            .sort((a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity));
          return (
            <li key={e.id} className="rounded-md border border-stone-200 bg-white p-3 text-sm">
              <p className="text-xs font-semibold uppercase tracking-wide text-stone-500">
                {t(`evidence.${e.kind}` as MessageKey)}
              </p>
              <p className="mt-1 whitespace-pre-wrap break-words text-stone-900">
                {e.content.split("[REDACTED]").map((part, i, parts) => (
                  <span key={i}>
                    {part}
                    {i < parts.length - 1 && (
                      <mark className="rounded bg-stone-800 px-1 font-mono text-xs text-white">[REDACTED]</mark>
                    )}
                  </span>
                ))}
              </p>
              {signals.length === 0 ? (
                <p className="mt-2 text-xs text-stone-500">{t("result.no_signals_here")}</p>
              ) : (
                <ul className="mt-2 space-y-1.5 border-t border-stone-100 pt-2">
                  {signals.map((s) => (
                    <li key={s.id} className="flex flex-wrap items-start gap-2 text-xs">
                      <SeverityChip severity={s.severity} />
                      {s.matched_text && <span className="font-mono text-stone-500">“{s.matched_text}”</span>}
                      <span className="text-stone-700">{signalText(s)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}

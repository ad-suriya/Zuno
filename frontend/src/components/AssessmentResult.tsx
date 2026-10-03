"use client";

import { useI18n } from "@/components/I18nProvider";
import { SpeakButton } from "@/components/Voice";
import { hasKey, type MessageKey } from "@/lib/i18n";
import type {
  AssessmentLevel,
  InvestigationDetail,
  Severity,
  Signal,
  SpeechTarget,
  VerificationRecord,
  VerificationStatus,
} from "@/lib/types";

const LEVEL_STYLE: Record<AssessmentLevel, string> = {
  LOW_CONCERN: "border-emerald-700 bg-emerald-50 text-emerald-900",
  NEEDS_VERIFICATION: "border-amber-600 bg-amber-50 text-amber-900",
  HIGH_CONCERN: "border-red-700 bg-red-50 text-red-900",
};
const STATUS_STYLE: Record<VerificationStatus, string> = {
  VERIFIED: "bg-emerald-100 text-emerald-800",
  NOT_VERIFIED: "bg-amber-100 text-amber-800",
  CONTRADICTED: "bg-red-100 text-red-800",
  UNKNOWN: "bg-stone-200 text-stone-800",
  NOT_APPLICABLE: "bg-stone-100 text-stone-600",
};
export const SEVERITY_ORDER: Severity[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export interface Speech {
  play: (target: SpeechTarget, questionId?: string) => void;
  playing: string | null;
  error: string | null;
}

/** Text for a signal from its code; falls back to the server's English explanation. */
export function useSignalText() {
  const { t, language } = useI18n();
  return (s: Signal) => {
    const key = `signal.${s.code}`;
    return hasKey(key) ? t(key) : language === "en" ? s.explanation : s.code;
  };
}

export function SeverityChip({ severity }: { severity: Severity }) {
  const { t } = useI18n();
  const style =
    severity === "CRITICAL" || severity === "HIGH" ? "bg-red-100 text-red-800" : "bg-amber-100 text-amber-800";
  return (
    <span className={`rounded px-1.5 py-0.5 text-xs font-semibold ${style}`}>
      {t(`severity.${severity}` as MessageKey)}
    </span>
  );
}

function verificationText(t: ReturnType<typeof useI18n>["t"], language: string, v: VerificationRecord) {
  const key = `vcode.${v.code}`;
  if (hasKey(key)) return t(key, v.params);
  return language === "en" ? v.explanation : v.claim;
}

export function AssessmentResult({ detail, speech }: { detail: InvestigationDetail; speech: Speech }) {
  const { t, language } = useI18n();
  const signalText = useSignalText();
  const assessment = detail.investigation.assessment;
  if (!assessment) return null;

  const warnings = detail.signals
    .filter((s) => s.kind === "WARNING")
    .sort((a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity));
  const reassuring = detail.signals.filter((s) => s.kind === "REASSURING");
  const checks = detail.verifications;
  const redacted = detail.evidence.some((e) => e.redacted);
  const level = assessment.level;
  const explanation = assessment.explanation;
  // The explanation was generated in the investigation's language; show it when the UI matches.
  const showExplanation = explanation && explanation.language === language;

  return (
    <section className="space-y-5" aria-live="polite">
      <div className={`rounded-lg border-l-4 p-4 ${LEVEL_STYLE[level]}`}>
        <p className="text-xs font-semibold uppercase tracking-wide">{t("result.assessment")}</p>
        <p className="mt-1 text-xl font-semibold">{t(`level.${level}` as MessageKey)}</p>
        <p className="mt-1 text-sm">{t(`level.${level}.summary` as MessageKey)}</p>

        {showExplanation && (
          <div className="mt-3 rounded-md bg-white/70 p-3 text-sm text-stone-900">
            <p>{explanation.text}</p>
            <div className="mt-2 flex flex-wrap items-center justify-between gap-2">
              {explanation.source === "llm" && <p className="text-xs text-stone-500">{t("result.ai_note")}</p>}
              <SpeakButton
                label={t("result.listen")}
                busy={speech.playing === "explanation:"}
                onClick={() => speech.play("explanation")}
              />
            </div>
          </div>
        )}

        <p className="mt-3 text-xs font-semibold uppercase tracking-wide">{t("result.why")}</p>
        <ul className="mt-1 list-disc space-y-1 pl-5 text-sm">
          {assessment.reasons.map((r) => {
            const key = `reason.${r.rule}`;
            return (
              <li key={r.rule}>
                {hasKey(key) ? t(key) : r.explanation}{" "}
                {r.signal_ids.length > 0 && (
                  <a href={`#signal-${r.signal_ids[0]}`} className="text-xs underline underline-offset-2">
                    {t("result.cites_signals", { count: r.signal_ids.length })}
                  </a>
                )}{" "}
                {r.verification_ids.length > 0 && (
                  <a href={`#check-${r.verification_ids[0]}`} className="text-xs underline underline-offset-2">
                    {t("result.cites_checks", { count: r.verification_ids.length })}
                  </a>
                )}
              </li>
            );
          })}
        </ul>
      </div>

      {speech.error && <p className="text-xs text-stone-600">{speech.error}</p>}

      {redacted && <p className="rounded-md bg-stone-100 p-3 text-sm text-stone-700">{t("result.redacted")}</p>}

      {assessment.next_steps.length > 0 && (
        <div className="rounded-lg border border-stone-200 bg-white p-4">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-sm font-semibold text-stone-900">{t("result.next_steps")}</h2>
            <SpeakButton
              label={t("result.listen")}
              busy={speech.playing === "next_steps:"}
              onClick={() => speech.play("next_steps")}
            />
          </div>
          <ol className="mt-2 list-decimal space-y-1.5 pl-5 text-sm text-stone-800">
            {assessment.next_steps
              .map((code) => `step.${code}`)
              .filter(hasKey)
              .map((key) => (
                <li key={key}>{t(key)}</li>
              ))}
          </ol>
        </div>
      )}

      {checks.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-stone-900">{t("result.checked")}</h2>
          <ul className="mt-2 space-y-2">
            {checks.map((v) => (
              <li key={v.id} id={`check-${v.id}`} className="rounded-md border border-stone-200 bg-white p-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`rounded px-1.5 py-0.5 text-xs font-semibold ${STATUS_STYLE[v.status]}`}>
                    {t(`vstatus.${v.status}` as MessageKey)}
                  </span>
                  {v.params.reg_no && <span className="font-mono text-xs text-stone-600">{v.params.reg_no}</span>}
                </div>
                <p className="mt-1 text-stone-800">{verificationText(t, language, v)}</p>
                <p className="mt-1 text-xs text-stone-500">
                  {t("result.source")}: {v.source}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h2 className="text-sm font-semibold text-stone-900">{t("result.warnings", { count: warnings.length })}</h2>
        {warnings.length === 0 ? (
          <p className="mt-2 text-sm text-stone-600">{t("result.no_warnings")}</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {warnings.map((s) => (
              <li key={s.id} id={`signal-${s.id}`} className="rounded-md border border-stone-200 bg-white p-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <SeverityChip severity={s.severity} />
                  {s.matched_text && <span className="font-mono text-xs text-stone-500">“{s.matched_text}”</span>}
                </div>
                <p className="mt-1 text-stone-800">{signalText(s)}</p>
              </li>
            ))}
          </ul>
        )}
      </div>

      {reassuring.length > 0 && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <h2 className="text-sm font-semibold text-emerald-900">{t("result.reassuring")}</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-emerald-900">
            {reassuring.map((s) => (
              <li key={s.id}>{signalText(s)}</li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-emerald-800">{t("result.reassuring_caveat")}</p>
        </div>
      )}

      <FactsPanel detail={detail} />
    </section>
  );
}

function FactsPanel({ detail }: { detail: InvestigationDetail }) {
  const { t } = useI18n();
  const facts = detail.facts;
  if (!facts || (facts.entities.length === 0 && facts.claims.length === 0 && facts.money.length === 0)) return null;
  return (
    <div>
      <h2 className="text-sm font-semibold text-stone-900">{t("result.understood")}</h2>
      <p className="text-xs text-stone-500">{t("result.understood_help")}</p>
      <ul className="mt-2 flex flex-wrap gap-1.5 text-xs">
        {facts.entities.map((e) => (
          <li key={`${e.type}:${e.value}`} className="rounded-full border border-stone-300 bg-white px-2.5 py-1">
            <span className="text-stone-500">{t(`entity.${e.type}` as MessageKey)}:</span>{" "}
            <span className="text-stone-900">{e.value}</span>
          </li>
        ))}
        {facts.claims.map((c) => (
          <li key={`${c.category}:${c.text}`} className="rounded-full border border-stone-300 bg-white px-2.5 py-1">
            <span className="text-stone-500">{t(`claim.${c.category}` as MessageKey)}:</span>{" "}
            <span className="text-stone-900">{c.quote ?? c.text}</span>
          </li>
        ))}
        {facts.money.map((m) => (
          <li key={`money:${m}`} className="rounded-full border border-stone-300 bg-white px-2.5 py-1">
            <span className="text-stone-500">{t("facts.money")}:</span> <span className="text-stone-900">{m}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

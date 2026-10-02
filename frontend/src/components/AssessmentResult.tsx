"use client";

import { AddEvidenceForm } from "@/components/AddEvidenceForm";
import { CaseFile } from "@/components/CaseFile";
import { WhatLooksRight, WhatZunoChecked } from "@/components/Checks";
import { NextSteps } from "@/components/NextSteps";
import { LEVEL, TONE } from "@/components/tone";
import { buildTrail, type Note } from "@/lib/trail";
import type { InvestigationDetail } from "@/lib/types";

export function AssessmentResult({
  detail,
  onUpdated,
  onReset,
}: {
  detail: InvestigationDetail;
  onUpdated: (detail: InvestigationDetail) => void;
  onReset: () => void;
}) {
  const { investigation } = detail;
  const assessment = investigation.assessment;
  const trail = buildTrail(detail);
  const noteFor = (signalId: string) => trail.notes.find((n) => n.signal.id === signalId);
  const redacted = detail.evidence.some((e) => e.redacted);
  const reassuring = detail.signals.filter((s) => s.kind === "REASSURING");
  const level = assessment ? LEVEL[assessment.level] : null;

  return (
    <div className="enter space-y-12">
      {assessment && level && (
        <section
          role="status"
          aria-live="polite"
          aria-labelledby="level-heading"
          className={`rounded-2xl border-[1.5px] p-5 sm:p-7 ${TONE[level.tone].panel}`}
        >
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <p className="text-sm font-semibold">Zuno&apos;s assessment</p>
            <p className="font-mono text-xs">Check {investigation.id.slice(0, 8)}</p>
          </div>
          <h2 id="level-heading" className="font-display mt-3 flex items-center gap-3 text-4xl uppercase sm:text-6xl">
            <level.icon size={44} weight="bold" className="shrink-0" aria-hidden />
            {level.label}
          </h2>
          <p className="mt-3 max-w-prose text-lg text-fg">{level.summary}</p>

          {assessment.reasons.length > 0 && (
            <div className="mt-5 border-t border-current/20 pt-4">
              <p className="text-sm font-bold">Why</p>
              <ul className="mt-2 space-y-2">
                {assessment.reasons.map((r) => {
                  const refs = r.signal_ids.map(noteFor).filter((n): n is Note => !!n);
                  return (
                    <li key={r.rule} className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                      <span>{r.explanation}</span>
                      {refs.map((ref) => (
                        <a
                          key={ref.n}
                          href={`#note-${ref.n}`}
                          aria-label={`See note ${ref.n}`}
                          className="-my-1 px-1 py-1 font-mono text-sm font-bold underline underline-offset-4"
                        >
                          [{ref.n}]
                        </a>
                      ))}
                      {r.verification_ids.map((id) => (
                        <a
                          key={id}
                          href={`#check-${id}`}
                          className="-my-1 px-1 py-1 font-mono text-sm font-bold underline underline-offset-4"
                        >
                          [checked]
                        </a>
                      ))}
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </section>
      )}

      {redacted && (
        <p className="-mt-6 rounded-xl bg-surface-muted p-4 text-sm">
          Zuno removed what looked like an OTP, PIN, password or card number before saving. Never share these with
          anyone.
        </p>
      )}

      {assessment && <NextSteps steps={assessment.next_steps} />}
      <WhatZunoChecked records={detail.verifications} />
      <WhatLooksRight signals={reassuring} />
      <CaseFile trail={trail} language={investigation.language} />
      <AddEvidenceForm investigationId={investigation.id} language={investigation.language} onUpdated={onUpdated} />

      <button
        type="button"
        onClick={onReset}
        className="flex min-h-12 w-full cursor-pointer items-center justify-center rounded-lg border border-border-strong bg-surface px-6 font-semibold transition-colors duration-150 hover:bg-surface-muted sm:w-auto"
      >
        Start a new check
      </button>
    </div>
  );
}

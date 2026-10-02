import { CheckCircleIcon, CheckIcon, InfoIcon, QuestionIcon, XIcon } from "@phosphor-icons/react/ssr";

import { TIER_TEXT, VERIFICATION_TEXT } from "@/lib/content";
import type { Signal, VerificationRecord, VerificationStatus } from "@/lib/types";

const STATUS_CHIP: Record<VerificationStatus, string> = {
  VERIFIED: "bg-low-line text-bg",
  CONTRADICTED: "bg-high-line text-bg",
  NOT_VERIFIED: "border-[1.5px] border-dashed border-fg-muted text-fg",
  UNKNOWN: "border-[1.5px] border-dashed border-fg-muted text-fg",
  NOT_APPLICABLE: "bg-surface-muted text-fg-muted",
};

const STATUS_ICON = {
  VERIFIED: CheckIcon,
  CONTRADICTED: XIcon,
  NOT_VERIFIED: QuestionIcon,
  UNKNOWN: QuestionIcon,
  NOT_APPLICABLE: InfoIcon,
} satisfies Record<VerificationStatus, unknown>;

const dateFormat = new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric" });

/** F08: each claim, what the official source says, and where that came from. */
export function WhatZunoChecked({ records }: { records: VerificationRecord[] }) {
  if (records.length === 0) return null;

  return (
    <section aria-labelledby="checked-heading">
      <h2 id="checked-heading" className="text-xl font-semibold">
        What Zuno checked
      </h2>
      <ul className="mt-4 space-y-3">
        {records.map((r) => {
          const text = VERIFICATION_TEXT[r.status];
          const Icon = STATUS_ICON[r.status];
          return (
            <li key={r.id} id={`check-${r.id}`} className="scroll-mt-24 space-y-2 rounded-xl border border-border bg-surface p-4">
              <p className="text-sm text-fg-muted">They said</p>
              <p className="font-semibold">{r.claim}</p>
              <span
                className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-sm font-bold ${STATUS_CHIP[r.status]}`}
              >
                <Icon size={16} weight="bold" aria-hidden />
                {text.label}
              </span>
              <p>{r.explanation}</p>
              {text.note && (
                <p className="flex gap-2 rounded-lg bg-surface-muted p-3 text-sm">
                  <InfoIcon size={18} className="mt-0.5 shrink-0 text-accent" aria-hidden />
                  {text.note}
                </p>
              )}
              <p className="text-sm text-fg-muted">
                Source: {r.source} ({TIER_TEXT[r.source_tier]}) · checked {dateFormat.format(new Date(r.checked_at))}
              </p>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

/** F09: reassuring signals are shown, but never change the level (ADR-011). */
export function WhatLooksRight({ signals }: { signals: Signal[] }) {
  if (signals.length === 0) return null;

  return (
    <section aria-labelledby="right-heading">
      <h2 id="right-heading" className="text-xl font-semibold">
        What looks right
      </h2>
      <ul className="mt-4 space-y-2">
        {signals.map((s) => (
          <li key={s.id} className="flex gap-2.5 rounded-xl bg-low-bg p-3.5">
            <CheckCircleIcon size={20} className="mt-0.5 shrink-0 text-low-line" aria-hidden />
            {s.explanation}
          </li>
        ))}
      </ul>
      <p className="mt-2 text-sm text-fg-muted">
        These do not make an offer safe on their own. A message can sound right and still be fake.
      </p>
    </section>
  );
}

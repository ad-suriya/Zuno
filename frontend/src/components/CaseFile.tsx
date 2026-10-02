import { LockSimpleIcon } from "@phosphor-icons/react/ssr";

import { SEVERITY, TONE, type Tone } from "@/components/tone";
import type { buildTrail } from "@/lib/trail";
import type { Language } from "@/lib/types";

type Trail = ReturnType<typeof buildTrail>;

function NoteBadge({ n, tone }: { n: number; tone: Tone }) {
  return (
    <span
      className={`inline-flex size-6 shrink-0 items-center justify-center rounded-full font-mono text-xs font-bold text-bg tabular-nums ${TONE[tone].badge}`}
    >
      {n}
    </span>
  );
}

/** The user's own words with each warning marked in place, numbered notes underneath (the signature element). */
export function CaseFile({ trail, language }: { trail: Trail; language: Language }) {
  const { items, notes } = trail;
  let added = 0;

  return (
    <section aria-labelledby="casefile-heading">
      <h2 id="casefile-heading" className="text-xl font-semibold">
        What you told Zuno
      </h2>
      <p className="mt-1 text-fg-muted">
        {notes.length > 0
          ? "Highlighted words are what Zuno noticed. Tap a number to read why it matters."
          : "Nothing here matched a known warning sign. That does not make the offer safe: it still needs checking."}
      </p>

      <div className="mt-4 overflow-hidden rounded-xl border border-border bg-surface shadow-sm">
        {items.map(({ evidence, segments }) => {
          const label = evidence.kind === "story" ? "Your story" : `Added detail ${++added}`;
          return (
            <blockquote key={evidence.id} className="border-b border-border p-5 last:border-b-0 sm:p-6">
              <p className="mb-2 text-sm font-semibold text-fg-muted">{label}</p>
              <p lang={language} className="text-lg whitespace-pre-wrap">
                {segments.map((seg, i) =>
                  seg.kind === "text" ? (
                    <span key={i}>{seg.text}</span>
                  ) : seg.kind === "redacted" ? (
                    <span
                      key={i}
                      lang="en"
                      className="mx-0.5 inline-flex items-center gap-1 rounded-full bg-surface-muted px-2 align-baseline text-sm text-fg-muted"
                    >
                      <LockSimpleIcon size={14} aria-hidden />
                      hidden for your safety
                    </span>
                  ) : (
                    <a
                      key={i}
                      id={`mark-${seg.note}`}
                      href={`#note-${seg.note}`}
                      className={`scroll-mt-24 rounded-sm px-0.5 text-fg underline decoration-2 underline-offset-4 ${TONE[SEVERITY[seg.signal.severity].tone].mark}`}
                    >
                      {seg.text}
                      <sup className="ml-0.5 font-mono text-xs font-bold">{seg.note}</sup>
                    </a>
                  ),
                )}
              </p>
            </blockquote>
          );
        })}

        {notes.length > 0 && (
          <ol className="divide-y divide-border border-t border-dashed border-border-strong bg-surface-muted">
            {notes.map(({ n, signal, located }) => {
              const sev = SEVERITY[signal.severity];
              return (
                <li key={signal.id} id={`note-${n}`} className="flex scroll-mt-24 gap-3 p-4 sm:px-6">
                  <NoteBadge n={n} tone={sev.tone} />
                  <div className="min-w-0 flex-1">
                    <p className={`flex items-center gap-1 text-sm font-semibold ${TONE[sev.tone].text}`}>
                      <sev.icon size={16} weight="bold" aria-hidden />
                      {sev.label} warning
                    </p>
                    <p className="mt-1">{signal.explanation}</p>
                    {located ? (
                      <a href={`#mark-${n}`} className="mt-1 inline-block text-sm text-accent underline underline-offset-4">
                        Show in message
                      </a>
                    ) : (
                      signal.matched_text && <p className="mt-1 text-sm text-fg-muted">Found: “{signal.matched_text}”</p>
                    )}
                  </div>
                </li>
              );
            })}
          </ol>
        )}
      </div>
    </section>
  );
}

import { ArrowSquareOutIcon, PhoneIcon } from "@phosphor-icons/react/ssr";

import { STEP_LINK, STEP_TEXT } from "@/lib/content";

/** F02: rules-chosen steps, in the order the backend returns them. Unknown codes are skipped. */
export function NextSteps({ steps }: { steps: string[] }) {
  const known = steps.filter((code) => code in STEP_TEXT);
  if (known.length === 0) return null;

  return (
    <section aria-labelledby="steps-heading">
      <h2 id="steps-heading" className="text-xl font-semibold">
        What to do now
      </h2>
      <ol className="mt-4 space-y-3">
        {known.map((code, i) => {
          const link = STEP_LINK[code];
          return (
            <li key={code} className="flex gap-3 rounded-xl border border-border bg-surface p-4">
              <span className="inline-flex size-7 shrink-0 items-center justify-center rounded-full bg-primary font-mono text-sm font-bold text-on-primary tabular-nums">
                {i + 1}
              </span>
              <div className={i === 0 ? "font-semibold" : undefined}>
                <p>{STEP_TEXT[code]}</p>
                {link && (
                  <a
                    href={link.href}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-1 inline-flex min-h-9 items-center gap-1 font-semibold text-accent underline underline-offset-4"
                  >
                    {link.label}
                    <ArrowSquareOutIcon size={16} aria-hidden />
                  </a>
                )}
              </div>
            </li>
          );
        })}
      </ol>
      {known.includes("REPORT_IF_LOST") && (
        <a
          href="tel:1930"
          className="mt-4 flex min-h-12 items-center justify-center gap-2 rounded-lg bg-primary px-6 font-semibold text-on-primary transition-opacity duration-150 hover:opacity-90 sm:inline-flex"
        >
          <PhoneIcon size={20} aria-hidden />
          Call 1930, the cyber crime helpline
        </a>
      )}
    </section>
  );
}

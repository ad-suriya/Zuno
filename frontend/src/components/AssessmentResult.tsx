import type { AssessmentLevel, InvestigationDetail, Severity } from "@/lib/types";

const LEVEL: Record<AssessmentLevel, { label: string; className: string; summary: string }> = {
  LOW_CONCERN: {
    label: "Low concern",
    className: "border-emerald-700 bg-emerald-50 text-emerald-900",
    summary: "No major warning signals were identified from the information available.",
  },
  NEEDS_VERIFICATION: {
    label: "Needs verification",
    className: "border-amber-600 bg-amber-50 text-amber-900",
    summary: "Important information is missing or could not be independently verified.",
  },
  HIGH_CONCERN: {
    label: "High concern",
    className: "border-red-700 bg-red-50 text-red-900",
    summary: "Significant warning signals are present, based on the information provided.",
  },
};

const SEVERITY_ORDER: Severity[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export function AssessmentResult({ detail }: { detail: InvestigationDetail }) {
  const assessment = detail.investigation.assessment;
  const warnings = detail.signals
    .filter((s) => s.kind === "WARNING")
    .sort((a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity));
  const redacted = detail.evidence.some((e) => e.redacted);

  return (
    <section className="space-y-5" aria-live="polite">
      {assessment && (
        <div className={`rounded-lg border-l-4 p-4 ${LEVEL[assessment.level].className}`}>
          <p className="text-xs font-semibold uppercase tracking-wide">Assessment</p>
          <p className="mt-1 text-xl font-semibold">{LEVEL[assessment.level].label}</p>
          <p className="mt-1 text-sm">{LEVEL[assessment.level].summary}</p>
          <ul className="mt-3 list-disc space-y-1 pl-5 text-sm">
            {assessment.reasons.map((r) => (
              <li key={r.rule}>{r.explanation}</li>
            ))}
          </ul>
        </div>
      )}

      {redacted && (
        <p className="rounded-md bg-stone-100 p-3 text-sm text-stone-700">
          We removed what looked like an OTP, PIN, password or card number before saving. Never share these with
          anyone.
        </p>
      )}

      <div>
        <h2 className="text-sm font-semibold text-stone-900">Warning signals found ({warnings.length})</h2>
        {warnings.length === 0 ? (
          <p className="mt-2 text-sm text-stone-600">
            None found in the text so far. This does not mean the offer is safe; it still needs checking.
          </p>
        ) : (
          <ul className="mt-2 space-y-2">
            {warnings.map((s) => (
              <li key={s.id} className="rounded-md border border-stone-200 bg-white p-3 text-sm">
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-1.5 py-0.5 text-xs font-semibold ${
                      s.severity === "CRITICAL" || s.severity === "HIGH"
                        ? "bg-red-100 text-red-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {s.severity}
                  </span>
                  {s.matched_text && <span className="font-mono text-xs text-stone-500">“{s.matched_text}”</span>}
                </div>
                <p className="mt-1 text-stone-800">{s.explanation}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

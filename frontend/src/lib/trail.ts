// Builds the annotated evidence trail: each warning is marked where it appears and numbered in reading order.
import type { Evidence, InvestigationDetail, Signal } from "./types";

const REDACTED = "[REDACTED]";

export type Segment =
  | { kind: "text"; text: string }
  | { kind: "redacted" }
  | { kind: "mark"; text: string; note: number; signal: Signal };

export interface Note {
  n: number;
  signal: Signal;
  located: boolean;
}

/** Split one evidence item into plain text, redaction pills and marks for the signals found in it. */
function annotate(evidence: Evidence, signals: Signal[]) {
  type Range = { start: number; end: number; signal?: Signal };
  const ranges: Range[] = [];
  const overlaps = (s: number, e: number) => ranges.some((r) => s < r.end && e > r.start);
  const lower = evidence.content.toLowerCase();

  for (const signal of signals) {
    if (!signal.matched_text) continue;
    const needle = signal.matched_text.toLowerCase();
    for (let i = lower.indexOf(needle); i !== -1; i = lower.indexOf(needle, i + 1)) {
      if (!overlaps(i, i + needle.length)) {
        ranges.push({ start: i, end: i + needle.length, signal });
        break;
      }
    }
  }
  for (let i = evidence.content.indexOf(REDACTED); i !== -1; i = evidence.content.indexOf(REDACTED, i + 1)) {
    if (!overlaps(i, i + REDACTED.length)) ranges.push({ start: i, end: i + REDACTED.length });
  }
  ranges.sort((a, b) => a.start - b.start);

  const segments: (Segment | { kind: "pending"; text: string; signal: Signal })[] = [];
  let cursor = 0;
  for (const r of ranges) {
    if (r.start > cursor) segments.push({ kind: "text", text: evidence.content.slice(cursor, r.start) });
    const text = evidence.content.slice(r.start, r.end);
    segments.push(r.signal ? { kind: "pending", text, signal: r.signal } : { kind: "redacted" });
    cursor = r.end;
  }
  if (cursor < evidence.content.length) segments.push({ kind: "text", text: evidence.content.slice(cursor) });
  return segments;
}

/** Number notes in reading order across evidence; signals that cannot be located come last. */
export function buildTrail(detail: InvestigationDetail) {
  const warnings = detail.signals.filter((s) => s.kind === "WARNING");
  const evidence = [...detail.evidence].sort((a, b) => a.created_at.localeCompare(b.created_at));
  const notes: Note[] = [];

  const items = evidence.map((e) => {
    const segments: Segment[] = annotate(
      e,
      warnings.filter((s) => s.evidence_id === e.id),
    ).map((seg) => {
      if (seg.kind !== "pending") return seg;
      const n = notes.length + 1;
      notes.push({ n, signal: seg.signal, located: true });
      return { kind: "mark", text: seg.text, note: n, signal: seg.signal };
    });
    return { evidence: e, segments };
  });

  for (const signal of warnings) {
    if (!notes.some((n) => n.signal.id === signal.id)) {
      notes.push({ n: notes.length + 1, signal, located: false });
    }
  }
  return { items, notes };
}

"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { AssessmentResult } from "@/components/AssessmentResult";
import { ErrorNotice } from "@/components/ErrorNotice";
import { StoryForm } from "@/components/StoryForm";
import { api, ApiError, toApiError } from "@/lib/api";
import type { InvestigationDetail } from "@/lib/types";

type State =
  | { kind: "start" }
  | { kind: "loading"; id: string }
  | { kind: "failed"; id: string; error: ApiError }
  | { kind: "result"; detail: InvestigationDetail };

// The check lives in the URL (?id=) so a refresh or shared link restores it. The ID is random hex, not PII.
function setUrlId(id: string | null) {
  window.history.replaceState(null, "", id ? `?id=${encodeURIComponent(id)}` : window.location.pathname);
}

export function Checker({ initialId }: { initialId: string | null }) {
  const [state, setState] = useState<State>(initialId ? { kind: "loading", id: initialId } : { kind: "start" });
  const topRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async (id: string) => {
    setState({ kind: "loading", id });
    try {
      let detail = await api.getInvestigation(id);
      if (!detail.investigation.assessment) detail = await api.assess(id);
      setState({ kind: "result", detail });
    } catch (err) {
      setState({ kind: "failed", id, error: toApiError(err) });
    }
  }, []);

  useEffect(() => {
    // Restore a check from the URL once on mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (initialId) load(initialId);
  }, [initialId, load]);

  function show(detail: InvestigationDetail) {
    setUrlId(detail.investigation.id);
    setState({ kind: "result", detail });
    // Bring the (possibly changed) assessment into view and move focus to it.
    requestAnimationFrame(() => {
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      topRef.current?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      topRef.current?.focus({ preventScroll: true });
    });
  }

  function reset() {
    setUrlId(null);
    setState({ kind: "start" });
    window.scrollTo({ top: 0 });
  }

  return (
    <div ref={topRef} tabIndex={-1} className="scroll-mt-6 focus:outline-none">
      {state.kind === "start" && <StoryForm onCreated={show} />}

      {state.kind === "loading" && (
        <div role="status" aria-label="Loading your check" className="space-y-4">
          <div className="h-44 animate-pulse rounded-2xl bg-surface-muted motion-reduce:animate-none" />
          <div className="h-24 animate-pulse rounded-xl bg-surface-muted motion-reduce:animate-none" />
          <div className="h-24 animate-pulse rounded-xl bg-surface-muted motion-reduce:animate-none" />
        </div>
      )}

      {state.kind === "failed" && (
        <div className="space-y-6">
          <ErrorNotice
            error={
              state.error.code === "NOT_FOUND"
                ? new ApiError("NOT_FOUND", "This check could not be found. The link may be wrong or expired.", 404)
                : state.error
            }
            onRetry={state.error.code === "NOT_FOUND" ? undefined : () => load(state.id)}
          />
          <button
            type="button"
            onClick={reset}
            className="min-h-12 cursor-pointer rounded-lg bg-primary px-6 font-semibold text-on-primary hover:opacity-90"
          >
            Start a new check
          </button>
        </div>
      )}

      {state.kind === "result" && <AssessmentResult detail={state.detail} onUpdated={show} onReset={reset} />}
    </div>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";

import { api, ApiError } from "@/lib/api";

type State =
  | { kind: "checking" }
  | { kind: "offline"; message: string }
  | { kind: "online"; version: string; firestore: "ok" | "unavailable" };

export function BackendStatus() {
  const [state, setState] = useState<State>({ kind: "checking" });

  const check = useCallback(async () => {
    try {
      const [health, ready] = await Promise.all([api.health(), api.readiness()]);
      setState({ kind: "online", version: health.version, firestore: ready.checks.firestore });
    } catch (err) {
      setState({ kind: "offline", message: err instanceof ApiError ? err.message : "Unknown error." });
    }
  }, []);

  useEffect(() => {
    // Initial check on mount, then poll so the indicator recovers when the backend comes up.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    check();
    const id = setInterval(check, 15_000);
    return () => clearInterval(id);
  }, [check]);

  const dot =
    state.kind === "checking"
      ? "bg-border-strong"
      : state.kind === "offline"
        ? "bg-high-line"
        : state.firestore === "ok"
          ? "bg-low-line"
          : "bg-verify-line";

  const label =
    state.kind === "checking"
      ? "Checking server…"
      : state.kind === "offline"
        ? state.message
        : state.firestore === "ok"
          ? `Server v${state.version} · database connected`
          : `Server v${state.version} · database unavailable`;

  return (
    <div role="status" className="flex items-center gap-2 text-sm text-fg-muted">
      <span className={`inline-block h-2.5 w-2.5 rounded-full ${dot}`} aria-hidden />
      <span>{label}</span>
      {state.kind !== "checking" && (
        <button onClick={check} className="ml-1 min-h-11 cursor-pointer underline underline-offset-4 hover:text-fg">
          Recheck
        </button>
      )}
    </div>
  );
}

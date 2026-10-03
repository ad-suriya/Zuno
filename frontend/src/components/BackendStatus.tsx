"use client";

import { useCallback, useEffect, useState } from "react";

import { useErrorText } from "@/components/ErrorNotice";
import { useI18n } from "@/components/I18nProvider";
import { api } from "@/lib/api";

type State =
  | { kind: "checking" }
  | { kind: "offline"; error: unknown }
  | { kind: "online"; version: string; firestore: "ok" | "unavailable" };

export function BackendStatus() {
  const { t } = useI18n();
  const errorText = useErrorText();
  const [state, setState] = useState<State>({ kind: "checking" });

  const check = useCallback(async () => {
    try {
      const [health, ready] = await Promise.all([api.health(), api.readiness()]);
      setState({ kind: "online", version: health.version, firestore: ready.checks.firestore });
    } catch (err) {
      setState({ kind: "offline", error: err });
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
      ? "bg-stone-400"
      : state.kind === "offline"
        ? "bg-red-600"
        : state.firestore === "ok"
          ? "bg-emerald-600"
          : "bg-amber-500";

  const label =
    state.kind === "checking"
      ? t("status.checking")
      : state.kind === "offline"
        ? errorText(state.error)
        : t(state.firestore === "ok" ? "status.db_ok" : "status.db_down", { version: state.version });

  return (
    <div role="status" className="flex items-center gap-2 text-sm text-stone-600">
      <span className={`inline-block h-2.5 w-2.5 rounded-full ${dot}`} aria-hidden />
      <span>{label}</span>
      {state.kind !== "checking" && (
        <button onClick={check} className="ml-1 underline underline-offset-2 hover:text-stone-900">
          {t("status.recheck")}
        </button>
      )}
    </div>
  );
}

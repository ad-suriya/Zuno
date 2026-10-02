import { WarningCircleIcon } from "@phosphor-icons/react/ssr";

import type { ApiError } from "@/lib/api";

export function ErrorNotice({ error, onRetry, busy }: { error: ApiError; onRetry?: () => void; busy?: boolean }) {
  return (
    <div role="alert" className="enter flex gap-3 rounded-xl border border-high-line bg-high-bg p-4 text-high-fg">
      <WarningCircleIcon size={24} className="shrink-0" aria-hidden />
      <div>
        <p className="font-medium">{error.message}</p>
        {error.requestId && <p className="mt-1 font-mono text-xs">Reference: {error.requestId}</p>}
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            disabled={busy}
            className="mt-2 min-h-11 cursor-pointer font-semibold underline underline-offset-4 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Try again
          </button>
        )}
      </div>
    </div>
  );
}

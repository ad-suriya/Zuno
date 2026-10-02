"use client"; // Error boundaries must be Client Components

import { useEffect } from "react";

export default function Error({ error, retry }: { error: Error & { digest?: string }; retry: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-16">
      <h1 className="font-display text-4xl">Something went wrong</h1>
      <p className="mt-3 text-fg-muted">This page could not be shown. Your information was not shared.</p>
      <button
        onClick={() => retry()}
        className="mt-6 min-h-12 cursor-pointer rounded-lg bg-primary px-6 font-semibold text-on-primary hover:opacity-90"
      >
        Try again
      </button>
    </main>
  );
}

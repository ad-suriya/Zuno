"use client"; // Error boundaries must be Client Components

import { useEffect } from "react";

export default function Error({ error, retry }: { error: Error & { digest?: string }; retry: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-16">
      <h1 className="text-xl font-semibold text-stone-900">Something went wrong</h1>
      <p className="mt-2 text-stone-700">This page could not be shown. Your information was not shared.</p>
      <button
        onClick={() => retry()}
        className="mt-6 rounded-md bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-700"
      >
        Try again
      </button>
    </main>
  );
}

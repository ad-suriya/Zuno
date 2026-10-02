import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-16">
      <h1 className="text-xl font-semibold text-stone-900">Page not found</h1>
      <Link href="/" className="mt-6 inline-block text-sm underline underline-offset-2">
        Back to Zuno
      </Link>
    </main>
  );
}

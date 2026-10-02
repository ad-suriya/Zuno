import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-16">
      <h1 className="font-display text-4xl">Page not found</h1>
      <Link href="/" className="mt-6 inline-block text-accent underline underline-offset-4">
        Back to Zuno
      </Link>
    </main>
  );
}

import { BackendStatus } from "@/components/BackendStatus";
import { Checker } from "@/components/Checker";

export default async function Home({ searchParams }: PageProps<"/">) {
  const { id } = await searchParams;

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-4 pt-6 pb-16 sm:pt-10">
      <header className="mb-10">
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-b border-border pb-4">
          <p className="font-display text-2xl tracking-wide">ZUNO</p>
          <BackendStatus />
        </div>
      </header>

      <Checker initialId={typeof id === "string" ? id : null} />

      <footer className="mt-16 border-t border-border pt-4 text-sm text-fg-muted">
        Zuno does not give investment advice or predict prices. If you have lost money, call{" "}
        <a href="tel:1930" className="font-semibold text-accent underline underline-offset-4">
          1930
        </a>{" "}
        or report it at{" "}
        <a
          href="https://cybercrime.gov.in"
          target="_blank"
          rel="noreferrer"
          className="text-accent underline underline-offset-4"
        >
          cybercrime.gov.in
        </a>
        .
      </footer>
    </main>
  );
}

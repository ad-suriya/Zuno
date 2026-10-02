import { BackendStatus } from "@/components/BackendStatus";
import { StoryForm } from "@/components/StoryForm";

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-10 sm:py-16">
      <header className="mb-8 space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight text-stone-900">Zuno</h1>
        <p className="text-stone-700">Know before you act. Check a financial offer before you put money at risk.</p>
        <BackendStatus />
      </header>

      <StoryForm />

      <footer className="mt-12 border-t border-stone-200 pt-4 text-xs text-stone-500">
        Zuno does not give investment advice or predict prices. If you have lost money, report it at
        cybercrime.gov.in or call 1930.
      </footer>
    </main>
  );
}

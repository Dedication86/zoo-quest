import Link from "next/link";
import { HealthBadge } from "@/components/HealthBadge";

/**
 * Root. In production a visitor never lands here; they arrive via a marker
 * (/s/[code]) or a zoo's welcome page (/z/[zoo]). This page is the developer
 * lobby: links to every route plus a live API health check.
 */
export default function Home() {
  const zoo = "cedar-hollow";
  const routes: [string, string][] = [
    [`/s/CHZ-BASECAMP-001`, "Marker landing (/s/[code])"],
    [`/z/${zoo}`, "Welcome"],
    [`/z/${zoo}/quests`, "Choose Adventure"],
    [`/z/${zoo}/quest/savanna-safari`, "Active Quest"],
    [`/z/${zoo}/challenge/1`, "Challenge"],
    [`/z/${zoo}/scan`, "In-app scanner"],
    [`/z/${zoo}/success`, "Success"],
    [`/z/${zoo}/map`, "Map"],
    [`/z/${zoo}/animals/giraffe`, "Animal"],
    [`/z/${zoo}/profile`, "Explorer Profile"],
  ];
  return (
    <main className="mx-auto flex min-h-dvh max-w-md flex-col px-6 pb-10 pt-16">
      <p className="font-display text-sm font-semibold uppercase tracking-[0.18em] text-ember">Milestone 0</p>
      <h1 className="mt-2 text-6xl font-bold leading-none">Zoo Quest</h1>
      <p className="mt-3 text-lg text-sand-dim">Your adventure starts here.</p>
      <HealthBadge />
      <nav className="mt-8 flex flex-col gap-2" aria-label="Route skeleton">
        {routes.map(([href, label]) => (
          <Link
            key={href}
            href={href}
            className="flex min-h-14 items-center justify-between rounded-card border border-line bg-canopy px-4 hover:bg-canopy-2"
          >
            <span className="font-semibold">{label}</span>
            <span className="font-mono text-xs text-sand-dim">{href}</span>
          </Link>
        ))}
      </nav>
    </main>
  );
}

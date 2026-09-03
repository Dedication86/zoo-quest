import Link from "next/link";

/**
 * Stand-in for screens that arrive in later milestones. Keeps every route in
 * Section F reachable from day one so navigation can be tested end to end.
 */
export function Placeholder({
  eyebrow,
  title,
  milestone,
  children,
}: {
  eyebrow: string;
  title: string;
  milestone: string;
  children?: React.ReactNode;
}) {
  return (
    <main className="mx-auto flex min-h-dvh max-w-md flex-col px-6 pb-10 pt-14">
      <p className="font-display text-sm font-semibold uppercase tracking-[0.18em] text-ember">{eyebrow}</p>
      <h1 className="mt-2 text-5xl font-bold leading-none">{title}</h1>
      <p className="mt-4 text-sand-dim">This screen is built in {milestone}.</p>
      <div className="mt-6 flex flex-col gap-3">{children}</div>
      <Link href="/" className="mt-auto pt-10 text-sm text-sand-dim underline-offset-4 hover:underline">
        Back to start
      </Link>
    </main>
  );
}

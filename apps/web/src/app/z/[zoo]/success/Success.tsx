"use client";

import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Confetti } from "@/components/Confetti";
import { XPCounter } from "@/components/XPCounter";
import { useStore } from "@/lib/store";

/**
 * The celebration. Reads the last scan result from the store; if there is
 * none (deep link, refresh) it sends the family back to their quest.
 * Sequence: headline → XP roll → fact → level-up → what next.
 */
export function Success({ zoo }: { zoo: string }) {
  const router = useRouter();
  const qc = useQueryClient();
  const result = useStore((s) => s.lastResult);
  const token = useStore((s) => s.guestToken);
  const [stage, setStage] = useState(0);

  useEffect(() => {
    if (!result) {
      router.replace(`/z/${zoo}/quests`);
      return;
    }
    qc.invalidateQueries({ queryKey: ["me", token] });
    const timers = [400, 1300, 2000].map((ms, i) => setTimeout(() => setStage(i + 1), ms));
    return () => timers.forEach(clearTimeout);
  }, [result, router, zoo, qc, token]);

  if (!result) return null;

  const { animal, discovery, level_up, totals, suggested_quest, marker } = result;
  const isNew = discovery.is_new;
  const headline = isNew ? "Discovered!" : discovery.result === "repeat" ? "Already found" : "Checkpoint";
  const fact = animal?.fun_facts?.[0];

  return (
    <main className="relative mx-auto flex min-h-dvh max-w-md flex-col overflow-hidden px-6 pb-10 pt-14">
      <Confetti fire={isNew} />
      <div
        aria-hidden
        className={`absolute inset-0 -z-10 ${isNew ? "bg-[radial-gradient(ellipse_at_top,_#2c5a41_0%,_#0b1a14_65%)]" : "bg-night"}`}
      />

      <p className="font-display text-sm font-semibold uppercase tracking-[0.18em] text-ember">
        {isNew ? "Mission update" : marker.exhibit.name}
      </p>
      <h1 className="mt-1 text-6xl font-bold leading-none">{headline}</h1>

      <div className="mt-8 flex items-center gap-5">
        <div className="flex size-24 shrink-0 items-center justify-center rounded-3xl bg-canopy text-6xl shadow-[0_0_0_6px_rgba(240,150,58,.15)]">
          {animal?.emoji ?? "📍"}
        </div>
        <div>
          <p className="text-2xl font-semibold leading-tight">{animal ? `You found a ${animal.name.toLowerCase()}!` : marker.exhibit.name}</p>
          <p className="mt-1 text-sand-dim">{animal ? animal.exhibit_name : marker.label}</p>
        </div>
      </div>

      <div className={`mt-8 transition-opacity duration-500 ${stage >= 1 ? "opacity-100" : "opacity-0"}`}>
        {isNew ? (
          <div className="flex items-baseline gap-3">
            <XPCounter value={discovery.xp} />
            <span className="font-display text-xl font-semibold uppercase tracking-wider text-sand-dim">XP</span>
          </div>
        ) : (
          <p className="text-lg text-sand-dim">
            {discovery.result === "repeat" ? "You've already discovered this one. No extra XP, but nice to see you again." : "Every checkpoint counts. Keep going."}
          </p>
        )}
      </div>

      {fact && (
        <div className={`mt-6 rounded-card border border-line bg-canopy p-5 transition-all duration-500 ${stage >= 2 ? "translate-y-0 opacity-100" : "translate-y-3 opacity-0"}`}>
          <p className="font-display text-xs font-semibold uppercase tracking-[0.16em] text-moss">Did you know?</p>
          <p className="mt-2 text-lg leading-snug">{fact}</p>
        </div>
      )}

      {level_up && (
        <div className={`mt-4 rounded-card bg-ember p-5 text-night transition-all duration-500 ${stage >= 3 ? "scale-100 opacity-100" : "scale-95 opacity-0"}`}>
          <p className="font-display text-xs font-bold uppercase tracking-[0.16em]">Level up</p>
          <p className="mt-1 font-display text-4xl font-bold leading-none">{level_up.title}</p>
        </div>
      )}

      <div className={`mt-auto flex flex-col gap-3 pt-8 transition-opacity duration-500 ${stage >= 3 ? "opacity-100" : "opacity-0"}`}>
        {suggested_quest && (
          <Link href={`/z/${zoo}/quest/${suggested_quest.slug}`} className="btn btn-primary w-full">
            {isNew ? "Next mission" : "Back to quest"} →
          </Link>
        )}
        <Link href={`/z/${zoo}/profile`} className={`btn w-full ${suggested_quest ? "btn-secondary" : "btn-primary"}`}>
          {totals.xp.toLocaleString()} XP · See my profile
        </Link>
      </div>
    </main>
  );
}

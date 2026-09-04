"use client";

import type { Profile } from "@/lib/api";

/** Level title, XP total and progress to the next level. Reads only from the profile. */
export function XPBar({ profile }: { profile: Profile | null }) {
  if (!profile) {
    return <div className="h-11 animate-pulse rounded-xl bg-canopy" aria-hidden />;
  }
  const { level, total_xp } = profile;
  const span = level.next_at ? level.next_at - level.xp_required : 1;
  const pct = level.next_at ? Math.min(100, ((total_xp - level.xp_required) / span) * 100) : 100;
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span className="font-display text-sm font-bold uppercase tracking-[0.16em] text-ember">
          Lv {level.number} · {level.title}
        </span>
        <span className="font-display text-sm font-semibold tabular-nums text-sand">
          {total_xp.toLocaleString()} XP
          {level.next_at && <span className="text-sand-dim"> / {level.next_at.toLocaleString()}</span>}
        </span>
      </div>
      <div
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(pct)}
        aria-label="Progress to next level"
        className="mt-1.5 h-2 overflow-hidden rounded-full bg-canopy-2"
      >
        <div className="h-full rounded-full bg-ember transition-[width] duration-700 ease-out" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

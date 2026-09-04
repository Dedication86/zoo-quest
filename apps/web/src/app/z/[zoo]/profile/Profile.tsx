"use client";

import { ErrorNote, Loading } from "@/components/Loading";
import { useSession } from "@/hooks/useSession";

export function Profile({ zoo }: { zoo: string }) {
  const s = useSession(zoo);
  if (s.error) return <ErrorNote message={s.error.message} onRetry={() => s.refetch()} />;
  if (!s.profile) return <Loading />;
  const p = s.profile;
  const remaining = p.stats.animals_total - p.stats.animals_discovered;

  return (
    <div>
      <p className="font-display text-sm font-semibold uppercase tracking-[0.18em] text-ember">Explorer profile</p>
      <h1 className="mt-1 text-5xl font-bold leading-none">{p.team_name || "Your team"}</h1>
      <p className="mt-2 text-sand-dim">
        Level {p.level.number} · {p.level.title}
        {p.level.next_at && ` · ${(p.level.next_at - p.total_xp).toLocaleString()} XP to ${p.level.next_title}`}
      </p>

      <dl className="mt-6 grid grid-cols-3 gap-3">
        <Stat label="XP" value={p.total_xp} />
        <Stat label="Animals" value={`${p.stats.animals_discovered}/${p.stats.animals_total}`} />
        <Stat label="Missions" value={p.stats.challenges_completed} />
      </dl>

      <h2 className="mt-8 font-display text-2xl font-semibold">Discovered</h2>
      {p.discoveries.length === 0 ? (
        <p className="mt-2 rounded-card border border-dashed border-line p-5 text-sand-dim">
          Nothing yet. Find a Zoo Quest sign and scan it with your camera.
        </p>
      ) : (
        <ul className="mt-3 grid grid-cols-3 gap-3">
          {p.discoveries.map((d) => (
            <li key={d.slug} className="rounded-card bg-canopy p-3 text-center">
              <div className="text-4xl leading-none">{d.emoji || "🐾"}</div>
              <div className="mt-2 text-sm font-semibold leading-tight">{d.name}</div>
              <div className="mt-0.5 text-[11px] text-sand-dim">{d.exhibit}</div>
            </li>
          ))}
        </ul>
      )}
      {remaining > 0 && p.discoveries.length > 0 && (
        <p className="mt-3 text-sm text-sand-dim">{remaining} more to find.</p>
      )}

      <h2 className="mt-8 font-display text-2xl font-semibold">Badges</h2>
      <p className="mt-2 rounded-card border border-dashed border-line p-5 text-sand-dim">
        Badges unlock in the next update. Keep scanning; nothing you earn now is lost.
      </p>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-card bg-canopy p-3">
      <dt className="font-display text-[11px] font-semibold uppercase tracking-[0.16em] text-sand-dim">{label}</dt>
      <dd className="mt-1 font-display text-3xl font-bold tabular-nums">{typeof value === "number" ? value.toLocaleString() : value}</dd>
    </div>
  );
}

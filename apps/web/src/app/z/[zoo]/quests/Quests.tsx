"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { ErrorNote, Loading } from "@/components/Loading";
import { getQuests } from "@/lib/api";

/** Choose Adventure. Lists quests (not mechanics: Blueprint, Section 0 decision 2). Starting one is M3. */
export function Quests({ zoo }: { zoo: string }) {
  const q = useQuery({ queryKey: ["quests", zoo], queryFn: () => getQuests(zoo) });
  if (q.isError) return <ErrorNote message="Couldn't load quests." onRetry={() => q.refetch()} />;
  if (!q.data) return <Loading label="Loading quests…" />;

  return (
    <div>
      <p className="font-display text-sm font-semibold uppercase tracking-[0.18em] text-ember">Choose adventure</p>
      <h1 className="mt-1 text-5xl font-bold leading-none">What&apos;s your mission?</h1>
      <ul className="mt-6 flex flex-col gap-4">
        {q.data.map((quest) => (
          <li key={quest.slug}>
            <Link
              href={`/z/${zoo}/quest/${quest.slug}`}
              className="block rounded-card border border-line bg-canopy p-5 transition hover:bg-canopy-2"
            >
              <div className="flex items-start justify-between gap-3">
                <h2 className="font-display text-3xl font-semibold leading-none">{quest.name}</h2>
                {quest.is_featured && (
                  <span className="shrink-0 rounded-md bg-ember/15 px-2 py-0.5 font-display text-[11px] font-bold uppercase tracking-wider text-ember">
                    Featured
                  </span>
                )}
              </div>
              <p className="mt-2 text-sand-dim">{quest.description}</p>
              <p className="mt-3 font-display text-sm font-semibold uppercase tracking-wider text-sand-dim">
                {quest.mission_count} missions · about {quest.estimated_minutes} min · +{quest.xp_reward} XP
                {quest.badge && ` · ${quest.badge.icon} ${quest.badge.name}`}
              </p>
            </Link>
          </li>
        ))}
      </ul>
      <p className="mt-6 text-center text-sm text-sand-dim">
        Or just explore: scan any Zoo Quest sign to discover animals and earn XP.
      </p>
    </div>
  );
}

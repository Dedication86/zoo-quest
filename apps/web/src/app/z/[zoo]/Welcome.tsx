"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { ErrorNote, Loading } from "@/components/Loading";
import { useSession } from "@/hooks/useSession";
import { getZoo, updateTeamName } from "@/lib/api";

export function Welcome({ zoo }: { zoo: string }) {
  const router = useRouter();
  const info = useQuery({ queryKey: ["zoo", zoo], queryFn: () => getZoo(zoo) });
  const session = useSession(zoo);
  const [team, setTeam] = useState("");
  const save = useMutation({
    mutationFn: (name: string) => updateTeamName(name),
    onSettled: () => router.push(`/z/${zoo}/quests`),
  });

  if (info.isError) return <ErrorNote message="We couldn't find that zoo." />;
  if (!info.data || session.isLoading) return <Loading />;

  const returning = (session.profile?.stats.scans ?? 0) > 0;
  const start = () => {
    const name = team.trim();
    if (name && name !== session.profile?.team_name) save.mutate(name);
    else router.push(`/z/${zoo}/quests`);
  };

  return (
    <main className="relative mx-auto flex min-h-dvh max-w-md flex-col justify-end overflow-hidden px-6 pb-10">
      <div aria-hidden className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_#1f4a35_0%,_#0b1a14_60%)]" />
      <div className="relative">
        <p className="font-display text-sm font-semibold uppercase tracking-[0.18em] text-ember">{info.data.name}</p>
        <h1 className="mt-2 text-7xl font-bold leading-[0.9]">Zoo Quest</h1>
        <p className="mt-4 text-xl text-sand-dim">
          {returning
            ? `Welcome back${session.profile?.team_name ? `, ${session.profile.team_name}` : ""}. Your adventure is saved.`
            : `Your adventure starts here. ${info.data.animal_count} animals to discover, ${info.data.quest_count} quests to finish.`}
        </p>

        {!returning && (
          <label className="mt-8 block">
            <span className="font-display text-xs font-semibold uppercase tracking-[0.16em] text-sand-dim">
              Team name (optional)
            </span>
            <input
              value={team}
              onChange={(e) => setTeam(e.target.value)}
              maxLength={40}
              placeholder="The Giraffe Gang"
              autoComplete="off"
              className="mt-2 w-full rounded-2xl border border-line bg-canopy px-4 py-4 text-lg text-sand placeholder:text-sand-dim/60 focus:border-ember focus:outline-none"
            />
          </label>
        )}

        <button onClick={start} disabled={save.isPending} className="btn btn-primary mt-6 w-full">
          {returning ? "Continue exploring" : "Start exploring"}
        </button>
        <p className="mt-4 text-center text-xs text-sand-dim">
          No account needed. Progress stays on this phone.
        </p>
      </div>
    </main>
  );
}

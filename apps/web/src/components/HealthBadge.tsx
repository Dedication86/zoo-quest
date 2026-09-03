"use client";

import { useQuery } from "@tanstack/react-query";
import { getHealth } from "@/lib/api";

/** Proves the web app can reach the API. Removed once real screens exist. */
export function HealthBadge() {
  const { data, error, isPending } = useQuery({ queryKey: ["health"], queryFn: getHealth });
  const ok = data?.status === "ok";
  return (
    <div className="mt-6 flex items-center gap-3 rounded-card border border-line bg-canopy px-4 py-3 text-sm">
      <span
        aria-hidden
        className={`size-3 rounded-full ${isPending ? "bg-sand-dim" : ok ? "bg-moss" : "bg-ember"}`}
      />
      <span className="text-sand-dim">
        API{" "}
        {isPending ? "checking…" : error ? "unreachable" : ok ? `ok · database ${data.database} · v${data.version}` : "degraded"}
      </span>
    </div>
  );
}

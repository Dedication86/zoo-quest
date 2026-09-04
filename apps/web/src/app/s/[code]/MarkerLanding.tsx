"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { ErrorNote, Loading } from "@/components/Loading";
import { useSession } from "@/hooks/useSession";
import { ApiError, lookupMarker, scanMarker } from "@/lib/api";
import { useStore } from "@/lib/store";

/**
 * 1. Resolve the printed code to a zoo (public, no session needed).
 * 2. Make sure we have a session for that zoo (creates one on first visit).
 * 3. POST /scan once, stash the result, go celebrate.
 */
export function MarkerLanding({ code }: { code: string }) {
  const router = useRouter();
  const setLastResult = useStore((s) => s.setLastResult);
  const marker = useQuery({ queryKey: ["marker", code], queryFn: () => lookupMarker(code), retry: 1 });
  const zoo = marker.data?.zoo.slug ?? null;
  const session = useSession(zoo);
  const fired = useRef(false);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (!marker.data || !session.ready || fired.current) return;
    fired.current = true;
    scanMarker(code)
      .then((result) => {
        setLastResult(result);
        router.replace(`/z/${zoo}/success`);
      })
      .catch((e: ApiError) => {
        fired.current = false;
        setError(e);
      });
  }, [marker.data, session.ready, code, zoo, router, setLastResult]);

  if (marker.isError) {
    return (
      <Shell>
        <ErrorNote
          message={
            (marker.error as ApiError).status === 404
              ? "This marker isn't part of any quest. Look for a Zoo Quest sign nearby."
              : (marker.error as ApiError).message
          }
        />
      </Shell>
    );
  }
  if (error) {
    return (
      <Shell>
        <ErrorNote message={error.message} onRetry={() => setError(null)} />
      </Shell>
    );
  }
  if (session.error) {
    return (
      <Shell>
        <ErrorNote message={session.error.message} onRetry={session.retryCreate} />
      </Shell>
    );
  }
  return (
    <Shell>
      <p className="font-display text-sm font-semibold uppercase tracking-[0.18em] text-ember">Quest marker</p>
      <h1 className="mt-2 text-5xl font-bold leading-none">
        {marker.data ? marker.data.exhibit_name : "Scanning…"}
      </h1>
      {marker.data?.animal_name && <p className="mt-2 text-lg text-sand-dim">{marker.data.animal_name}</p>}
      <Loading label={marker.data ? "Checking your discovery…" : "Finding this marker…"} />
    </Shell>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return <main className="mx-auto flex min-h-dvh max-w-md flex-col px-6 pt-16">{children}</main>;
}

"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { ApiError, createSession, getMe, type Profile } from "@/lib/api";
import { useStore } from "@/lib/store";

/**
 * Only one session may be created at a time, no matter how many components
 * call useSession() in the same render (the app frame and the page both do).
 */
let inflight: { zoo: string; promise: Promise<Profile> } | null = null;

function createOnce(zoo: string): Promise<Profile> {
  if (inflight?.zoo === zoo) return inflight.promise;
  const promise = createSession(zoo).finally(() => {
    if (inflight?.promise === promise) inflight = null;
  });
  inflight = { zoo, promise };
  return promise;
}

/**
 * Guarantees a guest session for `zooSlug` and exposes the profile.
 * - No token yet → creates one (once).
 * - Token for a different zoo → replaces it (a family at a new zoo is a new adventure).
 * - Token rejected by the API (401) → clears it and starts over.
 */
export function useSession(zooSlug: string | null) {
  const { guestToken, zooSlug: storedZoo, hydrated, setSession, clearSession } = useStore();
  const qc = useQueryClient();
  const [createError, setCreateError] = useState<ApiError | null>(null);

  const needsNew = hydrated && !!zooSlug && (!guestToken || storedZoo !== zooSlug);

  useEffect(() => {
    if (!needsNew || !zooSlug || createError) return;
    let cancelled = false;
    createOnce(zooSlug)
      .then((profile) => {
        if (cancelled) return;
        setSession(profile.token, profile.zoo.slug);
        qc.setQueryData(["me", profile.token], profile);
      })
      .catch((e: ApiError) => {
        if (!cancelled) setCreateError(e);
      });
    return () => {
      cancelled = true;
    };
  }, [needsNew, zooSlug, createError, setSession, qc]);

  const me = useQuery<Profile, ApiError>({
    queryKey: ["me", guestToken],
    queryFn: getMe,
    enabled: hydrated && !!guestToken && !needsNew,
    retry: (count, err) => err.status !== 401 && count < 2,
  });

  useEffect(() => {
    if (me.error?.status === 401) clearSession();
  }, [me.error, clearSession]);

  return {
    ready: hydrated && !!guestToken && !needsNew && !!me.data,
    profile: me.data ?? null,
    isLoading: !hydrated || needsNew || me.isPending,
    error: createError ?? (me.error?.status === 401 ? null : me.error) ?? null,
    refetch: me.refetch,
    retryCreate: () => setCreateError(null),
    token: guestToken,
  };
}

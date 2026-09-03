/**
 * Client-only state. Deliberately tiny (Blueprint, Section F "State management").
 * Everything that comes from the server belongs in TanStack Query, not here.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

type State = {
  guestToken: string | null;
  zooSlug: string | null;
  /** The last scan/submit result, handed to the Success screen to celebrate. */
  lastResult: unknown | null;
  setSession: (token: string, zooSlug: string) => void;
  setLastResult: (result: unknown | null) => void;
};

export const useStore = create<State>()(
  persist(
    (set) => ({
      guestToken: null,
      zooSlug: null,
      lastResult: null,
      setSession: (guestToken, zooSlug) => set({ guestToken, zooSlug }),
      setLastResult: (lastResult) => set({ lastResult }),
    }),
    {
      name: "zooquest",
      partialize: (s) => ({ guestToken: s.guestToken, zooSlug: s.zooSlug }), // lastResult is per-visit
    },
  ),
);

/** Non-hook accessor for use inside api.ts. */
export const getGuestToken = () => useStore.getState().guestToken;

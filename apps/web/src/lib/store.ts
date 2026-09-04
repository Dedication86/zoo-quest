/**
 * Client-only state. Deliberately tiny (Blueprint, Section F "State management").
 * Everything that comes from the server belongs in TanStack Query, not here.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { ScanResult } from "./api";

type State = {
  guestToken: string | null;
  zooSlug: string | null;
  /** True once the persisted values have been read back from storage. */
  hydrated: boolean;
  /** The last scan result, handed to the Success screen to celebrate. Not persisted. */
  lastResult: ScanResult | null;
  setSession: (token: string, zooSlug: string) => void;
  clearSession: () => void;
  setLastResult: (result: ScanResult | null) => void;
  setHydrated: () => void;
};

export const useStore = create<State>()(
  persist(
    (set) => ({
      guestToken: null,
      zooSlug: null,
      hydrated: false,
      lastResult: null,
      setSession: (guestToken, zooSlug) => set({ guestToken, zooSlug }),
      clearSession: () => set({ guestToken: null, zooSlug: null, lastResult: null }),
      setLastResult: (lastResult) => set({ lastResult }),
      setHydrated: () => set({ hydrated: true }),
    }),
    {
      name: "zooquest",
      partialize: (s) => ({ guestToken: s.guestToken, zooSlug: s.zooSlug }),
      onRehydrateStorage: () => (state) => state?.setHydrated(),
    },
  ),
);

/** Non-hook accessor for use inside api.ts. */
export const getGuestToken = () => useStore.getState().guestToken;

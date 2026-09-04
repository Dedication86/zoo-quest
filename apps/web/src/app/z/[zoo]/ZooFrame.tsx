"use client";

import { usePathname } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { useSession } from "@/hooks/useSession";

const FULLSCREEN = [/^\/z\/[^/]+\/?$/, /\/success$/];

export function ZooFrame({ zoo, children }: { zoo: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const session = useSession(zoo);
  if (FULLSCREEN.some((re) => re.test(pathname))) return <>{children}</>;
  return (
    <AppShell zoo={zoo} profile={session.profile}>
      {children}
    </AppShell>
  );
}

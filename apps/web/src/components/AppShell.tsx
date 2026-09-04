"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import type { Profile } from "@/lib/api";
import { XPBar } from "./XPBar";

const tabs = [
  { key: "quests", label: "Quest", icon: "🧭" },
  { key: "scan", label: "Scan", icon: "▣" },
  { key: "map", label: "Map", icon: "🗺️" },
  { key: "profile", label: "You", icon: "🎒" },
];

/** Persistent frame: XP bar on top, four-tab nav on the bottom, content between. */
export function AppShell({
  zoo,
  profile,
  children,
}: {
  zoo: string;
  profile: Profile | null;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  return (
    <div className="mx-auto flex min-h-dvh max-w-md flex-col">
      <header className="sticky top-0 z-20 bg-night/95 px-5 pb-2 pt-4 backdrop-blur">
        <XPBar profile={profile} />
      </header>
      <main className="flex-1 px-5 pb-28 pt-2">{children}</main>
      <nav
        aria-label="Main"
        className="fixed inset-x-0 bottom-0 z-20 mx-auto max-w-md border-t border-line bg-canopy/95 px-2 pb-[max(env(safe-area-inset-bottom),8px)] pt-2 backdrop-blur"
      >
        <ul className="grid grid-cols-4">
          {tabs.map((t) => {
            const href = `/z/${zoo}/${t.key}`;
            const active = pathname.startsWith(href) || (t.key === "quests" && pathname.includes("/quest/"));
            return (
              <li key={t.key}>
                <Link
                  href={href}
                  aria-current={active ? "page" : undefined}
                  className={`flex min-h-14 flex-col items-center justify-center gap-0.5 rounded-xl font-display text-xs font-semibold uppercase tracking-wider ${
                    active ? "text-ember" : "text-sand-dim"
                  }`}
                >
                  <span aria-hidden className="text-xl leading-none">
                    {t.icon}
                  </span>
                  {t.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}

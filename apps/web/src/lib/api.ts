/**
 * The one place the frontend talks to the Django API.
 *
 * - Attaches X-Guest-Token (Blueprint, Section E).
 * - Normalizes errors into ApiError.
 * - Retries idempotent POSTs (scan, start, submit) a few times for spotty signal.
 */
import { getGuestToken } from "./store";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: unknown,
  ) {
    super(
      typeof detail === "string"
        ? detail
        : detail && typeof detail === "object" && "detail" in detail
          ? String((detail as { detail: unknown }).detail)
          : `Something went wrong (${status}).`,
    );
  }
  get code(): string | undefined {
    const d = this.detail as { error?: string } | null;
    return d?.error;
  }
}

type Options = RequestInit & { retries?: number; token?: string | null };

export async function api<T>(path: string, options: Options = {}): Promise<T> {
  const { retries = 0, headers, token: explicitToken, ...rest } = options;
  const token = explicitToken === undefined ? getGuestToken() : explicitToken;

  const attempt = async (remaining: number): Promise<T> => {
    let response: Response;
    try {
      response = await fetch(`${API_BASE}${path}`, {
        ...rest,
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "X-Guest-Token": token } : {}),
          ...headers,
        },
      });
    } catch {
      if (remaining > 0) {
        await sleep(600 * (retries - remaining + 1));
        return attempt(remaining - 1);
      }
      throw new ApiError(0, "You seem to be offline. Try again in a moment.");
    }
    if (!response.ok) {
      const detail = await response.json().catch(() => response.statusText);
      throw new ApiError(response.status, detail);
    }
    return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
  };

  return attempt(retries);
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// ---------------------------------------------------------------- types
// Hand-typed for now; generated from the OpenAPI schema in M3.

export type Health = { status: "ok" | "degraded"; database: string; version: string };

export type LevelInfo = {
  number: number;
  title: string;
  xp_required: number;
  next_title: string | null;
  next_at: number | null;
};

export type DiscoveryCard = {
  slug: string;
  name: string;
  emoji: string;
  image: string | null;
  exhibit: string;
  discovered_at: string;
};

export type Profile = {
  token: string;
  zoo: { slug: string; name: string };
  team_name: string;
  total_xp: number;
  level: LevelInfo;
  stats: {
    animals_discovered: number;
    animals_total: number;
    scans: number;
    challenges_completed: number;
    badges: number;
  };
  discoveries: DiscoveryCard[];
  created_at: string;
};

export type ZooSummary = {
  slug: string;
  name: string;
  logo: string | null;
  primary_color: string;
  quest_count: number;
  animal_count: number;
  levels: { number: number; title: string; xp_required: number }[];
};

export type Badge = {
  id: number;
  slug: string;
  name: string;
  description: string;
  icon: string;
  image: string | null;
  xp_reward: number;
  is_secret: boolean;
  requirement: string;
};

export type QuestCard = {
  id: number;
  slug: string;
  name: string;
  description: string;
  cover_image: string | null;
  xp_reward: number;
  badge: Badge | null;
  estimated_minutes: number | null;
  is_featured: boolean;
  mission_count: number;
};

export type AnimalDetail = {
  id: number;
  slug: string;
  name: string;
  emoji: string;
  image: string | null;
  exhibit: string;
  exhibit_name: string;
  conservation_status: string;
  conservation_status_label: string;
  species: string;
  scientific_name: string;
  description: string;
  fun_facts: string[];
  conservation_info: string;
  tags: string[];
};

export type MarkerLookup = {
  code: string;
  exhibit: string;
  animal: string | null;
  label: string;
  zoo: { slug: string; name: string };
  exhibit_name: string;
  animal_name: string | null;
};

export type ScanResult = {
  marker: { code: string; label: string; exhibit: { slug: string; name: string } };
  animal: AnimalDetail | null;
  discovery: { result: "discovery" | "repeat" | "exhibit"; is_new: boolean; xp: number };
  completed_challenges: unknown[];
  unlocked_badges: unknown[];
  level_up: { number: number; title: string; xp_required: number } | null;
  totals: { xp: number; level: LevelInfo };
  suggested_quest: QuestCard | null;
};

// ---------------------------------------------------------------- endpoints
export const getHealth = () => api<Health>("/health/");
export const getZoo = (zoo: string) => api<ZooSummary>(`/zoos/${zoo}/`);
export const getQuests = (zoo: string) => api<QuestCard[]>(`/zoos/${zoo}/quests/`);
export const lookupMarker = (code: string) => api<MarkerLookup>(`/markers/${encodeURIComponent(code)}/`);
export const createSession = (zoo: string, team_name = "") =>
  api<Profile>(`/zoos/${zoo}/sessions/`, {
    method: "POST",
    body: JSON.stringify({ team_name }),
    token: null,
    retries: 2,
  });
export const getMe = () => api<Profile>("/me/");
export const updateTeamName = (team_name: string) =>
  api<Profile>("/me/", { method: "PATCH", body: JSON.stringify({ team_name }) });
export const scanMarker = (code: string) =>
  api<ScanResult>("/scan/", { method: "POST", body: JSON.stringify({ code }), retries: 3 });

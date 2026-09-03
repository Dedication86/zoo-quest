/**
 * The one place the frontend talks to the Django API.
 *
 * - Attaches X-Guest-Token (Blueprint, Section E).
 * - Normalizes errors into ApiError.
 * - Retries idempotent POSTs (scan, start, submit) a few times for spotty signal.
 *
 * Typed request/response shapes are generated from the OpenAPI schema in M2
 * (`npm run api:types`); until then endpoints are typed by hand at the call site.
 */
import { getGuestToken } from "./store";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: unknown,
  ) {
    super(typeof detail === "string" ? detail : `API error ${status}`);
  }
}

type Options = RequestInit & { retries?: number };

export async function api<T>(path: string, options: Options = {}): Promise<T> {
  const { retries = 0, headers, ...rest } = options;
  const token = getGuestToken();

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

// ---- endpoints that exist today ------------------------------------------
export type Health = { status: "ok" | "degraded"; database: string; version: string };
export const getHealth = () => api<Health>("/health/");

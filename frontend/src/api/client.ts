import type {
  ApiErrorBody,
  PreferencesPayload,
  RecommendationResponse,
} from "../types";
import { apiUrl } from "./config";

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    const detail = body.detail as ApiErrorBody | string | undefined;
    if (typeof detail === "string") return detail;
    if (detail?.message) return detail.message;
    return `Request failed (${res.status})`;
  } catch {
    return `Request failed (${res.status})`;
  }
}

export async function fetchHealth(): Promise<{ restaurants_loaded: number }> {
  const res = await fetch(apiUrl("/api/v1/health"));
  if (!res.ok) throw new Error("API unavailable");
  return res.json();
}

export async function fetchLocations(): Promise<string[]> {
  const res = await fetch(apiUrl("/api/v1/metadata/locations"));
  if (!res.ok) throw new Error("Could not load locations");
  const data = await res.json();
  return data.items as string[];
}

export async function fetchCuisines(): Promise<string[]> {
  const res = await fetch(apiUrl("/api/v1/metadata/cuisines"));
  if (!res.ok) throw new Error("Could not load cuisines");
  const data = await res.json();
  return data.items as string[];
}

export async function postRecommendations(
  payload: PreferencesPayload,
): Promise<RecommendationResponse> {
  const res = await fetch(apiUrl("/api/v1/recommendations"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  return res.json();
}

export function formatLabel(value: string): string {
  return value
    .replace(/[_-]/g, " ")
    .split(" ")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function cuisineOptions(raw: string[]): {
  labels: string[];
  labelToRaw: Record<string, string>;
} {
  const labelToRaw: Record<string, string> = {};
  const labels = raw.map((c) => {
    const label = formatLabel(c);
    labelToRaw[label] = c;
    return label;
  });
  return { labels, labelToRaw };
}

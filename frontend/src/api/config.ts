/** API origin: empty in dev (Vite proxy); set VITE_API_URL on Vercel for Railway. */

const raw = (import.meta.env.VITE_API_URL ?? "").trim();

export const API_BASE = raw.replace(/\/$/, "");

export function apiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${normalized}`;
}

/** Static assets (/images/*) — same origin as API in production. */
export function assetUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return API_BASE ? `${API_BASE}${normalized}` : normalized;
}

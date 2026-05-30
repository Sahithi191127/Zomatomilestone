/** API origin: empty in dev (Vite proxy); set VITE_API_URL on Vercel for Railway. */

const raw = (import.meta.env.VITE_API_URL ?? "").trim();

export const API_BASE = raw.replace(/\/$/, "");

/** True when a production build has no Railway API URL configured. */
export const isProductionApiMissing =
  import.meta.env.PROD && API_BASE.length === 0;

export function apiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${normalized}`;
}

/**
 * Static assets (/images/*).
 * Production: Railway via VITE_API_URL when set; else Vercel `public/images/`.
 * Dev: relative path → Vite proxy to :8000.
 */
export function assetUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (API_BASE) {
    return `${API_BASE}${normalized}`;
  }
  return normalized;
}

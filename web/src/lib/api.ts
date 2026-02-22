const CACHE_TTL_MS = 5 * 60 * 1000; // 5 min
const CACHE_PREFIX = 'sp_api_';

function cacheKey(url: string): string {
  return CACHE_PREFIX + url.replace(/\//g, '_');
}

/** Get cached JSON if present and not expired. */
function getCached<T>(url: string): T | null {
  if (typeof sessionStorage === 'undefined') return null;
  try {
    const raw = sessionStorage.getItem(cacheKey(url));
    if (!raw) return null;
    const { data, ts } = JSON.parse(raw) as { data: T; ts: number };
    if (Date.now() - ts > CACHE_TTL_MS) return null;
    return data;
  } catch {
    return null;
  }
}

function setCached<T>(url: string, data: T): void {
  if (typeof sessionStorage === 'undefined') return;
  try {
    sessionStorage.setItem(cacheKey(url), JSON.stringify({ data, ts: Date.now() }));
  } catch {
    // ignore quota / private mode
  }
}

export const BACKEND_HELP =
  'Cannot reach the server. Ensure the backend is running at http://localhost:8000. From project root run: python -m uvicorn api.main:app --port 8000';

/**
 * API fetch helper with consistent error handling.
 * Use apiFetchWithCache for dashboard/pipeline endpoints to get quick reloads.
 */
export async function apiFetch<T>(url: string, useCache = false): Promise<T> {
  if (useCache) {
    const cached = getCached<T>(url);
    if (cached != null) return cached;
  }
  let r: Response;
  try {
    r = await fetch(url);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    throw new Error(msg.includes('fetch') || msg.includes('Network') ? BACKEND_HELP : msg);
  }
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    const detail = typeof err?.detail === 'string' ? err.detail : `API error ${r.status}`;
    throw new Error(detail);
  }
  const data = (await r.json()) as T;
  if (useCache) setCached(url, data);
  return data;
}

/** Fetch with 5-min session cache for fast reloads when data is unchanged. */
export async function apiFetchWithCache<T>(url: string): Promise<T> {
  return apiFetch<T>(url, true);
}

/**
 * API fetch helper with consistent error handling.
 */
export async function apiFetch<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(
      typeof err?.detail === 'string' ? err.detail : `API error ${r.status}`
    );
  }
  return r.json();
}

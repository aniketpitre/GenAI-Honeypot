import { Alert, AlertStatus, HoneyToken, Stats, TokenType } from '../types';

const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? '/api/v1';
const KEY = 'tripwire.adminToken';

export class AuthError extends Error {}

export const auth = {
  get: () => sessionStorage.getItem(KEY),
  set: (t: string) => sessionStorage.setItem(KEY, t),
  clear: () => sessionStorage.removeItem(KEY),
};

async function request(path: string, init: RequestInit = {}): Promise<Response> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${auth.get() ?? ''}`,
      ...init.headers,
    },
  });
  if (res.status === 401) throw new AuthError('Invalid admin token');
  if (!res.ok) throw new Error(`${init.method ?? 'GET'} ${path} failed: ${res.status}`);
  return res;
}

const json = async <T,>(p: string, init?: RequestInit) => (await request(p, init)).json() as Promise<T>;
const body = (b: unknown): RequestInit => ({ body: JSON.stringify(b) });

export const api = {
  getTokens: () => json<HoneyToken[]>('/tokens'),
  getStats: () => json<Stats>('/stats'),
  getAlerts: () => json<Alert[]>('/alerts?limit=500'),
  createToken: (t: { name: string; type: TokenType; decoy_url?: string }) =>
    json<HoneyToken>('/tokens', { method: 'POST', ...body(t) }),
  updateToken: (id: string, patch: Partial<Pick<HoneyToken, 'name' | 'status'>>) =>
    json<HoneyToken>(`/tokens/${id}`, { method: 'PATCH', ...body(patch) }),
  deleteToken: async (id: string) => { await request(`/tokens/${id}`, { method: 'DELETE' }); },
  updateAlert: (id: number, patch: { notes?: string; status?: AlertStatus }) =>
    json<Alert>(`/alerts/${id}`, { method: 'PATCH', ...body(patch) }),
  generateUrls: async (prompt: string) =>
    (await json<{ urls: string[] }>('/generate/urls', { method: 'POST', ...body({ prompt }) })).urls,
  downloadToken: async (id: string): Promise<Blob> => (await request(`/tokens/${id}/download`)).blob(),
};

/**
 * Subscribe to server-sent "alert" events. EventSource can't send an
 * Authorization header, so this reads the stream with fetch. Reconnects with
 * backoff until the returned function is called.
 */
export function subscribeAlerts(onAlert: () => void, onAuthError: () => void): () => void {
  const ctrl = new AbortController();
  let delay = 1000;
  (async () => {
    while (!ctrl.signal.aborted) {
      try {
        const res = await fetch(`${BASE}/stream`, {
          headers: { Authorization: `Bearer ${auth.get() ?? ''}` },
          signal: ctrl.signal,
        });
        if (res.status === 401) { onAuthError(); return; }
        if (!res.ok || !res.body) throw new Error(`stream ${res.status}`);
        delay = 1000;
        const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
        let buf = '';
        for (;;) {
          const { value, done } = await reader.read();
          if (done) break;
          buf += value;
          let i: number;
          while ((i = buf.indexOf('\n\n')) >= 0) {
            const frame = buf.slice(0, i);
            buf = buf.slice(i + 2);
            if (frame.includes('event: alert')) onAlert();
          }
        }
      } catch {
        if (ctrl.signal.aborted) return;
      }
      await new Promise((r) => setTimeout(r, delay));
      delay = Math.min(delay * 2, 15000);
    }
  })();
  return () => ctrl.abort();
}

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

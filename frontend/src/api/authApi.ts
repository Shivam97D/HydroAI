const BASE = import.meta.env.VITE_API_URL ?? ''

async function req<T>(path: string, body: object): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

type AuthUser = { id: string; name: string; email: string; location: string; role: string }
type AuthResponse = { token: string; user: AuthUser }

export const authApi = {
  register: (name: string, email: string, password: string, location: string) =>
    req<AuthResponse>('/auth/register', { name, email, password, location }),
  login: (email: string, password: string) =>
    req<AuthResponse>('/auth/login', { email, password }),
  subscribe: (name: string, email: string, location: string) =>
    req<{ message: string; email: string }>('/subscribers/subscribe', { name, email, location }),
}

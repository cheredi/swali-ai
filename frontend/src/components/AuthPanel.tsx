import { useEffect, useState } from 'react'

type AuthMode = 'login' | 'register'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export function AuthPanel() {
  const [mode, setMode] = useState<AuthMode>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [userEmail, setUserEmail] = useState<string | null>(null)

  const token = localStorage.getItem('swali_access_token')

  const loadMe = async () => {
    const savedToken = localStorage.getItem('swali_access_token')
    if (!savedToken) {
      setUserEmail(null)
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${savedToken}` },
      })
      if (!response.ok) {
        localStorage.removeItem('swali_access_token')
        setUserEmail(null)
        return
      }
      const payload = (await response.json()) as { email?: string }
      setUserEmail(payload.email ?? null)
    } catch {
      setUserEmail(null)
    }
  }

  useEffect(() => {
    loadMe()
  }, [])

  const submitAuth = async () => {
    setError('')
    if (!email.trim() || !password.trim()) {
      setError('Email and password are required.')
      return
    }

    setIsLoading(true)
    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register'
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const payload = (await response.json().catch(() => ({}))) as { detail?: string }
        throw new Error(payload.detail ?? 'Authentication failed.')
      }

      const payload = (await response.json()) as { access_token: string; email: string }
      localStorage.setItem('swali_access_token', payload.access_token)
      setUserEmail(payload.email)
      setPassword('')
    } catch (authError) {
      const message = authError instanceof Error ? authError.message : 'Authentication failed.'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('swali_access_token')
    setUserEmail(null)
    setPassword('')
  }

  if (token && userEmail) {
    return (
      <div className="rounded-2xl border border-green-200 bg-green-50 px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-green-700">Authenticated</p>
        <p className="mt-1 text-sm font-medium text-green-900">{userEmail}</p>
        <button
          type="button"
          onClick={logout}
          className="mt-3 rounded-full border border-green-300 bg-white px-3 py-1.5 text-xs font-semibold text-green-800 transition hover:border-green-400"
        >
          Log out
        </button>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-black/10 bg-white px-4 py-3">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setMode('login')}
          className={`rounded-full px-3 py-1.5 text-xs font-semibold ${
            mode === 'login' ? 'bg-neutral-900 text-white' : 'border border-neutral-300 text-neutral-700'
          }`}
        >
          Login
        </button>
        <button
          type="button"
          onClick={() => setMode('register')}
          className={`rounded-full px-3 py-1.5 text-xs font-semibold ${
            mode === 'register' ? 'bg-neutral-900 text-white' : 'border border-neutral-300 text-neutral-700'
          }`}
        >
          Register
        </button>
      </div>

      <div className="mt-3 grid gap-2">
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Email"
          className="rounded-lg border border-neutral-300 px-3 py-2 text-sm outline-none transition focus:border-orange-500"
        />
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Password"
          className="rounded-lg border border-neutral-300 px-3 py-2 text-sm outline-none transition focus:border-orange-500"
        />
        {error ? <p className="text-xs text-red-600">{error}</p> : null}
        <button
          type="button"
          disabled={isLoading}
          onClick={submitAuth}
          className="rounded-full bg-orange-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-orange-500 disabled:opacity-60"
        >
          {isLoading ? 'Working...' : mode === 'login' ? 'Log in' : 'Create account'}
        </button>
      </div>
    </div>
  )
}

import { useState } from 'react'

type AuthMode = 'login' | 'register'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type AuthFormProps = {
  initialMode?: AuthMode
  onSuccess: () => void
}

export function AuthForm({ initialMode = 'login', onSuccess }: AuthFormProps) {
  const [mode, setMode] = useState<AuthMode>(initialMode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

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

      const payload = (await response.json()) as { access_token: string }
      localStorage.setItem('swali_access_token', payload.access_token)
      onSuccess()
    } catch (authError) {
      const message = authError instanceof Error ? authError.message : 'Authentication failed.'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="rounded-2xl border border-black/10 bg-white p-5 shadow-[0_1px_3px_rgba(0,0,0,0.08)]">
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

import { Link, useNavigate } from 'react-router-dom'
import { AuthForm } from '../components/AuthForm'

type AuthPageProps = {
  mode: 'login' | 'register'
}

export function AuthPage({ mode }: AuthPageProps) {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-[#f9f6f2] px-4 py-8 text-[#555] antialiased sm:px-6 md:py-12 lg:px-8">
      <div className="mx-auto w-full max-w-md">
        <Link
          to="/"
          className="mb-4 inline-flex rounded-full border border-neutral-300 bg-white px-4 py-2 text-sm font-semibold text-neutral-700 transition hover:border-neutral-400"
        >
          ← Back to Home
        </Link>
        <h1 className="mb-2 text-3xl font-black text-neutral-950">{mode === 'login' ? 'Welcome back' : 'Create account'}</h1>
        <p className="mb-4 text-sm font-normal text-[#555]">Authenticate to continue into the practice workspace.</p>
        <AuthForm initialMode={mode} onSuccess={() => navigate('/practice?mode=general')} />
      </div>
    </div>
  )
}
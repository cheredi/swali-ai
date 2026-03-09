import { useMemo } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useState } from 'react'
import { AuthModal } from '../components/AuthModal'
import { PracticeSection } from '../components/PracticeSection'

type PracticeMode = 'general' | 'job_aligned' | 'mock_interview'

export function PracticePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)

  const activeMode = useMemo<PracticeMode>(() => {
    const mode = searchParams.get('mode')
    if (mode === 'job_aligned') return 'job_aligned'
    if (mode === 'mock_interview') return 'mock_interview'
    return 'general'
  }, [searchParams])

  const onModeChange = (mode: PracticeMode) => {
    setSearchParams({ mode })
  }

  return (
    <div className="min-h-screen bg-[#f9f6f2] px-4 py-6 text-[#555] antialiased sm:px-6 md:py-10 lg:px-8">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
        <div className="flex items-center justify-between rounded-2xl border border-black/10 bg-white px-4 py-3">
          <Link
            to="/"
            className="rounded-full border border-neutral-300 bg-white px-4 py-2 text-sm font-semibold text-neutral-700 transition hover:border-neutral-400"
          >
            ← Back to Home
          </Link>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-orange-700">Practice Workspace</p>
        </div>

        <PracticeSection
          activeMode={activeMode}
          onModeChange={onModeChange}
          onRequireAuth={() => setIsAuthModalOpen(true)}
        />
      </div>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        initialMode="login"
        onSuccess={() => {
          setIsAuthModalOpen(false)
          navigate('/practice')
        }}
      />
    </div>
  )
}

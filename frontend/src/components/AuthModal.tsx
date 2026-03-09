import { AuthForm } from './AuthForm'

type AuthModalProps = {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  initialMode?: 'login' | 'register'
}

export function AuthModal({ isOpen, onClose, onSuccess, initialMode = 'login' }: AuthModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 p-4" role="dialog" aria-modal="true">
      <div className="w-full max-w-md rounded-2xl bg-[#f9f6f2] p-4 shadow-[0_20px_50px_rgba(0,0,0,0.25)]">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-neutral-900">Sign in to continue</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-neutral-300 bg-white px-2.5 py-1 text-xs font-semibold text-neutral-600"
          >
            Close
          </button>
        </div>
        <p className="mb-3 text-sm font-normal text-[#555]">
          Login or create an account to start and save your practice session.
        </p>
        <AuthForm initialMode={initialMode} onSuccess={onSuccess} />
      </div>
    </div>
  )
}

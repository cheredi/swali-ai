import { useScrollReveal } from '../hooks/useScrollReveal'

type SocialProofStripProps = {
  labels: string[]
}

export function SocialProofStrip({ labels }: SocialProofStripProps) {
  const { ref, revealClass } = useScrollReveal<HTMLElement>()

  return (
    <section ref={ref} className={`visible transition-all duration-700 ease-out ${revealClass}`}>
      <div className="rounded-2xl border border-black/5 bg-white/70 px-4 py-5 shadow-[0_16px_45px_rgba(16,10,6,0.06)] backdrop-blur-sm md:px-6">
        <p className="mb-3 text-center text-xs font-semibold uppercase tracking-[0.2em] text-neutral-500">
          Interview Domains Covered
        </p>
        <div className="flex flex-wrap justify-center gap-2.5">
          {labels.map((label) => (
            <div
              key={label}
              className="rounded-full border border-neutral-200 bg-white px-4 py-2 text-sm font-medium text-neutral-700"
            >
              {label}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

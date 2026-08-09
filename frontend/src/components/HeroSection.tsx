import { useScrollReveal } from '../hooks/useScrollReveal'

type HeroSectionProps = {
  eyebrow: string
  headline: string
  subtext: string
  primaryCta: { label: string; href: string }
  secondaryCta: { label: string; href: string }
  onPrimaryClick?: () => void
}

export function HeroSection({ eyebrow, headline, subtext, primaryCta, secondaryCta, onPrimaryClick }: HeroSectionProps) {
  const { ref, revealClass } = useScrollReveal<HTMLElement>()

  const handleSecondaryClick = (event: React.MouseEvent<HTMLAnchorElement>) => {
    if (!secondaryCta.href.startsWith('#')) return
    event.preventDefault()
    const target = document.querySelector<HTMLElement>(secondaryCta.href)
    target?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <section
      ref={ref}
      className={`visible transition-all duration-700 ease-out ${revealClass} border border-black/5 bg-white/85 px-6 py-14 shadow-[0_24px_80px_rgba(21,14,10,0.08)] backdrop-blur-sm md:px-10 md:py-20`}
    >
      <div className="mx-auto max-w-5xl">
        <p className="mb-4 text-xs font-semibold uppercase tracking-[0.25em] text-orange-700">{eyebrow}</p>
        <h1 className="max-w-4xl text-4xl font-black leading-[0.96] tracking-[-0.03em] text-neutral-950 sm:text-5xl md:text-6xl lg:text-7xl">
          {headline}
        </h1>
        <p className="mt-6 max-w-2xl text-base font-normal leading-relaxed text-[#555] md:text-lg">{subtext}</p>

        <div className="mt-9 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={onPrimaryClick}
            className="rounded-full bg-orange-600 px-6 py-3 text-sm font-semibold text-white shadow-[0_14px_30px_rgba(242,101,36,0.35)] transition hover:-translate-y-0.5 hover:bg-orange-500"
          >
            {primaryCta.label}
          </button>
          <a
            href={secondaryCta.href}
            onClick={handleSecondaryClick}
            className="rounded-full border border-neutral-300 bg-white px-6 py-3 text-sm font-semibold text-neutral-700 transition hover:-translate-y-0.5 hover:border-neutral-400"
          >
            {secondaryCta.label}
          </a>
        </div>

        <div className="mt-10 overflow-hidden rounded-2xl border border-black/10 bg-[#111217] p-4 shadow-[0_24px_80px_rgba(10,10,15,0.35)] md:p-5">
          <div className="mb-4 flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
            <span className="h-2.5 w-2.5 rounded-full bg-yellow-400" />
            <span className="h-2.5 w-2.5 rounded-full bg-green-400" />
            <p className="ml-2 text-xs text-white/70">Swali Practice Workspace</p>
          </div>
          <div className="grid gap-3 md:grid-cols-[280px_1fr]">
            <aside className="rounded-xl border border-white/10 bg-white/5 p-3">
              <p className="text-xs uppercase tracking-[0.2em] text-orange-300">Session</p>
              <h3 className="mt-2 text-sm font-semibold text-white">Backend Interview Prep</h3>
              <p className="mt-1 text-xs text-white/65">Question 3 of 8 · Standard set</p>
              <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/10">
                <div className="h-full w-[37%] rounded-full bg-orange-400" />
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="rounded-full bg-orange-500/20 px-2 py-1 text-[11px] text-orange-200">Job-Aligned</span>
                <span className="rounded-full bg-sky-500/20 px-2 py-1 text-[11px] text-sky-200">RAG-Cited</span>
              </div>
            </aside>
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <p className="text-xs uppercase tracking-[0.18em] text-white/55">Live response</p>
              <p className="mt-2 text-sm text-white/90">
                Start with a hash map lookup to track complements in one pass, then discuss collision handling and
                tradeoffs for memory-constrained environments.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="rounded-full bg-white/10 px-2 py-1 text-[11px] text-white/80">NeetCode</span>
                <span className="rounded-full bg-white/10 px-2 py-1 text-[11px] text-white/80">LeetCode</span>
                <span className="rounded-full bg-white/10 px-2 py-1 text-[11px] text-white/80">System Design</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

import { useScrollReveal } from '../hooks/useScrollReveal'
import { Briefcase, Database, Layers3, Route, SearchCheck, Sparkles, type LucideIcon } from 'lucide-react'

type FeatureItem = {
  id: string
  category: string
  title: string
  description: string
  icon: 'briefcase' | 'layers' | 'sparkles' | 'search' | 'database' | 'route'
}

type FeatureGridSectionProps = {
  title: string
  subtitle: string
  features: FeatureItem[]
  onFeatureClick?: (featureId: string) => void
}

export function FeatureGridSection({ title, subtitle, features, onFeatureClick }: FeatureGridSectionProps) {
  const { ref, revealClass } = useScrollReveal<HTMLElement>()

  const iconMap: Record<FeatureItem['icon'], LucideIcon> = {
    briefcase: Briefcase,
    layers: Layers3,
    sparkles: Sparkles,
    search: SearchCheck,
    database: Database,
    route: Route,
  }

  return (
    <section ref={ref} className={`visible transition-all duration-700 ease-out ${revealClass}`} id="how-it-works">
      <div className="mb-8">
        <h2 className="text-3xl font-semibold tracking-[-0.02em] text-neutral-950 md:text-4xl">{title}</h2>
        <p className="mt-3 max-w-2xl font-normal text-[#555]">{subtitle}</p>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((feature) => (
          <article
            key={feature.id}
            onClick={() => onFeatureClick?.(feature.id)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault()
                onFeatureClick?.(feature.id)
              }
            }}
            role={onFeatureClick ? 'button' : undefined}
            tabIndex={onFeatureClick ? 0 : undefined}
            className="group overflow-hidden rounded-2xl border border-black/5 bg-white/90 shadow-[0_12px_35px_rgba(19,13,9,0.06)] transition duration-300 hover:-translate-y-1.5 hover:shadow-[0_20px_45px_rgba(19,13,9,0.12)]"
          >
            <div className="flex h-40 items-center justify-center bg-[#1a1a1a] p-5">
              {(() => {
                const Icon = iconMap[feature.icon]
                return <Icon size={48} strokeWidth={2.2} color="#E84C1E" />
              })()}
            </div>
            <div className="p-5">
              <span className="rounded-full bg-orange-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-wide text-orange-700">
                {feature.category}
              </span>
              <h3 className="mt-3 text-xl font-semibold tracking-[-0.01em] text-neutral-900">{feature.title}</h3>
              <p className="mt-2 text-sm font-normal leading-relaxed text-[#555]">{feature.description}</p>
              <p className="mt-3 text-sm font-semibold text-orange-700">Open practice →</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

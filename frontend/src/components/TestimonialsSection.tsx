import { useScrollReveal } from '../hooks/useScrollReveal'

type Testimonial = {
  id: string
  quote: string
  author: string
  role: string
  avatar: string
}

type TestimonialsSectionProps = {
  title: string
  items: Testimonial[]
}

export function TestimonialsSection({ title, items }: TestimonialsSectionProps) {
  const { ref, revealClass } = useScrollReveal<HTMLElement>()

  return (
    <section ref={ref} className={`visible transition-all duration-700 ease-out ${revealClass}`} id="testimonials">
      <h2 className="mb-6 text-3xl font-semibold tracking-[-0.02em] text-neutral-950 md:text-4xl">{title}</h2>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <figure
            key={item.id}
            className="rounded-2xl border border-black/5 bg-white/90 p-5 shadow-[0_10px_30px_rgba(19,13,9,0.06)]"
          >
            <blockquote className="text-sm leading-relaxed text-neutral-700">“{item.quote}”</blockquote>
            <figcaption className="mt-5 flex items-center gap-3">
              <img src={item.avatar} alt={item.author} className="h-11 w-11 rounded-full object-cover" loading="lazy" />
              <div>
                <p className="text-sm font-semibold text-neutral-900">{item.author}</p>
                <p className="text-xs text-neutral-500">{item.role}</p>
              </div>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  )
}

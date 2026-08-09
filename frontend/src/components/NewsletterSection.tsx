import { useScrollReveal } from '../hooks/useScrollReveal'

type NewsletterSectionProps = {
  title: string
  subtitle: string
  placeholder: string
  buttonLabel: string
}

export function NewsletterSection({ title, subtitle, placeholder, buttonLabel }: NewsletterSectionProps) {
  const { ref, revealClass } = useScrollReveal<HTMLElement>()

  return (
    <section ref={ref} className={`visible transition-all duration-700 ease-out ${revealClass}`} id="newsletter">
      <div className="rounded-2xl border border-black/10 bg-gradient-to-br from-orange-50 to-white p-7 text-center md:p-10">
        <h2 className="text-3xl font-semibold tracking-[-0.02em] text-neutral-950 md:text-4xl">{title}</h2>
        <p className="mx-auto mt-3 max-w-2xl text-neutral-600">{subtitle}</p>
        <form className="mx-auto mt-7 flex w-full max-w-xl flex-col gap-3 sm:flex-row" onSubmit={(e) => e.preventDefault()}>
          <input
            type="email"
            placeholder={placeholder}
            className="h-12 flex-1 rounded-full border border-neutral-300 bg-white px-5 text-sm text-neutral-700 outline-none transition focus:border-orange-500"
          />
          <button
            type="submit"
            className="h-12 rounded-full bg-orange-600 px-6 text-sm font-semibold text-white transition hover:bg-orange-500"
          >
            {buttonLabel}
          </button>
        </form>
      </div>
    </section>
  )
}

import { useState } from 'react'
import { useScrollReveal } from '../hooks/useScrollReveal'

type FAQItem = {
  id: string
  question: string
  answer: string
}

type FAQSectionProps = {
  title: string
  items: FAQItem[]
}

export function FAQSection({ title, items }: FAQSectionProps) {
  const { ref, revealClass } = useScrollReveal<HTMLElement>()
  const [openId, setOpenId] = useState<string | null>(items[0]?.id ?? null)

  return (
    <section ref={ref} className={`visible transition-all duration-700 ease-out ${revealClass}`} id="faq">
      <h2 className="mb-6 text-3xl font-semibold tracking-[-0.02em] text-neutral-950 md:text-4xl">{title}</h2>
      <div className="space-y-3">
        {items.map((item) => {
          const isOpen = item.id === openId
          return (
            <div key={item.id} className="overflow-hidden rounded-xl border border-black/10 bg-white/90">
              <button
                type="button"
                onClick={() => setOpenId(isOpen ? null : item.id)}
                className="flex w-full items-center justify-between px-5 py-4 text-left"
              >
                <span className="font-medium text-neutral-900">{item.question}</span>
                <span className="ml-3 text-orange-600">{isOpen ? '−' : '+'}</span>
              </button>
              <div
                className={`grid transition-all duration-300 ${isOpen ? 'grid-rows-[1fr] border-t border-black/5' : 'grid-rows-[0fr]'}`}
              >
                <p className="overflow-hidden px-5 py-3 text-sm leading-relaxed text-neutral-600">{item.answer}</p>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

import { useEffect, useRef, useState } from 'react'

export function useScrollReveal<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.unobserve(entry.target)
        }
      },
      {
        threshold: 0.15,
        rootMargin: '0px 0px -40px 0px',
      },
    )

    observer.observe(element)
    return () => observer.disconnect()
  }, [])

  const revealClass = isVisible ? 'visible opacity-100 translate-y-0' : 'opacity-0 translate-y-8'

  return { ref, revealClass }
}

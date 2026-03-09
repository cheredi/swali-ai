import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthModal } from '../components/AuthModal'
import { FAQSection } from '../components/FAQSection'
import { FeatureGridSection } from '../components/FeatureGridSection'
import { FooterSection } from '../components/FooterSection'
import { HeroSection } from '../components/HeroSection'
import { NewsletterSection } from '../components/NewsletterSection'
import { SocialProofStrip } from '../components/SocialProofStrip'
import { TestimonialsSection } from '../components/TestimonialsSection'

export function LandingPage() {
  const navigate = useNavigate()

  const heroData = {
    eyebrow: 'Swali-AI · Interview Preparation Platform',
    headline: 'From random practice to role-aligned interview readiness.',
    subtext:
      'Swali-AI helps engineers prepare faster with job-specific interview drills, retrieval-grounded coaching, and structured learning loops for coding, system design, and AI/ML.',
    primaryCta: { label: 'Start Practicing', href: '/practice?mode=general' },
    secondaryCta: { label: 'See How It Works', href: '#how-it-works' },
  }

  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)

  const socialProofLabels = [
    'Backend Interviews',
    'System Design Prep',
    'AI/ML Interview Drills',
    'Retrieval-Grounded Coaching',
    'Role-Aligned Question Sets',
    'Progressive Hinting',
    'Follow-up Simulation',
    'FastAPI + Gemini + Chroma',
  ]

  const features = [
    {
      id: 'f1',
      category: 'Role Alignment',
      title: 'Job Description Aligned Practice',
      description:
        'Paste a JD and generate interview questions focused on the exact skills, tools, and responsibilities that role expects.',
      icon: 'briefcase' as const,
    },
    {
      id: 'f2',
      category: 'General Preparation',
      title: 'Broad Interview Practice Mode',
      description:
        'Get balanced question sets for coding, architecture, and applied reasoning when you want robust all-round prep.',
      icon: 'layers' as const,
    },
    {
      id: 'f3',
      category: 'Coaching',
      title: 'Progressive Hints and Follow-ups',
      description:
        'Move from nudge to deep guidance and then test your depth with follow-up prompts that mimic real interview pressure.',
      icon: 'sparkles' as const,
    },
    {
      id: 'f4',
      category: 'RAG Engine',
      title: 'Retrieval-Grounded Responses',
      description:
        'Answers and practice sets are backed by indexed interview corpora, improving relevance and reducing generic output.',
      icon: 'search' as const,
    },
    {
      id: 'f5',
      category: 'Question Bank',
      title: 'Expanding Multi-Source Corpus',
      description:
        'Uses curated NeetCode, system design material, AI/ML interview data, and added LeetCode coverage for breadth.',
      icon: 'database' as const,
    },
    {
      id: 'f6',
      category: 'Workflow',
      title: 'Built for Consistent Practice',
      description:
        'Turn interview prep into a repeatable system with clear modes, source transparency, and fast iteration loops.',
      icon: 'route' as const,
    },
  ]

  const testimonials = [
    {
      id: 't1',
      quote:
        'The job-aligned mode forced me to prepare for the exact role language instead of generic leetcode-only prep.',
      author: 'Lena K.',
      role: 'Backend Engineer Candidate',
      avatar: 'https://ui-avatars.com/api/?name=Lena+K&background=FED7AA&color=7C2D12&size=240',
    },
    {
      id: 't2',
      quote:
        'I liked that follow-up questions tested trade-offs and edge-case thinking, not just memorized solutions.',
      author: 'Marcus D.',
      role: 'Senior SWE Applicant',
      avatar: 'https://ui-avatars.com/api/?name=Marcus+D&background=BFDBFE&color=1E3A8A&size=240',
    },
    {
      id: 't3',
      quote:
        'The source-grounded coaching made the explanations feel less random and much more interview-relevant.',
      author: 'Priya R.',
      role: 'ML Engineer Candidate',
      avatar: 'https://ui-avatars.com/api/?name=Priya+R&background=C7D2FE&color=312E81&size=240',
    },
  ]

  const faqs = [
    {
      id: 'q1',
      question: 'How is this different from normal AI chat tools?',
      answer:
        'Swali-AI uses retrieval-augmented generation. It first fetches relevant interview content from a curated vector index, then generates grounded responses from that context.',
    },
    {
      id: 'q2',
      question: 'Can I practice without a job description?',
      answer:
        'Yes. General Practice mode generates balanced interview sets across coding, systems, and problem-solving fundamentals.',
    },
    {
      id: 'q3',
      question: 'How does JD-aligned mode work?',
      answer:
        'You paste or attach a role description. Swali-AI aligns generated questions to the role requirements and prioritizes high-signal competencies from that JD.',
    },
    {
      id: 'q4',
      question: 'Can I track improvement across repeated practice sessions?',
      answer:
        'Yes. A good workflow is to repeat job-aligned and general drills weekly, compare your responses over time, and use hint levels plus follow-up prompts to measure depth and consistency.',
    },
  ]

  const newsletter = {
    title: 'Get weekly interview drill packs',
    subtitle:
      'New question bundles, role-specific prep tips, and practical system-design prompts delivered to your inbox.',
    placeholder: 'Enter your email',
    buttonLabel: 'Subscribe',
  }

  const footer = {
    brand: 'Swali-AI',
    copyright: '© 2026 Swali-AI. Built for deliberate interview preparation.',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'Testimonials', href: '#testimonials' },
      { label: 'FAQ', href: '#faq' },
      { label: 'Newsletter', href: '#newsletter' },
    ],
    socialLinks: [
      { label: 'GitHub', href: '#' },
      { label: 'LinkedIn', href: '#' },
      { label: 'Substack', href: '#' },
      { label: 'X / Twitter', href: '#' },
    ],
  }

  const handleFeatureClick = (featureId: string) => {
    const mode = featureId === 'f1' ? 'job_aligned' : 'general'
    navigate(`/practice?mode=${mode}`)
  }

  const handleStartPracticing = () => {
    const token = localStorage.getItem('swali_access_token')
    if (token) {
      navigate('/practice?mode=general')
      return
    }
    setIsAuthModalOpen(true)
  }

  return (
    <div className="min-h-screen bg-[#f9f6f2] text-[#555] antialiased">
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 md:py-10 lg:px-8">
        <HeroSection {...heroData} onPrimaryClick={handleStartPracticing} />
        <SocialProofStrip labels={socialProofLabels} />
        <section className="rounded-2xl bg-[#0f1116] px-6 py-10 text-white md:px-10" aria-label="product-metrics">
          <p className="text-xs uppercase tracking-[0.24em] text-orange-300">Why teams use Swali-AI</p>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <p className="text-3xl font-semibold">500+</p>
              <p className="mt-1 text-sm text-white/75">Indexed interview questions</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <p className="text-3xl font-semibold">6</p>
              <p className="mt-1 text-sm text-white/75">Practice domains and modes</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <p className="text-3xl font-semibold">2</p>
              <p className="mt-1 text-sm text-white/75">Retrieval methods</p>
              <p className="mt-1 text-xs text-white/60">Dense + sparse hybrid</p>
            </div>
          </div>
        </section>
        <FeatureGridSection
          title="What you can do with Swali-AI"
          subtitle="A practice system designed to map interview preparation to real role requirements while still strengthening core fundamentals."
          features={features}
          onFeatureClick={handleFeatureClick}
        />
        <TestimonialsSection title="What candidates value most" items={testimonials} />
        <FAQSection title="Frequently asked questions" items={faqs} />
        <NewsletterSection {...newsletter} />
        <FooterSection {...footer} />
      </div>
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        initialMode="login"
        onSuccess={() => {
          setIsAuthModalOpen(false)
          navigate('/practice?mode=general')
        }}
      />
    </div>
  )
}

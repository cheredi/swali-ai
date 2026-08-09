import { useEffect, useMemo, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Sparkles } from 'lucide-react'
import { useScrollReveal } from '../hooks/useScrollReveal'

type PracticeMode = 'general' | 'job_aligned' | 'mock_interview'

type PracticeSectionProps = {
  initialMode?: PracticeMode
  activeMode: PracticeMode
  onModeChange: (mode: PracticeMode) => void
  onRequireAuth: () => void
}

type PracticeResponse = {
  questions: string
  model: string
  tokens_used: number
  sources: Array<{ id: string; title: string; type?: string; difficulty?: string }>
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const SAMPLE_JD_PLACEHOLDER = `Senior Backend Engineer (Python/FastAPI)

Responsibilities:
- Build and maintain APIs for high-traffic services
- Improve caching, SQL query performance, and reliability
- Collaborate with ML teams on model inference endpoints

Must have: Python, FastAPI, PostgreSQL, Redis, system design.`

const DEPTH_OPTIONS = [
  { value: 5, label: 'Quick', description: 'Fast warm-up set' },
  { value: 10, label: 'Standard', description: 'Balanced depth and breadth' },
  { value: 15, label: 'Deep Dive', description: 'Full interview simulation' },
]

const parseQuestions = (raw: string): string[] => {
  const lines = raw
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  const numbered = lines
    .filter((line) => /^\d+[\).\-]\s+/.test(line) || /^[-*]\s+/.test(line))
    .map((line) => line.replace(/^\d+[\).\-]\s+/, '').replace(/^[-*]\s+/, ''))

  if (numbered.length >= 2) return numbered
  return raw.trim() ? [raw.trim()] : []
}

export function PracticeSection({ activeMode, onModeChange, onRequireAuth }: PracticeSectionProps) {
  const { ref, revealClass } = useScrollReveal<HTMLElement>()
  const [focusArea, setFocusArea] = useState('')
  const [difficulty, setDifficulty] = useState('mixed')
  const [jobDescription, setJobDescription] = useState('')
  const [questionCount, setQuestionCount] = useState(10)
  const [selectedQuestionIndex, setSelectedQuestionIndex] = useState(0)
  const [answerDraft, setAnswerDraft] = useState('')
  const [confidence, setConfidence] = useState<'low' | 'medium' | 'high' | null>(null)
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [isScoring, setIsScoring] = useState(false)
  const [mockScore, setMockScore] = useState<Record<string, unknown> | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [streamedText, setStreamedText] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState<PracticeResponse | null>(null)
  const [sessionId] = useState(() => `sess_${Math.random().toString(36).slice(2, 10)}`)

  const fileAccept = useMemo(() => '.txt,.md,.docx', [])
  const modeAccent =
    activeMode === 'job_aligned'
      ? 'from-orange-50 to-orange-100/40 border-orange-200'
      : activeMode === 'mock_interview'
        ? 'from-violet-50 to-fuchsia-100/40 border-violet-200'
        : 'from-sky-50 to-cyan-100/40 border-sky-200'

  const questions = useMemo(() => parseQuestions(result?.questions ?? ''), [result?.questions])
  const selectedQuestion = questions[selectedQuestionIndex] ?? ''
  const progressPercent = questions.length
    ? Math.min(100, Math.round(((selectedQuestionIndex + 1) / questions.length) * 100))
    : 0

  const readUploadedFile = async (file: File) => {
    const name = file.name.toLowerCase()
    if (name.endsWith('.txt') || name.endsWith('.md')) {
      return file.text()
    }
    if (name.endsWith('.docx')) {
      const mammoth = await import('mammoth')
      const arrayBuffer = await file.arrayBuffer()
      const extraction = await mammoth.extractRawText({ arrayBuffer })
      return extraction.value
    }
    throw new Error('Unsupported file type. Please upload .txt, .md, or .docx.')
  }

  const onFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      setError('')
      const text = await readUploadedFile(file)
      setJobDescription((prev) => (prev.trim() ? `${prev}\n\n${text}` : text))
    } catch (uploadError) {
      const uploadMessage = uploadError instanceof Error ? uploadError.message : 'Failed to parse uploaded file.'
      setError(uploadMessage)
    } finally {
      event.target.value = ''
    }
  }

  const submitPractice = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')

    const token = localStorage.getItem('swali_access_token')
    if (!token) {
      onRequireAuth()
      return
    }

    setResult(null)
    setStreamedText('')
    setSelectedQuestionIndex(0)
    setAnswerDraft('')
    setConfidence(null)
    setElapsedSeconds(0)
    setMockScore(null)

    if (activeMode === 'job_aligned' && !jobDescription.trim()) {
      setError('Paste or upload a job description to run Job-Aligned Practice.')
      return
    }

    try {
      setIsLoading(true)
      const practiceMode = activeMode === 'mock_interview' ? 'general' : activeMode
      const response = await fetch(`${API_BASE_URL}/api/chat/practice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: practiceMode,
          focus_area: focusArea,
          job_description: jobDescription,
          question_count: questionCount,
        }),
      })

      if (!response.ok) {
        const payload = (await response.json().catch(() => ({}))) as { detail?: string }
        throw new Error(payload.detail ?? 'Failed to generate practice questions.')
      }

      const payload = (await response.json()) as PracticeResponse
      setResult(payload)
    } catch (submitError) {
      const submitMessage = submitError instanceof Error ? submitError.message : 'Something went wrong.'
      setError(submitMessage)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (!result?.questions) {
      setStreamedText('')
      return
    }

    let index = 0
    setStreamedText('')
    const text = result.questions
    const timer = window.setInterval(() => {
      index += 2
      setStreamedText(text.slice(0, index))
      if (index >= text.length) window.clearInterval(timer)
    }, 8)

    return () => window.clearInterval(timer)
  }, [result?.questions])

  useEffect(() => {
    if (activeMode !== 'mock_interview' || !result || mockScore) return

    const timer = window.setInterval(() => setElapsedSeconds((value) => value + 1), 1000)
    return () => window.clearInterval(timer)
  }, [activeMode, result, mockScore])

  const scoreMockInterview = async () => {
    if (!selectedQuestion.trim() || !answerDraft.trim()) {
      setError('Add an answer first to score your mock interview response.')
      return
    }

    const token = localStorage.getItem('swali_access_token')
    if (!token) {
      onRequireAuth()
      return
    }

    setError('')
    setIsScoring(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/learning/mock-interview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          question: selectedQuestion,
          answer: answerDraft,
          duration_minutes: Math.max(1, Math.round(elapsedSeconds / 60)),
        }),
      })

      if (!response.ok) {
        const payload = (await response.json().catch(() => ({}))) as { detail?: string }
        throw new Error(payload.detail ?? 'Unable to score mock interview response.')
      }

      const payload = (await response.json()) as Record<string, unknown>
      setMockScore(payload)
    } catch (scoreError) {
      const scoreMessage = scoreError instanceof Error ? scoreError.message : 'Scoring failed.'
      setError(scoreMessage)
    } finally {
      setIsScoring(false)
    }
  }

  const sourceChips = useMemo(() => {
    const seen = new Set<string>()
    return (result?.sources ?? []).filter((source) => {
      if (seen.has(source.title)) return false
      seen.add(source.title)
      return true
    })
  }, [result?.sources])

  return (
    <section
      id="practice"
      ref={ref}
      className={`visible rounded-2xl border bg-gradient-to-br px-4 py-5 shadow-[0_12px_35px_rgba(19,13,9,0.06)] transition-all duration-700 ease-out md:px-6 md:py-6 ${modeAccent} ${revealClass}`}
    >
      <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
        <aside className="rounded-2xl border border-black/10 bg-white/90 p-4 shadow-[0_1px_3px_rgba(0,0,0,0.08)]">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-neutral-500">Active Session</p>
          <h2 className="mt-1 text-xl font-semibold text-neutral-900">Practice Workspace</h2>
          <p className="mt-1 text-xs text-neutral-500">Session {sessionId}</p>

          <div className="mt-4 flex flex-wrap gap-2">
            {(
              [
                { key: 'general', label: 'General Practice' },
                { key: 'job_aligned', label: 'Job-Aligned' },
                { key: 'mock_interview', label: 'Mock Interview' },
              ] as const
            ).map((mode) => (
              <button
                key={mode.key}
                type="button"
                onClick={() => onModeChange(mode.key)}
                className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
                  activeMode === mode.key
                    ? 'bg-neutral-900 text-white'
                    : 'border border-neutral-300 bg-white text-neutral-700 hover:border-neutral-400'
                }`}
              >
                {mode.label}
              </button>
            ))}
          </div>

          <form className="mt-4 grid gap-5" onSubmit={submitPractice}>
            <label className="grid gap-1">
              <span className="text-xs font-semibold uppercase tracking-[0.12em] text-[#888]">Focus area</span>
              <input
                type="text"
                value={focusArea}
                onChange={(event) => setFocusArea(event.target.value)}
                placeholder="Backend APIs, system design, ML fundamentals"
                className="rounded-xl border border-neutral-300 bg-white px-3 py-2 text-sm text-neutral-800 outline-none transition focus:border-orange-500"
              />
            </label>

            <label className="grid gap-1">
              <span className="text-xs font-semibold uppercase tracking-[0.12em] text-[#888]">Difficulty</span>
              <select
                value={difficulty}
                onChange={(event) => setDifficulty(event.target.value)}
                className="rounded-xl border border-neutral-300 bg-white px-3 py-2 text-sm text-neutral-800 outline-none transition focus:border-orange-500"
              >
                <option value="mixed">Mixed</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </label>

            <div className="grid gap-1">
              <span className="text-xs font-semibold uppercase tracking-[0.12em] text-[#888]">Question depth</span>
              <div className="grid gap-2">
                {DEPTH_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setQuestionCount(option.value)}
                    className={`rounded-xl border px-3 py-2 text-left transition ${
                      questionCount === option.value
                        ? 'border-neutral-900 bg-neutral-900 text-white'
                        : 'border-neutral-300 bg-white text-neutral-700 hover:border-neutral-500'
                    }`}
                  >
                    <p className="text-sm font-semibold">
                      {option.label} ({option.value})
                    </p>
                    <p className={`text-xs ${questionCount === option.value ? 'text-white/80' : 'text-neutral-500'}`}>
                      {option.description}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            <label className="grid gap-1">
              <span className="text-xs font-semibold uppercase tracking-[0.12em] text-[#888]">Job description</span>
              <textarea
                rows={7}
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                placeholder={SAMPLE_JD_PLACEHOLDER}
                className="rounded-xl border border-neutral-300 bg-white px-3 py-2 text-sm leading-relaxed text-neutral-800 outline-none transition focus:border-orange-500"
              />
            </label>

            <div className="flex flex-wrap items-center gap-2">
              <label className="inline-flex cursor-pointer items-center rounded-full border border-neutral-300 bg-white px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:border-neutral-400">
                Upload JD File
                <input type="file" accept={fileAccept} onChange={onFileChange} className="hidden" />
              </label>
              <span className="text-[11px] text-neutral-500">.txt .md .docx</span>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="mt-1 rounded-full bg-orange-600 px-5 py-2.5 text-sm font-semibold text-white shadow-[0_14px_30px_rgba(242,101,36,0.3)] transition hover:bg-orange-500 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isLoading ? 'Generating…' : 'Generate Practice Questions'}
            </button>
          </form>
        </aside>

        <div className="rounded-2xl border border-black/10 bg-white/90 p-4 shadow-[0_1px_3px_rgba(0,0,0,0.08)] md:p-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-neutral-500">Live Preview</p>
              <h3 className="text-lg font-semibold text-neutral-900">
                {questions.length ? `Question ${selectedQuestionIndex + 1} of ${questions.length}` : 'Live Preview'}
              </h3>
            </div>
            {activeMode === 'mock_interview' ? (
              <div className="rounded-full bg-violet-100 px-3 py-1 text-xs font-semibold text-violet-700">
                Timer {Math.floor(elapsedSeconds / 60)}:{String(elapsedSeconds % 60).padStart(2, '0')}
              </div>
            ) : null}
          </div>

          {questions.length ? (
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-neutral-200">
              <div className="h-full rounded-full bg-orange-500 transition-all" style={{ width: `${progressPercent}%` }} />
            </div>
          ) : null}

          {error ? <p className="mt-3 text-sm font-medium text-red-600">{error}</p> : null}

          {isLoading ? (
            <div className="mt-4 grid gap-3">
              <div className="h-5 w-1/2 animate-pulse rounded bg-neutral-200" />
              <div className="h-20 animate-pulse rounded-xl bg-neutral-100" />
              <div className="h-16 animate-pulse rounded-xl bg-neutral-100" />
            </div>
          ) : null}

          {!isLoading && !result ? (
            <div className="mt-5 flex min-h-[360px] items-center justify-center rounded-xl border-2 border-dashed border-neutral-200 bg-white/60 p-6 text-center">
              <div className="max-w-sm">
                <div className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-orange-50">
                  <Sparkles size={22} color="#E84C1E" />
                </div>
                <h4 className="text-lg font-semibold text-neutral-900">Your session hasn&apos;t started yet</h4>
                <p className="mt-2 text-sm font-normal text-[#555]">
                  Configure your settings on the left and click Generate to begin.
                </p>
              </div>
            </div>
          ) : null}

          {!isLoading && result ? (
            <div className="mt-4 grid gap-4 lg:grid-cols-[1.05fr_1fr]">
              <div className="rounded-xl border border-black/10 bg-[#fffaf5] p-4 shadow-[0_1px_3px_rgba(0,0,0,0.08)]">
                <p className="text-xs font-semibold uppercase tracking-[0.15em] text-orange-700">
                  Generated with {result.model} · {result.tokens_used} tokens
                </p>

                <div className="mt-3 flex flex-wrap gap-2">
                  {questions.map((_, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => setSelectedQuestionIndex(index)}
                      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                        selectedQuestionIndex === index
                          ? 'bg-orange-600 text-white'
                          : 'border border-orange-200 bg-white text-orange-700'
                      }`}
                    >
                      Q{index + 1}
                    </button>
                  ))}
                </div>

                <div className="mt-4 rounded-lg border border-black/5 bg-white p-3">
                  <p className="text-xs uppercase tracking-[0.14em] text-neutral-500">Selected Question</p>
                  <p className="mt-1 text-sm leading-relaxed text-neutral-800">{selectedQuestion || 'No question selected.'}</p>
                </div>

                <div className="mt-3">
                  <p className="text-xs uppercase tracking-[0.14em] text-neutral-500">Sources used</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {sourceChips.length === 0 ? (
                      <span className="text-xs text-neutral-500">No source metadata provided.</span>
                    ) : (
                      sourceChips.map((source) => (
                        <span
                          key={source.id}
                          className="rounded-full border border-neutral-300 bg-white px-2.5 py-1 text-xs font-medium text-neutral-700"
                        >
                          {source.title}
                        </span>
                      ))
                    )}
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-black/10 bg-white p-4 shadow-[0_1px_3px_rgba(0,0,0,0.08)]">
                <p className="text-xs uppercase tracking-[0.14em] text-neutral-500">Streaming output</p>
                <pre className="mt-2 min-h-28 whitespace-pre-wrap rounded-lg border border-black/5 bg-neutral-50 p-3 text-sm leading-relaxed text-neutral-800">
                  {streamedText}
                  <span className="ml-0.5 inline-block h-4 w-1 animate-pulse bg-neutral-700 align-middle" />
                </pre>

                <label className="mt-3 grid gap-1">
                  <span className="text-xs uppercase tracking-[0.14em] text-neutral-500">
                    {activeMode === 'mock_interview' ? 'Your interview answer' : 'Your notes/answer draft'}
                  </span>
                  <textarea
                    rows={5}
                    value={answerDraft}
                    onChange={(event) => setAnswerDraft(event.target.value)}
                    placeholder="Type your answer draft here..."
                    className="rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm leading-relaxed text-neutral-800 outline-none transition focus:border-orange-500"
                  />
                </label>

                <div className="mt-3">
                  <p className="text-xs uppercase tracking-[0.14em] text-neutral-500">How confident were you?</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(
                      [
                        { key: 'low', label: '🔴 Low' },
                        { key: 'medium', label: '🟡 Medium' },
                        { key: 'high', label: '🟢 High' },
                      ] as const
                    ).map((option) => (
                      <button
                        key={option.key}
                        type="button"
                        onClick={() => setConfidence(option.key)}
                        className={`rounded-full px-3 py-1.5 text-xs font-semibold ${
                          confidence === option.key
                            ? 'bg-neutral-900 text-white'
                            : 'border border-neutral-300 bg-white text-neutral-700'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>

                {activeMode === 'mock_interview' ? (
                  <div className="mt-3">
                    <button
                      type="button"
                      onClick={scoreMockInterview}
                      disabled={isScoring}
                      className="rounded-full bg-violet-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-70"
                    >
                      {isScoring ? 'Scoring…' : 'Score Mock Answer'}
                    </button>
                    <p className="mt-1 text-[11px] text-neutral-500">Hints are hidden by default in mock mode.</p>
                    {mockScore ? (
                      <div className="mt-3 rounded-lg border border-violet-200 bg-violet-50 p-3">
                        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-violet-700">Score Card</p>
                        <pre className="mt-1 whitespace-pre-wrap text-xs text-violet-900">
                          {JSON.stringify(mockScore, null, 2)}
                        </pre>
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  )
}

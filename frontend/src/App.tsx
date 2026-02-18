import { useMemo, useState } from 'react'
import './App.css'

type Mode = 'answer' | 'hint' | 'followup'

type Source = {
  id: string
  title: string
  type?: string
  difficulty?: string
  pattern?: string
}

type AnswerResponse = {
  answer: string
  sources: Source[]
  tokens_used: number
  model: string
}

type FollowupResponse = {
  questions: string
  sources: Source[]
  tokens_used: number
  model: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const [mode, setMode] = useState<Mode>('answer')
  const [message, setMessage] = useState('')
  const [problemTitle, setProblemTitle] = useState('')
  const [hintLevel, setHintLevel] = useState(1)
  const [solutionApproach, setSolutionApproach] = useState('')
  const [response, setResponse] = useState<AnswerResponse | FollowupResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const isHintMode = mode === 'hint'
  const isFollowupMode = mode === 'followup'

  const canSubmit = useMemo(() => {
    if (isFollowupMode) {
      return problemTitle.trim().length > 0 && solutionApproach.trim().length > 0
    }
    if (isHintMode) {
      return problemTitle.trim().length > 0 && message.trim().length > 0
    }
    return message.trim().length > 0
  }, [isFollowupMode, isHintMode, message, problemTitle, solutionApproach])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      // LEARNING NOTE: Keep endpoint selection explicit to avoid mixing payload shapes.
      let endpoint = '/api/chat'
      let payload: Record<string, unknown> = { message }

      if (isHintMode) {
        endpoint = '/api/chat/hint'
        payload = {
          problem_title: problemTitle,
          hint_level: hintLevel,
          student_attempt: message,
        }
      } else if (isFollowupMode) {
        endpoint = '/api/chat/followup'
        payload = {
          problem_title: problemTitle,
          solution_approach: solutionApproach,
        }
      }

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const detail = await res.text()
        throw new Error(detail || `Request failed with status ${res.status}`)
      }

      const data = (await res.json()) as AnswerResponse | FollowupResponse
      setResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error')
    } finally {
      setIsLoading(false)
    }
  }

  const renderResponseText = () => {
    if (!response) return null
    if ('answer' in response) return response.answer
    return response.questions
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Swali-AI Lab</p>
          <h1>RAG Practice Studio</h1>
          <p className="subtitle">
            Ask a question, request a hint, or generate follow-up interview prompts.
          </p>
        </div>
        <div className="hero-card">
          <p className="label">Active API</p>
          <p className="mono">{API_BASE}</p>
          <p className="small">
            Set <span className="mono">VITE_API_BASE_URL</span> if your backend runs elsewhere.
          </p>
        </div>
      </header>

      <main className="layout">
        <section className="panel">
          <h2>Request Builder</h2>
          <form onSubmit={handleSubmit} className="form">
            <div className="field-group">
              <label htmlFor="mode">Mode</label>
              <div className="segmented">
                {(['answer', 'hint', 'followup'] as Mode[]).map((option) => (
                  <button
                    key={option}
                    type="button"
                    className={`segment ${mode === option ? 'active' : ''}`}
                    onClick={() => setMode(option)}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className="field">
              <label htmlFor="problemTitle">Problem title</label>
              <input
                id="problemTitle"
                type="text"
                placeholder="Two Sum"
                value={problemTitle}
                onChange={(event) => setProblemTitle(event.target.value)}
              />
              <p className="help">Required for hints and follow-ups.</p>
            </div>

            {!isFollowupMode && (
              <div className="field">
                <label htmlFor="message">Question or attempt</label>
                <textarea
                  id="message"
                  placeholder="Explain how to solve Two Sum in O(n)."
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                />
              </div>
            )}

            {isHintMode && (
              <div className="field">
                <label htmlFor="hintLevel">Hint level</label>
                <input
                  id="hintLevel"
                  type="range"
                  min={1}
                  max={3}
                  value={hintLevel}
                  onChange={(event) => setHintLevel(Number(event.target.value))}
                />
                <div className="range-labels">
                  <span>1</span>
                  <span>2</span>
                  <span>3</span>
                </div>
              </div>
            )}

            {isFollowupMode && (
              <div className="field">
                <label htmlFor="solutionApproach">Solution approach</label>
                <textarea
                  id="solutionApproach"
                  placeholder="Used a HashMap to store complements while scanning once."
                  value={solutionApproach}
                  onChange={(event) => setSolutionApproach(event.target.value)}
                />
              </div>
            )}

            <button className="primary" type="submit" disabled={!canSubmit || isLoading}>
              {isLoading ? 'Working...' : 'Send request'}
            </button>
          </form>
        </section>

        <section className="panel output">
          <h2>Response</h2>
          {error && <div className="notice error">{error}</div>}
          {!error && !response && <div className="notice">No response yet.</div>}
          {response && (
            <div className="response-card">
              <p className="response-text">{renderResponseText()}</p>
              <div className="meta">
                <span>Model: {response.model}</span>
                <span>Tokens: {response.tokens_used}</span>
              </div>
              <div className="sources">
                <h3>Sources</h3>
                {response.sources.length === 0 && <p className="small">No sources found.</p>}
                {response.sources.map((source) => (
                  <div key={source.id} className="source">
                    <div>
                      <p className="source-title">{source.title}</p>
                      <p className="small">
                        {source.type || 'problem'} · {source.difficulty || 'n/a'}
                      </p>
                    </div>
                    {source.pattern && <span className="tag">{source.pattern}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App

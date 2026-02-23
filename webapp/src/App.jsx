import { useState, useEffect, useRef } from 'react'

const API_BASE = 'http://localhost:8000'
const NUM_BARS = 28

export default function App() {
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [response, setResponse] = useState('')
  const [typing, setTyping] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [bars, setBars] = useState(Array(NUM_BARS).fill(4))
  const [activeTab, setActiveTab] = useState('assistant')
  const animRef = useRef(null)
  const typeRef = useRef(null)
  const recognitionRef = useRef(null)

  // ── Waveform animation ─────────────────────────────────────────────────
  useEffect(() => {
    if (listening) {
      animRef.current = setInterval(() => {
        setBars(Array(NUM_BARS).fill(0).map(() => Math.floor(Math.random() * 52) + 4))
      }, 80)
    } else {
      clearInterval(animRef.current)
      setBars(Array(NUM_BARS).fill(4))
    }
    return () => clearInterval(animRef.current)
  }, [listening])

  // ── Typewriter effect ──────────────────────────────────────────────────
  const typeText = (text) => {
    setTyping(true)
    setResponse('')
    let i = 0
    clearInterval(typeRef.current)
    typeRef.current = setInterval(() => {
      setResponse(text.slice(0, i + 1))
      i++
      if (i >= text.length) {
        clearInterval(typeRef.current)
        setTyping(false)
      }
    }, 14)
  }

  // ── Call Nova Lite via FastAPI ─────────────────────────────────────────
  const callNova = async (text) => {
    setLoading(true)
    setError('')
    setResponse('')
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, language: 'en' }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      typeText(data.response)
    } catch (err) {
      setError('Could not reach Nova API. Is the api_server.py running on port 8000?')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // ── Web Speech API mic toggle ──────────────────────────────────────────
  const handleMicClick = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert('Your browser does not support speech recognition. Please use Chrome.')
      return
    }

    if (listening) {
      // Stop listening
      if (recognitionRef.current) recognitionRef.current.stop()
      setListening(false)
      return
    }

    // Start listening
    setListening(true)
    setTranscript('')
    setResponse('')
    setError('')
    clearInterval(typeRef.current)

    const recognition = new SpeechRecognition()
    recognitionRef.current = recognition
    recognition.lang = 'en-US'
    recognition.interimResults = true
    recognition.maxAlternatives = 1

    recognition.onresult = (e) => {
      let interim = ''
      let final = ''
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) final += e.results[i][0].transcript
        else interim += e.results[i][0].transcript
      }
      setTranscript(final || interim)
      if (final) {
        recognition.stop()
        setListening(false)
        callNova(final)
      }
    }

    recognition.onerror = (e) => {
      setListening(false)
      setError(`Mic error: ${e.error}. Try Chrome and allow microphone access.`)
    }

    recognition.onend = () => {
      setListening(false)
    }

    recognition.start()
  }

  // ── Quick chip handler ─────────────────────────────────────────────────
  const handleChip = (text) => {
    setTranscript(text)
    setResponse('')
    setError('')
    callNova(text)
  }

  const navItems = [
    { id: 'assistant', label: 'AI Assistant', icon: '\uD83C\uDF99' },
    { id: 'tracker', label: 'Case Tracker', icon: '\uD83D\uDCCB' },
    { id: 'legal', label: 'Legal Screening', icon: '\u2696\uFE0F' },
    { id: 'lawyers', label: 'Find Lawyers', icon: '\uD83D\uDC65' },
  ]

  const statusText = () => {
    if (listening) return '\uD83D\uDD34 Listening — speak now...'
    if (loading) return '\u23F3 Processing with Amazon Nova Lite...'
    if (typing) return '\u2728 Nova is responding...'
    if (response) return '\u2705 Nova has responded'
    return 'Click the mic or a quick question below'
  }

  const statusColor = () => {
    if (listening) return '#f87171'
    if (loading || typing) return '#f59e0b'
    if (response) return '#10b981'
    return '#6366f1'
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#050510', color: '#fff', fontFamily: 'Inter, sans-serif' }}>
      {/* Sidebar */}
      <div style={{ width: 240, background: 'rgba(255,255,255,0.03)', borderRight: '1px solid rgba(255,255,255,0.08)', padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#6366f1', letterSpacing: '.15em', textTransform: 'uppercase', marginBottom: 4 }}>Amazon Nova</div>
          <div style={{ fontSize: 18, fontWeight: 700, fontFamily: 'Outfit, sans-serif', lineHeight: 1.2 }}>Refugee Legal<br />Navigator</div>
        </div>
        {navItems.map(item => (
          <button key={item.id} onClick={() => setActiveTab(item.id)} style={{
            display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px', borderRadius: 10,
            background: activeTab === item.id ? 'rgba(99,102,241,0.2)' : 'transparent',
            border: activeTab === item.id ? '1px solid rgba(99,102,241,0.4)' : '1px solid transparent',
            color: activeTab === item.id ? '#a5b4fc' : '#6b7280',
            cursor: 'pointer', fontSize: 14, fontWeight: 500, textAlign: 'left', width: '100%'
          }}>
            <span style={{ fontSize: 18 }}>{item.icon}</span> {item.label}
          </button>
        ))}
        <div style={{ marginTop: 'auto', padding: '12px 14px', borderRadius: 10, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)' }}>
          <div style={{ fontSize: 11, color: '#10b981', fontWeight: 600 }}>&#9679; NOVA LITE ACTIVE</div>
          <div style={{ fontSize: 11, color: '#6b7280', marginTop: 2 }}>amazon.nova-lite-v1:0</div>
        </div>
      </div>

      {/* Main content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 40, gap: 28 }}>

        {/* Header */}
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontSize: 32, fontWeight: 700, fontFamily: 'Outfit, sans-serif', background: 'linear-gradient(135deg,#818cf8,#6366f1,#a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: 8 }}>
            How can I help you?
          </h1>
          <p style={{ color: statusColor(), fontSize: 14, fontWeight: 500, transition: 'color 0.4s', minHeight: 20 }}>
            {statusText()}
          </p>
        </div>

        {/* Waveform + Mic */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 3, height: 64 }}>
            {bars.map((h, i) => (
              <div key={i} style={{
                width: 4, height: h, borderRadius: 99,
                background: listening ? 'hsl(' + (220 + i * 3) + ', 80%, 65%)' : loading ? 'hsl(' + (40 + i * 2) + ', 80%, 60%)' : 'rgba(255,255,255,0.12)',
                transition: (listening || loading) ? 'height 0.08s ease' : 'height 0.6s ease, background 0.4s',
              }} />
            ))}
          </div>

          <div style={{ position: 'relative' }}>
            {listening && (
              <>
                <div className="ping-ring-outer" style={{ position: 'absolute', inset: -16, borderRadius: '50%', border: '2px solid rgba(239,68,68,0.5)' }} />
                <div className="ping-ring-inner" style={{ position: 'absolute', inset: -8, borderRadius: '50%', border: '2px solid rgba(239,68,68,0.3)' }} />
              </>
            )}
            {loading && (
              <div className="loading-ring" style={{ position: 'absolute', inset: -8, borderRadius: '50%', border: '3px solid transparent', borderTopColor: '#f59e0b' }} />
            )}
            <button onClick={handleMicClick} disabled={loading} style={{
              width: 80, height: 80, borderRadius: '50%',
              background: listening ? 'radial-gradient(circle,#ef4444,#b91c1c)' : loading ? 'radial-gradient(circle,#d97706,#92400e)' : 'radial-gradient(circle,#6366f1,#4338ca)',
              border: 'none', cursor: loading ? 'wait' : 'pointer', fontSize: 32,
              boxShadow: listening ? '0 0 40px rgba(239,68,68,0.6)' : loading ? '0 0 30px rgba(245,158,11,0.5)' : '0 0 30px rgba(99,102,241,0.5)',
              transition: 'all 0.3s ease', transform: listening ? 'scale(1.1)' : 'scale(1)'
            }}>
              {loading ? '\u23F3' : '\uD83C\uDF99'}
            </button>
          </div>

          <div style={{ fontSize: 12, color: '#4b5563' }}>
            {listening ? 'Speak now — click again to cancel' : loading ? 'Nova is thinking...' : 'Click to speak'}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div style={{ maxWidth: 560, width: '100%', padding: '12px 18px', borderRadius: 10, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', fontSize: 13, color: '#fca5a5' }}>
            &#9888; {error}
          </div>
        )}

        {/* Transcript */}
        {transcript && (
          <div style={{ maxWidth: 560, width: '100%', padding: '14px 20px', borderRadius: 14, background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)', fontSize: 14, color: '#c7d2fe' }}>
            <div style={{ fontSize: 11, color: '#6366f1', fontWeight: 600, marginBottom: 6 }}>YOU SAID</div>
            {transcript}
          </div>
        )}

        {/* Nova Response */}
        {(response || typing || loading) && (
          <div style={{ maxWidth: 560, width: '100%', padding: '18px 22px', borderRadius: 14, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)', fontSize: 14, lineHeight: 1.8, color: '#d1fae5', minHeight: 60 }}>
            <div style={{ fontSize: 11, color: '#10b981', fontWeight: 600, marginBottom: 8 }}>&#9878; NOVA LITE LEGAL ASSESSMENT</div>
            {loading && !response ? (
              <span style={{ color: '#6b7280', fontStyle: 'italic' }}>Consulting Amazon Nova...</span>
            ) : (
              <>
                {response}
                {typing && <span className="blink-cursor" style={{ display: 'inline-block', width: 2, height: 14, background: '#10b981', marginLeft: 2, verticalAlign: 'middle' }} />}
              </>
            )}
          </div>
        )}

        {/* Quick chips */}
        {!listening && !loading && !response && (
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center' }}>
            {['Am I eligible for asylum?', 'Find me a pro bono lawyer', 'What documents do I need?', 'How long does the process take?'].map(q => (
              <button key={q} onClick={() => handleChip(q)}
                style={{ padding: '8px 16px', borderRadius: 99, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: '#9ca3af', fontSize: 13, cursor: 'pointer' }}>
                {q}
              </button>
            ))}
          </div>
        )}

        {response && !typing && (
          <button onClick={() => { setResponse(''); setTranscript(''); setError('') }}
            style={{ padding: '8px 20px', borderRadius: 99, background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)', color: '#a5b4fc', fontSize: 13, cursor: 'pointer' }}>
            Ask another question
          </button>
        )}
      </div>

      <style>{`
        @keyframes ping { 0% { transform: scale(1); opacity: 0.8; } 100% { transform: scale(2); opacity: 0; } }
        @keyframes blink { 50% { opacity: 0; } }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .ping-ring-outer { animation: ping 1.2s ease-out infinite; }
        .ping-ring-inner { animation: ping 1.4s ease-out infinite 0.3s; }
        .loading-ring { animation: spin 0.8s linear infinite; }
        .blink-cursor { animation: blink 0.7s step-end infinite; }
        button:hover:not(:disabled) { opacity: 0.8; }
      `}</style>
    </div>
  )
}

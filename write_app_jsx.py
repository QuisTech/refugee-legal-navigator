import pathlib

p = pathlib.Path(r'C:\Users\Administrator\Downloads\refugee-legal-navigator\webapp\src\App.jsx')

content = """\
import { useState, useEffect, useRef } from 'react'

const RESPONSES = [
  'Based on the 1951 Refugee Convention, your situation in Syria may qualify under persecution grounds. You should document your fear of return and file within one year of arrival.',
  'I found 3 pro bono lawyers in your area. The closest is Jane Doe Legal Services, specializing in Asylum and Refugee Law. Would you like their contact details?',
  'Your USCIS case ZNY1234567890 was last updated 3 days ago. Status: Initial Review in Progress. Expected timeline: 6-8 months.',
  'You may be eligible for asylum if you can demonstrate a well-founded fear of persecution based on race, religion, nationality, political opinion, or membership in a particular social group.',
]

const NUM_BARS = 28

export default function App() {
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [response, setResponse] = useState('')
  const [typing, setTyping] = useState(false)
  const [bars, setBars] = useState(Array(NUM_BARS).fill(4))
  const [activeTab, setActiveTab] = useState('assistant')
  const animRef = useRef(null)
  const typeRef = useRef(null)
  const responseIdx = useRef(0)

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

  const typeText = (text) => {
    setTyping(true)
    setResponse('')
    let i = 0
    typeRef.current = setInterval(() => {
      setResponse(text.slice(0, i + 1))
      i++
      if (i >= text.length) {
        clearInterval(typeRef.current)
        setTyping(false)
      }
    }, 18)
  }

  const handleMicClick = () => {
    if (listening) {
      setListening(false)
      setTranscript('I need help with my asylum case. I am from Syria and afraid to go back.')
      setTimeout(() => {
        const r = RESPONSES[responseIdx.current % RESPONSES.length]
        responseIdx.current++
        typeText(r)
      }, 600)
    } else {
      setListening(true)
      setTranscript('')
      setResponse('')
      clearInterval(typeRef.current)
    }
  }

  const navItems = [
    { id: 'assistant', label: 'AI Assistant', icon: '\\uD83C\\uDF99' },
    { id: 'tracker', label: 'Case Tracker', icon: '\\uD83D\\uDCCB' },
    { id: 'legal', label: 'Legal Screening', icon: '\\u2696\\uFE0F' },
    { id: 'lawyers', label: 'Find Lawyers', icon: '\\uD83D\\uDC65' },
  ]

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
          <div style={{ fontSize: 11, color: '#10b981', fontWeight: 600 }}>&#9679; SYSTEM ONLINE</div>
          <div style={{ fontSize: 11, color: '#6b7280', marginTop: 2 }}>Nova Lite + Embeddings</div>
        </div>
      </div>

      {/* Main content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 40, gap: 32 }}>

        {/* Header */}
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontSize: 32, fontWeight: 700, fontFamily: 'Outfit, sans-serif', background: 'linear-gradient(135deg,#818cf8,#6366f1,#a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: 8 }}>
            How can I help you?
          </h1>
          <p style={{ color: listening ? '#f87171' : '#6366f1', fontSize: 14, fontWeight: 500, transition: 'color 0.4s' }}>
            {listening ? '\\uD83D\\uDD34 Listening for your voice...' : response ? '\\u2705 Nova has responded' : 'Click the mic to speak'}
          </p>
        </div>

        {/* Waveform + Mic */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 28 }}>

          {/* Waveform bars */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 3, height: 64 }}>
            {bars.map((h, i) => (
              <div key={i} style={{
                width: 4,
                height: h,
                borderRadius: 99,
                background: listening
                  ? 'hsl(' + (220 + i * 3) + ', 80%, 65%)'
                  : 'rgba(255,255,255,0.12)',
                transition: listening ? 'height 0.08s ease' : 'height 0.6s ease, background 0.4s',
              }} />
            ))}
          </div>

          {/* Mic button */}
          <div style={{ position: 'relative' }}>
            {listening && (
              <>
                <div className="ping-ring-outer" style={{ position: 'absolute', inset: -16, borderRadius: '50%', border: '2px solid rgba(239,68,68,0.5)' }} />
                <div className="ping-ring-inner" style={{ position: 'absolute', inset: -8, borderRadius: '50%', border: '2px solid rgba(239,68,68,0.3)' }} />
              </>
            )}
            <button onClick={handleMicClick} style={{
              width: 80, height: 80, borderRadius: '50%',
              background: listening ? 'radial-gradient(circle,#ef4444,#b91c1c)' : 'radial-gradient(circle,#6366f1,#4338ca)',
              border: 'none', cursor: 'pointer', fontSize: 32,
              boxShadow: listening ? '0 0 40px rgba(239,68,68,0.6), 0 0 80px rgba(239,68,68,0.2)' : '0 0 30px rgba(99,102,241,0.5)',
              transition: 'all 0.3s ease',
              transform: listening ? 'scale(1.1)' : 'scale(1)'
            }}>
              \\uD83C\\uDF99
            </button>
          </div>

          <div style={{ fontSize: 12, color: '#4b5563' }}>
            {listening ? 'Click again to stop and process' : 'Click to start speaking'}
          </div>
        </div>

        {/* Transcript */}
        {transcript && (
          <div style={{ maxWidth: 560, width: '100%', padding: '14px 20px', borderRadius: 14, background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)', fontSize: 14, color: '#c7d2fe' }}>
            <div style={{ fontSize: 11, color: '#6366f1', fontWeight: 600, marginBottom: 6 }}>YOU SAID</div>
            {transcript}
          </div>
        )}

        {/* AI Response */}
        {(response || typing) && (
          <div style={{ maxWidth: 560, width: '100%', padding: '18px 22px', borderRadius: 14, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)', fontSize: 14, lineHeight: 1.7, color: '#d1fae5' }}>
            <div style={{ fontSize: 11, color: '#10b981', fontWeight: 600, marginBottom: 8 }}>&#9878; NOVA LEGAL ASSESSMENT</div>
            {response}
            {typing && <span className="blink-cursor" style={{ display: 'inline-block', width: 2, height: 14, background: '#10b981', marginLeft: 2, verticalAlign: 'middle' }} />}
          </div>
        )}

        {/* Quick chips */}
        {!listening && !response && (
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center' }}>
            {['Asylum eligibility', 'Find a lawyer', 'Check case status', 'Document help'].map(q => (
              <button key={q}
                onClick={() => { setTranscript(q); setTimeout(() => typeText(RESPONSES[responseIdx.current++ % RESPONSES.length]), 400) }}
                style={{ padding: '8px 16px', borderRadius: 99, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: '#9ca3af', fontSize: 13, cursor: 'pointer' }}>
                {q}
              </button>
            ))}
          </div>
        )}
      </div>

      <style>{`
        @keyframes ping {
          0% { transform: scale(1); opacity: 0.8; }
          100% { transform: scale(2); opacity: 0; }
        }
        @keyframes blink {
          50% { opacity: 0; }
        }
        .ping-ring-outer { animation: ping 1.2s ease-out infinite; }
        .ping-ring-inner { animation: ping 1.4s ease-out infinite 0.3s; }
        .blink-cursor { animation: blink 0.7s step-end infinite; }
        button:hover { opacity: 0.8; }
      `}</style>
    </div>
  )
}
"""

p.write_text(content, encoding='utf-8')
print(f'Written {p.stat().st_size} bytes')
# Verify no corruption
assert 'hsl(' in content
assert 'ping' in content
print('Validation OK')

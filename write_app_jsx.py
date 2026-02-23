import pathlib

p = pathlib.Path(r'C:\Users\Administrator\Downloads\refugee-legal-navigator\webapp\src\App.jsx')

content = r"""import { useState, useEffect, useRef } from 'react'

const API_BASE = 'http://localhost:8000'
const NUM_BARS = 28

// Key refugee languages: BCP-47 tag, native name, English name
const LANGUAGES = [
  { code: 'en-US',  label: 'English',    native: 'English' },
  { code: 'ar-SA',  label: 'Arabic',     native: 'العربية' },
  { code: 'fr-FR',  label: 'French',     native: 'Français' },
  { code: 'es-ES',  label: 'Spanish',    native: 'Español' },
  { code: 'so-SO',  label: 'Somali',     native: 'Soomaali' },
  { code: 'am-ET',  label: 'Amharic',    native: 'አማርኛ' },
  { code: 'ti-ER',  label: 'Tigrinya',   native: 'ትግርኛ' },
  { code: 'ps-AF',  label: 'Pashto',     native: 'پښتو' },
  { code: 'fa-IR',  label: 'Dari/Farsi', native: 'دری' },
  { code: 'ur-PK',  label: 'Urdu',       native: 'اردو' },
  { code: 'ha-NG',  label: 'Hausa',      native: 'Hausa' },
  { code: 'sw-KE',  label: 'Swahili',    native: 'Kiswahili' },
  { code: 'my-MM',  label: 'Burmese',    native: 'မြန်မာ' },
  { code: 'uk-UA',  label: 'Ukrainian',  native: 'Українська' },
  { code: 'ru-RU',  label: 'Russian',    native: 'Русский' },
  { code: 'hi-IN',  label: 'Hindi',      native: 'हिन्दी' },
  { code: 'bn-BD',  label: 'Bengali',    native: 'বাংলা' },
  { code: 'tr-TR',  label: 'Turkish',    native: 'Türkçe' },
  { code: 'ku-IQ',  label: 'Kurdish',    native: 'کوردی' },
  { code: 'sw-TZ',  label: 'Swahili (TZ)', native: 'Kiswahili (TZ)' },
]

function getLangLabel(code) {
  return LANGUAGES.find(l => l.code === code) || LANGUAGES[0]
}

export default function App() {
  const [listening, setListening] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [loading, setLoading] = useState(false)
  const [bars, setBars] = useState(Array(NUM_BARS).fill(4))
  const [lang, setLang] = useState('en-US')
  const [showLangMenu, setShowLangMenu] = useState(false)
  const [conversation, setConversation] = useState([]) // [{role:'user'|'nova', text, ts}]
  const [inputText, setInputText] = useState('')
  const chatEndRef = useRef(null)
  const animRef = useRef(null)
  const recognitionRef = useRef(null)

  // Scroll chat to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation, loading])

  // Waveform animation
  useEffect(() => {
    if (listening || speaking) {
      animRef.current = setInterval(() => {
        setBars(Array(NUM_BARS).fill(0).map(() => Math.floor(Math.random() * 52) + 4))
      }, 80)
    } else {
      clearInterval(animRef.current)
      setBars(Array(NUM_BARS).fill(4))
    }
    return () => clearInterval(animRef.current)
  }, [listening, speaking])

  // Text-to-speech using Web Speech API
  const speakText = (text, langCode) => {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = langCode
    utterance.rate = 0.95
    utterance.pitch = 1.0

    // Try to find a voice for this language
    const voices = window.speechSynthesis.getVoices()
    const match = voices.find(v => v.lang.startsWith(langCode.split('-')[0]))
    if (match) utterance.voice = match

    utterance.onstart = () => setSpeaking(true)
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)
    window.speechSynthesis.speak(utterance)
  }

  // Call Nova API with full conversation history
  const callNova = async (text) => {
    const userMsg = { role: 'user', text, ts: Date.now() }
    setConversation(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const history = conversation.map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.text }))
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, language: lang.split('-')[0], history }),
      })
      if (!res.ok) throw new Error(`Server error ${res.status}`)
      const data = await res.json()
      const novaMsg = { role: 'nova', text: data.response, ts: Date.now() }
      setConversation(prev => [...prev, novaMsg])
      // Speak the response
      speakText(data.response, lang)
    } catch (err) {
      const errMsg = { role: 'nova', text: 'Unable to reach the Nova API. Please ensure api_server.py is running on port 8000.', ts: Date.now(), isError: true }
      setConversation(prev => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }

  // Mic button: start/stop Web Speech recognition
  const handleMicClick = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { alert('Speech recognition requires Google Chrome.'); return }

    if (listening) {
      recognitionRef.current?.stop()
      setListening(false)
      return
    }

    // Stop any ongoing speech before listening
    window.speechSynthesis.cancel()
    setSpeaking(false)
    setListening(true)
    setTranscript('')

    const r = new SR()
    recognitionRef.current = r
    r.lang = lang
    r.interimResults = true
    r.maxAlternatives = 1
    r.continuous = false

    r.onresult = (e) => {
      let interim = '', final = ''
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) final += e.results[i][0].transcript
        else interim += e.results[i][0].transcript
      }
      setTranscript(final || interim)
      if (final) {
        r.stop()
        setListening(false)
        callNova(final)
        setTranscript('')
      }
    }
    r.onerror = (e) => {
      setListening(false)
      setTranscript(`Mic error: ${e.error}`)
    }
    r.onend = () => setListening(false)
    r.start()
  }

  const handleSendText = (e) => {
    e.preventDefault()
    if (!inputText.trim()) return
    callNova(inputText.trim())
    setInputText('')
  }

  const handleChip = (text) => callNova(text)

  const clearConversation = () => {
    window.speechSynthesis.cancel()
    setSpeaking(false)
    setConversation([])
    setTranscript('')
  }

  const selectedLang = getLangLabel(lang)
  const isRTL = ['ar-SA','ps-AF','fa-IR','ur-PK','ku-IQ'].includes(lang)

  const waveColor = (i) => {
    if (listening) return `hsl(${0 + i * 2}, 85%, 65%)`
    if (speaking) return `hsl(${120 + i * 2}, 75%, 55%)`
    if (loading) return `hsl(${40 + i * 2}, 80%, 60%)`
    return 'rgba(255,255,255,0.10)'
  }

  return (
    <div style={{ display:'flex', minHeight:'100vh', background:'#050510', color:'#fff', fontFamily:'Inter, sans-serif' }}>

      {/* Sidebar */}
      <div style={{ width:220, background:'rgba(255,255,255,0.03)', borderRight:'1px solid rgba(255,255,255,0.07)', padding:'24px 14px', display:'flex', flexDirection:'column', gap:8, flexShrink:0 }}>
        <div style={{ marginBottom:28 }}>
          <div style={{ fontSize:10, fontWeight:700, color:'#6366f1', letterSpacing:'.15em', textTransform:'uppercase', marginBottom:4 }}>Amazon Nova</div>
          <div style={{ fontSize:16, fontWeight:700, fontFamily:'Outfit,sans-serif', lineHeight:1.3 }}>Refugee Legal<br/>Navigator</div>
          <div style={{ marginTop:8, padding:'8px 10px', borderRadius:8, background:'rgba(16,185,129,0.1)', border:'1px solid rgba(16,185,129,0.2)', fontSize:11 }}>
            <div style={{ color:'#10b981', fontWeight:600 }}>● NOVA LITE ACTIVE</div>
            <div style={{ color:'#6b7280', marginTop:2 }}>+ Titan Embeddings RAG</div>
          </div>
        </div>

        {/* Language selector */}
        <div style={{ position:'relative' }}>
          <div style={{ fontSize:10, color:'#6b7280', fontWeight:600, textTransform:'uppercase', letterSpacing:'.1em', marginBottom:6 }}>Language / لغة</div>
          <button onClick={() => setShowLangMenu(v => !v)} style={{ width:'100%', padding:'8px 12px', borderRadius:8, background:'rgba(99,102,241,0.15)', border:'1px solid rgba(99,102,241,0.3)', color:'#a5b4fc', fontSize:13, cursor:'pointer', textAlign:'left', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <span>{selectedLang.native}</span>
            <span style={{ fontSize:10 }}>▼</span>
          </button>
          {showLangMenu && (
            <div style={{ position:'absolute', top:'100%', left:0, right:0, zIndex:50, background:'#0f0f1a', border:'1px solid rgba(255,255,255,0.1)', borderRadius:8, maxHeight:220, overflowY:'auto', marginTop:4 }}>
              {LANGUAGES.map(l => (
                <button key={l.code} onClick={() => { setLang(l.code); setShowLangMenu(false) }}
                  style={{ display:'block', width:'100%', padding:'8px 12px', background: l.code===lang ? 'rgba(99,102,241,0.2)' : 'transparent', border:'none', color: l.code===lang ? '#a5b4fc' : '#9ca3af', fontSize:12, cursor:'pointer', textAlign:'left' }}>
                  {l.native} <span style={{ color:'#4b5563', fontSize:11 }}>({l.label})</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div style={{ marginTop:8, fontSize:11, color:'#4b5563', lineHeight:1.5 }}>
          Supports 20 refugee languages including Arabic, Somali, Amharic, Dari, Pashto, Hausa, Tigrinya…
        </div>

        {conversation.length > 0 && (
          <button onClick={clearConversation} style={{ marginTop:'auto', padding:'8px 12px', borderRadius:8, background:'rgba(239,68,68,0.1)', border:'1px solid rgba(239,68,68,0.2)', color:'#fca5a5', fontSize:12, cursor:'pointer' }}>
            Clear conversation
          </button>
        )}
      </div>

      {/* Main */}
      <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden' }}>

        {/* Header */}
        <div style={{ padding:'20px 32px 0', textAlign:'center' }}>
          <h1 style={{ fontSize:26, fontWeight:700, fontFamily:'Outfit,sans-serif', background:'linear-gradient(135deg,#818cf8,#6366f1,#a78bfa)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', margin:0 }}>
            Refugee Legal Assistant
          </h1>
          <p style={{ color:'#4b5563', fontSize:12, marginTop:4 }}>
            {speaking ? '🔊 Speaking...' : listening ? '🔴 Listening in ' + selectedLang.label + '...' : loading ? '⏳ Nova is thinking...' : 'Speak or type in your language'}
          </p>
        </div>

        {/* Waveform */}
        <div style={{ display:'flex', justifyContent:'center', alignItems:'center', gap:3, height:52, padding:'8px 0', flexShrink:0 }}>
          {bars.map((h, i) => (
            <div key={i} style={{ width:3, borderRadius:99, background:waveColor(i), height:Math.max(4, Math.min(h, 48)), transition:(listening||speaking||loading)?'height 0.08s ease':'height 0.6s ease, background 0.4s' }} />
          ))}
        </div>

        {/* Chat conversation */}
        <div style={{ flex:1, overflowY:'auto', padding:'8px 32px', display:'flex', flexDirection:'column', gap:12 }}>
          {conversation.length === 0 && !loading && (
            <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:16, paddingTop:20 }}>
              <div style={{ fontSize:48 }}>🎙️</div>
              <div style={{ color:'#4b5563', fontSize:14, textAlign:'center', maxWidth:340 }}>
                Ask me anything about asylum, refugee rights, or immigration law — in your own language.
              </div>
              <div style={{ display:'flex', gap:8, flexWrap:'wrap', justifyContent:'center', marginTop:4 }}>
                {['Am I eligible for asylum?','What documents do I need?','What is non-refoulement?','Can I work while pending?'].map(q => (
                  <button key={q} onClick={() => handleChip(q)} style={{ padding:'8px 14px', borderRadius:99, background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', color:'#9ca3af', fontSize:12, cursor:'pointer' }}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {conversation.map((msg, idx) => (
            <div key={idx} style={{ display:'flex', justifyContent: msg.role==='user' ? 'flex-end' : 'flex-start' }}>
              <div style={{
                maxWidth:'72%', padding:'12px 16px', borderRadius: msg.role==='user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                background: msg.role==='user' ? 'rgba(99,102,241,0.25)' : msg.isError ? 'rgba(239,68,68,0.12)' : 'rgba(16,185,129,0.1)',
                border: `1px solid ${msg.role==='user' ? 'rgba(99,102,241,0.35)' : msg.isError ? 'rgba(239,68,68,0.25)' : 'rgba(16,185,129,0.25)'}`,
                fontSize:14, lineHeight:1.7,
                color: msg.role==='user' ? '#c7d2fe' : msg.isError ? '#fca5a5' : '#d1fae5',
                direction: isRTL ? 'rtl' : 'ltr',
              }}>
                <div style={{ fontSize:10, fontWeight:700, marginBottom:4, color: msg.role==='user' ? '#818cf8' : '#10b981', opacity:0.8 }}>
                  {msg.role==='user' ? '👤 YOU' : '⚖️ NOVA LITE'}
                </div>
                {msg.text}
                {msg.role==='nova' && !msg.isError && (
                  <button onClick={() => speakText(msg.text, lang)} style={{ display:'block', marginTop:8, padding:'3px 10px', borderRadius:99, background:'rgba(16,185,129,0.15)', border:'1px solid rgba(16,185,129,0.25)', color:'#6ee7b7', fontSize:11, cursor:'pointer' }}>
                    🔊 Play again
                  </button>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display:'flex', justifyContent:'flex-start' }}>
              <div style={{ padding:'12px 16px', borderRadius:'18px 18px 18px 4px', background:'rgba(16,185,129,0.07)', border:'1px solid rgba(16,185,129,0.2)', fontSize:13, color:'#6b7280', fontStyle:'italic' }}>
                ⚖️ Nova is reasoning…
                <span style={{ display:'inline-flex', gap:3, marginLeft:8 }}>
                  {[0,1,2].map(i => <span key={i} style={{ display:'inline-block', width:6, height:6, borderRadius:'50%', background:'#10b981', animation:`bounce 0.9s ease ${i*0.2}s infinite` }} />)}
                </span>
              </div>
            </div>
          )}

          {transcript && (
            <div style={{ textAlign:'center', fontSize:13, color:'#6366f1', fontStyle:'italic', direction: isRTL?'rtl':'ltr' }}>
              {transcript}
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input bar */}
        <div style={{ padding:'16px 32px 24px', borderTop:'1px solid rgba(255,255,255,0.06)', display:'flex', gap:12, alignItems:'center', flexShrink:0 }}>

          {/* Microphone */}
          <div style={{ position:'relative', flexShrink:0 }}>
            {listening && (
              <>
                <div style={{ position:'absolute', inset:-12, borderRadius:'50%', border:'2px solid rgba(239,68,68,0.4)', animation:'ping 1.2s ease-out infinite' }} />
                <div style={{ position:'absolute', inset:-6, borderRadius:'50%', border:'2px solid rgba(239,68,68,0.25)', animation:'ping 1.5s ease-out infinite 0.3s' }} />
              </>
            )}
            {speaking && (
              <div style={{ position:'absolute', inset:-6, borderRadius:'50%', border:'2px solid rgba(16,185,129,0.5)', animation:'ping 1s ease-out infinite' }} />
            )}
            <button onClick={handleMicClick} disabled={loading}
              style={{ width:56, height:56, borderRadius:'50%',
                background: listening ? 'radial-gradient(circle,#ef4444,#b91c1c)' : speaking ? 'radial-gradient(circle,#10b981,#065f46)' : 'radial-gradient(circle,#6366f1,#4338ca)',
                border:'none', cursor:loading?'wait':'pointer', fontSize:24,
                boxShadow: listening ? '0 0 30px rgba(239,68,68,0.5)' : speaking ? '0 0 25px rgba(16,185,129,0.5)' : '0 0 20px rgba(99,102,241,0.4)',
                transition:'all 0.3s', transform:listening?'scale(1.1)':'scale(1)' }}>
              {listening ? '⏹' : speaking ? '🔊' : '🎙️'}
            </button>
          </div>

          {/* Text input */}
          <form onSubmit={handleSendText} style={{ flex:1, display:'flex', gap:8 }}>
            <input
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder={`Type in ${selectedLang.native}…`}
              dir={isRTL ? 'rtl' : 'ltr'}
              style={{ flex:1, padding:'14px 18px', borderRadius:14, background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.1)', color:'#fff', fontSize:14, outline:'none' }}
            />
            <button type="submit" disabled={loading || !inputText.trim()} style={{ padding:'14px 22px', borderRadius:14, background:'rgba(99,102,241,0.8)', border:'none', color:'#fff', fontSize:14, fontWeight:600, cursor:'pointer' }}>
              Send
            </button>
          </form>
        </div>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700&display=swap');
        @keyframes ping { 0%{transform:scale(1);opacity:0.8} 100%{transform:scale(2.2);opacity:0} }
        @keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
        *{box-sizing:border-box;margin:0;padding:0}
        ::-webkit-scrollbar{width:4px}
        ::-webkit-scrollbar-track{background:transparent}
        ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:99px}
        button:hover:not(:disabled){opacity:0.82;transition:opacity 0.2s}
        input::placeholder{color:#374151}
      `}</style>
    </div>
  )
}
"""

p.write_text(content, encoding='utf-8')
print(f'Written {p.stat().st_size} bytes')
print('OK' if 'speechSynthesis' in content and 'conversation' in content and 'LANGUAGES' in content else 'MISSING FEATURES')

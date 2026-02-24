import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Director Mode Script for Refugee Legal Navigator
const SCRIPT = [
    // --- 0:00 - 0:30: INTRODUCTION & MISSION ---
    { type: 'cursor', x: '50%', y: '50%', delay: 2000 },
    { type: 'subtitle', text: 'Scenario: Imagine being a refugee in a foreign land, seeking safety but blocked by complex legal jargon and language barriers.', delay: 6000 },
    { type: 'log', text: '[System] Initializing Refugee Legal Navigator v1.0...', status: 'info' },
    { type: 'subtitle', text: 'We built the Refugee Legal Navigator to bridge this gap using the power of Amazon Nova and Agentic AI.', delay: 6000 },
    { type: 'log', text: '[System] Connected to amazon.nova-lite-v1:0', status: 'success' },
    { type: 'log', text: '[System] Connected to amazon.titan-embed-text-v2:0', status: 'success' },
    
    // --- 0:30 - 1:15: STEP 1 - LEGAL RAG (TRUTH & GROUNDING) ---
    { type: 'subtitle', text: 'Step 1: Legally-Grounded Reasoning. We don\'t just use AI; we ground it in real asylum law.', delay: 6000 },
    { type: 'cursor', targetId: 'chat-input', delay: 1500 },
    { type: 'subtitle', text: 'The user asks about their rights under the 1951 Refugee Convention.', delay: 3000 },
    { type: 'type', text: 'What are my rights as a refugee under international law?', targetId: 'chat-input', delay: 500 },
    { type: 'cursor', targetId: 'send-button', delay: 1000 },
    { type: 'click', targetId: 'send-button', delay: 500 },
    { type: 'log', text: '[Retrieval] Searching 5,600+ word legal corpus via Titan Embeddings...', status: 'info' },
    { type: 'log', text: '[Found] 1951 Convention Article 33 (Non-Refoulement)', status: 'success' },
    { type: 'subtitle', text: 'Nova Lite analyzes the retrieved documents to provide a compassionate, legally-accurate response.', delay: 7000 },
    { type: 'log', text: '[Nova] Responding with grounded context (Reference: UNHCR Article 33)', status: 'info' },
    { type: 'wait', delay: 5000 },

    // --- 1:15 - 2:00: STEP 2 - MULTILINGUAL INCLUSIVITY ---
    { type: 'subtitle', text: 'Step 2: Radical Inclusivity. Legal aid is only useful if you can understand it.', delay: 6000 },
    { type: 'cursor', targetId: 'language-select', delay: 2000 },
    { type: 'subtitle', text: 'We support 22 refugee-focused languages, including Arabic, Somali, Amharic, and Igbo.', delay: 6000 },
    { type: 'click', targetId: 'language-select', delay: 800 },
    { type: 'subtitle', text: 'Let\'s switch to Arabic. Notice the UI instantly adapts to Right-to-Left (RTL) formatting.', delay: 6000 },
    { type: 'select', targetId: 'language-select', value: 'ar-SA', delay: 1500 },
    { type: 'log', text: '[System] UI Direction set to RTL (Arabic)', status: 'info' },
    { type: 'subtitle', text: 'The AI continues the conversation seamlessly in the new language, maintaining context and compassion.', delay: 7000 },
    { type: 'log', text: '[Nova] Context preserved. Switching output locale to ar-SA.', status: 'success' },
    { type: 'wait', delay: 6000 },

    // --- 2:00 - 2:45: STEP 3 - NOVA ACT AGENTIC AUTOMATION ---
    { type: 'subtitle', text: 'Step 3: Agentic Automation. Our AI doesn\'t just talk; it acts.', delay: 6000 },
    { type: 'cursor', targetId: 'chat-input', delay: 2000 },
    { type: 'subtitle', text: 'The user needs to track their USCIS case status. Instead of sending them to a portal, the AI does it for them.', delay: 7000 },
    { type: 'type', text: 'Can you check my status for MSC2390123456?', targetId: 'chat-input', delay: 500 },
    { type: 'cursor', targetId: 'send-button', delay: 1000 },
    { type: 'click', targetId: 'send-button', delay: 500 },
    { type: 'subtitle', text: 'Nova Act triggers a custom Playwright agent to navigate the government portal in real-time.', delay: 6000 },
    { type: 'log', text: '[Nova Act] UI Automation Triggered: USCIS Case Status Check', status: 'info' },
    { type: 'log', text: '[Nova Act] Navigating to my.uscis.gov/casestatus...', status: 'info' },
    { type: 'log', text: '[Nova Act] Status Extracted: "Decision Pending - Interview Scheduled"', status: 'success' },
    { type: 'subtitle', text: 'The result is fed back into the conversation, providing instant, actionable updates.', delay: 7000 },
    { type: 'log', text: '[Nova] Your interview has been scheduled. Would you like to see preparation tips?', status: 'info' },
    { type: 'wait', delay: 4000 },

    // --- 2:45 - 3:00: CONCLUSION & IMPACT ---
    { type: 'subtitle', text: 'This is the Refugee Legal Navigator: A compassionate, autonomous agent for the most vulnerable.', delay: 7000 },
    { type: 'log', text: '[System] Mission: Justice for All.', status: 'success' },
    { type: 'subtitle', text: 'Built with Amazon Nova. Empowering human rights through Agentic AI.', delay: 7000 },
    { type: 'cursor', x: '95%', y: '95%', delay: 1000 },
];

export function DirectorMode({ onClose, onSelectLanguage, onSetInputText, onSendMessage }) {
    const [subtitle, setSubtitle] = useState('');
    const [cursorPos, setCursorPos] = useState({ x: 100, y: 100 });
    const [isClicking, setIsClicking] = useState(false);
    const [logs, setLogs] = useState([]);
    const [isCountingDown, setIsCountingDown] = useState(false);
    
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);
    const webcamRef = useRef(null);
    const hasStartedRef = useRef(false);

    const addLog = (msg, status = 'info') => {
        const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        setLogs(prev => [...prev, { time, msg, status }].slice(-8));
    };

    const speak = (text) => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    };

    const typeSim = async (text) => {
        let current = '';
        for (let char of text) {
            current += char;
            onSetInputText(current);
            await new Promise(r => setTimeout(r, 30 + Math.random() * 40));
        }
    };

    const startRecordingFlow = async () => {
        try {
            // Setup Webcam
            try {
                const camStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
                if (webcamRef.current) webcamRef.current.srcObject = camStream;
            } catch (e) {
                console.warn("No camera found", e);
            }

            // Setup Screen Share
            const stream = await navigator.mediaDevices.getDisplayMedia({ 
                video: { displaySurface: "browser" }, 
                audio: true 
            });
            
            const recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
            chunksRef.current = [];
            recorder.ondataavailable = (e) => {
                if (e.data.size > 0) chunksRef.current.push(e.data);
            };
            recorder.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: 'video/webm' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `refugee-legal-navigator-demo-${Date.now()}.webm`;
                a.click();
            };
            
            mediaRecorderRef.current = recorder;
            setIsCountingDown(true);
            
            // 5 second countdown before script starts
            for (let i = 5; i > 0; i--) {
                setSubtitle(`Recording starts in ${i}...`);
                await new Promise(r => setTimeout(r, 1000));
            }
            
            setIsCountingDown(false);
            setSubtitle(""); 
            recorder.start();
            runScript();
            
        } catch (err) {
            console.error("Recording failed:", err);
            onClose();
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
        if (webcamRef.current && webcamRef.current.srcObject) {
            webcamRef.current.srcObject.getTracks().forEach(track => track.stop());
        }
    };

    const runScript = async () => {
        for (const step of SCRIPT) {
            if (step.type === 'subtitle') {
                setSubtitle(step.text);
                speak(step.text);
            } else if (step.type === 'log') {
                addLog(step.text, step.status);
            }

            let nextPos = null;
            if ('targetId' in step && step.targetId) {
                const el = document.getElementById(step.targetId);
                if (el) {
                    const rect = el.getBoundingClientRect();
                    nextPos = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
                }
            } else if (step.type === 'cursor' && step.x !== undefined && step.y !== undefined) {
                nextPos = {
                    x: typeof step.x === 'string' ? (parseFloat(step.x) / 100) * window.innerWidth : step.x,
                    y: typeof step.y === 'string' ? (parseFloat(step.y) / 100) * window.innerHeight : step.y
                };
            }

            if (nextPos) setCursorPos(nextPos);

            if (step.type === 'type' && step.text) {
                await typeSim(step.text);
            }

            if (step.type === 'click' && step.targetId) {
                setIsClicking(true);
                await new Promise(r => setTimeout(r, 200));
                const el = document.getElementById(step.targetId);
                if (el) {
                    el.click();
                    // If it's the send button, trigger the actual App action
                    if (step.targetId === 'send-button') {
                        // Finding the value from the input field if possible, or just using onSendMessage
                        const input = document.getElementById('chat-input');
                        if (input) onSendMessage(input.value);
                    }
                }
                await new Promise(r => setTimeout(r, 200));
                setIsClicking(false);
            }

            if (step.type === 'select' && step.targetId) {
                onSelectLanguage(step.value);
            }

            if (step.delay) await new Promise(r => setTimeout(r, step.delay));
        }
        
        stopRecording();
        setSubtitle("Saving Recording...");
        setTimeout(onClose, 3000);
    };

    useEffect(() => {
        if (hasStartedRef.current) return;
        hasStartedRef.current = true;
        startRecordingFlow();
    }, []);

    return (
        <div className="director-overlay fixed inset-0 pointer-events-none z-[9999]">
            {/* Dark Backdrop during countdown */}
            {isCountingDown && (
                <div className="absolute inset-0 bg-black/40 backdrop-blur-sm pointer-events-auto" />
            )}

            {/* Subtitle */}
            <AnimatePresence>
                {subtitle && (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="absolute top-20 left-0 right-0 text-center px-10"
                    >
                        <span className="bg-black/80 text-white text-2xl font-bold px-6 py-3 rounded-2xl shadow-2xl border border-white/10 backdrop-blur-md">
                            {subtitle}
                        </span>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Virtual Console */}
            <div className="absolute bottom-10 left-10 w-96 bg-black/90 border border-white/20 rounded-2xl p-4 font-mono text-[10px] shadow-2xl backdrop-blur-md overflow-hidden">
                <div className="flex justify-between border-b border-white/10 pb-2 mb-2 text-white/50 uppercase tracking-widest text-[8px]">
                    <span>Nova Console</span>
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                </div>
                <div className="space-y-1">
                    {logs.map((log, i) => (
                        <div key={i} className={`flex gap-2 ${log.status === 'success' ? 'text-green-400' : log.status === 'error' ? 'text-red-400' : 'text-blue-300'}`}>
                            <span className="opacity-40">[{log.time}]</span>
                            <span>{log.msg}</span>
                        </div>
                    ))}
                    {logs.length === 0 && <div className="text-white/20">System Idle...</div>}
                </div>
            </div>

            {/* Webcam Bubble */}
            <div className="absolute bottom-10 right-10 w-48 h-48 rounded-full border-4 border-indigo-500 overflow-hidden shadow-2xl bg-black">
                <video 
                    ref={webcamRef} 
                    autoPlay 
                    muted 
                    playsInline 
                    className="w-full h-full object-cover scale-x-[-1]" 
                />
            </div>

            {/* Virtual Mouse */}
            <motion.div 
                className="absolute w-8 h-8 z-[10000]"
                animate={{ x: cursorPos.x, y: cursorPos.y }}
                transition={{ duration: 1.2, ease: "easeInOut" }}
            >
                <div className={`w-6 h-6 border-2 border-white shadow-xl rounded-full flex items-center justify-center transition-transform ${isClicking ? 'scale-75 bg-white/50' : 'bg-transparent'}`}>
                    <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                </div>
            </motion.div>

            {/* Stop Button */}
            <button 
                className="absolute top-5 right-5 pointer-events-auto bg-red-500/20 hover:bg-red-500/40 text-red-500 p-3 rounded-full border border-red-500/50 transition-colors shadow-lg flex items-center gap-2 group"
                onClick={() => { stopRecording(); onClose(); }}
            >
                <div className="w-3 h-3 bg-red-500 rounded-sm animate-pulse group-hover:animate-none"></div>
                <span className="text-[10px] font-bold uppercase tracking-widest pr-1">Stop Recording</span>
            </button>
        </div>
    );
}

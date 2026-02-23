import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Director Mode Script for Refugee Legal Navigator
const SCRIPT = [
    { type: 'cursor', x: '50%', y: '50%', delay: 1500 },
    { type: 'subtitle', text: 'Welcome to the Refugee Legal Navigator.', delay: 3000 },
    { type: 'log', text: '[System] Initializing Nova Reasoning Engine...', status: 'info' },
    { type: 'log', text: '[System] Vector Store Ready: 50 chunks indexed.', status: 'success' },

    // Step 1: Legal RAG Demo
    { type: 'subtitle', text: 'Step 1: AI-Powered Legal Reasoning (RAG)', delay: 2000 },
    { type: 'cursor', targetId: 'mic-button', delay: 1500 },
    { type: 'subtitle', text: 'Ask about asylum eligibility in natural language.', delay: 3000 },
    { type: 'log', text: '[User] Am I eligible for asylum in the US?', status: 'info' },
    { type: 'log', text: '[Nova] Retrieving legal context from 1951 Convention...', status: 'info' },
    { type: 'log', text: '[Nova] Responding with grounded legal guidance.', status: 'success' },

    // Step 2: Multilingual Demo
    { type: 'subtitle', text: 'Step 2: Breaking Language Barriers (22 Languages)', delay: 2000 },
    { type: 'cursor', targetId: 'language-select', delay: 1500 },
    { type: 'click', targetId: 'language-select', delay: 500 },
    { type: 'select', targetId: 'language-select', value: 'ar-SA', delay: 1000 },
    { type: 'subtitle', text: 'Switching to Arabic. Notice the RTL UI adjustment.', delay: 3000 },
    { type: 'log', text: '[System] UI Language set to: Arabic (Saudi Arabia)', status: 'info' },

    // Step 3: Nova Act Demo
    { type: 'subtitle', text: 'Step 3: Autonomous Case Tracking (Nova Act)', delay: 2000 },
    { type: 'cursor', targetId: 'chat-input', delay: 1500 },
    { type: 'subtitle', text: 'Track specific USCIS cases automatically.', delay: 3000 },
    { type: 'log', text: '[User] Check status for MSC1234567890', status: 'info' },
    { type: 'log', text: '[Nova Act] Navigating to USCIS Portal...', status: 'info' },
    { type: 'log', text: '[Nova Act] Extracting real-time status: "Card Was Produced"', status: 'success' },

    // Outro
    { type: 'subtitle', text: 'Refugee Legal Navigator: Justice for All.', delay: 4000 },
];

export function DirectorMode({ onClose, onSelectLanguage }) {
    const [subtitle, setSubtitle] = useState('');
    const [cursorPos, setCursorPos] = useState({ x: 100, y: 100 });
    const [isClicking, setIsClicking] = useState(false);
    const [logs, setLogs] = useState([]);
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

            if (step.type === 'click' && step.targetId) {
                setIsClicking(true);
                await new Promise(r => setTimeout(r, 200));
                const el = document.getElementById(step.targetId);
                if (el) el.click();
                await new Promise(r => setTimeout(r, 200));
                setIsClicking(false);
            }

            if (step.type === 'select' && step.targetId) {
                onSelectLanguage(step.value);
            }

            if (step.delay) await new Promise(r => setTimeout(r, step.delay));
        }
        setTimeout(onClose, 2000);
    };

    useEffect(() => {
        if (hasStartedRef.current) return;
        hasStartedRef.current = true;
        runScript();
    }, []);

    return (
        <div className="director-overlay fixed inset-0 pointer-events-none z-[9999]">
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
                className="absolute top-5 right-5 pointer-events-auto bg-red-500/20 hover:bg-red-500/40 text-red-500 p-3 rounded-full border border-red-500/50 transition-colors shadow-lg"
                onClick={onClose}
            >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="6" y="6" width="12" height="12" rx="2" />
                </svg>
            </button>
        </div>
    );
}

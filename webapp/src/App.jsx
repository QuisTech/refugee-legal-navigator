import React, { useState } from 'react';
import { 
  Mic, FileSearch, Scale, MapPin, MessageSquare, ShieldCheck, User, ChevronRight, Activity, Globe
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <button 
    onClick={onClick}
    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
      active ? 'bg-blue-600 shadow-lg shadow-blue-900/40 text-white' : 'text-gray-400 hover:bg-white/5 hover:text-white'
    }`}
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </button>
);

const StatusCard = ({ title, value, status, icon: Icon }) => (
  <div className="glass p-5 rounded-2xl flex flex-col space-y-3">
    <div className="flex justify-between items-start">
      <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
        <Icon size={20} />
      </div>
      <span className={`px-2 py-1 rounded-md text-[10px] uppercase tracking-wider font-bold ${
        status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
      }`}>
        {status}
      </span>
    </div>
    <div>
      <p className="text-gray-400 text-sm font-medium">{title}</p>
      <p className="text-2xl font-bold tracking-tight">{value}</p>
    </div>
  </div>
);

export default function App() {
  const [activeTab, setActiveTab] = useState('Assistant');
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("Hello! How can I help you today?");

  const toggleListening = () => {
    setIsListening(!isListening);
    if (!isListening) {
      setTranscript("Listening for your voice...");
    } else {
      setTranscript("Processing your inquiry with Amazon Nova...");
    }
  };

  return (
    <div className="min-h-screen flex bg-dot-pattern">
      <aside className="w-72 border-r border-white/10 bg-black/40 backdrop-blur-xl flex flex-col p-6 space-y-8">
        <div className="flex items-center space-x-3 px-2">
          <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 to-sky-400 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Scale className="text-white" size={24} />
          </div>
          <h1 className="text-xl font-bold tracking-tight">Refugee<span className="text-blue-500">Legal</span></h1>
        </div>
        <nav className="flex-1 space-y-2">
          <SidebarItem icon={MessageSquare} label="Assistant" active={activeTab === 'Assistant'} onClick={() => setActiveTab('Assistant')} />
          <SidebarItem icon={FileSearch} label="Case Tracker" active={activeTab === 'Case Tracker'} onClick={() => setActiveTab('Case Tracker')} />
          <SidebarItem icon={ShieldCheck} label="Legal Screening" active={activeTab === 'Legal Screening'} onClick={() => setActiveTab('Legal Screening')} />
          <SidebarItem icon={MapPin} label="Lawyer Matching" active={activeTab === 'Lawyer Matching'} onClick={() => setActiveTab('Lawyer Matching')} />
          <SidebarItem icon={Globe} label="Language Support" active={activeTab === 'Language Support'} onClick={() => setActiveTab('Language Support')} />
        </nav>
        <div className="glass p-4 rounded-2xl space-y-3">
          <div className="flex items-center space-x-3 text-xs">
            <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center overflow-hidden">
               <User size={16} className="text-gray-400" />
            </div>
            <div>
              <p className="font-bold">Guest User</p>
              <p className="text-gray-500">ID: #8359-6099</p>
            </div>
          </div>
        </div>
      </aside>
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="px-10 py-6 border-b border-white/10 flex justify-between items-center bg-black/20">
          <div>
            <h2 className="text-2xl font-bold font-outfit">{activeTab}</h2>
            <p className="text-gray-400 text-sm italic">Empowered by Amazon Nova AI</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-xs text-gray-400">
               <Activity size={14} className="text-green-500" />
               <span>Nova 2 Sonic Online</span>
            </div>
            <button className="bg-white/5 hover:bg-white/10 p-2 rounded-xl transition-colors">
              <User size={20} />
            </button>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto p-10 space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatusCard title="Case Status" value="In Progress" status="active" icon={FileSearch} />
            <StatusCard title="Legal Grounds" value="Screening Pending" status="waiting" icon={Scale} />
            <StatusCard title="Assigned Lawyer" value="Finding Match..." status="waiting" icon={User} />
          </div>
          <div className="relative h-[400px] glass rounded-3xl overflow-hidden flex flex-col">
            <div className="absolute inset-0 bg-gradient-to-b from-blue-600/5 to-transparent pointer-events-none" />
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-center space-y-8">
              <div className="relative">
                <AnimatePresence>
                  {isListening && (
                    <motion.div 
                      key="pulse"
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1.5, opacity: 1 }}
                      exit={{ scale: 0.8, opacity: 0 }}
                      className="absolute inset-0 bg-blue-500/20 rounded-full filter blur-xl"
                    />
                  )}
                </AnimatePresence>
                <button 
                  onClick={toggleListening}
                  className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all duration-500 ${
                    isListening ? 'bg-red-500 shadow-2xl shadow-red-500/50 scale-110' : 'bg-blue-600 shadow-2xl shadow-blue-600/50 hover:scale-105'
                  }`}
                >
                  <Mic className="text-white" size={36} />
                </button>
              </div>
              <div className="space-y-3 max-w-lg">
                <h3 className="text-3xl font-bold tracking-tight">How can I help you?</h3>
                <p className="text-gray-400 leading-relaxed text-lg">{transcript}</p>
              </div>
            </div>
            <div className="p-6 bg-white/5 border-t border-white/10 flex items-center space-x-4 uppercase tracking-tighter">
               <input 
                type="text" 
                placeholder="Type your message here..."
                className="flex-1 bg-transparent border-none focus:ring-0 text-lg placeholder:text-gray-600"
               />
               <button className="bg-blue-600 hover:bg-blue-500 p-3 rounded-xl transition-all shadow-lg shadow-blue-600/20">
                <ChevronRight size={24} />
               </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

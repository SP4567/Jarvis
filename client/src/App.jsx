import React, { useState, useEffect, useRef } from 'react';
import { Shield, Sparkles, Activity, Settings, Radio, Volume2, ShieldAlert, Layers, Power, Brain, Cpu, GitBranch, Terminal, Eye } from 'lucide-react';
import ArcReactor from './components/ArcReactor';
import VoiceController from './components/VoiceController';
import AgentMatrix from './components/AgentMatrix';
import TelemetryPanel from './components/TelemetryPanel';
import ActivityFeed from './components/ActivityFeed';
import GuardrailModal from './components/GuardrailModal';
import CommandInput from './components/CommandInput';
import CyberPlayer from './components/CyberPlayer';
import SocDashboard from './components/soc/SocDashboard';
import SmartMemoryModal from './components/SmartMemoryModal';
import AudioWaveVisualizer from './components/AudioWaveVisualizer';
import ReasoningTraceDrawer from './components/ReasoningTraceDrawer';
import ThoughtGraphModal from './components/ThoughtGraphModal';
import CodeCanvasDrawer from './components/CodeCanvasDrawer';
import ScreenVisionHUD from './components/ScreenVisionHUD';
import CompactPiPWidget from './components/CompactPiPWidget';
import { playWakeSound } from './utils/audioEffects';

export default function App() {
  const [activeView, setActiveView] = useState('ASSISTANT'); // 'ASSISTANT' | 'SOC_OPERATIONS'
  const [jarvisState, setJarvisState] = useState('idle'); // idle | thinking | speaking | guardrail_alert
  const [audioLevel, setAudioLevel] = useState(0);
  const [vitals, setVitals] = useState({});
  const [agents, setAgents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [pendingGuardrails, setPendingGuardrails] = useState([]);
  const [socData, setSocData] = useState({ metrics: {}, pending_containment: [] });
  const [socEnabled, setSocEnabled] = useState(true);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  // JARVIS-V2 Modals & Drawers
  const [isMemoryModalOpen, setIsMemoryModalOpen] = useState(false);
  const [isTraceDrawerOpen, setIsTraceDrawerOpen] = useState(false);
  const [isThoughtGraphOpen, setIsThoughtGraphOpen] = useState(false);
  const [isCodeCanvasOpen, setIsCodeCanvasOpen] = useState(false);
  const [isVisionHudOpen, setIsVisionHudOpen] = useState(false);

  const wsRef = useRef(null);
  const currentAudioRef = useRef(null);

  // Initialize WebSocket Connection
  useEffect(() => {
    let ws;
    const connectWS = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname || '127.0.0.1';
      const wsUrl = `${protocol}//${host}:8000/ws/live`;

      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        playWakeSound();
        addLogMessage('assistant', 'J.A.R.V.I.S. V2 Online. Autonomous Swarm, Vision 2.0 & Cognitive Core fully operational, Sir.');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'telemetry_update') {
            if (data.vitals) setVitals(data.vitals);
            if (data.agents) setAgents(data.agents);
            if (data.soc) setSocData(data.soc);
            if (data.pending_guardrails) {
              setPendingGuardrails(data.pending_guardrails);
              if (data.pending_guardrails.length > 0) {
                setJarvisState('guardrail_alert');
              }
            }
          } else if (data.type === 'agent_thought') {
            if (data.thought) {
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                if (last && last.role === 'assistant') {
                  const updated = {
                    ...last,
                    thoughts: [...(last.thoughts || []), data.thought]
                  };
                  return [...prev.slice(0, -1), updated];
                }
                return prev;
              });
            }
          } else if (data.type === 'jarvis_state') {
            setJarvisState(data.state);
            if (data.response_text) {
              addLogMessage('assistant', data.response_text, data.agent_used, data.actions, data.thoughts, data.latency_ms);
              if (data.actions) {
                for (const act of data.actions) {
                  const resData = act.result?.result || act.result;
                  if (resData && resData.video_id) {
                    setCurrentTrack({
                      video_id: resData.video_id,
                      title: resData.title,
                      url: resData.url
                    });
                  }
                }
              }
            }
          } else if (data.type === 'audio_payload') {
            playAudioPayload(data.audio_base64, data.text);
          } else if (data.type === 'interrupted') {
            stopAudioPlayback();
            setJarvisState('idle');
          } else if (data.type === 'handshake') {
            if (data.vitals) setVitals(data.vitals);
            if (data.agents) setAgents(data.agents);
            if (data.soc_metrics) setSocData((prev) => ({ ...prev, metrics: data.soc_metrics }));
          }

        } catch (e) {
          console.error('WS Parse Error:', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setTimeout(connectWS, 3000);
      };

      ws.onerror = () => {
        setIsConnected(false);
      };

      wsRef.current = ws;
    };

    connectWS();

    return () => {
      if (wsRef.current) wsRef.current.close();
      stopAudioPlayback();
    };
  }, []);

  const addLogMessage = (role, content, agent_used = null, actions = [], thoughts = [], latency_ms = 0.0) => {
    setMessages((prev) => [
      ...prev,
      {
        role,
        content,
        agent_used,
        actions,
        thoughts,
        latency_ms,
        timestamp: new Date().toLocaleTimeString()
      }
    ]);
  };

  const levelIntervalRef = useRef(null);

  const speakBrowserFallback = (text) => {
    if (!('speechSynthesis' in window) || !text) {
      setJarvisState('idle');
      return;
    }

    try {
      window.speechSynthesis.cancel();
      const clean = text.replace(/```[\s\S]*?```/g, '').replace(/[*_#>`~]/g, ' ').trim();
      if (!clean) {
        setJarvisState('idle');
        return;
      }

      const utterance = new SpeechSynthesisUtterance(clean);
      const voices = window.speechSynthesis.getVoices() || [];
      const jarvisVoice = voices.find((v) =>
        v.lang.includes('en-GB') ||
        v.name.toLowerCase().includes('british') ||
        v.name.toLowerCase().includes('ryan') ||
        v.name.toLowerCase().includes('daniel') ||
        v.name.toLowerCase().includes('george')
      ) || voices.find((v) => v.lang.startsWith('en'));

      if (jarvisVoice) utterance.voice = jarvisVoice;
      utterance.rate = 1.05;
      utterance.pitch = 1.0;

      utterance.onstart = () => {
        setJarvisState('speaking');
        if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
        levelIntervalRef.current = setInterval(() => {
          setAudioLevel(Math.floor(Math.random() * 45) + 30);
        }, 100);
      };

      utterance.onend = () => {
        if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
        levelIntervalRef.current = null;
        setAudioLevel(0);
        setJarvisState('idle');
      };

      utterance.onerror = () => {
        if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
        levelIntervalRef.current = null;
        setAudioLevel(0);
        setJarvisState('idle');
      };

      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn('SpeechSynthesis error:', e);
      setJarvisState('idle');
    }
  };

  const playAudioPayload = (base64Audio, fallbackText = '') => {
    stopAudioPlayback();

    if (!base64Audio) {
      speakBrowserFallback(fallbackText);
      return;
    }

    try {
      const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
      currentAudioRef.current = audio;
      
      setJarvisState('speaking');
      
      if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
      levelIntervalRef.current = setInterval(() => {
        setAudioLevel(Math.floor(Math.random() * 45) + 30);
      }, 100);

      audio.onended = () => {
        if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
        levelIntervalRef.current = null;
        setAudioLevel(0);
        setJarvisState('idle');
        currentAudioRef.current = null;
      };

      audio.onerror = (err) => {
        console.warn('Audio playback fallback:', err);
        if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
        levelIntervalRef.current = null;
        currentAudioRef.current = null;
        speakBrowserFallback(fallbackText);
      };

      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch((e) => {
          console.warn('Audio play fallback:', e);
          if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
          levelIntervalRef.current = null;
          currentAudioRef.current = null;
          speakBrowserFallback(fallbackText);
        });
      }
    } catch (e) {
      console.warn('Audio construct error:', e);
      speakBrowserFallback(fallbackText);
    }
  };

  const stopAudioPlayback = () => {
    if (levelIntervalRef.current) {
      clearInterval(levelIntervalRef.current);
      levelIntervalRef.current = null;
    }
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
    }
    setAudioLevel(0);
  };

  const handleInterrupt = () => {
    stopAudioPlayback();
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'interrupt' }));
    }
    setJarvisState('idle');
  };

  const handleSendMessage = (text) => {
    if (!text.trim()) return;
    addLogMessage('user', text);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'user_message',
        text: text
      }));
    } else {
      fetch('http://127.0.0.1:8000/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: text })
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.response) {
            addLogMessage('assistant', data.response, data.agent_used, data.actions);
            if (data.actions) {
              for (const act of data.actions) {
                const resData = act.result?.result || act.result;
                if (resData && resData.video_id) {
                  setCurrentTrack({
                    video_id: resData.video_id,
                    title: resData.title,
                    url: resData.url
                  });
                }
              }
            }
            if (data.audio_base64 || data.response) {
              playAudioPayload(data.audio_base64, data.response);
            }
          }
        })
        .catch((err) => console.error(err));
    }
  };

  const handleResolveGuardrail = (action_id, approved) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'guardrail_resolve',
        action_id,
        approved
      }));
    } else {
      fetch('http://127.0.0.1:8000/api/guardrails/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id, approved })
      });
    }
    setPendingGuardrails((prev) => prev.filter((req) => req.action_id !== action_id));
    setJarvisState('idle');
  };

  const handleToggleSoc = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/soc/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !socEnabled })
      });
      if (res.ok) {
        const data = await res.json();
        setSocEnabled(data.enabled);
        addLogMessage('assistant', `SOC Security Matrix is now ${data.enabled ? 'ACTIVE' : 'IN STANDBY'}, Sir.`);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const criticalIncidentCount = socData.metrics?.critical_p0_p1 || 0;

  return (
    <div className="min-h-screen bg-cyber-grid text-slate-100 p-4 md:p-6 flex flex-col justify-between relative overflow-hidden font-sans">
      {/* Executive Command Header */}
      <header className="flex flex-wrap items-center justify-between gap-4 pb-3 mb-4 border border-white/[0.08] bg-slate-900/70 backdrop-blur-xl px-5 py-2.5 rounded-xl shadow-2xl">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
            <Sparkles size={16} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-wider text-slate-100 font-mono">
                J.A.R.V.I.S.
              </h1>
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-950 border border-white/[0.08] text-sky-300 font-bold">
                V2.0 PRO
              </span>
            </div>
            <p className="text-[10px] font-mono text-slate-400">
              NEXT-GEN COGNITIVE OPERATING SYSTEM
            </p>
          </div>
        </div>

        {/* Audio Equalizer Visualizer */}
        <div className="hidden lg:flex items-center">
          <AudioWaveVisualizer state={jarvisState} audioLevel={audioLevel} />
        </div>

        {/* HUD View Mode Switcher & V2 Tools */}
        <div className="flex items-center gap-1.5 p-1 rounded-lg bg-slate-950/80 border border-white/[0.06] flex-wrap">
          <button
            onClick={() => setActiveView('ASSISTANT')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
              activeView === 'ASSISTANT'
                ? 'bg-slate-800 text-white shadow-sm font-semibold border border-white/[0.08]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers size={13} /> ASSISTANT
          </button>
          
          <button
            onClick={() => setActiveView('SOC_OPERATIONS')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all relative ${
              activeView === 'SOC_OPERATIONS'
                ? 'bg-rose-950/80 text-rose-200 shadow-sm font-semibold border border-rose-800/60'
                : 'text-slate-400 hover:text-rose-300'
            }`}
          >
            <ShieldAlert size={13} /> CYBER SOC
            {criticalIncidentCount > 0 && (
              <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping absolute -top-0.5 -right-0.5" />
            )}
          </button>

          {/* V2 Thought Graph Button */}
          <button
            onClick={() => setIsThoughtGraphOpen(true)}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-[11px] font-mono font-medium text-sky-400 hover:text-sky-200 hover:bg-slate-900 transition-all border border-transparent hover:border-white/[0.06]"
            title="Open Swarm Thought Graph"
          >
            <GitBranch size={12} />
            <span>DAG GRAPH</span>
          </button>

          {/* V2 Code Canvas Button */}
          <button
            onClick={() => setIsCodeCanvasOpen(true)}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-[11px] font-mono font-medium text-emerald-400 hover:text-emerald-200 hover:bg-slate-900 transition-all border border-transparent hover:border-white/[0.06]"
            title="Open Code Canvas IDE"
          >
            <Terminal size={12} />
            <span>CANVAS</span>
          </button>

          {/* V2 Vision Grounding Button */}
          <button
            onClick={() => setIsVisionHudOpen(true)}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-[11px] font-mono font-medium text-amber-400 hover:text-amber-200 hover:bg-slate-900 transition-all border border-transparent hover:border-white/[0.06]"
            title="Open Screen Vision 2.0"
          >
            <Eye size={12} />
            <span>VISION</span>
          </button>

          {/* Smart Memory Button */}
          <button
            onClick={() => setIsMemoryModalOpen(true)}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-[11px] font-mono font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-all border border-transparent hover:border-white/[0.06]"
            title="Open Smart Memory Matrix"
          >
            <Brain size={12} />
            <span>MEMORY</span>
          </button>

          {/* Reasoning Trace Drawer Button */}
          <button
            onClick={() => setIsTraceDrawerOpen(true)}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-[11px] font-mono font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-all border border-transparent hover:border-white/[0.06]"
            title="Open Agent Reasoning Trace"
          >
            <Cpu size={12} />
            <span>TRACES</span>
          </button>

          {/* Master SOC Power Switch */}
          <button
            onClick={handleToggleSoc}
            title={socEnabled ? "SOC Security Active" : "SOC Security Standby"}
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-md text-[11px] font-mono font-medium transition-all ${
              socEnabled 
                ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/40' 
                : 'bg-amber-950/60 text-amber-300 border border-amber-800/40'
            }`}
          >
            <Power size={11} className={socEnabled ? 'text-emerald-400' : 'text-amber-400'} />
            <span>SOC: {socEnabled ? 'ON' : 'OFF'}</span>
          </button>
        </div>

        {/* Live Network & Security Status */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-950/80 border border-white/[0.06]">
            <span
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-emerald-400 status-dot-pulse' : 'bg-rose-500'
              }`}
            />
            <span className={isConnected ? 'text-slate-300 text-[11px]' : 'text-rose-400 text-[11px]'}>
              {isConnected ? 'ONLINE' : 'DISCONNECTED'}
            </span>
          </div>
        </div>
      </header>

      {/* Main View Container */}
      {activeView === 'ASSISTANT' ? (
        <main className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1 items-start mb-4">
          {/* Left Telemetry Panel (3 cols) */}
          <div className="lg:col-span-3 h-full">
            <TelemetryPanel vitals={vitals} />
          </div>

          {/* Center Holographic Core & Voice Controls (5 cols) */}
          <div className="lg:col-span-5 flex flex-col items-center justify-center gap-4 py-2">
            <ArcReactor state={jarvisState} audioLevel={audioLevel} size={300} />
            
            <VoiceController
              onSendMessage={handleSendMessage}
              onAudioLevelChange={setAudioLevel}
              isJarvisSpeaking={jarvisState === 'speaking'}
              onInterrupt={handleInterrupt}
            />
          </div>

          {/* Right Activity Feed with Integrated Directives & Prompt Field (4 cols) */}
          <div className="lg:col-span-4 h-full">
            <ActivityFeed 
              messages={messages} 
              onSendCommand={handleSendMessage}
              disabled={!isConnected}
              onClearFeed={() => setMessages([])}
            />
          </div>
        </main>
      ) : (
        <main className="flex-1 mb-4">
          <SocDashboard socData={socData} socEnabled={socEnabled} />
        </main>
      )}

      {/* Bottom Subagents Matrix */}
      {activeView === 'ASSISTANT' && (
        <footer className="space-y-3">
          <AgentMatrix agents={agents} />
        </footer>
      )}

      {/* Embedded Cyber Music Player */}
      <CyberPlayer
        currentTrack={currentTrack}
        onClose={() => setCurrentTrack(null)}
      />

      {/* Security Guardrail Modal */}
      <GuardrailModal
        pendingApprovals={pendingGuardrails}
        onResolve={handleResolveGuardrail}
      />

      {/* Smart Memory Matrix Modal */}
      <SmartMemoryModal
        isOpen={isMemoryModalOpen}
        onClose={() => setIsMemoryModalOpen(false)}
      />

      {/* Reasoning Trace Drawer */}
      <ReasoningTraceDrawer
        isOpen={isTraceDrawerOpen}
        onClose={() => setIsTraceDrawerOpen(false)}
        agents={agents}
        messages={messages}
      />

      {/* JARVIS-V2: Thought Graph Modal */}
      <ThoughtGraphModal
        isOpen={isThoughtGraphOpen}
        onClose={() => setIsThoughtGraphOpen(false)}
        thoughts={messages.flatMap((m) => m.thoughts || [])}
      />

      {/* JARVIS-V2: Code Canvas Drawer */}
      <CodeCanvasDrawer
        isOpen={isCodeCanvasOpen}
        onClose={() => setIsCodeCanvasOpen(false)}
      />

      {/* JARVIS-V2: Screen Vision HUD */}
      <ScreenVisionHUD
        isOpen={isVisionHudOpen}
        onClose={() => setIsVisionHudOpen(false)}
      />

      {/* JARVIS-V2: Compact PiP Widget */}
      <CompactPiPWidget
        state={jarvisState}
        onExpand={() => setActiveView('ASSISTANT')}
        onSendCommand={handleSendMessage}
      />
    </div>
  );
}

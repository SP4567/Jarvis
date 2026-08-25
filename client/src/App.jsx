import React, { useState, useEffect, useRef } from 'react';
import { Shield, Sparkles, Activity, Settings, Radio, Volume2, ShieldAlert, Layers, Power, Brain, Cpu } from 'lucide-react';
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

  // New Modals & Drawers
  const [isMemoryModalOpen, setIsMemoryModalOpen] = useState(false);
  const [isTraceDrawerOpen, setIsTraceDrawerOpen] = useState(false);

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
        addLogMessage('assistant', 'J.A.R.V.I.S. Core Online. Autonomous SOC Security Matrix & Subagent protocols fully initialized, Sir.');
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
            playAudioPayload(data.audio_base64);
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


  const playAudioPayload = (base64Audio) => {
    try {
      stopAudioPlayback();
      const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
      currentAudioRef.current = audio;
      
      setJarvisState('speaking');
      
      let levelInterval = setInterval(() => {
        setAudioLevel(Math.floor(Math.random() * 45) + 30);
      }, 100);

      audio.onended = () => {
        clearInterval(levelInterval);
        setAudioLevel(0);
        setJarvisState('idle');
        currentAudioRef.current = null;
      };

      audio.onerror = () => {
        clearInterval(levelInterval);
        setAudioLevel(0);
        setJarvisState('idle');
      };

      audio.play().catch((e) => {
        console.warn('Auto-play error:', e);
        clearInterval(levelInterval);
        setAudioLevel(0);
        setJarvisState('idle');
      });
    } catch (e) {
      console.warn('Audio playback error:', e);
    }
  };

  const stopAudioPlayback = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
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
            if (data.audio_base64) {
              playAudioPayload(data.audio_base64);
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
    <div className="min-h-screen bg-[#030712] text-slate-100 bg-cyber-grid p-4 md:p-6 flex flex-col justify-between relative overflow-hidden">
      {/* Top HUD Header */}
      <header className="flex flex-wrap items-center justify-between gap-4 pb-4 mb-4 border-b border-cyan-500/20 glass-panel px-6 py-3 rounded-2xl">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-neon-cyan">
            <Sparkles size={20} className="text-black" />
          </div>
          <div>
            <h1 className="text-lg md:text-xl font-orbitron font-extrabold tracking-wider text-cyan-300 glow-text-cyan">
              J.A.R.V.I.S.
            </h1>
            <p className="text-[10px] font-mono text-slate-400">
              JUST A RATHER VERY INTELLIGENT SYSTEM // ENTERPRISE SOC CORE
            </p>
          </div>
        </div>

        {/* Audio Equalizer Visualizer */}
        <div className="hidden lg:flex items-center">
          <AudioWaveVisualizer state={jarvisState} audioLevel={audioLevel} />
        </div>

        {/* HUD View Mode Switcher & Tools */}
        <div className="flex items-center gap-2 p-1 rounded-xl bg-black/60 border border-cyan-500/30">
          <button
            onClick={() => setActiveView('ASSISTANT')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
              activeView === 'ASSISTANT'
                ? 'bg-cyan-500 text-black shadow-neon-cyan'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers size={13} /> ASSISTANT HUD
          </button>
          
          <button
            onClick={() => setActiveView('SOC_OPERATIONS')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all relative ${
              activeView === 'SOC_OPERATIONS'
                ? 'bg-rose-600 text-white shadow-neon-danger'
                : 'text-slate-400 hover:text-rose-300'
            }`}
          >
            <ShieldAlert size={13} /> CYBER SOC OPERATIONS
            {criticalIncidentCount > 0 && (
              <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping absolute -top-1 -right-1" />
            )}
          </button>

          {/* Smart Memory Matrix Button */}
          <button
            onClick={() => setIsMemoryModalOpen(true)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-[11px] font-mono font-bold text-cyan-300 hover:text-cyan-100 hover:bg-cyan-500/10 border border-cyan-500/30 transition-all"
            title="Open Smart Memory Matrix"
          >
            <Brain size={12} className="text-cyan-400" />
            <span>MEMORY</span>
          </button>

          {/* Reasoning Trace Drawer Button */}
          <button
            onClick={() => setIsTraceDrawerOpen(true)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-[11px] font-mono font-bold text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-700 transition-all"
            title="Open Agent Reasoning Trace"
          >
            <Cpu size={12} className="text-slate-400" />
            <span>TRACES</span>
          </button>

          {/* Master SOC Power Switch */}
          <button
            onClick={handleToggleSoc}
            title={socEnabled ? "SOC Security Active - Click to Turn Off" : "SOC Security Standby - Click to Turn On"}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-[11px] font-mono font-bold transition-all border ${
              socEnabled 
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-neon-cyan hover:bg-emerald-500/30' 
                : 'bg-amber-500/20 text-amber-300 border-amber-500/50 hover:bg-amber-500/30'
            }`}
          >
            <Power size={12} className={socEnabled ? 'text-emerald-400' : 'text-amber-400'} />
            <span>SOC: {socEnabled ? 'ON' : 'OFF'}</span>
          </button>
        </div>

        {/* Live Network & Security Status */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-cyan-500/30">
            <span
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'
              }`}
            />
            <span className={isConnected ? 'text-emerald-300' : 'text-rose-400'}>
              {isConnected ? 'ONLINE // CORE SYNCED' : 'DISCONNECTED'}
            </span>
          </div>
        </div>
      </header>

      {/* Main View Container */}
      {activeView === 'ASSISTANT' ? (
        <main className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 items-start mb-4">
          {/* Left Telemetry Panel (3 cols) */}
          <div className="lg:col-span-3 h-full">
            <TelemetryPanel vitals={vitals} />
          </div>

          {/* Center Holographic Core & Voice Controls (5 cols) */}
          <div className="lg:col-span-5 flex flex-col items-center justify-center gap-6 py-2">
            <ArcReactor state={jarvisState} audioLevel={audioLevel} size={300} />
            
            <VoiceController
              onSendMessage={handleSendMessage}
              onAudioLevelChange={setAudioLevel}
              isJarvisSpeaking={jarvisState === 'speaking'}
              onInterrupt={handleInterrupt}
            />
          </div>

          {/* Right Activity Feed (4 cols) */}
          <div className="lg:col-span-4 h-full">
            <ActivityFeed messages={messages} />
          </div>
        </main>
      ) : (
        <main className="flex-1 mb-4">
          <SocDashboard socData={socData} socEnabled={socEnabled} />
        </main>
      )}

      {/* Bottom Subagents Matrix & Command Bar */}
      <footer className="space-y-4">
        {activeView === 'ASSISTANT' && <AgentMatrix agents={agents} />}
        <CommandInput onSendCommand={handleSendMessage} disabled={!isConnected} />
      </footer>

      {/* Embedded Cyber Music Player */}
      {currentTrack && (
        <CyberPlayer
          currentTrack={currentTrack}
          onClose={() => setCurrentTrack(null)}
        />
      )}

      {/* Security Interlock Human-In-The-Loop Modal */}
      {pendingGuardrails.length > 0 && (
        <GuardrailModal
          pendingApprovals={pendingGuardrails}
          onResolve={handleResolveGuardrail}
        />
      )}

      {/* Smart Memory Matrix Modal */}
      <SmartMemoryModal
        isOpen={isMemoryModalOpen}
        onClose={() => setIsMemoryModalOpen(false)}
      />

      {/* Agent Reasoning Trace Drawer */}
      <ReasoningTraceDrawer
        isOpen={isTraceDrawerOpen}
        onClose={() => setIsTraceDrawerOpen(false)}
        agents={agents}
        messages={messages}
      />
    </div>
  );
}

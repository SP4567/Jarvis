import React from 'react';
import { 
  Cpu, 
  Globe, 
  Calendar, 
  Music, 
  Eye, 
  Terminal, 
  ShieldCheck, 
  Activity,
  CheckCircle2,
  Clock,
  Sparkles,
  Zap,
  RotateCcw,
  Search,
  CheckSquare
} from 'lucide-react';

const AGENT_ICONS = {
  system_agent: Cpu,
  research_agent: Globe,
  productivity_agent: Calendar,
  media_agent: Music,
  vision_agent: Eye,
  coding_agent: Terminal
};

const getStatusBadge = (status) => {
  const s = (status || 'READY').toUpperCase();
  switch (s) {
    case 'PLANNING':
      return {
        label: 'PLANNING',
        dotClass: 'bg-indigo-400',
        badgeClass: 'bg-indigo-950/50 border-indigo-500/30 text-indigo-300'
      };
    case 'VERIFYING':
      return {
        label: 'VERIFYING',
        dotClass: 'bg-emerald-400',
        badgeClass: 'bg-emerald-950/50 border-emerald-500/30 text-emerald-300'
      };
    case 'RECOVERING':
      return {
        label: 'SELF-HEALING',
        dotClass: 'bg-amber-400',
        badgeClass: 'bg-amber-950/50 border-amber-500/30 text-amber-300'
      };
    case 'AWAITING_APPROVAL':
      return {
        label: 'AWAITING AUTH',
        dotClass: 'bg-rose-400 animate-pulse',
        badgeClass: 'bg-rose-950/50 border-rose-500/30 text-rose-300'
      };
    case 'EXECUTING':
    case 'BUSY':
      return {
        label: 'EXECUTING',
        dotClass: 'bg-sky-400 animate-pulse',
        badgeClass: 'bg-sky-950/50 border-sky-500/30 text-sky-300'
      };
    default:
      return {
        label: 'ONLINE',
        dotClass: 'bg-emerald-400',
        badgeClass: 'bg-slate-950/60 border-white/[0.06] text-slate-300'
      };
  }
};

export default function AgentMatrix({ agents = [] }) {
  const defaultAgents = [
    { name: 'system_agent', display_name: 'OS & System Controller', status: 'ready', calls_count: 142, avg_latency_ms: 6.2 },
    { name: 'research_agent', display_name: 'Deep Research & Web Engine', status: 'ready', calls_count: 88, avg_latency_ms: 180.4 },
    { name: 'productivity_agent', display_name: 'Memory & Notes Matrix', status: 'ready', calls_count: 54, avg_latency_ms: 12.0 },
    { name: 'media_agent', display_name: 'Hifi Audio & Ambient Music', status: 'ready', calls_count: 31, avg_latency_ms: 45.0 },
    { name: 'vision_agent', display_name: 'Vision 2.0 & OCR Grounding', status: 'ready', calls_count: 42, avg_latency_ms: 24.5 },
    { name: 'coding_agent', display_name: 'Software Engineer & Sandbox', status: 'ready', calls_count: 96, avg_latency_ms: 15.8 }
  ];

  const displayAgents = agents && agents.length > 0 ? agents : defaultAgents;

  return (
    <div className="bg-slate-900/70 backdrop-blur-xl rounded-xl p-4 border border-white/[0.08] shadow-2xl space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
            <ShieldCheck size={14} />
          </div>
          <div>
            <h2 className="text-xs uppercase tracking-wider font-mono text-slate-100 font-bold">
              AUTONOMOUS SUBAGENT FLEET
            </h2>
            <p className="text-[9px] font-mono text-slate-500">DISTRIBUTED DOMAIN EXECUTION NODES</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-950/80 border border-white/[0.06] text-[10px] font-mono text-slate-300 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 status-dot-pulse" />
            {displayAgents.length} NODES ACTIVE
          </span>
        </div>
      </div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
        {displayAgents.map((agent) => {
          const Icon = AGENT_ICONS[agent.name] || Activity;
          const badge = getStatusBadge(agent.status);

          return (
            <div
              key={agent.name}
              className="p-3 rounded-lg bg-slate-950/60 border border-white/[0.06] hover:border-white/[0.14] transition-all flex flex-col justify-between space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded bg-slate-900 border border-white/[0.06] text-sky-400 group-hover:text-sky-300 transition-colors">
                    <Icon size={13} />
                  </div>
                  <div>
                    <h3 className="text-[11px] font-bold text-slate-200 font-mono tracking-tight">
                      {agent.display_name || agent.name}
                    </h3>
                    <p className="text-[9px] text-slate-500 font-mono">{agent.name}</p>
                  </div>
                </div>

                <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded border text-[9px] font-mono font-semibold ${badge.badgeClass}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${badge.dotClass}`} />
                  <span>{badge.label}</span>
                </div>
              </div>

              {/* Execution Telemetry Footer */}
              <div className="flex items-center justify-between text-[9px] font-mono text-slate-500 pt-1.5 border-t border-white/[0.04]">
                <span>Calls: <strong className="text-slate-300 font-mono-num">{agent.calls_count || 0}</strong></span>
                <span>Latency: <strong className="text-slate-300 font-mono-num">{agent.avg_latency_ms || 8.0}ms</strong></span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

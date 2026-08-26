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
        badgeClass: 'bg-indigo-950/60 border-indigo-800/50 text-indigo-300'
      };
    case 'VERIFYING':
      return {
        label: 'VERIFYING',
        dotClass: 'bg-emerald-400',
        badgeClass: 'bg-emerald-950/60 border-emerald-800/50 text-emerald-300'
      };
    case 'RECOVERING':
      return {
        label: 'SELF-HEALING',
        dotClass: 'bg-amber-400',
        badgeClass: 'bg-amber-950/60 border-amber-800/50 text-amber-300'
      };
    case 'AWAITING_APPROVAL':
      return {
        label: 'AWAITING AUTH',
        dotClass: 'bg-rose-400 animate-pulse',
        badgeClass: 'bg-rose-950/60 border-rose-800/50 text-rose-300'
      };
    case 'EXECUTING':
    case 'BUSY':
      return {
        label: 'EXECUTING',
        dotClass: 'bg-sky-400 animate-pulse',
        badgeClass: 'bg-sky-950/60 border-sky-800/50 text-sky-300'
      };
    default:
      return {
        label: 'READY',
        dotClass: 'bg-emerald-400',
        badgeClass: 'bg-slate-950 border-slate-800 text-slate-300'
      };
  }
};

export default function AgentMatrix({ agents = [] }) {
  return (
    <div className="bg-slate-900/95 rounded-xl p-4 border border-slate-800 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-slate-800 text-slate-300">
            <ShieldCheck size={14} className="text-sky-400" />
          </div>
          <div>
            <h2 className="text-xs uppercase tracking-wider font-mono text-slate-100 font-bold">
              AUTONOMOUS SUBAGENT FLEET
            </h2>
            <p className="text-[9px] font-mono text-slate-500">DISTRIBUTED DOMAIN EXECUTION NODES</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-300 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            {agents.length || 6} NODES ONLINE
          </span>
        </div>
      </div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {agents.map((agent) => {
          const Icon = AGENT_ICONS[agent.name] || Activity;
          const isBusy = agent.status && agent.status.toLowerCase() !== 'idle' && agent.status.toLowerCase() !== 'ready';
          const statusInfo = getStatusBadge(agent.status);

          return (
            <div
              key={agent.name}
              className={`p-3 rounded-lg border transition-all duration-200 ${
                isBusy
                  ? 'bg-slate-850 border-slate-700 shadow-sm'
                  : 'bg-slate-950/80 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`p-1.5 rounded ${isBusy ? 'bg-sky-950 text-sky-400 border border-sky-800/60' : 'bg-slate-900 text-slate-400 border border-slate-800'}`}>
                    <Icon size={14} />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-slate-100 truncate max-w-[130px]">
                      {agent.display_name}
                    </h3>
                    <p className="text-[9px] text-slate-500 font-mono">
                      {agent.tools_count} Registered Tools
                    </p>
                  </div>
                </div>

                {/* Status Badge */}
                <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded border text-[8px] font-mono uppercase font-bold ${statusInfo.badgeClass}`}>
                  <span className={`w-1 h-1 rounded-full ${statusInfo.dotClass}`} />
                  <span>{statusInfo.label}</span>
                </div>
              </div>

              {/* Task or description */}
              <p className="text-[10px] text-slate-400 font-mono mb-2 line-clamp-1">
                {agent.current_task || agent.description}
              </p>

              {/* Card Footer: Metrics */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[9px] font-mono text-slate-500">
                <span className="flex items-center gap-1">
                  <Clock size={10} />
                  {agent.calls_count || 0} runs
                </span>
                <span className="text-slate-400">
                  {agent.last_latency_ms ? `${agent.last_latency_ms}ms` : 'Nominal'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

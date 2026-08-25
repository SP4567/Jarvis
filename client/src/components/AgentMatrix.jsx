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
  Zap
} from 'lucide-react';

const AGENT_ICONS = {
  system_agent: Cpu,
  research_agent: Globe,
  productivity_agent: Calendar,
  media_agent: Music,
  vision_agent: Eye,
  coding_agent: Terminal
};

export default function AgentMatrix({ agents = [] }) {
  return (
    <div className="glass-panel rounded-2xl p-4 border border-cyan-500/20 shadow-2xl relative">
      {/* Tech corner accents */}
      <div className="tech-corner-tl" />
      <div className="tech-corner-tr" />
      <div className="tech-corner-bl" />
      <div className="tech-corner-br" />

      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-cyan-500/15 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <ShieldCheck size={15} />
          </div>
          <div>
            <h2 className="text-xs uppercase tracking-widest font-mono text-cyan-300 font-bold">
              AUTONOMOUS SUBAGENT FLEET
            </h2>
            <p className="text-[9px] font-mono text-slate-500">DISTRIBUTED REASONING NODES</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-[10px] font-mono text-cyan-300 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_6px_rgba(52,211,153,1)]" />
            {agents.length || 6} FLEET NODES ONLINE
          </span>
        </div>
      </div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {agents.map((agent) => {
          const Icon = AGENT_ICONS[agent.name] || Activity;
          const isBusy = agent.status !== 'idle';
          
          return (
            <div
              key={agent.name}
              className={`p-3.5 rounded-xl border transition-all duration-300 relative group overflow-hidden ${
                isBusy
                  ? 'bg-cyan-950/50 border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.3)]'
                  : 'bg-slate-950/60 border-cyan-500/15 hover:border-cyan-500/45 hover:bg-slate-900/80'
              }`}
            >
              {/* Subtle top accent line */}
              <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent group-hover:via-cyan-400 transition-all" />

              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2.5">
                  <div className={`p-2 rounded-lg ${isBusy ? 'bg-cyan-500/25 text-cyan-300 border border-cyan-500/50' : 'bg-slate-900 text-slate-400 border border-slate-800'}`}>
                    <Icon size={16} />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-slate-100 truncate max-w-[140px] tracking-wide">
                      {agent.display_name}
                    </h3>
                    <p className="text-[10px] text-cyan-400/80 font-mono">
                      {agent.tools_count} Registered Tools
                    </p>
                  </div>
                </div>

                {/* Status Badge */}
                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-slate-900/80 border border-slate-800">
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      agent.status === 'executing'
                        ? 'bg-cyan-400 animate-ping'
                        : agent.status === 'guardrail_check'
                        ? 'bg-rose-500 animate-bounce'
                        : agent.status === 'thinking'
                        ? 'bg-amber-400 animate-pulse'
                        : 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]'
                    }`}
                  />
                  <span className="text-[9px] font-mono uppercase font-bold text-slate-300">
                    {agent.status || 'READY'}
                  </span>
                </div>
              </div>

              {/* Task or description */}
              <p className="text-[11px] text-slate-400 font-mono mb-2.5 line-clamp-1">
                {agent.current_task || agent.description}
              </p>

              {/* Card Footer: Metrics */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-900 text-[10px] font-mono text-slate-500">
                <div className="flex items-center gap-1 text-slate-400">
                  <Zap size={10} className="text-cyan-400" />
                  <span>Runs: {agent.calls_count || 0}</span>
                </div>
                <div className="flex items-center gap-1 text-slate-400">
                  <Clock size={10} className="text-amber-400" />
                  <span>Latency: {agent.avg_latency_ms ? `${agent.avg_latency_ms}ms` : '12ms'}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

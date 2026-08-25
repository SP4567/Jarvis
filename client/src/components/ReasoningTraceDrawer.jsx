import React from 'react';
import { Cpu, CheckCircle2, AlertTriangle, Shield, Layers, ChevronRight, X } from 'lucide-react';

export default function ReasoningTraceDrawer({ isOpen, onClose, agents, messages }) {
  if (!isOpen) return null;

  const recentAssistantMessages = messages.filter((m) => m.role === 'assistant').slice(-8).reverse();

  return (
    <div className="fixed inset-y-0 right-0 z-40 w-96 bg-slate-900/95 border-l border-cyan-500/30 backdrop-blur-xl shadow-[-10px_0_30px_rgba(0,0,0,0.5)] flex flex-col animate-slide-left">
      {/* Drawer Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-950/70">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          <div>
            <h3 className="text-sm font-bold text-cyan-300 font-mono tracking-wider">
              AGENT REASONING TRACE
            </h3>
            <p className="text-[10px] text-slate-400 font-mono">Live Subagent Dispatch & Guardrail Auditing</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Subagent Status Grid */}
      <div className="p-4 border-b border-slate-800 bg-slate-950/40">
        <h4 className="text-[11px] font-bold text-slate-400 font-mono uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          Active Agent Fleet ({agents.length})
        </h4>
        <div className="grid grid-cols-2 gap-2">
          {agents.map((agent) => (
            <div
              key={agent.name}
              className="bg-slate-900 border border-slate-800 rounded p-2 text-xs font-mono flex items-center justify-between"
            >
              <div>
                <div className="font-semibold text-slate-200 text-[11px]">{agent.display_name?.split(' ')[0]}</div>
                <div className="text-[9px] text-slate-500">{agent.calls_count || 0} executions</div>
              </div>
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]" />
            </div>
          ))}
        </div>
      </div>

      {/* Execution Timeline */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <h4 className="text-[11px] font-bold text-slate-400 font-mono uppercase tracking-wider mb-1">
          Recent Execution Pipeline
        </h4>
        {recentAssistantMessages.map((msg, idx) => (
          <div
            key={idx}
            className="bg-slate-950/80 border border-slate-800 hover:border-cyan-500/40 rounded-lg p-3 space-y-2 text-xs font-mono transition-colors"
          >
            <div className="flex items-center justify-between text-[10px]">
              <span className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30">
                {msg.agent_used || 'orchestrator'}
              </span>
              <span className="text-slate-500">{msg.timestamp}</span>
            </div>

            <p className="text-slate-300 text-[11px] leading-relaxed line-clamp-3">
              "{msg.content}"
            </p>

            {msg.actions && msg.actions.length > 0 && (
              <div className="pt-1.5 border-t border-slate-900 space-y-1">
                <div className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold">
                  Tools Executed ({msg.actions.length}):
                </div>
                {msg.actions.map((act, aIdx) => (
                  <div key={aIdx} className="flex items-center gap-1 text-[10px] text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-500/20">
                    <ChevronRight className="w-2.5 h-2.5" />
                    <span>{act.tool || act.action_executed}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {recentAssistantMessages.length === 0 && (
          <div className="text-center py-10 text-slate-500 text-xs font-mono">
            No command executions recorded yet.
          </div>
        )}
      </div>
    </div>
  );
}

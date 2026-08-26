import React from 'react';
import { Cpu, CheckCircle2, AlertTriangle, Shield, Layers, ChevronRight, X, GitBranch, CheckCheck, RefreshCw } from 'lucide-react';

export default function ReasoningTraceDrawer({ isOpen, onClose, agents = [], messages = [] }) {
  if (!isOpen) return null;

  const recentAssistantMessages = messages.filter((m) => m.role === 'assistant').slice(-8).reverse();

  return (
    <div className="fixed inset-y-0 right-0 z-40 w-96 bg-slate-900 border-l border-slate-800 backdrop-blur-xl shadow-2xl flex flex-col">
      {/* Drawer Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-950/80">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-sky-400" />
          <div>
            <h3 className="text-sm font-bold text-slate-100 font-mono tracking-wider">
              AGENT REASONING TRACE
            </h3>
            <p className="text-[10px] text-slate-400 font-mono">Continuous Verification & Multi-Agent Plans</p>
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
          <Cpu className="w-3.5 h-3.5 text-sky-400" />
          Active Fleet Nodes ({agents.length})
        </h4>
        <div className="grid grid-cols-2 gap-2">
          {agents.map((agent) => (
            <div
              key={agent.name}
              className="bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono flex items-center justify-between"
            >
              <div>
                <div className="font-semibold text-slate-200 text-[11px]">{agent.display_name?.split(' ')[0]}</div>
                <div className="text-[9px] text-slate-500">{agent.calls_count || 0} executions</div>
              </div>
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
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
            className="bg-slate-950 border border-slate-800 hover:border-slate-700 rounded-lg p-3 space-y-2 text-xs font-mono transition-colors"
          >
            <div className="flex items-center justify-between text-[10px]">
              <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-bold border border-slate-700">
                {msg.agent_used || 'orchestrator'}
              </span>
              <span className="text-slate-500">{msg.timestamp}</span>
            </div>

            <p className="text-slate-300 text-[11px] leading-relaxed line-clamp-3">
              "{msg.content}"
            </p>

            {/* Task Plan Steps */}
            {msg.task_plan && msg.task_plan.steps && msg.task_plan.steps.length > 0 && (
              <div className="p-2 rounded bg-slate-900 border border-slate-800 space-y-1">
                <div className="text-[9px] text-indigo-300 uppercase tracking-wider font-semibold flex items-center gap-1">
                  <GitBranch className="w-2.5 h-2.5" />
                  Task Plan ({msg.task_plan.steps.length} Steps):
                </div>
                {msg.task_plan.steps.map((st, sIdx) => (
                  <div key={sIdx} className="flex items-center justify-between text-[9px] text-slate-300">
                    <span>{st.step_number}. {st.description}</span>
                    <span className="px-1 py-0.2 rounded bg-slate-800 text-slate-400 text-[8px]">
                      {st.status}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Actions & Verification */}
            {msg.actions && msg.actions.length > 0 && (
              <div className="pt-1.5 border-t border-slate-900 space-y-1">
                <div className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold">
                  Executed Tools & Verification:
                </div>
                {msg.actions.map((act, aIdx) => (
                  <div key={aIdx} className="flex items-center justify-between text-[10px] text-slate-300 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    <div className="flex items-center gap-1">
                      <ChevronRight className="w-2.5 h-2.5 text-slate-500" />
                      <span className="font-semibold text-slate-200">{act.tool || act.action_executed}</span>
                    </div>
                    <span className="text-[9px] text-emerald-400 font-semibold">VERIFIED</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

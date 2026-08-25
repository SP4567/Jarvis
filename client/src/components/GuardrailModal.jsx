import React, { useEffect } from 'react';
import { AlertTriangle, ShieldAlert, Check, X, Terminal } from 'lucide-react';
import { playWarningAlarmSound, playAuthorizeSound, playRejectSound } from '../utils/audioEffects';

export default function GuardrailModal({ pendingApprovals = [], onResolve }) {
  const currentRequest = pendingApprovals[0];

  useEffect(() => {
    if (currentRequest) {
      playWarningAlarmSound();
    }
  }, [currentRequest?.action_id]);

  if (!currentRequest) return null;

  const handleApprove = () => {
    playAuthorizeSound();
    onResolve(currentRequest.action_id, true);
  };

  const handleReject = () => {
    playRejectSound();
    onResolve(currentRequest.action_id, false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel border-2 border-rose-500 shadow-neon-danger">
        {/* Corner tech accents in red */}
        <div className="tech-corner-tl !border-rose-500" />
        <div className="tech-corner-tr !border-rose-500" />
        <div className="tech-corner-bl !border-rose-500" />
        <div className="tech-corner-br !border-rose-500" />

        {/* Warning Header */}
        <div className="flex items-center gap-3 pb-4 border-b border-rose-500/30 mb-4">
          <div className="p-3 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse">
            <ShieldAlert size={28} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-rose-500/30 text-rose-300 border border-rose-500/50">
                SECURITY INTERLOCK // TIER 3
              </span>
              <span className="text-xs font-mono text-slate-400">ID: {currentRequest.action_id}</span>
            </div>
            <h2 className="text-lg font-bold font-orbitron text-rose-400 glow-text-danger mt-1">
              HUMAN AUTHORIZATION REQUIRED
            </h2>
          </div>
        </div>

        {/* Action Details */}
        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400">Initiating Subagent:</span>
            <span className="text-cyan-300 font-bold">{currentRequest.agent_name}</span>
          </div>

          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400">Requested Action:</span>
            <span className="text-amber-400 font-bold">{currentRequest.action_name}</span>
          </div>

          <div className="p-3 rounded-lg bg-black/60 border border-rose-500/30">
            <div className="text-[11px] font-mono text-slate-400 mb-1 flex items-center gap-1.5">
              <Terminal size={12} className="text-rose-400" />
              <span>Target Parameters / Command:</span>
            </div>
            <pre className="text-xs font-mono text-rose-200 overflow-x-auto p-2 rounded bg-rose-950/30 border border-rose-500/20">
              {JSON.stringify(currentRequest.details, null, 2)}
            </pre>
          </div>

          <p className="text-xs font-mono text-slate-300 leading-relaxed">
            <span className="text-amber-400 font-bold">Safety Note:</span> {currentRequest.description || currentRequest.reason}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between gap-4 pt-2">
          <button
            onClick={handleReject}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-slate-900 border border-rose-500/50 text-rose-400 hover:bg-rose-950/60 hover:border-rose-400 text-xs font-mono font-bold transition-all shadow-md"
          >
            <X size={16} />
            ABORT ACTION
          </button>

          <button
            onClick={handleApprove}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-black text-xs font-mono font-bold transition-all shadow-lg hover:shadow-emerald-500/30"
          >
            <Check size={16} />
            AUTHORIZE & RUN
          </button>
        </div>

        {/* Voice prompt hint */}
        <div className="mt-4 text-center text-[10px] font-mono text-slate-400">
          Or speak voice command: <span className="text-cyan-300">"JARVIS, authorize"</span> or <span className="text-rose-400">"JARVIS, abort"</span>
        </div>
      </div>
    </div>
  );
}

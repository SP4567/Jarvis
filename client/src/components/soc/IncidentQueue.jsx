import React, { useState } from 'react';
import { AlertTriangle, ShieldAlert, ShieldCheck, Clock, Server, User, ArrowRight, Filter } from 'lucide-react';

const SEVERITY_COLORS = {
  P0: "border-purple-500 bg-purple-950/40 text-purple-300 shadow-neon-danger",
  P1: "border-rose-500 bg-rose-950/40 text-rose-300 shadow-neon-danger",
  P2: "border-amber-500 bg-amber-950/40 text-amber-300 shadow-neon-amber",
  P3: "border-cyan-500 bg-cyan-950/40 text-cyan-300 shadow-neon-cyan",
  P4: "border-slate-700 bg-slate-900/40 text-slate-400"
};

const SEVERITY_BADGES = {
  P0: "bg-purple-600 text-white",
  P1: "bg-rose-600 text-white",
  P2: "bg-amber-500 text-black",
  P3: "bg-cyan-500 text-black",
  P4: "bg-slate-700 text-slate-200"
};

export default function IncidentQueue({ cases = [], selectedCaseId, onSelectCase }) {
  const [filterSeverity, setFilterSeverity] = useState('ALL');

  const filteredCases = cases.filter(c => {
    if (filterSeverity === 'ALL') return true;
    return c.severity === filterSeverity;
  });

  return (
    <div className="glass-panel rounded-xl p-4 border border-cyan-500/20 flex flex-col h-[520px]">
      <div className="tech-corner-tl" />
      <div className="tech-corner-tr" />
      <div className="tech-corner-bl" />
      <div className="tech-corner-br" />

      {/* Header & Filter Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-cyan-500/15 mb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert size={16} className="text-cyan-400" />
          <h2 className="text-xs uppercase tracking-widest font-mono text-cyan-300 font-bold">
            Live Incident Queue
          </h2>
        </div>
        <div className="flex items-center gap-1 text-[10px] font-mono">
          {['ALL', 'P1', 'P2', 'P3'].map(sev => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-2 py-0.5 rounded transition-all ${
                filterSeverity === sev
                  ? 'bg-cyan-500 text-black font-bold shadow-neon-cyan'
                  : 'bg-slate-900/80 text-slate-400 hover:text-cyan-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Incidents List */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {filteredCases.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs font-mono">
            <ShieldCheck size={24} className="text-emerald-400 mb-2 opacity-60" />
            <span>Zero incidents matching filter. Perimeter nominal.</span>
          </div>
        ) : (
          filteredCases.map(c => {
            const isSelected = selectedCaseId === c.case_id;
            const host = c.initial_alert.affected_assets[0]?.hostname || "UNKNOWN_HOST";
            const user = c.initial_alert.affected_identities[0] || "SYSTEM";
            const mitre = c.initial_alert.mitre_attack[0]?.technique_name || "Suspicious Execution";

            return (
              <div
                key={c.case_id}
                onClick={() => onSelectCase(c.case_id)}
                className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${
                  isSelected
                    ? 'border-cyan-400 bg-cyan-950/60 shadow-neon-cyan'
                    : `${SEVERITY_COLORS[c.severity] || 'border-slate-800 bg-slate-900/40'} hover:border-cyan-500/50 hover:bg-slate-900/80`
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${SEVERITY_BADGES[c.severity] || 'bg-slate-700'}`}>
                      {c.severity}
                    </span>
                    <span className="text-xs font-mono font-bold text-slate-200">{c.case_id}</span>
                  </div>
                  <div className="flex items-center gap-1 text-[10px] font-mono text-cyan-300 font-bold">
                    <span>RISK: {c.risk_score}/100</span>
                  </div>
                </div>

                <p className="text-xs text-slate-200 font-mono font-semibold line-clamp-1 mb-1.5">
                  {c.title}
                </p>

                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800/80">
                  <div className="flex items-center gap-2">
                    <span className="flex items-center gap-1 text-slate-300">
                      <Server size={10} className="text-cyan-400" /> {host}
                    </span>
                    <span className="flex items-center gap-1 text-slate-300">
                      <User size={10} className="text-amber-400" /> {user}
                    </span>
                  </div>
                  <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-black/40 border border-slate-700 text-slate-300">
                    {c.status}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

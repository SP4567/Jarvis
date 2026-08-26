import React, { useState } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Clock, 
  Server, 
  User, 
  Search, 
  Filter, 
  AlertCircle,
  Activity,
  ChevronRight
} from 'lucide-react';

const SEVERITY_BADGES = {
  P0: "bg-rose-500/15 text-rose-400 border border-rose-500/30",
  P1: "bg-orange-500/15 text-orange-400 border border-orange-500/30",
  P2: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
  P3: "bg-sky-500/15 text-sky-400 border border-sky-500/30",
  P4: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
};

const STATUS_BADGES = {
  NEW: "bg-sky-950/60 text-sky-300 border-sky-800/40",
  TRIAGING: "bg-amber-950/60 text-amber-300 border-amber-800/40",
  INVESTIGATING: "bg-indigo-950/60 text-indigo-300 border-indigo-800/40",
  CONTAINMENT_PENDING: "bg-rose-950/60 text-rose-300 border-rose-800/40 animate-pulse",
  CONTAINED: "bg-emerald-950/60 text-emerald-300 border-emerald-800/40",
  REMEDIATED: "bg-emerald-950/60 text-emerald-300 border-emerald-800/40",
  CLOSED: "bg-slate-900 text-slate-400 border-slate-800"
};

export default function IncidentQueue({ cases = [], selectedCaseId, onSelectCase }) {
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCases = cases.filter(c => {
    const matchesSev = filterSeverity === 'ALL' || c.severity === filterSeverity;
    const matchesSearch = !searchQuery || 
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.case_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.affected_assets?.[0]?.hostname || "").toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSev && matchesSearch;
  });

  return (
    <div className="bg-slate-900/95 rounded-xl border border-slate-800 flex flex-col h-[540px] shadow-xl overflow-hidden">
      {/* Header & Filter Bar */}
      <div className="p-3.5 border-b border-slate-800 bg-slate-950/60 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1 rounded bg-slate-800 text-slate-300">
              <ShieldAlert size={14} className="text-rose-400" />
            </div>
            <div>
              <h2 className="text-xs uppercase tracking-wider font-mono font-bold text-slate-100">
                Incident Triage Queue
              </h2>
              <span className="text-[10px] text-slate-400 font-mono">
                {filteredCases.length} Active Security Cases
              </span>
            </div>
          </div>

          {/* Severity Filter Pills */}
          <div className="flex items-center gap-1">
            {['ALL', 'P0', 'P1', 'P2', 'P3'].map(sev => (
              <button
                key={sev}
                onClick={() => setFilterSeverity(sev)}
                className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold transition-all ${
                  filterSeverity === sev
                    ? 'bg-slate-700 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>

        {/* Search Box */}
        <div className="relative">
          <Search size={12} className="absolute left-2.5 top-2 text-slate-500" />
          <input
            type="text"
            placeholder="Filter by Case ID, Hostname, MITRE Technique..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 rounded-lg pl-7 pr-3 py-1 text-[11px] font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-slate-600 transition-colors"
          />
        </div>
      </div>

      {/* Incidents List Table */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60">
        {filteredCases.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center p-6 text-center text-slate-500">
            <ShieldCheck size={28} className="text-emerald-500/60 mb-2" />
            <span className="text-xs font-mono font-medium text-slate-300">No Incidents Found</span>
            <span className="text-[11px] text-slate-500 mt-0.5">All monitored systems and perimeter telemetry are nominal.</span>
          </div>
        ) : (
          filteredCases.map(c => {
            const isSelected = selectedCaseId === c.case_id;
            const host = c.affected_assets?.[0]?.hostname || c.initial_alert?.affected_assets?.[0]?.hostname || "CORP-HOST";
            const user = c.affected_users?.[0] || c.affected_identities?.[0] || c.initial_alert?.affected_identities?.[0] || "SYSTEM";
            const mitre = c.mitre_attack?.[0]?.technique_name || c.initial_alert?.mitre_attack?.[0]?.technique_name || "Suspicious Execution";

            return (
              <div
                key={c.case_id}
                onClick={() => onSelectCase(c.case_id)}
                className={`p-3 cursor-pointer transition-colors ${
                  isSelected
                    ? 'bg-slate-800/90 border-l-2 border-l-sky-500'
                    : 'hover:bg-slate-800/40'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${SEVERITY_BADGES[c.severity] || SEVERITY_BADGES.P3}`}>
                      {c.severity}
                    </span>
                    <span className="text-xs font-mono font-semibold text-slate-200">{c.case_id}</span>
                    <span className={`px-1.5 py-0.2 rounded text-[8px] font-mono uppercase font-bold border ${STATUS_BADGES[c.status] || STATUS_BADGES.NEW}`}>
                      {c.status}
                    </span>
                  </div>

                  <div className="flex items-center gap-1 text-[11px] font-mono font-bold">
                    <span className="text-slate-400">Risk</span>
                    <span className={c.risk_score >= 80 ? 'text-rose-400' : c.risk_score >= 50 ? 'text-amber-400' : 'text-sky-400'}>
                      {c.risk_score}
                    </span>
                  </div>
                </div>

                <div className="text-[11px] font-medium text-slate-200 line-clamp-1 mb-1.5">
                  {c.title}
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800/40">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1 text-slate-300">
                      <Server size={10} className="text-slate-400" />
                      {host}
                    </span>
                    <span className="flex items-center gap-1 text-slate-400">
                      <User size={10} className="text-slate-500" />
                      {user}
                    </span>
                  </div>
                  <span className="text-slate-500 truncate max-w-[120px]">
                    {mitre}
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

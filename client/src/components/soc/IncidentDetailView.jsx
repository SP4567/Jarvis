import React, { useState } from 'react';
import { 
  ShieldAlert, 
  Activity, 
  Clock, 
  Server, 
  User, 
  CheckCircle, 
  AlertCircle, 
  Code, 
  Terminal, 
  ShieldCheck, 
  XOctagon, 
  RotateCcw,
  Sparkles,
  Info
} from 'lucide-react';

export default function IncidentDetailView({ 
  caseData, 
  onResolveAction,
  onRollbackAction 
}) {
  const [activeTab, setActiveTab] = useState('EXPLAINABILITY'); // EXPLAINABILITY | TIMELINE | CONTAINMENT | RULES

  if (!caseData) {
    return (
      <div className="glass-panel rounded-xl p-8 border border-cyan-500/20 flex flex-col items-center justify-center h-[520px] text-center">
        <Activity size={32} className="text-cyan-400 mb-3 animate-pulse opacity-60" />
        <h3 className="text-sm font-mono font-bold text-slate-300">NO INCIDENT SELECTED</h3>
        <p className="text-xs font-mono text-slate-500 mt-1">Select an incident case from the queue to inspect deep forensics.</p>
      </div>
    );
  }

  const exp = caseData.explainability;
  const host = caseData.initial_alert.affected_assets[0]?.hostname || "UNKNOWN_HOST";
  const user = caseData.initial_alert.affected_identities[0] || "SYSTEM";

  return (
    <div className="glass-panel rounded-xl p-4 border border-cyan-500/30 flex flex-col h-[520px] overflow-hidden">
      <div className="tech-corner-tl" />
      <div className="tech-corner-tr" />
      <div className="tech-corner-bl" />
      <div className="tech-corner-br" />

      {/* Case Title Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-cyan-500/20 mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-600 text-white">
              {caseData.severity}
            </span>
            <span className="text-xs font-mono font-bold text-cyan-300">{caseData.case_id}</span>
            <span className="text-xs font-mono text-slate-400">// {caseData.assigned_tier}</span>
          </div>
          <h2 className="text-sm font-bold text-slate-100 mt-1 line-clamp-1">{caseData.title}</h2>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right font-mono">
            <span className="text-[10px] text-slate-400 block">RISK RATING</span>
            <span className="text-sm font-bold text-rose-400 glow-text-danger">{caseData.risk_score} / 100</span>
          </div>
          <span className="px-2 py-1 rounded-md bg-slate-900 border border-cyan-500/30 text-xs font-mono uppercase text-cyan-300">
            {caseData.status}
          </span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 mb-3 text-xs font-mono">
        {[
          { id: 'EXPLAINABILITY', label: '8-Point Explainability' },
          { id: 'TIMELINE', label: `Timeline (${caseData.timeline?.length || 0})` },
          { id: 'CONTAINMENT', label: `Containment (${caseData.containment_actions?.length || 0})` },
          { id: 'RULES', label: `Sigma Rules (${caseData.detection_rules?.length || 0})` }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1 rounded-lg transition-all ${
              activeTab === tab.id
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-neon-cyan'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content Area */}
      <div className="flex-1 overflow-y-auto pr-1 text-xs font-mono space-y-3">
        {/* 1. EXPLAINABILITY TAB */}
        {activeTab === 'EXPLAINABILITY' && exp && (
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-black/40 border border-cyan-500/20">
              <span className="text-[10px] uppercase text-cyan-400 font-bold block mb-1">1. What Happened?</span>
              <p className="text-slate-200 leading-relaxed">{exp.what_happened}</p>
            </div>

            <div className="p-3 rounded-lg bg-black/40 border border-cyan-500/20">
              <span className="text-[10px] uppercase text-amber-400 font-bold block mb-1">2. Concrete Supporting Evidence</span>
              <ul className="list-disc list-inside space-y-1 text-slate-300">
                {exp.supporting_evidence.map((ev, i) => (
                  <li key={i} className="text-[11px]">{ev}</li>
                ))}
              </ul>
            </div>

            <div className="p-3 rounded-lg bg-black/40 border border-cyan-500/20">
              <span className="text-[10px] uppercase text-slate-400 font-bold block mb-1">3. Alternative Explanations Ruled Out</span>
              <ul className="list-disc list-inside space-y-1 text-slate-400">
                {exp.alternative_explanations_considered.map((alt, i) => (
                  <li key={i} className="text-[11px]">{alt}</li>
                ))}
              </ul>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-black/40 border border-cyan-500/20">
                <span className="text-[10px] uppercase text-emerald-400 font-bold block mb-1">4. Confidence Model</span>
                <p className="text-slate-300 text-[11px]">{exp.confidence_calculation}</p>
              </div>

              <div className="p-3 rounded-lg bg-black/40 border border-cyan-500/20">
                <span className="text-[10px] uppercase text-cyan-400 font-bold block mb-1">5. MITRE ATT&CK Mapping</span>
                <div className="space-y-1">
                  {exp.mitre_techniques.map((mt, i) => (
                    <span key={i} className="inline-block px-1.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/30 text-[10px] text-cyan-300 mr-1">
                      {mt}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-black/40 border border-cyan-500/20">
              <span className="text-[10px] uppercase text-rose-400 font-bold block mb-1">6. Recommended Actions & Invalidation Conditions</span>
              <ul className="list-disc list-inside space-y-1 text-slate-300 mb-2">
                {exp.recommended_next_actions.map((rec, i) => (
                  <li key={i} className="text-[11px]">{rec}</li>
                ))}
              </ul>
              <p className="text-[10px] text-slate-500 italic">Invalidation: {exp.invalidation_conditions}</p>
            </div>
          </div>
        )}

        {/* 2. TIMELINE TAB */}
        {activeTab === 'TIMELINE' && (
          <div className="space-y-2 relative border-l-2 border-cyan-500/30 ml-3 pl-4">
            {caseData.timeline.map((entry, idx) => (
              <div key={idx} className="relative mb-3">
                <span className="absolute -left-[23px] top-1 w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-neon-cyan" />
                <div className="p-2.5 rounded-lg bg-black/50 border border-cyan-500/20">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] text-cyan-300 font-bold">{entry.source}</span>
                    <span className="text-[9px] text-slate-500">{entry.timestamp}</span>
                  </div>
                  <p className="text-slate-200 text-xs">{entry.description}</p>
                  <span className="text-[9px] text-slate-400 mt-1 block">Target: {entry.entity} // [{entry.provenance}]</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 3. CONTAINMENT ACTIONS TAB */}
        {activeTab === 'CONTAINMENT' && (
          <div className="space-y-3">
            {caseData.containment_actions.length === 0 ? (
              <div className="text-center py-8 text-slate-500">Zero containment actions requested.</div>
            ) : (
              caseData.containment_actions.map(action => {
                const isPending = action.approval_status === 'PENDING';
                const isExecuted = action.approval_status === 'APPROVED' || action.approval_status === 'AUTO_EXECUTED';
                const isRolledBack = action.is_rolled_back;

                return (
                  <div 
                    key={action.action_id}
                    className={`p-3 rounded-lg border ${
                      isPending ? 'border-rose-500 bg-rose-950/30 shadow-neon-danger' : 'border-slate-800 bg-black/40'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          action.risk_level === 'HIGH' ? 'bg-rose-600 text-white' : 'bg-amber-500 text-black'
                        }`}>
                          {action.risk_level} RISK
                        </span>
                        <span className="text-xs font-bold text-slate-200">{action.action_name}</span>
                      </div>
                      <span className="text-[10px] text-slate-400">{action.action_id}</span>
                    </div>

                    <p className="text-xs text-slate-300 mb-2">{action.reason}</p>
                    <div className="text-[11px] text-slate-400 mb-2">
                      <span className="text-amber-400">Impact:</span> {action.expected_impact}
                    </div>

                    {/* Action Controls */}
                    <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                      <span className={`text-[10px] font-bold uppercase ${
                        isPending ? 'text-rose-400 animate-pulse' : (isRolledBack ? 'text-slate-400' : 'text-emerald-400')
                      }`}>
                        STATUS: {action.approval_status}
                      </span>

                      {isPending && (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => onResolveAction(action.action_id, false)}
                            className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-rose-300 text-xs font-bold border border-rose-500/40"
                          >
                            REJECT
                          </button>
                          <button
                            onClick={() => onResolveAction(action.action_id, true)}
                            className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-black text-xs font-bold shadow-lg"
                          >
                            AUTHORIZE ACTION
                          </button>
                        </div>
                      )}

                      {isExecuted && !isRolledBack && (
                        <button
                          onClick={() => onRollbackAction(action.action_id)}
                          className="flex items-center gap-1 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-amber-300 text-[11px] border border-amber-500/40"
                        >
                          <RotateCcw size={11} /> ROLLBACK
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}

        {/* 4. SIGMA DETECTION RULES TAB */}
        {activeTab === 'RULES' && (
          <div className="space-y-3">
            {caseData.detection_rules.length === 0 ? (
              <div className="text-center py-8 text-slate-500">Zero synthesized detection rules for this case.</div>
            ) : (
              caseData.detection_rules.map(rule => (
                <div key={rule.rule_id} className="p-3 rounded-lg bg-black/60 border border-cyan-500/30">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Code size={14} className="text-cyan-400" />
                      <span className="text-xs font-bold text-cyan-300">{rule.title}</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">{rule.rule_id}</span>
                  </div>
                  <pre className="p-2 rounded bg-slate-950 border border-slate-800 text-[11px] text-cyan-200 overflow-x-auto">
                    {rule.rule_content}
                  </pre>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

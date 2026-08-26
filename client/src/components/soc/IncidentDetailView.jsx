import React, { useState } from 'react';
import { 
  ShieldAlert, 
  Activity, 
  Clock, 
  Server, 
  User, 
  CheckCircle2, 
  AlertCircle, 
  Code, 
  Terminal, 
  ShieldCheck, 
  XOctagon, 
  RotateCcw,
  Sparkles,
  Info,
  Check,
  X,
  FileText,
  Layers,
  Cpu,
  Globe,
  Database,
  Lock,
  Compass
} from 'lucide-react';

const SEVERITY_BADGES = {
  P0: "bg-rose-500/15 text-rose-400 border border-rose-500/30",
  P1: "bg-orange-500/15 text-orange-400 border border-orange-500/30",
  P2: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
  P3: "bg-sky-500/15 text-sky-400 border border-sky-500/30",
  P4: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
};

export default function IncidentDetailView({ 
  caseData, 
  onResolveAction,
  onRollbackAction 
}) {
  const [activeTab, setActiveTab] = useState('EXPLAINABILITY');

  if (!caseData) {
    return (
      <div className="bg-slate-900/95 rounded-xl border border-slate-800 p-8 flex flex-col items-center justify-center h-[540px] text-center shadow-xl">
        <Activity size={28} className="text-slate-500 mb-2 opacity-60 animate-pulse" />
        <h3 className="text-xs font-mono font-bold text-slate-300">NO INCIDENT SELECTED</h3>
        <p className="text-[11px] font-mono text-slate-500 mt-1">Select an active security case from the triage queue to inspect full telemetry.</p>
      </div>
    );
  }

  const exp = caseData.explainability;
  const host = caseData.affected_assets?.[0]?.hostname || caseData.initial_alert?.affected_assets?.[0]?.hostname || "CORP-HOST";
  const user = caseData.affected_users?.[0] || caseData.affected_identities?.[0] || caseData.initial_alert?.affected_identities?.[0] || "SYSTEM";
  const agentFindings = caseData.agent_findings || {};
  const findingsList = Object.values(agentFindings);

  return (
    <div className="bg-slate-900/95 rounded-xl border border-slate-800 flex flex-col h-[540px] shadow-xl overflow-hidden">
      {/* Incident Case Header Bar */}
      <div className="p-3.5 border-b border-slate-800 bg-slate-950/70 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${SEVERITY_BADGES[caseData.severity] || SEVERITY_BADGES.P3}`}>
              {caseData.severity}
            </span>
            <span className="text-xs font-mono font-bold text-slate-200">{caseData.case_id}</span>
            <span className="text-[10px] font-mono text-slate-400">// {caseData.assigned_tier}</span>
            <span className="text-[10px] font-mono text-slate-500">{caseData.created_at?.slice(0, 19)}</span>
          </div>
          <h2 className="text-xs font-semibold text-slate-100 line-clamp-1">{caseData.title}</h2>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right font-mono">
            <span className="text-[9px] text-slate-400 uppercase font-semibold block">Risk Score</span>
            <span className={`text-sm font-bold ${caseData.risk_score >= 80 ? 'text-rose-400' : caseData.risk_score >= 50 ? 'text-amber-400' : 'text-sky-400'}`}>
              {caseData.risk_score} / 100
            </span>
          </div>
          <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-[10px] font-mono uppercase font-bold text-slate-200">
            {caseData.status}
          </span>
        </div>
      </div>

      {/* High-Density Navigation Tabs */}
      <div className="flex items-center gap-1.5 px-3 pt-2 pb-1.5 border-b border-slate-800 bg-slate-950/40 text-[11px] font-mono overflow-x-auto">
        {[
          { id: 'EXPLAINABILITY', label: '8-Point Explainability' },
          { id: 'AGENT_FINDINGS', label: `Agent Findings (${findingsList.length})` },
          { id: 'TIMELINE', label: `Timeline (${caseData.timeline?.length || 0})` },
          { id: 'CONTAINMENT', label: `Containment (${caseData.containment_actions?.length || 0})` },
          { id: 'RULES', label: `Sigma Rules (${caseData.detection_rules?.length || 0})` },
          { id: 'COMPLIANCE', label: `Compliance (${caseData.compliance_mappings?.length || 0})` }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-2.5 py-1 rounded transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-slate-800 text-white font-semibold shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content Area */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-3 text-[11px] font-mono">
        {/* 1. EXPLAINABILITY TAB */}
        {activeTab === 'EXPLAINABILITY' && exp && (
          <div className="space-y-2.5">
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] uppercase text-sky-400 font-bold block mb-1">1. What Happened?</span>
              <p className="text-slate-300 leading-relaxed">{exp.what_happened}</p>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] uppercase text-sky-400 font-bold block mb-1">2. Observed Evidence Chain</span>
              <ul className="space-y-1 text-slate-300 list-disc list-inside">
                {exp.supporting_evidence?.map((ev, i) => (
                  <li key={i}>{ev}</li>
                ))}
              </ul>
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                <span className="text-[10px] uppercase text-sky-400 font-bold block mb-1">3. Ruled-Out Benign Hypotheses</span>
                <ul className="space-y-1 text-slate-400">
                  {exp.alternative_explanations_considered?.map((alt, i) => (
                    <li key={i}>• {alt}</li>
                  ))}
                </ul>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                <span className="text-[10px] uppercase text-sky-400 font-bold block mb-1">4. Confidence Model</span>
                <p className="text-slate-300">{exp.confidence_calculation}</p>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] uppercase text-sky-400 font-bold block mb-1">5. MITRE ATT&CK Techniques</span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {exp.mitre_techniques?.map((m, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300 text-[10px]">
                    {m}
                  </span>
                ))}
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] uppercase text-sky-400 font-bold block mb-1">6. Recommended Next Actions</span>
              <ul className="space-y-1 text-slate-300 list-disc list-inside">
                {exp.recommended_next_actions?.map((act, i) => (
                  <li key={i}>{act}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* 2. AGENT FINDINGS TAB */}
        {activeTab === 'AGENT_FINDINGS' && (
          <div className="space-y-2.5">
            {findingsList.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No structured subagent findings logged yet.</div>
            ) : (
              findingsList.map((f, i) => (
                <div key={i} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-bold text-[10px]">
                        {f.role_title}
                      </span>
                      <span className="text-[10px] text-slate-500">[{f.agent_name}]</span>
                    </div>
                    <span className="text-[10px] text-emerald-400 font-semibold">
                      Confidence: {Math.round(f.confidence * 100)}%
                    </span>
                  </div>
                  <p className="text-slate-200 leading-relaxed text-[11px]">{f.summary}</p>
                  {f.recommendations && f.recommendations.length > 0 && (
                    <div className="pt-1 border-t border-slate-900 text-slate-400 text-[10px]">
                      <span className="text-slate-500 font-bold uppercase">Recommendations:</span> {f.recommendations.join("; ")}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* 3. TIMELINE TAB */}
        {activeTab === 'TIMELINE' && (
          <div className="space-y-2">
            {caseData.timeline?.map((item, idx) => (
              <div key={idx} className="p-2.5 rounded bg-slate-950/70 border border-slate-800 flex items-start gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-sky-400 mt-1.5 shrink-0" />
                <div className="flex-1">
                  <div className="flex items-center justify-between text-[10px] text-slate-400 mb-0.5">
                    <span className="font-semibold text-slate-300">{item.source} // {item.entity}</span>
                    <span>{item.timestamp}</span>
                  </div>
                  <p className="text-slate-200 leading-relaxed">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 4. CONTAINMENT TAB */}
        {activeTab === 'CONTAINMENT' && (
          <div className="space-y-2.5">
            {caseData.containment_actions?.length === 0 ? (
              <div className="text-center py-8 text-slate-500">Zero containment actions proposed for this case.</div>
            ) : (
              caseData.containment_actions.map(act => {
                const isPending = act.approval_status === "PENDING";
                const isExecuted = act.approval_status === "APPROVED" || act.approval_status === "AUTO_EXECUTED";
                
                return (
                  <div key={act.action_id} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${
                          act.risk_level === 'HIGH' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                        }`}>
                          {act.risk_level} RISK
                        </span>
                        <span className="font-bold text-slate-100">{act.action_name}</span>
                        <span className="text-slate-500 text-[10px]">({act.action_id})</span>
                      </div>

                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${
                        isPending ? 'bg-amber-500/20 text-amber-300 animate-pulse' : isExecuted ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {act.approval_status}
                      </span>
                    </div>

                    <p className="text-slate-300 text-[11px]">{act.reason}</p>
                    <div className="text-[10px] text-slate-400 bg-slate-900 p-2 rounded border border-slate-800">
                      <span className="text-slate-500 block font-semibold uppercase">Expected Impact:</span>
                      {act.expected_impact}
                    </div>

                    {isPending && onResolveAction && (
                      <div className="flex items-center gap-2 pt-2 border-t border-slate-800">
                        <button
                          onClick={() => onResolveAction(act.action_id, true)}
                          className="flex items-center gap-1 px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-[11px] font-semibold transition-colors"
                        >
                          <Check size={12} />
                          APPROVE & EXECUTE
                        </button>
                        <button
                          onClick={() => onResolveAction(act.action_id, false)}
                          className="flex items-center gap-1 px-3 py-1 bg-rose-600/80 hover:bg-rose-600 text-white rounded text-[11px] font-semibold transition-colors"
                        >
                          <X size={12} />
                          REJECT
                        </button>
                      </div>
                    )}

                    {isExecuted && onRollbackAction && !act.is_rolled_back && (
                      <div className="pt-2 border-t border-slate-800">
                        <button
                          onClick={() => onRollbackAction(act.action_id)}
                          className="flex items-center gap-1 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[10px] transition-colors"
                        >
                          <RotateCcw size={11} />
                          ROLLBACK CONTAINMENT ACTION
                        </button>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        )}

        {/* 5. DETECTION RULES TAB */}
        {activeTab === 'RULES' && (
          <div className="space-y-2.5">
            {caseData.detection_rules?.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No detection rules synthesized for this case yet.</div>
            ) : (
              caseData.detection_rules.map(rule => (
                <div key={rule.rule_id} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-100">{rule.title}</span>
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[9px] font-bold">
                      {rule.rule_type}
                    </span>
                  </div>
                  <pre className="p-2.5 rounded bg-slate-900 text-slate-300 text-[10px] overflow-x-auto leading-relaxed border border-slate-850">
                    {rule.rule_content}
                  </pre>
                </div>
              ))
            )}
          </div>
        )}

        {/* 6. COMPLIANCE TAB */}
        {activeTab === 'COMPLIANCE' && (
          <div className="space-y-2">
            {caseData.compliance_mappings?.length === 0 ? (
              <div className="text-center py-8 text-slate-500">Compliance control mapping nominal.</div>
            ) : (
              caseData.compliance_mappings.map((c, i) => (
                <div key={i} className="p-2.5 rounded bg-slate-950/80 border border-slate-800 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[9px] font-bold">
                        {c.framework}
                      </span>
                      <span className="font-bold text-slate-200">{c.control_id} - {c.control_name}</span>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-0.5">{c.justification}</p>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/40 text-[9px] font-bold">
                    {c.status}
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

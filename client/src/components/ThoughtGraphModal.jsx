import React, { useState } from 'react';
import { GitBranch, X, Layers, Activity, CheckCircle2, Clock, AlertTriangle, RefreshCw, Cpu } from 'lucide-react';

export default function ThoughtGraphModal({ isOpen, onClose, dagPlan = null, thoughts = [] }) {
  if (!isOpen) return null;

  // Sample DAG nodes if none passed
  const nodes = dagPlan?.nodes ? Object.values(dagPlan.nodes) : [
    { node_id: "root_task", description: "Decompose User Directive", agent_name: "orchestrator", status: "verified", dependencies: [] },
    { node_id: "sec_sweep", description: "Kernel ETW & Socket Telemetry Sweep", agent_name: "endpoint_security", status: "verified", dependencies: ["root_task"] },
    { node_id: "cti_eval", description: "CTI Reputation Indicator Scoring", agent_name: "threat_intel", status: "verified", dependencies: ["root_task"] },
    { node_id: "code_synth", description: "Synthesize Patch & Verification AST", agent_name: "coding_agent", status: "attempting", dependencies: ["sec_sweep", "cti_eval"] },
    { node_id: "compliance_audit", description: "NIST CSF Control Verification", agent_name: "compliance_reporting", status: "planned", dependencies: ["code_synth"] }
  ];

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'verified':
      case 'completed':
        return 'border-emerald-500 bg-emerald-950/60 text-emerald-300';
      case 'attempting':
      case 'executing':
        return 'border-sky-500 bg-sky-950/60 text-sky-300 animate-pulse';
      case 'failed':
        return 'border-rose-500 bg-rose-950/60 text-rose-300';
      default:
        return 'border-slate-700 bg-slate-900 text-slate-400';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-fade-in">
      <div className="w-full max-w-5xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-slate-800 text-sky-400">
              <GitBranch size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-100 font-mono tracking-wider">
                THOUGHT GRAPH // DAG EXECUTION CANVAS
              </h2>
              <p className="text-[10px] text-slate-400 font-mono">
                Real-Time Multi-Agent Task Dependency & Swarm Reasoning Graph
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Thought Graph Interactive Canvas */}
        <div className="flex-1 overflow-y-auto p-6 font-mono text-xs space-y-6">
          <div className="p-4 bg-slate-950/90 border border-slate-800 rounded-xl space-y-4">
            <div className="flex items-center justify-between text-[11px] text-slate-400 pb-2 border-b border-slate-800/80">
              <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                <Cpu size={14} className="text-sky-400" />
                Active DAG Flow: {dagPlan?.goal || "Autonomous System Optimization & Threat Isolation"}
              </span>
              <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-emerald-400 text-[10px]">
                {nodes.length} Dynamic Nodes
              </span>
            </div>

            {/* Visual Node Tree */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
              {nodes.map((node) => (
                <div
                  key={node.node_id}
                  className={`p-3.5 rounded-lg border flex flex-col justify-between space-y-2 transition-all ${getStatusColor(node.status)}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      ID: {node.node_id}
                    </span>
                    <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800">
                      {node.status?.toUpperCase()}
                    </span>
                  </div>

                  <p className="text-xs font-semibold text-slate-100">
                    {node.description}
                  </p>

                  <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400">
                    <span>Node Agent: <strong className="text-slate-200">{node.agent_name}</strong></span>
                    {node.dependencies?.length > 0 && (
                      <span className="text-slate-500">Deps: [{node.dependencies.join(', ')}]</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sequential Agent Thought Stream */}
          {thoughts && thoughts.length > 0 && (
            <div className="p-4 bg-slate-950/90 border border-slate-800 rounded-xl space-y-2.5">
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                <Activity size={14} className="text-sky-400" />
                Live Agent Cognitive Stream
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {thoughts.map((th, idx) => (
                  <div key={idx} className="p-2.5 bg-slate-900 border border-slate-800 rounded text-[11px] text-slate-300 flex items-start justify-between">
                    <div>
                      <span className="font-bold text-sky-400 mr-2">[{th.agent_name || th.agent}]</span>
                      <span>{th.thought}</span>
                    </div>
                    <span className="text-[9px] text-slate-500 shrink-0 ml-2">Step {th.step || idx + 1}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

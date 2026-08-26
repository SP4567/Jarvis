import React, { useState, useEffect } from 'react';
import { AlertTriangle, ShieldAlert, Check, X, Terminal, Edit3, RefreshCw } from 'lucide-react';
import { playWarningAlarmSound, playAuthorizeSound, playRejectSound } from '../utils/audioEffects';

export default function GuardrailModal({ pendingApprovals = [], onResolve }) {
  const currentRequest = pendingApprovals[0];
  const [isEditing, setIsEditing] = useState(false);
  const [editedParamsJson, setEditedParamsJson] = useState('');
  const [jsonError, setJsonError] = useState('');

  useEffect(() => {
    if (currentRequest) {
      playWarningAlarmSound();
      setIsEditing(false);
      setEditedParamsJson(JSON.stringify(currentRequest.details || {}, null, 2));
      setJsonError('');
    }
  }, [currentRequest?.action_id]);

  if (!currentRequest) return null;

  const handleApprove = () => {
    playAuthorizeSound();
    if (isEditing) {
      try {
        const parsed = JSON.parse(editedParamsJson);
        onResolve(currentRequest.action_id, true, parsed);
      } catch (err) {
        setJsonError('Invalid JSON format for modified parameters.');
        return;
      }
    } else {
      onResolve(currentRequest.action_id, true);
    }
  };

  const handleReject = () => {
    playRejectSound();
    onResolve(currentRequest.action_id, false);
  };

  const riskLevel = currentRequest.risk_level || 'HIGH';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-lg p-5 rounded-xl bg-slate-900 border border-rose-500/60 shadow-2xl space-y-4">
        {/* Warning Header */}
        <div className="flex items-center gap-3 pb-3 border-b border-slate-800">
          <div className="p-2 rounded-lg bg-rose-950/80 text-rose-400 border border-rose-800/60">
            <ShieldAlert size={22} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-rose-950 text-rose-300 border border-rose-800">
                SECURITY INTERLOCK // {riskLevel} RISK
              </span>
              <span className="text-xs font-mono text-slate-400">ID: {currentRequest.action_id}</span>
            </div>
            <h2 className="text-sm font-bold font-mono text-slate-100 mt-1">
              HUMAN AUTHORIZATION REQUIRED
            </h2>
          </div>
        </div>

        {/* Action Details */}
        <div className="space-y-2.5 text-xs font-mono">
          <div className="flex justify-between">
            <span className="text-slate-400">Initiating Subagent:</span>
            <span className="text-slate-200 font-semibold">{currentRequest.agent_name}</span>
          </div>

          <div className="flex justify-between">
            <span className="text-slate-400">Requested Action:</span>
            <span className="text-amber-400 font-semibold">{currentRequest.action_name}</span>
          </div>

          {currentRequest.target_resource && (
            <div className="flex justify-between">
              <span className="text-slate-400">Target Environment/Resource:</span>
              <span className="text-rose-300 font-semibold">{currentRequest.target_resource}</span>
            </div>
          )}

          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-[11px] font-mono text-slate-400 mb-1.5 flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Terminal size={12} className="text-rose-400" />
                <span>Target Parameters / Execution Payload:</span>
              </div>
              <button
                type="button"
                onClick={() => setIsEditing(!isEditing)}
                className="flex items-center gap-1 text-[10px] text-sky-400 hover:text-sky-300 transition-colors"
              >
                <Edit3 size={11} />
                <span>{isEditing ? 'Cancel Edit' : 'Edit Parameters'}</span>
              </button>
            </div>

            {isEditing ? (
              <div className="space-y-1.5">
                <textarea
                  rows={4}
                  value={editedParamsJson}
                  onChange={(e) => {
                    setEditedParamsJson(e.target.value);
                    setJsonError('');
                  }}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-slate-500 resize-none"
                />
                {jsonError && <p className="text-[10px] text-rose-400 font-mono">{jsonError}</p>}
              </div>
            ) : (
              <pre className="text-slate-300 text-[11px] font-mono overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(currentRequest.details || {}, null, 2)}
              </pre>
            )}
          </div>

          {/* Expected Impact & Rollback Plan */}
          {currentRequest.expected_impact && (
            <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 text-[11px] space-y-1">
              <div>
                <span className="text-slate-400 font-bold uppercase text-[9px] block">Expected Impact:</span>
                <span className="text-slate-300">{currentRequest.expected_impact}</span>
              </div>
              {currentRequest.rollback_strategy && (
                <div className="pt-1 border-t border-slate-900">
                  <span className="text-slate-500 font-bold uppercase text-[9px] block">Rollback Strategy:</span>
                  <span className="text-slate-400">{currentRequest.rollback_strategy}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800">
          <button
            onClick={handleReject}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-mono font-semibold transition-colors"
          >
            <X size={14} />
            REJECT ACTION
          </button>
          <button
            onClick={handleApprove}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-semibold transition-colors"
          >
            <Check size={14} />
            AUTHORIZE & EXECUTE
          </button>
        </div>
      </div>
    </div>
  );
}

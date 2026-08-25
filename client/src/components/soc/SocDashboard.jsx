import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  ShieldAlert, 
  ShieldCheck,
  Target, 
  Zap, 
  Activity, 
  Cpu, 
  Clock, 
  TrendingUp, 
  Layers, 
  RefreshCw,
  Terminal,
  Wifi,
  Power
} from 'lucide-react';
import IncidentQueue from './IncidentQueue';
import IncidentDetailView from './IncidentDetailView';
import ThreatHuntingView from './ThreatHuntingView';
import LiveEndpointTelemetryView from './LiveEndpointTelemetryView';

export default function SocDashboard({ socData = {}, onActionResolve }) {
  const [subView, setSubView] = useState('LIVE_ENDPOINT'); // LIVE_ENDPOINT | INCIDENT_OPERATIONS | THREAT_HUNTING
  const [socEnabled, setSocEnabled] = useState(true);
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [metrics, setMetrics] = useState({});
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [simulating, setSimulating] = useState(false);

  const fetchSocData = async () => {
    try {
      setLoading(true);
      const [casesRes, metricsRes, rulesRes, stateRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/soc/cases'),
        fetch('http://127.0.0.1:8000/api/soc/metrics'),
        fetch('http://127.0.0.1:8000/api/soc/rules'),
        fetch('http://127.0.0.1:8000/api/soc/state')
      ]);

      if (casesRes.ok) {
        const casesJson = await casesRes.json();
        setCases(casesJson);
        if (casesJson.length > 0 && !selectedCaseId) {
          setSelectedCaseId(casesJson[0].case_id);
        }
      }
      if (metricsRes.ok) {
        setMetrics(await metricsRes.json());
      }
      if (rulesRes.ok) {
        setRules(await rulesRes.json());
      }
      if (stateRes.ok) {
        const stateJson = await stateRes.json();
        setSocEnabled(stateJson.enabled);
      }
    } catch (e) {
      console.warn('Failed to fetch SOC telemetry:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSocData();
    const interval = setInterval(fetchSocData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleSoc = async () => {
    try {
      setToggling(true);
      const res = await fetch('http://127.0.0.1:8000/api/soc/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !socEnabled })
      });
      if (res.ok) {
        const data = await res.json();
        setSocEnabled(data.enabled);
      }
    } catch (e) {
      console.error('Failed to toggle SOC:', e);
    } finally {
      setToggling(false);
    }
  };

  const handleSimulateScenario = async (scenarioId) => {
    try {
      setSimulating(true);
      const res = await fetch('http://127.0.0.1:8000/api/soc/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: scenarioId })
      });
      if (res.ok) {
        await fetchSocData();
        setSubView('INCIDENT_OPERATIONS');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSimulating(false);
    }
  };

  const handleResolveAction = async (actionId, approved) => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/soc/resolve_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: actionId, approved, approver: "HUD_OPERATOR" })
      });
      if (res.ok) {
        fetchSocData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleRollbackAction = async (actionId) => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/soc/rollback_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: actionId, operator: "HUD_OPERATOR" })
      });
      if (res.ok) {
        fetchSocData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const selectedCase = cases.find(c => c.case_id === selectedCaseId) || cases[0];

  return (
    <div className="space-y-4">
      {/* Master SOC Power Switch Bar */}
      <div className={`p-3 rounded-xl border flex flex-wrap items-center justify-between gap-3 transition-all ${
        socEnabled 
          ? 'glass-panel border-emerald-500/30 bg-emerald-950/10' 
          : 'glass-panel border-amber-500/30 bg-amber-950/20'
      }`}>
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold ${
            socEnabled ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-neon-cyan' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
          }`}>
            <Power size={16} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider text-white">
                AUTONOMOUS SOC DEFENSE MATRIX
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                socEnabled 
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' 
                  : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
              }`}>
                {socEnabled ? 'STATE: ACTIVE (CONTINUOUS MONITORING)' : 'STATE: STANDBY (OFFLINE)'}
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400">
              {socEnabled 
                ? 'Tier 1 Triage, Tier 2 Incident Responder & Tier 3 Threat Hunter are actively analyzing kernel telemetry.'
                : 'Security agents and continuous background telemetry analysis are paused in standby mode.'}
            </p>
          </div>
        </div>

        {/* Big Interactive Power Toggle */}
        <button
          onClick={handleToggleSoc}
          disabled={toggling}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-mono font-bold text-xs transition-all shadow-md ${
            socEnabled
              ? 'bg-rose-600/80 hover:bg-rose-500 text-white border border-rose-500/50'
              : 'bg-emerald-600/80 hover:bg-emerald-500 text-white border border-emerald-500/50 shadow-neon-cyan'
          }`}
        >
          <Power size={14} className={toggling ? 'animate-spin' : ''} />
          {socEnabled ? 'SWITCH SOC OFF (STANDBY)' : 'SWITCH SOC ON (ACTIVATE)'}
        </button>
      </div>

      {/* Top Metrics Telemetry Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="glass-panel p-3 rounded-xl border border-cyan-500/20">
          <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono">
            <span>ACTIVE INCIDENTS</span>
            <ShieldAlert size={13} className="text-rose-400" />
          </div>
          <div className="text-lg font-mono font-extrabold text-rose-400 glow-text-danger mt-1">
            {metrics.active_incidents || 0}
          </div>
        </div>

        <div className="glass-panel p-3 rounded-xl border border-cyan-500/20">
          <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono">
            <span>CRITICAL P0/P1</span>
            <Zap size={13} className="text-amber-400" />
          </div>
          <div className="text-lg font-mono font-extrabold text-amber-400 mt-1">
            {metrics.critical_p0_p1 || 0}
          </div>
        </div>

        <div className="glass-panel p-3 rounded-xl border border-cyan-500/20">
          <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono">
            <span>MTTD (DETECTION)</span>
            <Clock size={13} className="text-cyan-400" />
          </div>
          <div className="text-lg font-mono font-extrabold text-cyan-300 mt-1">
            {metrics.mean_time_to_detect_sec || 42}s
          </div>
        </div>

        <div className="glass-panel p-3 rounded-xl border border-cyan-500/20">
          <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono">
            <span>MTTR (RESPONSE)</span>
            <Activity size={13} className="text-emerald-400" />
          </div>
          <div className="text-lg font-mono font-extrabold text-emerald-300 mt-1">
            {metrics.mean_time_to_respond_sec || 78}s
          </div>
        </div>

        <div className="glass-panel p-3 rounded-xl border border-cyan-500/20">
          <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono">
            <span>NOISE REDUCTION</span>
            <TrendingUp size={13} className="text-cyan-400" />
          </div>
          <div className="text-lg font-mono font-extrabold text-cyan-300 mt-1">
            {metrics.false_positive_reduction_rate || '84.6%'}
          </div>
        </div>

        <div className="glass-panel p-3 rounded-xl border border-cyan-500/20">
          <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono">
            <span>AUTONOMOUS TRIAGE</span>
            <Cpu size={13} className="text-purple-400" />
          </div>
          <div className="text-lg font-mono font-extrabold text-purple-300 mt-1">
            {metrics.autonomous_triage_rate || '92.3%'}
          </div>
        </div>
      </div>

      {/* Sub-View Switcher Bar */}
      <div className="flex items-center justify-between glass-panel px-4 py-2 rounded-xl border border-cyan-500/20">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSubView('LIVE_ENDPOINT')}
            className={`px-4 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
              subView === 'LIVE_ENDPOINT'
                ? 'bg-cyan-500 text-black shadow-neon-cyan'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Shield size={13} />
            LIVE ENDPOINT TELEMETRY (REAL-TIME)
          </button>
          <button
            onClick={() => setSubView('INCIDENT_OPERATIONS')}
            className={`px-4 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
              subView === 'INCIDENT_OPERATIONS'
                ? 'bg-cyan-500 text-black shadow-neon-cyan'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Terminal size={13} />
            INCIDENT OPERATIONS ({cases.length})
          </button>
          <button
            onClick={() => setSubView('THREAT_HUNTING')}
            className={`px-4 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
              subView === 'THREAT_HUNTING'
                ? 'bg-cyan-500 text-black shadow-neon-cyan'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Target size={13} />
            THREAT HUNTING & DEOBFUSCATION
          </button>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchSocData}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 transition-all"
            title="Refresh Telemetry"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          </button>
          <span className={`text-[10px] font-mono flex items-center gap-1 ${
            socEnabled ? 'text-emerald-400' : 'text-amber-400'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${socEnabled ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'}`} />
            {socEnabled ? 'SOC STREAM ACTIVE' : 'SOC IN STANDBY'}
          </span>
        </div>
      </div>

      {/* Main View Container */}
      {subView === 'LIVE_ENDPOINT' ? (
        <LiveEndpointTelemetryView socEnabled={socEnabled} onToggleSoc={handleToggleSoc} />
      ) : subView === 'INCIDENT_OPERATIONS' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-4">
            <IncidentQueue
              cases={cases}
              selectedCaseId={selectedCase?.case_id}
              onSelectCase={(id) => setSelectedCaseId(id)}
            />
          </div>
          <div className="lg:col-span-8">
            <IncidentDetailView
              caseData={selectedCase}
              onResolveAction={handleResolveAction}
              onRollbackAction={handleRollbackAction}
            />
          </div>
        </div>
      ) : (
        <ThreatHuntingView
          onSimulateScenario={handleSimulateScenario}
          rules={rules}
          isSimulating={simulating}
        />
      )}
    </div>
  );
}

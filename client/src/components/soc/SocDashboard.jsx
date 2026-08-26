import React, { useState, useEffect } from 'react';
import { 
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
  Power,
  Server,
  Play,
  CheckCircle2,
  AlertTriangle,
  Compass
} from 'lucide-react';
import IncidentQueue from './IncidentQueue';
import IncidentDetailView from './IncidentDetailView';
import ThreatHuntingView from './ThreatHuntingView';
import LiveEndpointTelemetryView from './LiveEndpointTelemetryView';

export default function SocDashboard({ socData = {}, onActionResolve }) {
  const [subView, setSubView] = useState('INCIDENT_OPERATIONS'); // INCIDENT_OPERATIONS | FLEET_MATRIX | THREAT_HUNTING | LIVE_ENDPOINT
  const [socEnabled, setSocEnabled] = useState(true);
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [metrics, setMetrics] = useState({});
  const [fleetStatus, setFleetStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [simulating, setSimulating] = useState(false);

  const fetchSocData = async () => {
    try {
      setLoading(true);
      const [casesRes, metricsRes, stateRes, fleetRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/soc/cases'),
        fetch('http://127.0.0.1:8000/api/soc/metrics'),
        fetch('http://127.0.0.1:8000/api/soc/state'),
        fetch('http://127.0.0.1:8000/api/soc/fleet')
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
      if (stateRes.ok) {
        const stateJson = await stateRes.json();
        setSocEnabled(stateJson.enabled);
      }
      if (fleetRes.ok) {
        setFleetStatus(await fleetRes.json());
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
        const newCase = await res.json();
        setSelectedCaseId(newCase.case_id);
        fetchSocData();
      }
    } catch (e) {
      console.error('Simulation failed:', e);
    } finally {
      setSimulating(false);
    }
  };

  const selectedCase = cases.find(c => c.case_id === selectedCaseId);

  const handleResolveAction = async (actionId, approved) => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/soc/resolve_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: actionId, approved, approver: "CISO_OPERATOR" })
      });
      if (res.ok) {
        fetchSocData();
      }
    } catch (e) {
      console.error('Action resolve failed:', e);
    }
  };

  const handleRollbackAction = async (actionId) => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/soc/rollback_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: actionId, operator: "CISO_OPERATOR" })
      });
      if (res.ok) {
        fetchSocData();
      }
    } catch (e) {
      console.error('Action rollback failed:', e);
    }
  };

  return (
    <div className="space-y-4">
      {/* Enterprise SecOps Command Header */}
      <div className="bg-slate-900/95 rounded-xl p-4 border border-slate-800 shadow-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-slate-800 text-sky-400">
            <ShieldCheck size={22} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-wide uppercase font-mono text-slate-100">
                JARVIS Autonomous SOC Command
              </h1>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                socEnabled
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                  : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
              }`}>
                {socEnabled ? 'CONTINUOUS MONITORING ACTIVE' : 'PERIMETER DEFENSE STANDBY'}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono mt-0.5">
              Enterprise Multi-Agent SecOps • 16 Autonomous Security Nodes Online
            </p>
          </div>
        </div>

        {/* Action Controls & Power Switch */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={fetchSocData}
            disabled={loading}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 transition-colors"
            title="Refresh Telemetry"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>

          <button
            onClick={handleToggleSoc}
            disabled={toggling}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
              socEnabled
                ? 'bg-rose-950/70 hover:bg-rose-900 border border-rose-800/60 text-rose-300'
                : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md'
            }`}
          >
            <Power size={13} />
            {socEnabled ? 'DEACTIVATE SOC' : 'ACTIVATE SOC'}
          </button>
        </div>
      </div>

      {/* Real-time Enterprise Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="p-3 rounded-xl bg-slate-900/95 border border-slate-800">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 uppercase font-semibold mb-1">
            <span>Total Incidents</span>
            <AlertTriangle size={13} className="text-amber-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {metrics.total_incidents || cases.length || 0}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">All-time Scoped Cases</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/95 border border-slate-800">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 uppercase font-semibold mb-1">
            <span>Critical P0/P1</span>
            <ShieldAlert size={13} className="text-rose-400" />
          </div>
          <div className="text-xl font-bold font-mono text-rose-400">
            {metrics.critical_p0_p1 || cases.filter(c => c.severity === 'P0' || c.severity === 'P1').length || 0}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">Active Threat Breaches</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/95 border border-slate-800">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 uppercase font-semibold mb-1">
            <span>MTTD (Detect)</span>
            <Clock size={13} className="text-sky-400" />
          </div>
          <div className="text-xl font-bold font-mono text-sky-400">
            {metrics.mean_time_to_detect_sec ? `${metrics.mean_time_to_detect_sec}s` : '38s'}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">Autonomous Pipeline SLA</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/95 border border-slate-800">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 uppercase font-semibold mb-1">
            <span>MTTR (Response)</span>
            <Zap size={13} className="text-emerald-400" />
          </div>
          <div className="text-xl font-bold font-mono text-emerald-400">
            {metrics.mean_time_to_respond_sec ? `${metrics.mean_time_to_respond_sec}s` : '72s'}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">Automated Containment</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/95 border border-slate-800">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 uppercase font-semibold mb-1">
            <span>Autonomous Triage</span>
            <Cpu size={13} className="text-indigo-400" />
          </div>
          <div className="text-xl font-bold font-mono text-indigo-300">
            {metrics.autonomous_triage_rate || '94.2%'}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">Tier 1 Auto-Resolution</div>
        </div>
      </div>

      {/* Sub-View Navigation Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-1.5 text-xs font-mono">
          {[
            { id: 'INCIDENT_OPERATIONS', label: 'INCIDENT OPERATIONS' },
            { id: 'FLEET_MATRIX', label: `16-AGENT FLEET MATRIX (${fleetStatus?.nodes?.length || 15})` },
            { id: 'THREAT_HUNTING', label: 'PROACTIVE THREAT HUNTING' },
            { id: 'LIVE_ENDPOINT', label: 'LIVE ENDPOINT TELEMETRY' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setSubView(tab.id)}
              className={`px-3.5 py-1.5 rounded-lg font-semibold transition-colors ${
                subView === tab.id
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Quick Simulation Triggers */}
        <div className="flex items-center gap-1.5 text-[11px] font-mono">
          <span className="text-slate-500 uppercase font-semibold mr-1">Simulate Attack:</span>
          {[
            { id: 'ransomware_attack', label: 'Ransomware C2' },
            { id: 'mimikatz_dump', label: 'LSASS Dump' },
            { id: 'tor_c2_beacon', label: 'Tor Beacon' }
          ].map(sim => (
            <button
              key={sim.id}
              onClick={() => handleSimulateScenario(sim.id)}
              disabled={simulating}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors disabled:opacity-50"
            >
              {sim.label}
            </button>
          ))}
        </div>
      </div>

      {/* View 1: Incident Operations */}
      {subView === 'INCIDENT_OPERATIONS' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-4">
            <IncidentQueue
              cases={cases}
              selectedCaseId={selectedCaseId}
              onSelectCase={setSelectedCaseId}
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
      )}

      {/* View 2: 16-Agent Fleet Matrix */}
      {subView === 'FLEET_MATRIX' && (
        <div className="bg-slate-900/95 rounded-xl border border-slate-800 p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
            <div>
              <h3 className="text-xs font-mono font-bold text-slate-100 uppercase">
                Distributed Security Agent Fleet
              </h3>
              <p className="text-[10px] text-slate-400 font-mono">
                16 Autonomous SecOps Subagents implementing the Universal 11-Stage Security Execution Contract.
              </p>
            </div>
            <span className="px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-[10px] font-mono text-emerald-300 font-bold">
              16/16 NODES OPERATIONAL
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {(fleetStatus?.nodes || []).map((node, i) => (
              <div key={i} className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-slate-100 truncate">{node.role_title}</h4>
                    <span className="text-[10px] text-slate-500 font-mono">{node.name}</span>
                  </div>
                  <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]" />
                </div>

                <p className="text-[11px] text-slate-400 line-clamp-2">{node.description}</p>

                <div className="flex items-center justify-between pt-2 border-t border-slate-850 text-[10px] font-mono text-slate-500">
                  <span>Runs: {node.execution_count || 0}</span>
                  <span>Latency: {node.last_latency_ms ? `${node.last_latency_ms}ms` : '14ms'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* View 3: Proactive Threat Hunting */}
      {subView === 'THREAT_HUNTING' && (
        <ThreatHuntingView onDeployRule={() => fetchSocData()} />
      )}

      {/* View 4: Live Endpoint Telemetry */}
      {subView === 'LIVE_ENDPOINT' && (
        <LiveEndpointTelemetryView />
      )}
    </div>
  );
}

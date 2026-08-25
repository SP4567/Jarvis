import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  ShieldAlert, 
  ShieldCheck, 
  Terminal, 
  Activity, 
  Wifi, 
  FileText, 
  Search, 
  RefreshCw, 
  AlertTriangle, 
  Play, 
  Cpu, 
  Database,
  Lock,
  Power,
  EyeOff
} from 'lucide-react';

export default function LiveEndpointTelemetryView({ socEnabled = true, onToggleSoc }) {
  const [activeTab, setActiveTab] = useState('PROCESSES'); // PROCESSES | SOCKETS | PERSISTENCE | SYSTEM_LOGS
  const [telemetry, setTelemetry] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [auditing, setAuditing] = useState(false);
  const [auditResult, setAuditResult] = useState(null);
  const [searchFilter, setSearchFilter] = useState('');

  const fetchLiveTelemetry = async () => {
    if (!socEnabled) {
      setProcesses([]);
      setConnections([]);
      return;
    }

    try {
      setLoading(true);
      const [telRes, procRes, connRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/soc/live_telemetry'),
        fetch('http://127.0.0.1:8000/api/soc/live_processes?limit=100'),
        fetch('http://127.0.0.1:8000/api/soc/live_connections?limit=100')
      ]);

      if (telRes.ok) setTelemetry(await telRes.json());
      if (procRes.ok) setProcesses(await procRes.json());
      if (connRes.ok) setConnections(await connRes.json());
    } catch (e) {
      console.warn('Error fetching live endpoint telemetry:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (socEnabled) {
      fetchLiveTelemetry();
      const interval = setInterval(fetchLiveTelemetry, 6000);
      return () => clearInterval(interval);
    } else {
      setProcesses([]);
      setConnections([]);
      setTelemetry(null);
    }
  }, [socEnabled]);

  const handleRunLiveAudit = async () => {
    if (!socEnabled) return;
    try {
      setAuditing(true);
      const res = await fetch('http://127.0.0.1:8000/api/soc/audit_host', {
        method: 'POST'
      });
      if (res.ok) {
        const audit = await res.json();
        setAuditResult(audit);
        await fetchLiveTelemetry();
      }
    } catch (e) {
      console.error('Failed to run live security audit:', e);
    } finally {
      setAuditing(false);
    }
  };

  const isActuallyActive = socEnabled && (telemetry ? telemetry.soc_enabled !== false : true);

  const filteredProcesses = processes.filter(p => 
    (p.name && p.name.toLowerCase().includes(searchFilter.toLowerCase())) ||
    (p.exe && p.exe.toLowerCase().includes(searchFilter.toLowerCase())) ||
    (p.pid && p.pid.toString().includes(searchFilter))
  );

  const filteredConnections = connections.filter(c => 
    (c.process_name && c.process_name.toLowerCase().includes(searchFilter.toLowerCase())) ||
    (c.local_address && c.local_address.includes(searchFilter)) ||
    (c.remote_address && c.remote_address.includes(searchFilter))
  );

  return (
    <div className="space-y-4">
      {/* Live Host Telemetry Header Banner */}
      <div className={`p-4 rounded-xl border flex flex-wrap items-center justify-between gap-4 transition-all ${
        isActuallyActive 
          ? 'glass-panel border-cyan-500/30' 
          : 'glass-panel border-amber-500/30 bg-amber-950/20'
      }`}>
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            isActuallyActive 
              ? 'bg-cyan-500/10 border border-cyan-500/30 text-cyan-400' 
              : 'bg-amber-500/10 border border-amber-500/30 text-amber-400'
          }`}>
            <Shield size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-mono font-bold text-white tracking-wide">
                LIVE ENDPOINT DEFENSE: {telemetry?.hostname || 'LOCAL_HOST'}
              </h2>
              {isActuallyActive ? (
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1 font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  EDR SENSORS: ONLINE (REAL-TIME)
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1 font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                  EDR SENSORS: OFFLINE (STANDBY)
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              {isActuallyActive 
                ? 'Live kernel process inspection, network socket tracking, registry autorun persistence & Windows event auditing'
                : 'Security telemetry scanning is currently paused. System process access is deactivated.'}
            </p>
          </div>
        </div>

        {/* 360-Degree Host Audit Trigger */}
        <div className="flex items-center gap-3">
          {isActuallyActive && (
            <button
              onClick={handleRunLiveAudit}
              disabled={auditing}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-rose-600 to-amber-600 hover:from-rose-500 hover:to-amber-500 text-white font-mono font-bold text-xs shadow-lg transition-all disabled:opacity-50"
            >
              <ShieldCheck size={15} className={auditing ? 'animate-spin' : ''} />
              {auditing ? 'AUDITING LIVE HOST...' : 'RUN 360° LIVE SECURITY AUDIT'}
            </button>
          )}
          {isActuallyActive && (
            <button
              onClick={fetchLiveTelemetry}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 transition-all"
              title="Refresh"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            </button>
          )}
        </div>
      </div>

      {/* Standby View When SOC is Turned Off */}
      {!isActuallyActive ? (
        <div className="glass-panel p-8 rounded-2xl border border-amber-500/30 bg-amber-950/10 text-center space-y-4 animate-fadeIn">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto text-amber-400 shadow-neon-amber">
            <EyeOff size={32} />
          </div>
          <div className="max-w-md mx-auto space-y-2">
            <h3 className="text-lg font-orbitron font-bold text-amber-300">
              HOST PROCESS & EDR SENSORS ARE IN STANDBY
            </h3>
            <p className="text-xs font-mono text-slate-400 leading-relaxed">
              All live endpoint process scanning, network connection querying, and autorun registry polling are completely paused. JARVIS is not accessing host processes while SOC is switched off.
            </p>
          </div>
          {onToggleSoc && (
            <button
              onClick={onToggleSoc}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-mono font-bold text-xs flex items-center gap-2 mx-auto shadow-neon-cyan transition-all"
            >
              <Power size={14} /> ACTIVATE SOC & RESUME LIVE MONITORING
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Live Audit Report Modal / Banner */}
          {auditResult && (
            <div className="glass-panel p-4 rounded-xl border border-amber-500/40 bg-amber-950/20 space-y-2 animate-fadeIn">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle size={16} className="text-amber-400" />
                  <span className="text-sm font-mono font-bold text-amber-300">
                    LIVE AUDIT REPORT [{auditResult.audit_id}] — STATUS: {auditResult.status}
                  </span>
                </div>
                <span className="text-xs font-mono text-slate-400">
                  Risk Score: <strong className="text-amber-400">{auditResult.host_risk_score}/100</strong>
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono pt-1">
                <div className="p-2 rounded bg-slate-900/60 border border-slate-800">
                  <div className="text-slate-500 text-[10px]">SCANNED PROCESSES</div>
                  <div className="text-cyan-400 font-bold mt-0.5">{auditResult.total_active_processes}</div>
                </div>
                <div className="p-2 rounded bg-slate-900/60 border border-slate-800">
                  <div className="text-slate-500 text-[10px]">SUSPICIOUS PROCESSES</div>
                  <div className="text-rose-400 font-bold mt-0.5">{auditResult.suspicious_process_count}</div>
                </div>
                <div className="p-2 rounded bg-slate-900/60 border border-slate-800">
                  <div className="text-slate-500 text-[10px]">LISTENING PORTS</div>
                  <div className="text-purple-400 font-bold mt-0.5">{auditResult.listening_ports_count}</div>
                </div>
                <div className="p-2 rounded bg-slate-900/60 border border-slate-800">
                  <div className="text-slate-500 text-[10px]">STARTUP PERSISTENCE</div>
                  <div className="text-emerald-400 font-bold mt-0.5">{auditResult.startup_persistence_items?.length || 0}</div>
                </div>
              </div>
            </div>
          )}

          {/* Tabs Switcher & Search Filter */}
          <div className="flex flex-wrap items-center justify-between gap-3 glass-panel px-4 py-2 rounded-xl border border-cyan-500/20">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('PROCESSES')}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
                  activeTab === 'PROCESSES'
                    ? 'bg-cyan-500 text-black shadow-neon-cyan'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Cpu size={13} />
                ACTIVE PROCESSES ({processes.length})
              </button>
              <button
                onClick={() => setActiveTab('SOCKETS')}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
                  activeTab === 'SOCKETS'
                    ? 'bg-cyan-500 text-black shadow-neon-cyan'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Wifi size={13} />
                NETWORK SOCKETS ({connections.length})
              </button>
              <button
                onClick={() => setActiveTab('PERSISTENCE')}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
                  activeTab === 'PERSISTENCE'
                    ? 'bg-cyan-500 text-black shadow-neon-cyan'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Lock size={13} />
                STARTUP PERSISTENCE ({telemetry?.startup_persistence_count || 0})
              </button>
              <button
                onClick={() => setActiveTab('SYSTEM_LOGS')}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
                  activeTab === 'SYSTEM_LOGS'
                    ? 'bg-cyan-500 text-black shadow-neon-cyan'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <FileText size={13} />
                WINDOWS EVENT VIEWER
              </button>
            </div>

            {/* Live Filter Search Input */}
            <div className="relative">
              <Search size={13} className="absolute left-2.5 top-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Filter live telemetry..."
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                className="pl-8 pr-3 py-1 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500/50 w-48 sm:w-64"
              />
            </div>
          </div>

          {/* Tab 1: Live Processes Table */}
          {activeTab === 'PROCESSES' && (
            <div className="glass-panel p-4 rounded-xl border border-cyan-500/20 overflow-x-auto">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 text-[11px]">
                    <th className="pb-2">PID</th>
                    <th className="pb-2">PROCESS NAME</th>
                    <th className="pb-2">CPU %</th>
                    <th className="pb-2">MEM %</th>
                    <th className="pb-2">EXECUTABLE PATH</th>
                    <th className="pb-2">STATUS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredProcesses.map((p) => (
                    <tr key={p.pid} className="hover:bg-slate-900/40">
                      <td className="py-2 text-cyan-400 font-bold">{p.pid}</td>
                      <td className="py-2 text-slate-200 font-medium">{p.name}</td>
                      <td className="py-2 text-amber-400">{p.cpu_percent}%</td>
                      <td className="py-2 text-purple-400">{p.memory_percent}%</td>
                      <td className="py-2 text-slate-400 truncate max-w-xs" title={p.exe}>
                        {p.exe}
                      </td>
                      <td className="py-2">
                        {p.is_suspicious ? (
                          <span className="px-2 py-0.5 rounded text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold">
                            SUSPICIOUS
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            NOMINAL
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Tab 2: Live Network Sockets Table */}
          {activeTab === 'SOCKETS' && (
            <div className="glass-panel p-4 rounded-xl border border-cyan-500/20 overflow-x-auto">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 text-[11px]">
                    <th className="pb-2">PROTO</th>
                    <th className="pb-2">LOCAL ADDRESS</th>
                    <th className="pb-2">REMOTE ADDRESS</th>
                    <th className="pb-2">STATE</th>
                    <th className="pb-2">OWNING PROCESS</th>
                    <th className="pb-2">PID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredConnections.map((c, i) => (
                    <tr key={i} className="hover:bg-slate-900/40">
                      <td className="py-2 text-cyan-400 font-bold">{c.type}</td>
                      <td className="py-2 text-slate-300">{c.local_address}</td>
                      <td className="py-2 text-amber-300">{c.remote_address || '*:*'}</td>
                      <td className="py-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          c.status === 'LISTEN'
                            ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                            : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                        }`}>
                          {c.status}
                        </span>
                      </td>
                      <td className="py-2 text-slate-200">{c.process_name}</td>
                      <td className="py-2 text-slate-400">{c.pid || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Tab 3: Startup Persistence Table */}
          {activeTab === 'PERSISTENCE' && (
            <div className="glass-panel p-4 rounded-xl border border-cyan-500/20 overflow-x-auto">
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 text-[11px]">
                    <th className="pb-2">HIVE</th>
                    <th className="pb-2">REGISTRY PATH</th>
                    <th className="pb-2">VALUE NAME</th>
                    <th className="pb-2">AUTORUN COMMAND</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {(telemetry?.startup_items || []).map((it, i) => (
                    <tr key={i} className="hover:bg-slate-900/40">
                      <td className="py-2 text-amber-400 font-bold">{it.hive}</td>
                      <td className="py-2 text-slate-400">{it.key}</td>
                      <td className="py-2 text-cyan-300 font-medium">{it.name}</td>
                      <td className="py-2 text-slate-300 font-mono truncate max-w-sm" title={it.command}>
                        {it.command}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Tab 4: Windows Event Viewer */}
          {activeTab === 'SYSTEM_LOGS' && (
            <div className="glass-panel p-4 rounded-xl border border-cyan-500/20 space-y-3">
              {(telemetry?.recent_event_logs || []).map((ev, i) => (
                <div key={i} className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 font-mono text-xs space-y-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-cyan-400 font-bold">EVENT ID: {ev.event_id} — {ev.source}</span>
                    <span className="text-slate-500">{ev.timestamp}</span>
                  </div>
                  <p className="text-slate-300 text-xs">{ev.description}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

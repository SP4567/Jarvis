import React, { useState, useEffect } from 'react';
import { 
  Server, 
  Cpu, 
  Wifi, 
  Layers, 
  ShieldAlert, 
  ShieldCheck, 
  Search, 
  RefreshCw, 
  Activity,
  AlertTriangle,
  Play,
  CheckCircle2
} from 'lucide-react';

export default function LiveEndpointTelemetryView() {
  const [activeTab, setActiveTab] = useState('PROCESSES'); // PROCESSES | SOCKETS | STARTUP | EVENT_LOGS
  const [processes, setProcesses] = useState([]);
  const [connections, setConnections] = useState([]);
  const [telemetry, setTelemetry] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [auditing, setAuditing] = useState(false);
  const [auditResult, setAuditResult] = useState(null);

  const fetchLiveTelemetry = async () => {
    try {
      setLoading(true);
      const [telRes, procRes, connRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/soc/live_telemetry'),
        fetch('http://127.0.0.1:8000/api/soc/live_processes?limit=60'),
        fetch('http://127.0.0.1:8000/api/soc/live_connections?limit=60')
      ]);

      if (telRes.ok) setTelemetry(await telRes.json());
      if (procRes.ok) setProcesses(await procRes.json());
      if (connRes.ok) setConnections(await connRes.json());
    } catch (e) {
      console.warn('Telemetry fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveTelemetry();
    const interval = setInterval(fetchLiveTelemetry, 6000);
    return () => clearInterval(interval);
  }, []);

  const handleRunAudit = async () => {
    try {
      setAuditing(true);
      const res = await fetch('http://127.0.0.1:8000/api/soc/audit_host', { method: 'POST' });
      if (res.ok) {
        setAuditResult(await res.json());
        fetchLiveTelemetry();
      }
    } catch (e) {
      console.error('Audit failed:', e);
    } finally {
      setAuditing(false);
    }
  };

  const filteredProcesses = processes.filter(p => 
    !searchQuery || 
    p.name?.toLowerCase().includes(searchQuery.toLowerCase()) || 
    String(p.pid).includes(searchQuery) ||
    p.cmdline?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredConnections = connections.filter(c => 
    !searchQuery || 
    c.remote_address?.includes(searchQuery) || 
    c.process_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    String(c.local_port).includes(searchQuery)
  );

  return (
    <div className="space-y-4">
      {/* Top Telemetry Header & Health Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div className="p-3 rounded-xl bg-slate-900/95 border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
            <span>ACTIVE PROCESSES</span>
            <Cpu size={14} className="text-sky-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {telemetry.total_processes || processes.length || 0}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">Live Host Processes Monitored</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/95 border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
            <span>NETWORK SOCKETS</span>
            <Wifi size={14} className="text-emerald-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {telemetry.active_sockets || connections.length || 0}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">TCP/UDP Active Connections</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/95 border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
            <span>LISTENING PORTS</span>
            <Activity size={14} className="text-indigo-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {telemetry.listening_ports_count || 0}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">Inbound Listening Services</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/95 border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
            <span>ANOMALOUS PROCESSES</span>
            <ShieldAlert size={14} className="text-rose-400" />
          </div>
          <div className={`text-xl font-bold font-mono ${telemetry.suspicious_processes_count > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
            {telemetry.suspicious_processes_count || 0}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">Flagged for Triage</div>
        </div>
      </div>

      {/* Main Telemetry Inspector Panel */}
      <div className="bg-slate-900/95 rounded-xl border border-slate-800 shadow-xl overflow-hidden flex flex-col h-[480px]">
        {/* Controls Bar */}
        <div className="p-3 border-b border-slate-800 bg-slate-950/70 flex items-center justify-between gap-3">
          <div className="flex items-center gap-1.5 text-[11px] font-mono">
            {[
              { id: 'PROCESSES', label: `Processes (${processes.length})` },
              { id: 'SOCKETS', label: `Sockets (${connections.length})` },
              { id: 'STARTUP', label: 'Startup Persistence' },
              { id: 'EVENT_LOGS', label: 'Event Logs' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1 rounded transition-colors ${
                  activeTab === tab.id
                    ? 'bg-slate-800 text-white font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <div className="relative w-48">
              <Search size={12} className="absolute left-2.5 top-2 text-slate-500" />
              <input
                type="text"
                placeholder="Filter telemetry..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded pl-7 pr-2.5 py-1 text-[11px] font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-slate-600"
              />
            </div>

            <button
              onClick={handleRunAudit}
              disabled={auditing}
              className="flex items-center gap-1 px-3 py-1 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded text-[11px] font-mono font-semibold transition-colors"
            >
              <Play size={11} className={auditing ? "animate-spin" : ""} />
              {auditing ? "AUDITING..." : "360° AUDIT"}
            </button>
          </div>
        </div>

        {/* Telemetry Data Grid */}
        <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60 font-mono text-[11px]">
          {/* TAB 1: PROCESSES */}
          {activeTab === 'PROCESSES' && (
            <div className="p-0">
              <div className="grid grid-cols-12 gap-2 px-3 py-2 bg-slate-950/80 text-[10px] text-slate-500 font-bold uppercase border-b border-slate-800">
                <div className="col-span-1">PID</div>
                <div className="col-span-3">Process Name</div>
                <div className="col-span-2">User</div>
                <div className="col-span-2">CPU / RAM</div>
                <div className="col-span-4">Command Line</div>
              </div>
              {filteredProcesses.map(p => (
                <div key={p.pid} className="grid grid-cols-12 gap-2 px-3 py-2 hover:bg-slate-800/40 items-center text-slate-300">
                  <div className="col-span-1 text-slate-400">{p.pid}</div>
                  <div className="col-span-3 font-semibold text-slate-100 truncate">{p.name}</div>
                  <div className="col-span-2 text-slate-400 truncate">{p.username || "SYSTEM"}</div>
                  <div className="col-span-2 text-slate-400">{p.cpu_percent || 0}% / {p.memory_percent ? `${Math.round(p.memory_percent)}%` : "12MB"}</div>
                  <div className="col-span-4 text-slate-400 truncate font-mono text-[10px]">{p.cmdline || p.exe || "-"}</div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 2: SOCKETS */}
          {activeTab === 'SOCKETS' && (
            <div className="p-0">
              <div className="grid grid-cols-12 gap-2 px-3 py-2 bg-slate-950/80 text-[10px] text-slate-500 font-bold uppercase border-b border-slate-800">
                <div className="col-span-2">Protocol / PID</div>
                <div className="col-span-3">Process</div>
                <div className="col-span-3">Local Address</div>
                <div className="col-span-4">Remote Destination / Status</div>
              </div>
              {filteredConnections.map((c, i) => (
                <div key={i} className="grid grid-cols-12 gap-2 px-3 py-2 hover:bg-slate-800/40 items-center text-slate-300">
                  <div className="col-span-2 text-slate-400">{c.protocol || "TCP"} (PID: {c.pid || "-"})</div>
                  <div className="col-span-3 font-semibold text-slate-100 truncate">{c.process_name || "System"}</div>
                  <div className="col-span-3 text-slate-400">{c.local_address}:{c.local_port}</div>
                  <div className="col-span-4 text-slate-300 truncate">
                    {c.remote_address ? `${c.remote_address}:${c.remote_port}` : "LISTEN"} ({c.status})
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 3: STARTUP PERSISTENCE */}
          {activeTab === 'STARTUP' && (
            <div className="p-3 space-y-2">
              {(telemetry.startup_persistence_items || []).length === 0 ? (
                <div className="text-center py-8 text-slate-500">Zero unauthorized startup persistence entries detected.</div>
              ) : (
                telemetry.startup_persistence_items.map((item, i) => (
                  <div key={i} className="p-2.5 rounded bg-slate-950/70 border border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="font-bold text-slate-200 block">{item.name}</span>
                      <span className="text-slate-400 text-[10px]">{item.command || item.path}</span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[9px]">
                      {item.location || "Registry Run"}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}

          {/* TAB 4: EVENT LOGS */}
          {activeTab === 'EVENT_LOGS' && (
            <div className="p-3 space-y-2">
              {(telemetry.recent_event_logs || []).length === 0 ? (
                <div className="text-center py-8 text-slate-500">Security event log stream nominal.</div>
              ) : (
                telemetry.recent_event_logs.map((log, i) => (
                  <div key={i} className="p-2.5 rounded bg-slate-950/70 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span className="font-bold text-slate-300">Event ID {log.event_id || 4688} // {log.source || "Security"}</span>
                      <span>{log.time_generated || "Recent"}</span>
                    </div>
                    <p className="text-slate-200">{log.message || log.description}</p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

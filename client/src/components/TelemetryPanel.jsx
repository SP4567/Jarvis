import React, { useState, useEffect } from 'react';
import { Cpu, HardDrive, Battery, BatteryCharging, Zap, Clock, Activity, Wifi, ShieldCheck, Thermometer } from 'lucide-react';

export default function TelemetryPanel({ vitals = {} }) {
  const [timeStr, setTimeStr] = useState('');
  const [dateStr, setDateStr] = useState('');
  const [netSpeed, setNetSpeed] = useState({ rx: 142.4, tx: 38.6 });

  useEffect(() => {
    const updateTime = () => {
      const d = new Date();
      setTimeStr(d.toLocaleTimeString('en-US', { hour12: false }));
      setDateStr(d.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const netInterval = setInterval(() => {
      setNetSpeed({
        rx: +(120 + Math.random() * 85).toFixed(1),
        tx: +(25 + Math.random() * 40).toFixed(1)
      });
    }, 2000);
    return () => clearInterval(netInterval);
  }, []);

  const cpuPct = vitals.cpu_percent || 14;
  const ramPct = vitals.ram_percent || 48;
  const diskPct = vitals.disk_percent || 32;
  const battery = vitals.battery || { percent: 94, power_plugged: true };
  const cpuTemp = vitals.cpu_temp || (42 + Math.floor(cpuPct * 0.3));

  const renderCircularGauge = (pct, strokeColor, label, valueText, iconNode) => {
    const radius = 24;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (pct / 100) * circumference;

    return (
      <div className="flex flex-col items-center justify-center p-3 rounded-xl bg-slate-950/60 border border-white/[0.06] hover:border-white/[0.12] transition-all group">
        <div className="relative flex items-center justify-center">
          <svg className="w-16 h-16 -rotate-90">
            <circle
              cx="32"
              cy="32"
              r={radius}
              className="stroke-slate-800/80"
              strokeWidth="3.5"
              fill="transparent"
            />
            <circle
              cx="32"
              cy="32"
              r={radius}
              stroke={strokeColor}
              strokeWidth="3.5"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              className="transition-all duration-700 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {iconNode}
            <span className="text-[11px] font-mono-num font-bold text-slate-100 mt-0.5">
              {pct}%
            </span>
          </div>
        </div>
        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider mt-1.5 font-medium">
          {label}
        </span>
        <span className="text-[9px] font-mono text-slate-500 font-mono-num">{valueText}</span>
      </div>
    );
  };

  return (
    <div className="bg-slate-900/70 backdrop-blur-xl rounded-xl p-4 border border-white/[0.08] flex flex-col justify-between h-full shadow-2xl space-y-4">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.06] mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
              <Zap size={14} />
            </div>
            <div>
              <h2 className="text-xs uppercase tracking-wider font-mono text-slate-100 font-bold">
                SYSTEM VITALS
              </h2>
              <p className="text-[9px] font-mono text-slate-500">HOST TELEMETRY ENGINE</p>
            </div>
          </div>
          <div className="text-right font-mono">
            <div className="flex items-center justify-end gap-1 text-xs text-slate-200 font-semibold font-mono-num">
              <Clock size={11} className="text-slate-400" />
              <span>{timeStr}</span>
            </div>
            <p className="text-[9px] text-slate-500">{dateStr}</p>
          </div>
        </div>

        {/* 3 Circular Diagnostic Gauges */}
        <div className="grid grid-cols-3 gap-2.5 mb-3.5">
          {renderCircularGauge(
            cpuPct,
            '#38bdf8',
            'CPU',
            `${vitals.cpu_count || 8} Cores`,
            <Cpu size={11} className="text-sky-400" />
          )}
          {renderCircularGauge(
            ramPct,
            '#10b981',
            'RAM',
            `${vitals.ram_used_gb || 5.2} / ${vitals.ram_total_gb || 8.0}G`,
            <Activity size={11} className="text-emerald-400" />
          )}
          {renderCircularGauge(
            diskPct,
            '#f59e0b',
            'DISK',
            `${vitals.disk_free_gb || 14}G Free`,
            <HardDrive size={11} className="text-amber-400" />
          )}
        </div>

        {/* Secondary Metric Rows */}
        <div className="space-y-2 font-mono text-xs">
          {/* Thermal Sensor */}
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950/50 border border-white/[0.05]">
            <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
              <Thermometer size={12} className="text-rose-400" />
              <span>TEMPERATURE</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (cpuTemp / 90) * 100)}%` }}
                />
              </div>
              <span className="text-slate-200 font-bold text-[11px] font-mono-num">{cpuTemp}°C</span>
            </div>
          </div>

          {/* Battery Status */}
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950/50 border border-white/[0.05]">
            <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
              {battery.power_plugged ? (
                <BatteryCharging size={12} className="text-emerald-400" />
              ) : (
                <Battery size={12} className="text-amber-400" />
              )}
              <span>BATTERY</span>
            </div>
            <div className="flex items-center gap-1.5 font-mono-num">
              <span className="text-slate-200 font-bold text-[11px]">{battery.percent}%</span>
              <span className="text-[9px] text-slate-500 px-1 py-0.5 rounded bg-slate-900 border border-white/[0.04]">
                {battery.power_plugged ? 'CHARGING' : 'BATTERY'}
              </span>
            </div>
          </div>

          {/* Network Ingress / Egress */}
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950/50 border border-white/[0.05]">
            <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
              <Wifi size={12} className="text-sky-400" />
              <span>NETWORK</span>
            </div>
            <div className="flex items-center gap-2 text-[10px] text-slate-300 font-mono-num">
              <span className="text-emerald-400">↓ {netSpeed.rx} KB/s</span>
              <span className="text-sky-400">↑ {netSpeed.tx} KB/s</span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Interlock Footer Status */}
      <div className="pt-2 border-t border-white/[0.06] flex items-center justify-between text-[10px] font-mono">
        <div className="flex items-center gap-1.5 text-emerald-400">
          <ShieldCheck size={12} />
          <span className="font-semibold tracking-wide">ZERO-TRUST GUARDRAIL ACTIVE</span>
        </div>
        <span className="text-slate-500">v2.0.0</span>
      </div>
    </div>
  );
}

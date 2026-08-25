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

  // Fluctuating network telemetry
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

  // Circular gauge helper
  const renderCircularGauge = (pct, colorClass, strokeColor, label, valueText, iconNode) => {
    const radius = 28;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (pct / 100) * circumference;

    return (
      <div className="flex flex-col items-center justify-center p-3 rounded-xl bg-slate-950/70 border border-cyan-500/15 relative overflow-hidden group hover:border-cyan-500/40 transition-all">
        <div className="relative flex items-center justify-center">
          <svg className="w-20 h-20 -rotate-90">
            {/* Background Track */}
            <circle
              cx="40"
              cy="40"
              r={radius}
              className="stroke-slate-800"
              strokeWidth="5"
              fill="transparent"
            />
            {/* Dynamic Fill Arc */}
            <circle
              cx="40"
              cy="40"
              r={radius}
              stroke={strokeColor}
              strokeWidth="5"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              className="transition-all duration-700 ease-out"
            />
          </svg>
          {/* Center Value */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {iconNode}
            <span className={`text-xs font-mono font-bold ${colorClass} mt-0.5`}>
              {pct}%
            </span>
          </div>
        </div>
        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider mt-1 font-semibold">
          {label}
        </span>
        <span className="text-[9px] font-mono text-slate-500">{valueText}</span>
      </div>
    );
  };

  return (
    <div className="glass-panel rounded-2xl p-4 border border-cyan-500/20 flex flex-col justify-between h-full shadow-2xl relative">
      {/* Tech corner accents */}
      <div className="tech-corner-tl" />
      <div className="tech-corner-tr" />
      <div className="tech-corner-bl" />
      <div className="tech-corner-br" />

      {/* Header */}
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-cyan-500/15 mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Zap size={15} className="animate-pulse" />
            </div>
            <div>
              <h2 className="text-xs uppercase tracking-widest font-mono text-cyan-300 font-bold">
                SYSTEM VITALS
              </h2>
              <p className="text-[9px] font-mono text-slate-500">HOST TELEMETRY ENGINE</p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center justify-end gap-1 text-xs font-mono text-cyan-300 font-bold">
              <Clock size={12} className="text-cyan-400" />
              <span>{timeStr}</span>
            </div>
            <span className="text-[9px] font-mono text-slate-500">{dateStr}</span>
          </div>
        </div>

        {/* Circular Gauges Row */}
        <div className="grid grid-cols-2 gap-2.5 mb-3">
          {renderCircularGauge(
            cpuPct,
            'text-cyan-300',
            '#06b6d4',
            'CPU LOAD',
            `${vitals.cpu_count || 8} Cores Active`,
            <Cpu size={12} className="text-cyan-400" />
          )}
          {renderCircularGauge(
            ramPct,
            'text-amber-300',
            '#f59e0b',
            'MEMORY',
            `${vitals.ram_used_gb || '7.4'} / ${vitals.ram_total_gb || '16.0'} GB`,
            <Zap size={12} className="text-amber-400" />
          )}
        </div>

        {/* Thermal & Storage Bars */}
        <div className="space-y-2.5 mb-3">
          {/* Storage (C:) Bar */}
          <div className="p-2.5 rounded-xl bg-slate-950/70 border border-cyan-500/15">
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <span className="text-slate-400 flex items-center gap-1.5 text-[11px]">
                <HardDrive size={13} className="text-emerald-400" />
                <span>STORAGE (C:)</span>
              </span>
              <span className="text-emerald-300 font-bold text-xs">{diskPct}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 transition-all duration-700"
                style={{ width: `${Math.min(100, Math.max(5, diskPct))}%` }}
              />
            </div>
            <div className="flex justify-between text-[9px] font-mono text-slate-500 mt-1">
              <span>{vitals.disk_free_gb || '284'} GB Free</span>
              <span>{vitals.disk_total_gb || '512'} GB Total</span>
            </div>
          </div>

          {/* Thermal Engine */}
          <div className="p-2.5 rounded-xl bg-slate-950/70 border border-cyan-500/15 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Thermometer size={14} className="text-rose-400" />
              <div>
                <span className="text-[11px] font-mono text-slate-300 font-semibold block">
                  Core Temp
                </span>
                <span className="text-[9px] font-mono text-slate-500">Thermal Nominal</span>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono font-bold text-rose-300">{cpuTemp}°C</span>
              <span className="text-[9px] font-mono text-emerald-400 block">NOMINAL</span>
            </div>
          </div>
        </div>
      </div>

      {/* Network & Power Footer */}
      <div className="pt-3 border-t border-cyan-500/15 space-y-2">
        {/* Live Network IO */}
        <div className="flex items-center justify-between text-[11px] font-mono p-2 rounded-lg bg-slate-950/60 border border-slate-800">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Wifi size={12} className="text-cyan-400" />
            <span>NET I/O:</span>
          </div>
          <div className="flex items-center gap-2 font-mono text-[10px]">
            <span className="text-emerald-400">↓ {netSpeed.rx} KB/s</span>
            <span className="text-slate-600">|</span>
            <span className="text-cyan-400">↑ {netSpeed.tx} KB/s</span>
          </div>
        </div>

        {/* Battery / Power Grid */}
        <div className="flex items-center justify-between text-[11px] font-mono px-2 py-1">
          <div className="flex items-center gap-1.5 text-slate-400">
            {battery.power_plugged ? (
              <BatteryCharging size={13} className="text-emerald-400" />
            ) : (
              <Battery size={13} className="text-cyan-400" />
            )}
            <span>POWER GRID:</span>
          </div>
          <span className="font-bold text-slate-200">
            {battery.percent}% {battery.power_plugged ? '(AC ONLINE)' : '(DISCHARGING)'}
          </span>
        </div>
      </div>
    </div>
  );
}

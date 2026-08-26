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

  const renderCircularGauge = (pct, colorClass, strokeColor, label, valueText, iconNode) => {
    const radius = 28;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (pct / 100) * circumference;

    return (
      <div className="flex flex-col items-center justify-center p-3 rounded-xl bg-slate-950/80 border border-slate-800 relative overflow-hidden transition-all hover:border-slate-750">
        <div className="relative flex items-center justify-center">
          <svg className="w-20 h-20 -rotate-90">
            <circle
              cx="40"
              cy="40"
              r={radius}
              className="stroke-slate-850"
              strokeWidth="4"
              fill="transparent"
            />
            <circle
              cx="40"
              cy="40"
              r={radius}
              stroke={strokeColor}
              strokeWidth="4"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              className="transition-all duration-700 ease-out"
            />
          </svg>
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
    <div className="bg-slate-900/95 rounded-xl p-4 border border-slate-800 flex flex-col justify-between h-full shadow-xl">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1 rounded bg-slate-800 text-slate-300">
              <Zap size={14} className="text-sky-400" />
            </div>
            <div>
              <h2 className="text-xs uppercase tracking-wider font-mono text-slate-100 font-bold">
                SYSTEM VITALS
              </h2>
              <p className="text-[9px] font-mono text-slate-500">HOST TELEMETRY ENGINE</p>
            </div>
          </div>
          <div className="text-right font-mono">
            <div className="flex items-center justify-end gap-1 text-xs text-slate-200 font-semibold">
              <Clock size={11} className="text-slate-400" />
              <span>{timeStr}</span>
            </div>
            <span className="text-[9px] text-slate-500">{dateStr}</span>
          </div>
        </div>

        {/* Circular Gauges Row */}
        <div className="grid grid-cols-2 gap-2.5 mb-3">
          {renderCircularGauge(
            cpuPct,
            'text-sky-400',
            '#38bdf8',
            'CPU LOAD',
            `${vitals.cpu_count || 8} Cores Active`,
            <Cpu size={12} className="text-sky-400" />
          )}
          {renderCircularGauge(
            ramPct,
            'text-amber-400',
            '#fbbf24',
            'MEMORY',
            `${vitals.ram_used_gb || '7.4'} / ${vitals.ram_total_gb || '16.0'} GB`,
            <Zap size={12} className="text-amber-400" />
          )}
        </div>

        {/* Storage & Thermal Bars */}
        <div className="space-y-2.5 mb-3">
          {/* Storage (C:) Bar */}
          <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <span className="text-slate-400 flex items-center gap-1.5 text-[11px]">
                <HardDrive size={12} className="text-emerald-400" />
                <span>STORAGE (C:)</span>
              </span>
              <span className="text-emerald-400 font-bold text-xs">{diskPct}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all duration-700"
                style={{ width: `${diskPct}%` }}
              />
            </div>
            <div className="flex justify-between text-[9px] font-mono text-slate-500 mt-1">
              <span>Used: {vitals.disk_used_gb || '154'} GB</span>
              <span>Total: {vitals.disk_total_gb || '476'} GB</span>
            </div>
          </div>

          {/* Thermal Indicator */}
          <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <span className="text-slate-400 flex items-center gap-1.5 text-[11px]">
                <Thermometer size={12} className="text-indigo-400" />
                <span>TEMPERATURE</span>
              </span>
              <span className="text-indigo-300 font-bold text-xs">{cpuTemp}°C</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-500 transition-all duration-700"
                style={{ width: `${Math.min(100, (cpuTemp / 90) * 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-[9px] font-mono text-slate-500 mt-1">
              <span>Package Thermal State</span>
              <span>{cpuTemp < 65 ? 'NOMINAL' : 'ELEVATED'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Network Bandwidth & Battery Footer */}
      <div className="pt-2.5 border-t border-slate-800 space-y-2">
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 bg-slate-950/80 p-2 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5">
            <Wifi size={11} className="text-sky-400" />
            <span>NET RX:</span>
            <span className="text-slate-200 font-semibold">{netSpeed.rx} KB/s</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span>TX:</span>
            <span className="text-slate-200 font-semibold">{netSpeed.tx} KB/s</span>
          </div>
        </div>

        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 px-1">
          <div className="flex items-center gap-1.5">
            {battery.power_plugged ? (
              <BatteryCharging size={13} className="text-emerald-400" />
            ) : (
              <Battery size={13} className="text-amber-400" />
            )}
            <span>POWER: {battery.percent}% {battery.power_plugged ? '(A/C MAINS)' : '(BATTERY)'}</span>
          </div>
          <span className="text-emerald-400 font-semibold">ONLINE</span>
        </div>
      </div>
    </div>
  );
}

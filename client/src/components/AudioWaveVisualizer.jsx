import React from 'react';

export default function AudioWaveVisualizer({ state, audioLevel }) {
  const bars = 24;
  const isSpeaking = state === 'speaking';
  const isThinking = state === 'thinking';
  const isAlert = state === 'guardrail_alert';

  return (
    <div className="flex items-center justify-center gap-1 h-8 px-3 py-1 bg-slate-950/60 rounded-full border border-cyan-500/20 backdrop-blur-sm">
      {Array.from({ length: bars }).map((_, idx) => {
        let height = 4;
        let color = 'bg-cyan-500/40';

        if (isSpeaking) {
          const factor = Math.sin((idx / bars) * Math.PI) * (audioLevel / 100);
          const rand = (idx % 3 === 0 ? 0.8 : 1.2) * factor * 24;
          height = Math.max(4, Math.min(26, Math.floor(rand)));
          color = 'bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]';
        } else if (isThinking) {
          const phase = (Date.now() / 150 + idx * 0.4) % (Math.PI * 2);
          height = Math.max(4, Math.floor((Math.sin(phase) + 1) * 8) + 4);
          color = 'bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.6)]';
        } else if (isAlert) {
          height = 16;
          color = 'bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.8)]';
        }

        return (
          <div
            key={idx}
            className={`w-1 rounded-full transition-all duration-75 ${color}`}
            style={{ height: `${height}px` }}
          />
        );
      })}
    </div>
  );
}

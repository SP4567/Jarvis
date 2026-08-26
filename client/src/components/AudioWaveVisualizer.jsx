import React from 'react';

export default function AudioWaveVisualizer({ state, audioLevel }) {
  const bars = 24;
  const isSpeaking = state === 'speaking';
  const isThinking = state === 'thinking';
  const isAlert = state === 'guardrail_alert';

  return (
    <div className="flex items-center justify-center gap-1 h-7 px-3 py-1 bg-slate-950 rounded-lg border border-slate-800">
      {Array.from({ length: bars }).map((_, idx) => {
        let height = 3;
        let color = 'bg-slate-700';

        if (isSpeaking) {
          const factor = Math.sin((idx / bars) * Math.PI) * (audioLevel / 100);
          const rand = (idx % 3 === 0 ? 0.8 : 1.2) * factor * 20;
          height = Math.max(3, Math.min(22, Math.floor(rand)));
          color = 'bg-sky-400';
        } else if (isThinking) {
          const phase = (Date.now() / 150 + idx * 0.4) % (Math.PI * 2);
          height = Math.max(3, Math.floor((Math.sin(phase) + 1) * 7) + 3);
          color = 'bg-amber-400';
        } else if (isAlert) {
          height = 14;
          color = 'bg-rose-500 animate-pulse';
        }

        return (
          <div
            key={idx}
            className={`w-1 rounded-sm transition-all duration-75 ${color}`}
            style={{ height: `${height}px` }}
          />
        );
      })}
    </div>
  );
}

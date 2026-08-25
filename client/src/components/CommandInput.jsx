import React, { useState } from 'react';
import { Send, Sparkles, Terminal, CornerDownLeft, X } from 'lucide-react';
import { playCommandSendSound } from '../utils/audioEffects';

const QUICK_COMMANDS = [
  "Run live SOC security audit",
  "What are my system vitals?",
  "Play synthwave ambient soundtrack",
  "Write python script to calculate fibonacci",
  "Remember my name is Suyash",
  "What time is it in Tokyo?"
];

export default function CommandInput({ onSendCommand, disabled = false }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    playCommandSendSound();
    onSendCommand(text.trim());
    setText('');
  };

  const handleChipClick = (cmd) => {
    if (disabled) return;
    playCommandSendSound();
    onSendCommand(cmd);
  };

  return (
    <div className="w-full space-y-2.5">
      {/* Quick Suggestion Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs font-mono scrollbar-none">
        <span className="text-[10px] text-slate-400 font-bold uppercase flex items-center gap-1.5 flex-shrink-0">
          <Sparkles size={12} className="text-cyan-400" /> QUICK DIRECTIVES:
        </span>
        {QUICK_COMMANDS.map((cmd, i) => (
          <button
            key={i}
            onClick={() => handleChipClick(cmd)}
            disabled={disabled}
            className="px-3 py-1 rounded-lg bg-slate-950/80 hover:bg-cyan-950/80 border border-cyan-500/20 hover:border-cyan-400 text-slate-300 hover:text-cyan-200 text-[11px] whitespace-nowrap transition-all flex-shrink-0 shadow-sm"
          >
            {cmd}
          </button>
        ))}
      </div>

      {/* Manual Command Input Bar */}
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <div className="absolute left-4 text-cyan-400 flex items-center gap-1.5">
          <Terminal size={17} />
          <span className="text-slate-600 font-mono text-xs">&gt;</span>
        </div>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter command directive for J.A.R.V.I.S. (e.g., 'Check CPU load', 'Isolate endpoint', 'Explain quantum computing')..."
          disabled={disabled}
          className="w-full pl-14 pr-28 py-3.5 rounded-2xl bg-slate-950/90 border border-cyan-500/30 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 text-slate-100 placeholder-slate-500 text-xs font-mono transition-all shadow-[0_4px_25px_rgba(0,0,0,0.5)]"
        />
        {text && (
          <button
            type="button"
            onClick={() => setText('')}
            className="absolute right-24 p-1 text-slate-500 hover:text-slate-300 transition-colors"
            title="Clear text"
          >
            <X size={14} />
          </button>
        )}
        <button
          type="submit"
          disabled={!text.trim() || disabled}
          className="absolute right-2.5 flex items-center gap-1.5 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-30 disabled:cursor-not-allowed text-slate-950 font-mono font-bold text-xs transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)]"
        >
          <span>EXEC</span>
          <CornerDownLeft size={13} />
        </button>
      </form>
    </div>
  );
}

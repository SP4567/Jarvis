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
    <div className="w-full space-y-2 font-mono">
      {/* Quick Suggestion Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs scrollbar-none">
        <span className="text-[10px] text-slate-500 font-semibold uppercase flex items-center gap-1 flex-shrink-0">
          <Sparkles size={11} className="text-sky-400" /> QUICK DIRECTIVES:
        </span>
        {QUICK_COMMANDS.map((cmd, i) => (
          <button
            key={i}
            onClick={() => handleChipClick(cmd)}
            disabled={disabled}
            className="px-2.5 py-1 rounded-md bg-slate-900/80 hover:bg-slate-850 border border-white/[0.06] hover:border-white/[0.14] text-slate-400 hover:text-slate-200 text-[10px] whitespace-nowrap transition-all flex-shrink-0"
          >
            {cmd}
          </button>
        ))}
      </div>

      {/* Manual Command Input Bar */}
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <div className="absolute left-3.5 text-slate-400 flex items-center gap-1.5 pointer-events-none">
          <Terminal size={14} className="text-sky-400" />
          <span className="text-slate-600 text-xs">&gt;</span>
        </div>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter directive for J.A.R.V.I.S. (e.g. 'Check CPU load', 'Isolate endpoint', 'Explain quantum computing')..."
          disabled={disabled}
          className="w-full pl-11 pr-24 py-3 rounded-xl bg-slate-950/80 border border-white/[0.08] focus:border-sky-500/40 focus:ring-1 focus:ring-sky-500/20 focus:outline-none text-slate-100 placeholder-slate-500 text-xs font-mono transition-all shadow-inner"
        />
        {text && (
          <button
            type="button"
            onClick={() => setText('')}
            className="absolute right-20 p-1 text-slate-500 hover:text-slate-300 transition-colors"
            title="Clear text"
          >
            <X size={13} />
          </button>
        )}
        <button
          type="submit"
          disabled={!text.trim() || disabled}
          className="absolute right-2 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-mono font-semibold text-xs transition-all shadow-md"
        >
          <span>EXEC</span>
          <CornerDownLeft size={11} />
        </button>
      </form>
    </div>
  );
}

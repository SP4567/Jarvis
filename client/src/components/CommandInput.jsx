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
    <div className="w-full space-y-2">
      {/* Quick Suggestion Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs font-mono scrollbar-none">
        <span className="text-[10px] text-slate-500 font-semibold uppercase flex items-center gap-1 flex-shrink-0">
          <Sparkles size={11} className="text-sky-400" /> QUICK DIRECTIVES:
        </span>
        {QUICK_COMMANDS.map((cmd, i) => (
          <button
            key={i}
            onClick={() => handleChipClick(cmd)}
            disabled={disabled}
            className="px-2.5 py-0.5 rounded bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 text-[10px] whitespace-nowrap transition-colors flex-shrink-0"
          >
            {cmd}
          </button>
        ))}
      </div>

      {/* Manual Command Input Bar */}
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <div className="absolute left-3.5 text-slate-400 flex items-center gap-1">
          <Terminal size={14} className="text-sky-400" />
          <span className="text-slate-600 font-mono text-xs">&gt;</span>
        </div>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter command directive for J.A.R.V.I.S. (e.g., 'Check CPU load', 'Isolate endpoint', 'Explain quantum computing')..."
          disabled={disabled}
          className="w-full pl-11 pr-24 py-2.5 rounded-xl bg-slate-950/90 border border-slate-800 focus:border-slate-600 focus:outline-none text-slate-100 placeholder-slate-500 text-xs font-mono transition-colors shadow-inner"
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
          className="absolute right-2 flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200 hover:text-white font-mono font-semibold text-xs transition-colors border border-slate-700"
        >
          <span>EXEC</span>
          <CornerDownLeft size={11} />
        </button>
      </form>
    </div>
  );
}

import React, { useState } from 'react';
import { Sparkles, Maximize2, Mic, Terminal, Shield, Zap, X } from 'lucide-react';

export default function CompactPiPWidget({ state, onExpand, onSendCommand }) {
  const [inputVal, setInputVal] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputVal.trim()) return;
    onSendCommand(inputVal.trim());
    setInputVal('');
  };

  return (
    <div className="fixed top-4 right-4 z-50 font-mono">
      {!isOpen ? (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-700 shadow-xl hover:border-slate-500 text-xs text-slate-200 transition-all backdrop-blur-md"
          title="Open JARVIS PiP Mini-Bar"
        >
          <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse" />
          <span className="font-bold text-[11px] text-sky-300">J.A.R.V.I.S. V2</span>
          <Maximize2 size={12} className="text-slate-400" />
        </button>
      ) : (
        <div className="w-80 bg-slate-900 border border-slate-700 rounded-xl p-3 shadow-2xl space-y-2 backdrop-blur-xl animate-fade-in">
          <div className="flex items-center justify-between pb-1.5 border-b border-slate-800 text-xs">
            <div className="flex items-center gap-1.5 text-sky-300 font-bold">
              <Sparkles size={13} />
              <span>COMPACT COMPANION</span>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={onExpand}
                className="p-1 text-slate-400 hover:text-white rounded"
                title="Expand to Full HUD"
              >
                <Maximize2 size={12} />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 text-slate-400 hover:text-white rounded"
                title="Minimize"
              >
                <X size={13} />
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="relative flex items-center">
            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Directive..."
              className="w-full pl-7 pr-12 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-slate-600"
            />
            <Terminal size={12} className="absolute left-2 text-slate-500" />
            <button
              type="submit"
              className="absolute right-1.5 px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-bold"
            >
              RUN
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

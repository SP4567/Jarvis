import React, { useEffect, useRef, useState } from 'react';
import { Terminal, User, Bot, CheckCircle, ShieldCheck, Copy, Check, Trash2, ArrowUpRight, Cpu } from 'lucide-react';

export default function ActivityFeed({ messages = [] }) {
  const scrollEndRef = useRef(null);
  const [copiedIdx, setCopiedIdx] = useState(null);

  useEffect(() => {
    scrollEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <div className="glass-panel rounded-2xl p-4 border border-cyan-500/20 flex flex-col h-[400px] shadow-2xl relative">
      {/* Tech corner accents */}
      <div className="tech-corner-tl" />
      <div className="tech-corner-tr" />
      <div className="tech-corner-bl" />
      <div className="tech-corner-br" />

      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-cyan-500/15 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Terminal size={15} />
          </div>
          <div>
            <h2 className="text-xs uppercase tracking-widest font-mono text-cyan-300 font-bold">
              LIVE ACTION FEED
            </h2>
            <p className="text-[9px] font-mono text-slate-500">NEURAL TELEMETRY STREAM</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-[10px] font-mono text-cyan-300">
            {messages.length} EVENTS
          </span>
        </div>
      </div>

      {/* Scrollable message container */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1.5 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs font-mono space-y-2">
            <Cpu size={24} className="text-slate-600 animate-pulse" />
            <span>Neural Speech & Command stream awaiting user input, Sir...</span>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={index}
                className={`p-3.5 rounded-xl border text-xs font-mono transition-all group ${
                  isUser
                    ? 'bg-slate-950/90 border-cyan-500/30 text-slate-200 ml-5 shadow-lg'
                    : 'bg-cyan-950/25 border-cyan-500/20 text-cyan-100 mr-3 shadow-md'
                }`}
              >
                {/* Message Header */}
                <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-slate-800/80">
                  <div className="flex items-center gap-2">
                    {isUser ? (
                      <div className="flex items-center gap-1.5 text-cyan-400 font-bold">
                        <div className="w-5 h-5 rounded bg-cyan-500/20 flex items-center justify-center">
                          <User size={12} />
                        </div>
                        <span className="tracking-wide">OPERATOR</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
                        <div className="w-5 h-5 rounded bg-emerald-500/20 flex items-center justify-center">
                          <Bot size={12} />
                        </div>
                        <span className="text-emerald-300 tracking-wide">
                          J.A.R.V.I.S.
                        </span>
                        {msg.agent_used && (
                          <span className="text-[10px] font-normal px-1.5 py-0.2 rounded bg-slate-900 text-cyan-400 border border-cyan-500/30">
                            {msg.agent_used}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[9px] text-slate-500">
                      {msg.timestamp || new Date().toLocaleTimeString()}
                    </span>
                    <button
                      onClick={() => handleCopy(msg.content, index)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white"
                      title="Copy response"
                    >
                      {copiedIdx === index ? <Check size={11} className="text-emerald-400" /> : <Copy size={11} />}
                    </button>
                  </div>
                </div>

                {/* Message Content */}
                <p className="leading-relaxed whitespace-pre-wrap text-[11px] text-slate-200">
                  {msg.content}
                </p>

                {/* Render executed tool badges if available */}
                {msg.actions && msg.actions.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-cyan-900/40 space-y-1.5">
                    <div className="text-[9px] uppercase tracking-wider text-slate-500 font-semibold flex items-center gap-1">
                      <ShieldCheck size={10} className="text-cyan-400" />
                      <span>Executed Protocols:</span>
                    </div>
                    {msg.actions.map((act, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between text-[10px] px-2.5 py-1 rounded bg-black/50 border border-cyan-500/25 text-cyan-300"
                      >
                        <div className="flex items-center gap-1.5">
                          <CheckCircle size={10} className="text-emerald-400 flex-shrink-0" />
                          <span className="font-bold text-slate-300">{act.agent}</span>
                          <span className="text-slate-600">&rarr;</span>
                          <span className="text-amber-300 font-semibold">{act.tool || act.action_executed}</span>
                        </div>
                        <ArrowUpRight size={10} className="text-slate-500" />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
        <div ref={scrollEndRef} />
      </div>
    </div>
  );
}

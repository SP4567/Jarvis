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
    <div className="bg-slate-900/95 rounded-xl p-4 border border-slate-800 flex flex-col h-[400px] shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-slate-800 text-slate-300">
            <Terminal size={14} className="text-sky-400" />
          </div>
          <div>
            <h2 className="text-xs uppercase tracking-wider font-mono text-slate-100 font-bold">
              LIVE ACTION FEED
            </h2>
            <p className="text-[9px] font-mono text-slate-500">NEURAL TELEMETRY STREAM</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-400">
            {messages.length} EVENTS
          </span>
        </div>
      </div>

      {/* Scrollable message container */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 font-mono text-xs">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs font-mono space-y-1.5 text-center p-4">
            <Cpu size={22} className="text-slate-600 mb-1" />
            <span className="text-slate-400 font-medium">Telemetry Stream Idle</span>
            <span className="text-[10px] text-slate-500">Voice directives and subagent activity will stream here in real-time.</span>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={index}
                className={`p-3 rounded-lg border text-xs transition-all group ${
                  isUser
                    ? 'bg-slate-950 border-slate-800 text-slate-200 ml-4'
                    : 'bg-slate-850 border-slate-750 text-slate-200 mr-2'
                }`}
              >
                {/* Message Header */}
                <div className="flex items-center justify-between mb-1.5 pb-1 border-b border-slate-800/60">
                  <div className="flex items-center gap-2">
                    {isUser ? (
                      <div className="flex items-center gap-1.5 text-sky-400 font-semibold text-[11px]">
                        <User size={12} />
                        <span>OPERATOR</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5 text-emerald-400 font-semibold text-[11px]">
                        <Bot size={12} />
                        <span className="text-emerald-300">J.A.R.V.I.S.</span>
                        {msg.agent_used && (
                          <span className="text-[9px] font-normal px-1.5 py-0.2 rounded bg-slate-900 text-slate-300 border border-slate-800">
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
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 hover:bg-slate-800 rounded text-slate-500 hover:text-slate-300"
                      title="Copy response"
                    >
                      {copiedIdx === index ? <Check size={10} className="text-emerald-400" /> : <Copy size={10} />}
                    </button>
                  </div>
                </div>

                {/* Message Content */}
                <p className="leading-relaxed whitespace-pre-wrap text-[11px] text-slate-200">
                  {msg.content}
                </p>

                {/* Render executed tool badges */}
                {msg.actions && msg.actions.length > 0 && (
                  <div className="mt-2 pt-1.5 border-t border-slate-800/80 space-y-1">
                    <div className="text-[9px] uppercase tracking-wider text-slate-500 font-semibold flex items-center gap-1">
                      <ShieldCheck size={10} className="text-slate-400" />
                      <span>Executed Protocols:</span>
                    </div>
                    {msg.actions.map((act, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between text-[10px] px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300"
                      >
                        <div className="flex items-center gap-1.5">
                          <CheckCircle size={10} className="text-emerald-400 flex-shrink-0" />
                          <span className="font-semibold text-slate-300">{act.agent}</span>
                          <span className="text-slate-600">&rarr;</span>
                          <span className="text-sky-300">{act.tool || act.action_executed}</span>
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

import React, { useState } from 'react';
import { Music, Play, Pause, X, ExternalLink, Volume2, Minimize2, Maximize2, Radio } from 'lucide-react';

export default function CyberPlayer({ currentTrack = null, onClose }) {
  const [isMinimized, setIsMinimized] = useState(false);

  if (!currentTrack || !currentTrack.video_id) return null;

  const videoUrl = currentTrack.url || `https://www.youtube.com/watch?v=${currentTrack.video_id}`;
  const embedUrl = `https://www.youtube-nocookie.com/embed/${currentTrack.video_id}?autoplay=1&enablejsapi=1&rel=0`;

  return (
    <div className={`fixed bottom-20 right-6 z-40 transition-all duration-300 ${isMinimized ? 'w-64' : 'w-80 md:w-96'}`}>
      <div className="bg-slate-900/95 rounded-xl border border-slate-800 shadow-2xl overflow-hidden p-3 backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
          <div className="flex items-center gap-2 truncate pr-2">
            <div className="p-1 rounded bg-slate-800 text-sky-400">
              <Music size={13} />
            </div>
            <span className="text-xs font-mono font-bold text-slate-200 truncate">
              {currentTrack.title || "CyberPlayer Audio Stream"}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              title={isMinimized ? "Expand" : "Minimize"}
            >
              {isMinimized ? <Maximize2 size={12} /> : <Minimize2 size={12} />}
            </button>
            <a
              href={videoUrl}
              target="_blank"
              rel="noreferrer"
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              title="Open in YouTube"
            >
              <ExternalLink size={12} />
            </a>
            <button
              onClick={onClose}
              className="p-1 rounded hover:bg-rose-950 text-slate-400 hover:text-rose-400 transition-colors"
              title="Close Player"
            >
              <X size={13} />
            </button>
          </div>
        </div>

        {/* Video Embed Frame */}
        {!isMinimized && (
          <div className="relative w-full aspect-video rounded-lg overflow-hidden border border-slate-800 bg-black shadow-inner">
            <iframe
              src={embedUrl}
              title={currentTrack.title || "YouTube Audio Player"}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
              className="w-full h-full"
            />
          </div>
        )}

        {/* Status Indicator */}
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mt-2">
          <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            AUDIO STREAM
          </span>
          <a
            href={videoUrl}
            target="_blank"
            rel="noreferrer"
            className="text-slate-400 hover:text-slate-200 underline flex items-center gap-1 text-[10px]"
          >
            <span>SOURCE</span>
            <ExternalLink size={9} />
          </a>
        </div>
      </div>
    </div>
  );
}

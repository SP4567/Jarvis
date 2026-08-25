import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Radio, Sparkles, AlertCircle, Play, ShieldAlert, Cpu, Brain, Disc, RefreshCw } from 'lucide-react';
import { playWakeSound, playCommandSendSound } from '../utils/audioEffects';

export default function VoiceController({
  onSendMessage,
  onAudioLevelChange,
  isJarvisSpeaking,
  onInterrupt,
}) {
  // UI Active state
  const [isActive, setIsActive] = useState(false);
  const [continuousMode, setContinuousMode] = useState(true);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [permissionError, setPermissionError] = useState(null);
  const [micVolume, setMicVolume] = useState(0);

  // Callback & State refs (prevents dependency churn & teardown during audio updates)
  const onSendMessageRef = useRef(onSendMessage);
  const onAudioLevelChangeRef = useRef(onAudioLevelChange);
  const onInterruptRef = useRef(onInterrupt);
  const isJarvisSpeakingRef = useRef(isJarvisSpeaking);

  const isActiveRef = useRef(false);
  const continuousModeRef = useRef(true);
  const recognitionRef = useRef(null);
  const restartTimeoutRef = useRef(null);
  const isMountedRef = useRef(true);

  // Web Audio API refs
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const micStreamRef = useRef(null);
  const animFrameRef = useRef(null);

  // Keep callback refs synchronized without triggering re-renders
  useEffect(() => {
    onSendMessageRef.current = onSendMessage;
  }, [onSendMessage]);

  useEffect(() => {
    onAudioLevelChangeRef.current = onAudioLevelChange;
  }, [onAudioLevelChange]);

  useEffect(() => {
    onInterruptRef.current = onInterrupt;
  }, [onInterrupt]);

  useEffect(() => {
    isJarvisSpeakingRef.current = isJarvisSpeaking;
  }, [isJarvisSpeaking]);

  useEffect(() => {
    continuousModeRef.current = continuousMode;
  }, [continuousMode]);

  const quickActions = [
    { label: 'Run SOC Audit', icon: ShieldAlert, prompt: 'run a live security audit on this host', color: 'hover:border-rose-500/50 hover:text-rose-300' },
    { label: 'System Vitals', icon: Cpu, prompt: 'what are my system vitals?', color: 'hover:border-cyan-500/50 hover:text-cyan-300' },
    { label: 'Cyber Music', icon: Disc, prompt: 'play some cyberpunk ambient music', color: 'hover:border-emerald-500/50 hover:text-emerald-300' },
    { label: 'Memory Matrix', icon: Brain, prompt: 'who am I and what do you remember?', color: 'hover:border-amber-500/50 hover:text-amber-300' },
  ];

  // Stop Web Audio Analysis cleanly
  const stopAudioAnalysis = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (micStreamRef.current) {
      try {
        micStreamRef.current.getTracks().forEach((track) => track.stop());
      } catch (e) {}
      micStreamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      try {
        audioContextRef.current.close();
      } catch (e) {}
      audioContextRef.current = null;
    }
    analyserRef.current = null;
    setMicVolume(0);
    if (onAudioLevelChangeRef.current) onAudioLevelChangeRef.current(0);
  }, []);

  // Start Web Audio Frequency & Volume Analysis
  const startAudioAnalysis = useCallback(async () => {
    try {
      if (!micStreamRef.current) {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          },
          video: false
        });
        micStreamRef.current = stream;
      }

      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
        audioContextRef.current = new AudioCtx();
      }
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
      }

      if (!analyserRef.current && audioContextRef.current && micStreamRef.current) {
        const analyser = audioContextRef.current.createAnalyser();
        analyser.fftSize = 128;
        analyser.smoothingTimeConstant = 0.3;
        analyserRef.current = analyser;

        const source = audioContextRef.current.createMediaStreamSource(micStreamRef.current);
        source.connect(analyser);
      }

      if (!analyserRef.current) return;
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

      const updateLevel = () => {
        if (!analyserRef.current || !isActiveRef.current) {
          setMicVolume(0);
          if (onAudioLevelChangeRef.current) onAudioLevelChangeRef.current(0);
          return;
        }

        analyserRef.current.getByteFrequencyData(dataArray);

        let sum = 0;
        let peak = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
          if (dataArray[i] > peak) peak = dataArray[i];
        }
        const avg = sum / dataArray.length;
        const combined = avg * 0.4 + peak * 0.6;
        const normalized = Math.min(100, Math.floor((combined / 65) * 100));

        setMicVolume(normalized);

        if (!isJarvisSpeakingRef.current && onAudioLevelChangeRef.current) {
          onAudioLevelChangeRef.current(normalized);
        }

        animFrameRef.current = requestAnimationFrame(updateLevel);
      };

      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      updateLevel();
    } catch (e) {
      console.warn('[VoiceController] Audio analyzer note:', e);
    }
  }, []);

  // Safely restart recognition when in continuous active mode
  const scheduleRestart = useCallback(() => {
    if (restartTimeoutRef.current) clearTimeout(restartTimeoutRef.current);
    if (!isActiveRef.current || !isMountedRef.current) return;

    restartTimeoutRef.current = setTimeout(() => {
      if (!isActiveRef.current || !isMountedRef.current) return;
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          // Already running
        }
      }
    }, 150);
  }, []);

  // Initialize SpeechRecognition ONCE on mount with zero dependency churn
  useEffect(() => {
    isMountedRef.current = true;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setPermissionError("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setPermissionError(null);
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      if ((interim.trim().length > 1 || final.trim().length > 1) && isJarvisSpeakingRef.current) {
        if (onInterruptRef.current) onInterruptRef.current();
      }

      setInterimTranscript(interim);

      if (interim.trim().length > 0 && !isJarvisSpeakingRef.current && onAudioLevelChangeRef.current) {
        onAudioLevelChangeRef.current(60);
      }

      if (final.trim().length > 0) {
        setInterimTranscript('');
        playCommandSendSound();
        if (onSendMessageRef.current) {
          onSendMessageRef.current(final.trim());
        }
      }
    };

    recognition.onerror = (event) => {
      console.log('[VoiceController] SpeechRecognition notice:', event.error);
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        setPermissionError("Microphone permission denied. Please allow microphone access in your browser bar.");
        isActiveRef.current = false;
        setIsActive(false);
        stopAudioAnalysis();
      } else if (event.error === 'no-speech' || event.error === 'aborted') {
        // Expected browser timeouts handled by onend
      }
    };

    recognition.onend = () => {
      if (isActiveRef.current && continuousModeRef.current && isMountedRef.current) {
        scheduleRestart();
      } else if (!isActiveRef.current) {
        stopAudioAnalysis();
      }
    };

    recognitionRef.current = recognition;

    return () => {
      isMountedRef.current = false;
      isActiveRef.current = false;
      if (restartTimeoutRef.current) clearTimeout(restartTimeoutRef.current);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
      stopAudioAnalysis();
    };
  }, []); // Run ONCE on mount

  // Explicit User Start
  const startListening = async () => {
    setPermissionError(null);
    isActiveRef.current = true;
    setIsActive(true);
    playWakeSound();

    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch (e) {
        // If already started, proceed
      }
    }
    await startAudioAnalysis();
  };

  // Explicit User Stop
  const stopListening = () => {
    isActiveRef.current = false;
    setIsActive(false);
    setInterimTranscript('');
    if (restartTimeoutRef.current) clearTimeout(restartTimeoutRef.current);

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        try {
          recognitionRef.current.abort();
        } catch (e2) {}
      }
    }
    stopAudioAnalysis();
  };

  // Toggle button clicked by user
  const toggleMic = () => {
    if (isActive) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="flex flex-col items-center gap-3.5 w-full max-w-lg z-20">
      {/* Live Interim Transcript or Speaking Status */}
      <div className="min-h-[42px] px-4 py-2 rounded-xl bg-slate-950/85 border border-cyan-500/30 backdrop-blur-md flex items-center justify-center text-center shadow-lg w-full transition-all">
        {interimTranscript ? (
          <p className="text-xs font-mono text-cyan-300 flex items-center gap-2 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,1)]" />
            "{interimTranscript}"
          </p>
        ) : isJarvisSpeaking ? (
          <p className="text-xs font-mono text-emerald-300 flex items-center gap-2">
            <Volume2 size={14} className="text-emerald-400 animate-bounce" />
            <span>JARVIS Vocalizing... (Click Mic or Speak to Interrupt)</span>
          </p>
        ) : isActive ? (
          <p className="text-xs font-mono text-cyan-300 flex items-center gap-2">
            <Radio size={13} className="text-cyan-400 animate-pulse" />
            <span>Voice Uplink Active // Speak "Hey JARVIS" or any command...</span>
          </p>
        ) : (
          <p className="text-xs font-mono text-slate-500">
            Voice Uplink Muted. Click microphone to activate voice commands.
          </p>
        )}
      </div>

      {/* Voice Controls Pill */}
      <div className="flex items-center gap-3 p-1.5 rounded-full bg-slate-950/90 border border-cyan-500/35 backdrop-blur-xl shadow-[0_0_30px_rgba(6,182,212,0.2)]">
        {/* Main Microphone Button with Real-Time Audio Ripple */}
        <button
          onClick={toggleMic}
          className={`relative p-3.5 rounded-full transition-all duration-200 flex items-center justify-center cursor-pointer ${
            isActive
              ? 'bg-cyan-500 text-slate-950 shadow-[0_0_25px_rgba(6,182,212,0.95)] hover:scale-105 active:scale-95'
              : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-700 hover:border-cyan-500/50 hover:bg-slate-800 active:scale-95'
          }`}
          title={isActive ? 'Click to Mute Voice' : 'Click to Activate Voice'}
        >
          {/* Dynamic Audio Level Ripple Indicator */}
          {isActive && (
            <span
              style={{
                transform: `scale(${1.0 + (micVolume / 100) * 0.8})`,
                opacity: 0.25 + (micVolume / 100) * 0.5
              }}
              className="absolute inset-0 rounded-full bg-cyan-400 pointer-events-none transition-transform duration-75"
            />
          )}
          {isActive ? <Mic size={20} className="relative z-10" /> : <MicOff size={20} className="relative z-10" />}
        </button>

        {/* Continuous Mode Toggle */}
        <button
          onClick={() => {
            const next = !continuousMode;
            setContinuousMode(next);
            continuousModeRef.current = next;
          }}
          className={`px-3 py-1.5 rounded-full text-xs font-mono font-bold transition-all cursor-pointer ${
            continuousMode
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
              : 'text-slate-500 hover:text-slate-300 border border-transparent'
          }`}
          title="Toggle Continuous Hands-Free Listening"
        >
          AUTO-LISTEN: {continuousMode ? 'ON' : 'OFF'}
        </button>

        {/* Interrupt Button (Visible during speech) */}
        {isJarvisSpeaking && (
          <button
            onClick={onInterrupt}
            className="px-3.5 py-1.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 text-xs font-mono font-bold flex items-center gap-1 transition-all animate-pulse cursor-pointer"
          >
            <VolumeX size={13} />
            INTERRUPT
          </button>
        )}
      </div>

      {/* Quick Voice Prompt Suggestions */}
      <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
        {quickActions.map((qa, idx) => {
          const Icon = qa.icon;
          return (
            <button
              key={idx}
              onClick={() => onSendMessage(qa.prompt)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-950/70 border border-slate-800 text-[11px] font-mono text-slate-400 transition-all ${qa.color} hover:bg-slate-900 shadow-sm cursor-pointer`}
            >
              <Icon size={12} className="text-cyan-400" />
              <span>{qa.label}</span>
            </button>
          );
        })}
      </div>

      {/* Permission Error Banner with Retry */}
      {permissionError && (
        <div className="flex items-center justify-between gap-3 p-2.5 rounded-lg bg-rose-950/70 border border-rose-500/40 text-rose-300 text-xs font-mono w-full">
          <div className="flex items-center gap-2">
            <AlertCircle size={15} className="text-rose-400 flex-shrink-0" />
            <span>{permissionError}</span>
          </div>
          <button
            onClick={startListening}
            className="flex items-center gap-1 px-2 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 border border-rose-500/40 text-[10px] cursor-pointer"
          >
            <RefreshCw size={11} /> RETRY
          </button>
        </div>
      )}
    </div>
  );
}

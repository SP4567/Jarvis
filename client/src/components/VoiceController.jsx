import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Radio, Sparkles, AlertCircle, Play, ShieldAlert, Cpu, Brain, Disc, RefreshCw } from 'lucide-react';
import { playWakeSound, playCommandSendSound } from '../utils/audioEffects';

export default function VoiceController({
  onSendMessage,
  onAudioLevelChange,
  isJarvisSpeaking,
  onInterrupt,
}) {
  const [isActive, setIsActive] = useState(false);
  const [continuousMode, setContinuousMode] = useState(true);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [permissionError, setPermissionError] = useState(null);
  const [micVolume, setMicVolume] = useState(0);

  const onSendMessageRef = useRef(onSendMessage);
  const onAudioLevelChangeRef = useRef(onAudioLevelChange);
  const onInterruptRef = useRef(onInterrupt);
  const isJarvisSpeakingRef = useRef(isJarvisSpeaking);

  const isActiveRef = useRef(false);
  const continuousModeRef = useRef(true);
  const recognitionRef = useRef(null);
  const restartTimeoutRef = useRef(null);
  const isMountedRef = useRef(true);

  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const micStreamRef = useRef(null);
  const animFrameRef = useRef(null);

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
    { label: 'Run SOC Audit', icon: ShieldAlert, prompt: 'run a live security audit on this host' },
    { label: 'System Vitals', icon: Cpu, prompt: 'what are my system vitals?' },
    { label: 'Cyber Music', icon: Disc, prompt: 'play some cyberpunk ambient music' },
    { label: 'Memory Matrix', icon: Brain, prompt: 'who am I and what do you remember?' },
  ];

  const silenceTimerRef = useRef(null);
  const lastTranscriptRef = useRef('');

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

      const source = audioContextRef.current.createMediaStreamSource(micStreamRef.current);
      const analyser = audioContextRef.current.createAnalyser();
      analyser.fftSize = 64;
      analyser.smoothingTimeConstant = 0.6;
      source.connect(analyser);
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const updateVolume = () => {
        if (!analyserRef.current || !isActiveRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        const normalized = Math.min(100, Math.floor((avg / 128) * 100));

        setMicVolume(normalized);
        if (onAudioLevelChangeRef.current && !isJarvisSpeakingRef.current) {
          onAudioLevelChangeRef.current(normalized);
        }

        animFrameRef.current = requestAnimationFrame(updateVolume);
      };

      updateVolume();
    } catch (err) {
      console.warn('Microphone stream access error:', err);
    }
  }, []);

  const initRecognition = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setPermissionError('Web Speech API is not supported in this browser. Please use Chrome or Edge.');
      return null;
    }

    const rec = new SpeechRecognition();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = 'en-US';

    rec.onstart = () => {
      setPermissionError(null);
    };

    rec.onresult = (event) => {
      let finalTranscript = '';
      let interim = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }

      const currentText = (finalTranscript || interim).trim();
      setInterimTranscript(currentText);
      lastTranscriptRef.current = currentText;

      if (currentText.length > 0 && isJarvisSpeakingRef.current) {
        if (onInterruptRef.current) onInterruptRef.current();
      }

      if (finalTranscript.trim()) {
        const textToSend = finalTranscript.trim();
        setInterimTranscript('');
        lastTranscriptRef.current = '';
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        playCommandSendSound();
        if (onSendMessageRef.current) onSendMessageRef.current(textToSend);
      } else if (interim.trim()) {
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = setTimeout(() => {
          if (lastTranscriptRef.current.trim()) {
            const textToSend = lastTranscriptRef.current.trim();
            setInterimTranscript('');
            lastTranscriptRef.current = '';
            playCommandSendSound();
            if (onSendMessageRef.current) onSendMessageRef.current(textToSend);
          }
        }, 1600);
      }
    };

    rec.onerror = (event) => {
      if (event.error === 'no-speech') return;
      if (event.error === 'not-allowed') {
        setPermissionError('Microphone access denied. Please allow microphone permission in your browser.');
        setIsActive(false);
        isActiveRef.current = false;
        stopAudioAnalysis();
      }
    };

    rec.onend = () => {
      if (isActiveRef.current && continuousModeRef.current && isMountedRef.current) {
        restartTimeoutRef.current = setTimeout(() => {
          if (isActiveRef.current && recognitionRef.current) {
            try {
              recognitionRef.current.start();
            } catch (e) {}
          }
        }, 300);
      } else {
        setIsActive(false);
        isActiveRef.current = false;
        stopAudioAnalysis();
      }
    };

    return rec;
  }, [stopAudioAnalysis]);

  const toggleListening = useCallback(async () => {
    if (isActive) {
      setIsActive(false);
      isActiveRef.current = false;
      if (restartTimeoutRef.current) clearTimeout(restartTimeoutRef.current);
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      stopAudioAnalysis();
    } else {
      setPermissionError(null);
      if (!recognitionRef.current) {
        recognitionRef.current = initRecognition();
      }

      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
          setIsActive(true);
          isActiveRef.current = true;
          playWakeSound();
          startAudioAnalysis();
        } catch (e) {
          console.warn('Recognition start exception:', e);
        }
      }
    }
  }, [isActive, initRecognition, startAudioAnalysis, stopAudioAnalysis]);

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (restartTimeoutRef.current) clearTimeout(restartTimeoutRef.current);
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
      stopAudioAnalysis();
    };
  }, [stopAudioAnalysis]);

  return (
    <div className="flex flex-col items-center gap-3 w-full max-w-lg">
      {/* Mic State & Control Button */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggleListening}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all ${
            isActive
              ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-md'
              : 'bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700'
          }`}
        >
          {isActive ? <Mic size={15} className="animate-pulse" /> : <MicOff size={15} className="text-slate-400" />}
          <span>{isActive ? 'LISTENING (VAD ACTIVE)' : 'ENABLE VOICE COMMAND'}</span>
        </button>

        {isJarvisSpeaking && (
          <button
            onClick={onInterrupt}
            className="flex items-center gap-1 px-3 py-2 rounded-xl bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-300 text-xs font-mono font-semibold transition-all"
            title="Interrupt JARVIS Speech"
          >
            <VolumeX size={14} />
            <span>INTERRUPT</span>
          </button>
        )}
      </div>

      {/* Interim Speech Preview */}
      {interimTranscript && (
        <div className="w-full px-3.5 py-2 rounded-lg bg-slate-950/90 border border-slate-800 text-xs font-mono text-slate-200 text-center shadow-inner">
          <span className="text-slate-500 uppercase font-semibold text-[10px] mr-1.5">&gt; HEARD:</span>
          "{interimTranscript}"
        </div>
      )}

      {/* Permission Warning */}
      {permissionError && (
        <div className="flex items-center gap-2 text-[11px] font-mono text-rose-400 bg-rose-950/60 p-2 rounded-lg border border-rose-800/40">
          <AlertCircle size={14} className="shrink-0" />
          <span>{permissionError}</span>
        </div>
      )}

      {/* Quick Voice Directive Shortcuts */}
      <div className="flex items-center gap-1.5 flex-wrap justify-center pt-1">
        {quickActions.map((act, i) => {
          const Icon = act.icon;
          return (
            <button
              key={i}
              onClick={() => {
                playCommandSendSound();
                if (onSendMessageRef.current) onSendMessageRef.current(act.prompt);
              }}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 text-[11px] font-mono transition-colors"
            >
              <Icon size={12} className="text-slate-400" />
              <span>{act.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

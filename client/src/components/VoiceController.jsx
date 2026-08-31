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
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.8;
      source.connect(analyser);
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const updateVolume = () => {
        if (!analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        const normalized = Math.min(100, Math.round((avg / 128) * 100));

        setMicVolume(normalized);
        if (onAudioLevelChangeRef.current && !isJarvisSpeakingRef.current) {
          onAudioLevelChangeRef.current(normalized);
        }

        animFrameRef.current = requestAnimationFrame(updateVolume);
      };

      updateVolume();
    } catch (err) {
      console.warn('Audio analysis init error:', err);
    }
  }, []);

  const triggerCommand = useCallback((finalText) => {
    const clean = finalText.trim();
    if (!clean) return;

    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    setInterimTranscript('');
    lastTranscriptRef.current = '';

    playCommandSendSound();
    if (onSendMessageRef.current) {
      onSendMessageRef.current(clean);
    }
  }, []);

  const handleSpeechResult = useCallback((event) => {
    let interim = '';
    let final = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const trans = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        final += trans;
      } else {
        interim += trans;
      }
    }

    if (isJarvisSpeakingRef.current && (interim.length > 3 || final.length > 0)) {
      if (onInterruptRef.current) onInterruptRef.current();
    }

    if (interim) {
      setInterimTranscript(interim);
      lastTranscriptRef.current = interim;

      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = setTimeout(() => {
        if (lastTranscriptRef.current) {
          triggerCommand(lastTranscriptRef.current);
        }
      }, 1400);
    }

    if (final) {
      triggerCommand(final);
    }
  }, [triggerCommand]);

  const initRecognition = useCallback(() => {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
      setPermissionError('Web Speech API is not supported in this browser. Please use Chrome/Edge.');
      return null;
    }

    const rec = new SpeechRec();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = 'en-US';

    rec.onresult = handleSpeechResult;

    rec.onerror = (event) => {
      if (event.error === 'not-allowed') {
        setPermissionError('Microphone access was denied. Please allow microphone permissions.');
        setIsActive(false);
        isActiveRef.current = false;
        stopAudioAnalysis();
      }
    };

    rec.onend = () => {
      if (isActiveRef.current && continuousModeRef.current && isMountedRef.current) {
        restartTimeoutRef.current = setTimeout(() => {
          try {
            rec.start();
          } catch (e) {}
        }, 300);
      } else {
        setIsActive(false);
        isActiveRef.current = false;
        stopAudioAnalysis();
      }
    };

    return rec;
  }, [handleSpeechResult, stopAudioAnalysis]);

  const toggleMic = useCallback(async () => {
    if (isActive) {
      setIsActive(false);
      isActiveRef.current = false;
      if (restartTimeoutRef.current) clearTimeout(restartTimeoutRef.current);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      stopAudioAnalysis();
    } else {
      setPermissionError(null);
      playWakeSound();
      if (!recognitionRef.current) {
        recognitionRef.current = initRecognition();
      }

      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
          setIsActive(true);
          isActiveRef.current = true;
          startAudioAnalysis();
        } catch (e) {
          console.warn('Recognition start error:', e);
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
      stopAudioAnalysis();
    };
  }, [stopAudioAnalysis]);

  return (
    <div className="flex flex-col items-center gap-3 w-full max-w-md mx-auto font-mono">
      {/* Live Speech Recognition Waveform & Button */}
      <div className="flex items-center gap-3 bg-slate-900/80 backdrop-blur-md px-4 py-2 rounded-full border border-white/[0.08] shadow-lg">
        <button
          onClick={toggleMic}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide transition-all ${
            isActive
              ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-500/20 shadow-md animate-pulse'
              : 'bg-slate-800 hover:bg-slate-750 text-slate-200 border border-white/[0.06]'
          }`}
        >
          {isActive ? <Mic size={14} /> : <MicOff size={14} />}
          <span>{isActive ? 'MIC LISTENING' : 'ACTIVATE VOICE'}</span>
        </button>

        {/* Audio Level Meter */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-500">LEVEL:</span>
          <div className="w-16 bg-slate-950 h-2 rounded-full overflow-hidden border border-white/[0.04]">
            <div
              className="h-full bg-gradient-to-r from-sky-400 to-emerald-400 rounded-full transition-all duration-100"
              style={{ width: `${isActive ? Math.max(8, micVolume) : 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Interim Live Transcript Indicator */}
      {interimTranscript && (
        <div className="text-[11px] text-sky-300 bg-slate-950/80 border border-sky-500/30 px-3 py-1 rounded-lg animate-fade-in text-center max-w-sm">
          "{interimTranscript}..."
        </div>
      )}

      {/* Permission Warning */}
      {permissionError && (
        <div className="text-[10px] text-rose-300 bg-rose-950/60 border border-rose-800 px-3 py-1 rounded-lg text-center">
          {permissionError}
        </div>
      )}
    </div>
  );
}

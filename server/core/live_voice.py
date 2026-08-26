import io
import asyncio
import base64
import edge_tts
from typing import Optional, AsyncGenerator
from server.config import settings

class VoiceEngine:
    """
    JARVIS High-Fidelity Voice Synthesis & Live Audio Streaming Hub
    """
    def __init__(self):
        self.voice = settings.TTS_VOICE
        self.rate = settings.TTS_RATE
        self.pitch = settings.TTS_PITCH

    async def synthesize_speech_bytes(self, text: str) -> bytes:
        """
        Synthesizes text into high quality audio bytes using Edge TTS (en-GB-RyanNeural for JARVIS persona).
        Guarded with 4.0s timeout to prevent network stalls.
        """
        clean_text = self._sanitize_text_for_speech(text)
        if not clean_text:
            return b""

        async def _synthesize():
            communicate = edge_tts.Communicate(
                text=clean_text,
                voice=self.voice,
                rate=self.rate,
                pitch=self.pitch
            )
            audio_stream = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_stream.write(chunk["data"])
            return audio_stream.getvalue()

        try:
            return await asyncio.wait_for(_synthesize(), timeout=4.0)
        except asyncio.TimeoutError:
            print("[VoiceEngine] Edge TTS synthesis timed out after 4.0s - falling back to browser SpeechSynthesis.")
            return b""
        except Exception as e:
            print(f"[VoiceEngine] Edge TTS synthesis error: {e}")
            return b""

    async def synthesize_speech_base64(self, text: str) -> Optional[str]:
        """Returns base64 encoded audio for immediate WebSocket browser playback, or None if TTS failed"""
        audio_bytes = await self.synthesize_speech_bytes(text)
        if not audio_bytes:
            return None
        return base64.b64encode(audio_bytes).decode("utf-8")

    async def stream_audio_chunks(self, text: str) -> AsyncGenerator[bytes, None]:
        """Streams audio chunks in real-time for low latency audio playback"""
        clean_text = self._sanitize_text_for_speech(text)
        communicate = edge_tts.Communicate(
            text=clean_text,
            voice=self.voice,
            rate=self.rate,
            pitch=self.pitch
        )
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    def _sanitize_text_for_speech(self, text: str) -> str:
        """Strips markdown bold, bullets, links, and code blocks for smooth speech"""
        import re
        t = re.sub(r'```[\s\S]*?```', ' Code block omitted for brevity. ', text)
        t = re.sub(r'`([^`]+)`', r'\1', t)
        t = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', t)
        t = re.sub(r'[*_#>\-~]', ' ', t)
        t = re.sub(r'\s+', ' ', t).strip()
        return t

voice_engine = VoiceEngine()

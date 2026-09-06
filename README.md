# ⚡ J.A.R.V.I.S. Autonomous AI Engine

An end-to-end autonomous AI assistant featuring **live conversational voice interaction**, an Iron Man-inspired **Sci-Fi HUD** with an animated **Holographic Arc Reactor**, a **multi-agent orchestration matrix** for daily desktop tasks, and **3-Tier security guardrails** with human-in-the-loop interlocks.

---

## 🌟 Key Features

1. **Live Bidirectional Voice & Speech Interruption**:
   - Continuous listening & Push-to-Talk with Web Audio Voice Activity Detection (VAD).
   - Real-time speech synthesis in a refined British JARVIS persona (`en-GB-RyanNeural`).
   - Instant interruption: Speaking over JARVIS halts audio playback immediately.
   - Dual Mode: Powered by Gemini Live API / Gemini 2.5/3.x SDK with instant local fallback mode for zero-setup execution.

2. **Futuristic Sci-Fi HUD Interface**:
   - **Holographic Arc Reactor Canvas**: Dynamic WebGL/Canvas audio visualizer reacting in real time to voice frequency, thinking, speaking, and alert states.
   - **Autonomous Subagent Matrix**: Live status monitor for 6 specialist agents with telemetry, tool counts, and latency tracking.
   - **Hardware Telemetry Panel**: Real-time CPU load, memory utilization, disk C: capacity, and power/battery status.
   - **Live Action Stream**: Scrolling HUD terminal displaying conversational dialogue, agent routing decisions, and executed tool cards.

3. **Autonomous Specialist Subagents**:
   - **🖥️ System & OS Controller**: Application launcher (Chrome, VS Code, Notepad, Spotify, etc.), system volume & mute controls, process inspector & killer, safe terminal runner.
   - **🌐 Web Intelligence & Research**: Live internet searches, breaking news retrieval, weather forecasts, Wikipedia summaries.
   - **📅 Productivity & Daily Ops**: Personal notes, to-do reminders, alarms, and daily agenda briefings.
   - **🎵 Media & Entertainment**: YouTube search & playback, Spotify player integration, system media keys (play/pause/next/prev).
   - **👁️ Multimodal Vision & Screen**: Desktop screen capture & AI visual inspection with Gemini Vision.
   - **💻 Developer & Code Assistant**: Python sandbox code execution, Git status inspector.

4. **3-Tier Security Guardrail Interlock**:
   - **Tier 1 (Safe / Read-only)**: Search, weather, system vitals, reading notes & schedule -> Auto-approved.
   - **Tier 2 (Sensitive / Modifying)**: Launching apps, adding notes, setting alarms, volume change -> Auto-approved with audit logging.
   - **Tier 3 (Dangerous / Destructive)**: File deletion, process termination, arbitrary shell command execution -> **Requires explicit Human-in-the-Loop approval** via glowing red HUD security modal or voice confirmation (*"JARVIS, authorize"* / *"JARVIS, abort"*).
   - **Blocked Tier**: Absolute blacklist preventing system wipe commands (`del C:\Windows`, `format`, fork bombs).

---

## 🚀 Quick Start (One-Click Launch)

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

### Start JARVIS
Simply double-click or run:
```bash
# Windows Batch
run.bat

# Or PowerShell
.\run.ps1
```

This will automatically start:
- **Backend API & WebSockets**: `http://localhost:8000`
- **Sci-Fi HUD Web Client**: `http://localhost:3000`

---

## 🗣️ Example Voice & Text Commands

Try speaking or typing any of the following to JARVIS:

- **System Diagnostics**: *"JARVIS, what are my system vitals?"*
- **App Launching**: *"Open Google Chrome"* or *"Launch VS Code"*
- **Media Playback**: *"Play synthwave on YouTube"* or *"Search Spotify for Daft Punk"*
- **Weather Telemetry**: *"What is the weather in Tokyo?"*
- **Productivity**: *"Remind me to call Tony Stark at 6 PM"* or *"Save note: Project roadmap approved"*
- **Daily Agenda**: *"Give me a daily briefing"*
- **Screen Inspection**: *"Inspect current screen"*
- **Media Controls**: *"Pause playback"* or *"Mute audio"*
- **Security Interlocks**: *"Kill process notepad.exe"* (Triggers Tier 3 Security Modal)
- **Voice Authorizations**: *"JARVIS, authorize"* or *"JARVIS, abort"*

---

## ⚙️ Configuration (`server/.env`)

Edit `server/.env` to customize settings:

```env
# Gemini API Key (Enables multimodal vision and advanced LLM tool reasoning)
GEMINI_API_KEY=your_gemini_api_key_here

# Voice Persona
JARVIS_TTS_VOICE=en-GB-RyanNeural
JARVIS_TTS_RATE=+5%

# Security Guardrail Strictness (strict | normal | relaxed)
GUARDRAIL_STRICTNESS=strict
AUTO_APPROVE_TIER2=true
```

---

## 🧪 Running Tests

```bash
$env:PYTHONPATH="."
python -m pytest server/tests/test_jarvis.py -v
```

# Made with love, by Suyash Pandey.

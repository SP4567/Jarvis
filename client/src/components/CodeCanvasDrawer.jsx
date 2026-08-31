import React, { useState } from 'react';
import { Terminal, Play, CheckCircle2, AlertCircle, X, Copy, Check, Sparkles, RefreshCw } from 'lucide-react';

export default function CodeCanvasDrawer({ isOpen, onClose }) {
  const [code, setCode] = useState(`def calculate_entropy(data_bytes: bytes) -> float:
    """Calculates Shannon entropy of executable bytes."""
    import math
    if not data_bytes:
        return 0.0
    entropy = 0.0
    for x in range(256):
        p_x = float(data_bytes.count(bytes([x]))) / len(data_bytes)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return round(entropy, 4)

# Test invocation:
sample_bytes = b"\\x90\\x90\\x90\\xcc\\x48\\x89\\xe5"
print(f"Sample Section Entropy: {calculate_entropy(sample_bytes)}")
`);
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleRunCode = async () => {
    setIsRunning(true);
    setOutput('Compiling and executing in isolated AST sandbox...');
    const startTime = performance.now();

    try {
      const res = await fetch('http://127.0.0.1:8000/api/code/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });

      const elapsed = (performance.now() - startTime).toFixed(1);

      if (res.ok) {
        const data = await res.json();
        const stdout = data.stdout || '';
        const stderr = data.stderr || '';
        const isSuccess = data.success !== false && data.exit_code === 0;

        let statusHeader = isSuccess
          ? `>>> AST Verification: PASSED (Zero security violations)\n>>> Process exited with code 0 (Execution Time: ${elapsed}ms)\n`
          : `>>> AST / Runtime Result (Exit Code: ${data.exit_code}):\n`;

        setOutput(statusHeader + (stdout || stderr || 'Code executed successfully (no stdout returned).'));
      } else {
        setOutput('>>> Error: Failed to communicate with sandbox runtime backend.');
      }
    } catch (e) {
      setOutput(`>>> Sandbox Execution Error: ${e.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full md:w-[600px] bg-slate-900 border-l border-slate-800 backdrop-blur-xl shadow-2xl flex flex-col font-mono">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-950/80">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-sky-400" />
          <div>
            <h3 className="text-sm font-bold text-slate-100 tracking-wider">
              CODE CANVAS // SANDBOX IDE
            </h3>
            <p className="text-[10px] text-slate-400">Live AST-Validated Execution & Dynamic Synthesis</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Editor Toolbar */}
      <div className="flex items-center justify-between px-5 py-2 bg-slate-950/40 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">Python 3.11</span>
          <span className="text-slate-500 text-[11px]">Sandboxed Interpreter</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-750 text-slate-300 text-[11px] transition-colors"
          >
            {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
          <button
            onClick={handleRunCode}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-3.5 py-1 rounded bg-sky-600 hover:bg-sky-500 text-white text-[11px] font-bold transition-colors disabled:opacity-50"
          >
            <Play size={12} />
            <span>{isRunning ? 'Running...' : 'Run Sandbox'}</span>
          </button>
        </div>
      </div>

      {/* Editor Area */}
      <div className="flex-1 p-4 bg-slate-950 flex flex-col space-y-3 overflow-hidden">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="w-full flex-1 bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-slate-700 resize-none leading-relaxed font-mono"
          spellCheck={false}
        />

        {/* Sandbox Output Terminal */}
        <div className="h-44 bg-black/90 border border-slate-800 rounded-lg p-3 overflow-y-auto space-y-1 text-xs">
          <div className="flex items-center justify-between text-[10px] text-slate-500 border-b border-slate-900 pb-1 mb-1">
            <span>TERMINAL OUTPUT</span>
            <span className="text-emerald-400">ACTIVE</span>
          </div>
          <pre className="text-slate-300 whitespace-pre-wrap text-[11px] leading-relaxed">
            {output || "Press 'Run Sandbox' to execute script safely in AST sandbox."}
          </pre>
        </div>
      </div>
    </div>
  );
}

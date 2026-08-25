import React, { useState, useEffect } from 'react';
import { Database, Plus, Trash2, Search, Brain, History, Sparkles, X, ShieldCheck } from 'lucide-react';

export default function SmartMemoryModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('FACTS'); // 'FACTS' | 'ACTIONS'
  const [facts, setFacts] = useState([]);
  const [actions, setActions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [newCategory, setNewCategory] = useState('user_preference');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchFacts();
      fetchActions();
    }
  }, [isOpen]);

  const fetchFacts = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://127.0.0.1:8000/api/memory/facts');
      if (res.ok) {
        const data = await res.json();
        setFacts(data);
      }
    } catch (e) {
      console.error('Error fetching facts:', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchActions = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/memory/actions?limit=20');
      if (res.ok) {
        const data = await res.json();
        setActions(data);
      }
    } catch (e) {
      console.error('Error fetching episodic actions:', e);
    }
  };

  const handleAddFact = async (e) => {
    e.preventDefault();
    if (!newKey.trim() || !newValue.trim()) return;

    try {
      const res = await fetch('http://127.0.0.1:8000/api/memory/facts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: newCategory,
          key: newKey.trim(),
          value: newValue.trim()
        })
      });
      if (res.ok) {
        setNewKey('');
        setNewValue('');
        fetchFacts();
      }
    } catch (e) {
      console.error('Error saving fact:', e);
    }
  };

  const handleDeleteFact = async (key) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/memory/facts/${encodeURIComponent(key)}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        fetchFacts();
      }
    } catch (e) {
      console.error('Error deleting fact:', e);
    }
  };

  if (!isOpen) return null;

  const filteredFacts = facts.filter(
    (f) =>
      f.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.value.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-fade-in">
      <div className="w-full max-w-4xl bg-slate-900 border border-cyan-500/40 rounded-xl shadow-[0_0_50px_rgba(6,182,212,0.15)] flex flex-col max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-cyan-500/20 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Brain className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-cyan-300 tracking-wider flex items-center gap-2">
                SMART MEMORY MATRIX
                <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-mono">
                  v2.0 ACTIVE
                </span>
              </h2>
              <p className="text-xs text-slate-400 font-mono">Multi-Tier Permanent Semantic Facts & Episodic Action Logs</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between px-6 py-3 border-b border-slate-800 bg-slate-900/40">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('FACTS')}
              className={`px-4 py-1.5 rounded-lg text-xs font-mono font-semibold flex items-center gap-2 transition-all ${
                activeTab === 'FACTS'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                  : 'text-slate-400 hover:text-slate-200 border border-transparent'
              }`}
            >
              <Database className="w-3.5 h-3.5" />
              SEMANTIC FACTS ({facts.length})
            </button>
            <button
              onClick={() => setActiveTab('ACTIONS')}
              className={`px-4 py-1.5 rounded-lg text-xs font-mono font-semibold flex items-center gap-2 transition-all ${
                activeTab === 'ACTIONS'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                  : 'text-slate-400 hover:text-slate-200 border border-transparent'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              EPISODIC AUDIT LOG ({actions.length})
            </button>
          </div>

          {activeTab === 'FACTS' && (
            <div className="relative w-64">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search memory facts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-8 pr-3 py-1 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          )}
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {activeTab === 'FACTS' ? (
            <>
              {/* Add Fact Form */}
              <form onSubmit={handleAddFact} className="bg-slate-950/60 border border-cyan-500/20 rounded-lg p-3 grid grid-cols-12 gap-2 items-center">
                <div className="col-span-3">
                  <input
                    type="text"
                    placeholder="Key (e.g. user_name)"
                    value={newKey}
                    onChange={(e) => setNewKey(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 font-mono focus:outline-none"
                  />
                </div>
                <div className="col-span-5">
                  <input
                    type="text"
                    placeholder="Value (e.g. Suyash Pandey)"
                    value={newValue}
                    onChange={(e) => setNewValue(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 font-mono focus:outline-none"
                  />
                </div>
                <div className="col-span-2">
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1.5 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500"
                  >
                    <option value="identity">Identity</option>
                    <option value="user_preference">Preference</option>
                    <option value="project">Project</option>
                    <option value="system">System</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <button
                    type="submit"
                    className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs py-1.5 rounded flex items-center justify-center gap-1 transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    STORE
                  </button>
                </div>
              </form>

              {/* Facts Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {filteredFacts.map((fact) => (
                  <div
                    key={fact.id || fact.key}
                    className="bg-slate-950/80 border border-slate-800 hover:border-cyan-500/40 rounded-lg p-3.5 flex flex-col justify-between transition-all group"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
                          {fact.key}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                          {fact.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-200 font-mono break-words">{fact.value}</p>
                    </div>
                    <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-900 text-[10px] text-slate-500 font-mono">
                      <span>Hits: {fact.access_count || 1}</span>
                      <button
                        onClick={() => handleDeleteFact(fact.key)}
                        className="text-slate-600 hover:text-red-400 transition-colors p-1 rounded"
                        title="Delete fact"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {filteredFacts.length === 0 && (
                <div className="text-center py-10 text-slate-500 text-xs font-mono">
                  No memory facts found matching your search.
                </div>
              )}
            </>
          ) : (
            /* Episodic Actions Table */
            <div className="space-y-2">
              {actions.map((act, idx) => (
                <div
                  key={idx}
                  className="bg-slate-950 border border-slate-800/80 rounded-lg p-3 flex items-center justify-between text-xs font-mono hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <ShieldCheck className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-200">{act.tool_name}</span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-cyan-400">
                          {act.agent_name}
                        </span>
                        <span className="text-[10px] text-slate-500">
                          {new Date(act.timestamp * 1000).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 truncate max-w-lg mt-0.5">
                        Params: {act.params}
                      </p>
                    </div>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">
                    {act.status || 'SUCCESS'}
                  </span>
                </div>
              ))}
              {actions.length === 0 && (
                <div className="text-center py-10 text-slate-500 text-xs font-mono">
                  No episodic actions recorded yet.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between text-xs font-mono text-slate-500">
          <div className="flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Auto-extracts facts from natural voice utterances (e.g. "Remember my name is Suyash")
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono font-bold transition-colors"
          >
            CLOSE
          </button>
        </div>
      </div>
    </div>
  );
}

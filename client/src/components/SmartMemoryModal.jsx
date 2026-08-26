import React, { useState, useEffect } from 'react';
import { Database, Plus, Trash2, Search, Brain, History, Sparkles, X, ShieldCheck } from 'lucide-react';

export default function SmartMemoryModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('FACTS');
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-slate-800 text-sky-400">
              <Brain size={16} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-100 font-mono tracking-wider">
                SMART MEMORY MATRIX
              </h2>
              <p className="text-[10px] text-slate-400 font-mono">
                Long-Term Semantic & Episodic Knowledge Graph
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Tab Selector & Search */}
        <div className="flex items-center justify-between px-5 py-2.5 bg-slate-950/40 border-b border-slate-800 gap-4">
          <div className="flex items-center gap-1 text-xs font-mono">
            <button
              onClick={() => setActiveTab('FACTS')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'FACTS'
                  ? 'bg-slate-800 text-white font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Database size={13} />
              <span>Declarative Facts ({facts.length})</span>
            </button>
            <button
              onClick={() => setActiveTab('ACTIONS')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'ACTIONS'
                  ? 'bg-slate-800 text-white font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <History size={13} />
              <span>Episodic Log ({actions.length})</span>
            </button>
          </div>

          <div className="relative w-64">
            <Search size={13} className="absolute left-2.5 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search memory..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-7 pr-3 py-1 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-slate-600"
            />
          </div>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto p-5 font-mono text-xs space-y-4">
          {activeTab === 'FACTS' && (
            <>
              {/* Add Fact Form */}
              <form onSubmit={handleAddFact} className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
                <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider flex items-center gap-1">
                  <Plus size={11} className="text-sky-400" />
                  <span>Teach J.A.R.V.I.S. New Fact:</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-12 gap-2">
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="md:col-span-3 bg-slate-900 border border-slate-800 rounded p-1.5 text-slate-200 text-xs focus:outline-none focus:border-slate-600"
                  >
                    <option value="user_preference">User Preference</option>
                    <option value="system_setting">System Setting</option>
                    <option value="domain_knowledge">Domain Knowledge</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Key (e.g., user_name, project_lead)"
                    value={newKey}
                    onChange={(e) => setNewKey(e.target.value)}
                    className="md:col-span-4 bg-slate-900 border border-slate-800 rounded p-1.5 text-slate-200 text-xs focus:outline-none focus:border-slate-600"
                  />
                  <input
                    type="text"
                    placeholder="Value (e.g., Suyash Pandey)"
                    value={newValue}
                    onChange={(e) => setNewValue(e.target.value)}
                    className="md:col-span-4 bg-slate-900 border border-slate-800 rounded p-1.5 text-slate-200 text-xs focus:outline-none focus:border-slate-600"
                  />
                  <button
                    type="submit"
                    className="md:col-span-1 bg-sky-600 hover:bg-sky-500 text-white rounded font-bold text-xs flex items-center justify-center transition-colors"
                  >
                    <Plus size={14} />
                  </button>
                </div>
              </form>

              {/* Facts Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {filteredFacts.length === 0 ? (
                  <div className="col-span-2 text-center py-8 text-slate-500">
                    Zero declarative facts match your query.
                  </div>
                ) : (
                  filteredFacts.map((fact) => (
                    <div
                      key={fact.key}
                      className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg flex items-center justify-between group hover:border-slate-700 transition-colors"
                    >
                      <div>
                        <div className="flex items-center gap-1.5 mb-1">
                          <span className="px-1.5 py-0.2 rounded bg-slate-900 text-slate-400 text-[9px] border border-slate-800">
                            {fact.category}
                          </span>
                          <span className="font-bold text-slate-200">{fact.key}</span>
                        </div>
                        <p className="text-slate-300 text-[11px]">{fact.value}</p>
                      </div>
                      <button
                        onClick={() => handleDeleteFact(fact.key)}
                        className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-rose-400 transition-opacity"
                        title="Delete fact"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </>
          )}

          {activeTab === 'ACTIONS' && (
            <div className="space-y-2">
              {actions.length === 0 ? (
                <div className="text-center py-8 text-slate-500">Zero episodic memories logged yet.</div>
              ) : (
                actions.map((act) => (
                  <div key={act.action_id} className="p-2.5 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1">
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span className="font-bold text-slate-300">{act.agent_name} // {act.action_type}</span>
                      <span>{act.timestamp?.slice(0, 19)}</span>
                    </div>
                    <p className="text-slate-300 text-[11px]">Command: "{act.user_command}"</p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import asyncio
import json
import time
import re
from typing import List, Dict, Any, Optional
from collections import deque

from server.config import settings
from server.db.async_db import async_db

class AwaitableBool:
    """Dual synchronous and asynchronous Boolean result"""
    def __init__(self, value: bool = True):
        self.value = bool(value)

    def __bool__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other

    def __repr__(self):
        return repr(self.value)

    def __await__(self):
        async def _coro():
            return self.value
        return _coro().__await__()

class AwaitableList(list):
    """Dual synchronous and asynchronous List result"""
    def __await__(self):
        async def _coro():
            return list(self)
        return _coro().__await__()

class SmartMemoryEngine:
    """
    Unified Multi-Tier Async Memory & Knowledge System
    Tiers:
    1. Working Memory: High-speed multi-turn conversation buffer with pronoun resolution.
    2. Fact & Preference Memory: Permanent key-value facts with semantic keyword scoring.
    3. Episodic Memory: Searchable audit of subagent tool executions and latency.
    4. Notes & Reminders: Integrated digital memory bank.
    """
    def __init__(self, max_working_memory: int = 15):
        self.working_memory: deque = deque(maxlen=max_working_memory)
        self._cached_facts: Dict[str, Dict[str, Any]] = {}

    # =========================================================================
    # 1. WORKING MEMORY & CONVERSATION BUFFER
    # =========================================================================

    def add_working_turn(
        self,
        role: str,
        content: str,
        agent_used: Optional[str] = None,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        session_id: str = "default"
    ):
        """Adds a turn to fast in-memory working buffer and triggers async SQLite persistence"""
        turn = {
            "role": role,
            "content": content,
            "agent_used": agent_used,
            "intent": intent,
            "entities": entities or {},
            "session_id": session_id,
            "timestamp": time.time()
        }
        self.working_memory.append(turn)

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._persist_turn(role, content, agent_used, intent, entities, session_id))
        except Exception:
            pass

    async def _persist_turn(self, role: str, content: str, agent_used: Optional[str], intent: Optional[str], entities: Optional[Dict[str, Any]], session_id: str):
        try:
            await async_db.execute("""
                INSERT INTO conversation_history (session_id, role, content, agent_used, intent, entities, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, role, content, agent_used, intent, json.dumps(entities or {}), time.time()))
        except Exception as e:
            print(f"[SmartMemory] Error persisting turn: {e}")

    def get_recent_dialog(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Returns the most recent N turns from in-memory working buffer"""
        return list(self.working_memory)[-limit:]

    async def get_conversation_history(self, limit: int = 20, session_id: str = "default") -> List[Dict[str, Any]]:
        """Fetches history from persistent database"""
        rows = await async_db.fetch_all("""
            SELECT role, content, agent_used, intent, entities, timestamp
            FROM conversation_history
            WHERE session_id = ?
            ORDER BY id DESC LIMIT ?
        """, (session_id, limit))
        rows.reverse()
        return rows

    def resolve_contextual_pronouns(self, text: str) -> str:
        """Resolves ambiguous pronouns ('it', 'that', 'him', 'her') using recent working memory entities."""
        t = text.lower().strip()
        pronouns = ["it", "that", "this", "him", "her", "them"]
        has_pronoun = any(re.search(rf"\b{p}\b", t) for p in pronouns)

        if not has_pronoun or not self.working_memory:
            return text

        last_entity = None
        for turn in reversed(self.working_memory):
            ents = turn.get("entities", {})
            if ents:
                last_entity = ents.get("entity") or ents.get("target_app") or ents.get("query") or ents.get("filename")
                if last_entity:
                    break
        
        if last_entity:
            if t in ["play it", "start it", "play that"]:
                return f"play {last_entity}"
            elif t in ["run it", "execute that", "run that script"]:
                return f"run {last_entity}"
            elif t in ["tell me more", "explain more", "who was he", "who is he", "what is it"]:
                return f"explain {last_entity}"

        return text

    # =========================================================================
    # 2. AUTO FACT EXTRACTION & FACT MEMORY
    # =========================================================================

    def auto_extract_and_store_facts(self, text: str) -> Optional[Dict[str, str]]:
        """Extracts facts from natural language statements and stores them immediately in cache and DB"""
        t = text.strip()
        
        m_name = re.search(r"(?:remember\s+(?:that\s+)?)?my\s+name\s+is\s+([a-zA-Z\s]+)", t, re.IGNORECASE)
        if m_name:
            val = m_name.group(1).strip()
            self.store_fact(category="identity", key="user_name", value=val)
            return {"key": "user_name", "value": val}

        m1 = re.search(r"\bremember\s+(?:that\s+)?(?:my\s+)?([a-zA-Z\s_\-]+)\s+(?:is|are|to\s+be)\s+(.*)", t, re.IGNORECASE)
        if m1:
            raw_key = m1.group(1).strip().lower().replace(" ", "_")
            val = m1.group(2).strip()
            self.store_fact(category="user_preference", key=raw_key, value=val)
            return {"key": raw_key, "value": val}

        m3 = re.search(r"\bi\s+(?:prefer|like|use)\s+(.*)", t, re.IGNORECASE)
        if m3:
            val = m3.group(1).strip()
            key = f"preference_{int(time.time())}"
            self.store_fact(category="user_preference", key=key, value=val)
            return {"key": key, "value": val}

        return None

    def store_fact(self, category: str, key: str, value: str, confidence: float = 1.0) -> AwaitableBool:
        """Stores or updates a persistent user fact in SQLite cache and DB synchronously & asynchronously"""
        now = time.time()
        clean_key = key.strip().lower().replace(" ", "_")
        clean_val = value.strip()
        self._cached_facts[clean_key] = {"category": category, "key": clean_key, "value": clean_val, "confidence": confidence, "updated_at": now}
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._persist_fact(category, clean_key, clean_val, confidence, now))
        except Exception:
            pass
        return AwaitableBool(True)

    async def _persist_fact(self, category: str, clean_key: str, clean_val: str, confidence: float, now: float):
        try:
            await async_db.execute("""
                INSERT INTO user_facts (category, key, value, confidence, access_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    confidence=excluded.confidence,
                    access_count=user_facts.access_count + 1,
                    updated_at=excluded.updated_at
            """, (category, clean_key, clean_val, confidence, now, now))
        except Exception as e:
            print(f"[SmartMemory] Fact persist error: {e}")

    def recall_facts(self, query: str, limit: int = 5) -> AwaitableList:
        """Retrieves relevant user facts using token overlap and keyword relevance (dual sync/async compatible)"""
        tokens = set(re.findall(r"\w+", query.lower()))
        stop_words = {"what", "is", "my", "the", "do", "you", "remember", "who", "am", "i", "where", "how", "tell", "me", "which"}
        query_tokens = [t for t in tokens if t not in stop_words and len(t) > 1]

        all_facts = list(self._cached_facts.values())
        if not query_tokens:
            return AwaitableList(all_facts[:limit])

        scored_facts = []
        for fact in all_facts:
            key_tokens = set(fact["key"].split("_"))
            val_tokens = set(re.findall(r"\w+", str(fact["value"]).lower()))
            combined = key_tokens.union(val_tokens)

            overlap = len(combined.intersection(query_tokens))
            if overlap > 0 or any(q in fact["key"] or q in str(fact["value"]).lower() for q in query_tokens):
                score = overlap * 3 + (2 if any(q in fact["key"] for q in query_tokens) else 0)
                scored_facts.append((score, fact))

        scored_facts.sort(key=lambda x: x[0], reverse=True)
        return AwaitableList([f[1] for f in scored_facts[:limit]])

    async def list_all_facts(self) -> List[Dict[str, Any]]:
        """Returns all stored user facts sorted by recency from DB"""
        rows = await async_db.fetch_all("SELECT * FROM user_facts ORDER BY updated_at DESC")
        for r in rows:
            self._cached_facts[r["key"]] = dict(r)
        return list(self._cached_facts.values())

    async def delete_fact(self, key: str) -> bool:
        """Deletes a fact by key"""
        clean_key = key.lower().replace(" ", "_")
        self._cached_facts.pop(clean_key, None)
        self._cached_facts.pop(key, None)
        count = await async_db.execute("DELETE FROM user_facts WHERE key = ? OR key = ?", (key, clean_key))
        return count > 0

    # =========================================================================
    # 3. EPISODIC ACTION AUDITING
    # =========================================================================

    async def log_action_execution(
        self,
        action_id: str,
        agent_name: str,
        tool_name: str,
        params: Dict[str, Any],
        result: Any,
        latency_ms: float = 0.0,
        tier: str = "tier_1_safe",
        status: str = "SUCCESS",
        session_id: str = "default"
    ):
        """Logs episodic action execution with latency in SQLite"""
        try:
            await async_db.execute("""
                INSERT INTO episodic_actions (action_id, session_id, agent_name, tool_name, params, result, guardrail_tier, status, latency_ms, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action_id,
                session_id,
                agent_name,
                tool_name,
                json.dumps(params),
                json.dumps(result) if not isinstance(result, str) else result,
                tier,
                status,
                latency_ms,
                time.time()
            ))
        except Exception as e:
            print(f"[SmartMemory] Action log error: {e}")

    async def list_recent_actions(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Returns recent episodic actions"""
        return await async_db.fetch_all("SELECT * FROM episodic_actions ORDER BY timestamp DESC LIMIT ?", (limit,))

    # =========================================================================
    # 4. NOTES, REMINDERS & ALARMS
    # =========================================================================

    async def add_note(self, title: str, content: str, tags: str = "") -> int:
        now = time.time()
        return await async_db.execute(
            "INSERT INTO notes (title, content, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (title, content, tags, now, now)
        )

    async def list_notes(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        if query:
            return await async_db.fetch_all(
                "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? ORDER BY updated_at DESC",
                (f"%{query}%", f"%{query}%", f"%{query}%")
            )
        return await async_db.fetch_all("SELECT * FROM notes ORDER BY updated_at DESC LIMIT 50")

    async def delete_note(self, note_id: int) -> bool:
        count = await async_db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return count > 0

    async def add_reminder(self, task: str, due_time: Optional[str] = None) -> int:
        now = time.time()
        return await async_db.execute(
            "INSERT INTO reminders (task, due_time, is_completed, created_at) VALUES (?, ?, 0, ?)",
            (task, due_time, now)
        )

    async def list_reminders(self, include_completed: bool = False) -> List[Dict[str, Any]]:
        if include_completed:
            return await async_db.fetch_all("SELECT * FROM reminders ORDER BY created_at DESC")
        return await async_db.fetch_all("SELECT * FROM reminders WHERE is_completed = 0 ORDER BY created_at DESC")

    async def complete_reminder(self, reminder_id: int) -> bool:
        count = await async_db.execute("UPDATE reminders SET is_completed = 1 WHERE id = ?", (reminder_id,))
        return count > 0

    # =========================================================================
    # 5. CONTEXT ENRICHMENT FOR AGENT PROMPTS
    # =========================================================================

    async def generate_context_enrichment(self, user_query: str) -> str:
        """Builds concise grounding block for LLM Planner"""
        relevant_facts = self.recall_facts(user_query, limit=3)
        context_parts = []
        if relevant_facts:
            facts_str = ", ".join([f"{f['key'].replace('_', ' ').title()}: {f['value']}" for f in relevant_facts])
            context_parts.append(f"[Recalled Memory: {facts_str}]")

        recent_dialog = self.get_recent_dialog(limit=3)
        if recent_dialog:
            turns = [f"{t['role']}: {t['content']}" for t in recent_dialog]
            context_parts.append(f"[Recent Dialog: {' | '.join(turns)}]")

        return "\n".join(context_parts)

smart_memory = SmartMemoryEngine()

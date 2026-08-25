import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from server.config import settings

class MemoryBank:
    """
    JARVIS Long-Term & Short-Term Memory Manager with SQLite persistence
    """
    def __init__(self, db_path=None):
        self.db_path = str(db_path or settings.DB_PATH)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Notes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT DEFAULT '',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            
            # Reminders & Tasks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    due_time TEXT,
                    is_completed INTEGER DEFAULT 0,
                    created_at REAL NOT NULL
                )
            """)
            
            # Alarms
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alarms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time_str TEXT NOT NULL,
                    label TEXT DEFAULT 'Alarm',
                    is_active INTEGER DEFAULT 1,
                    created_at REAL NOT NULL
                )
            """)
            
            # User Facts & Preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            
            # Conversation logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    agent_used TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    # --- Notes ---
    def add_note(self, title: str, content: str, tags: str = "") -> int:
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (title, content, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (title, content, tags, now, now)
            )
            conn.commit()
            return cursor.lastrowid

    def list_notes(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if query:
                cursor.execute(
                    "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? ORDER BY updated_at DESC",
                    (f"%{query}%", f"%{query}%", f"%{query}%")
                )
            else:
                cursor.execute("SELECT * FROM notes ORDER BY updated_at DESC LIMIT 30")
            return [dict(row) for row in cursor.fetchall()]

    def delete_note(self, note_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0

    # --- Reminders ---
    def add_reminder(self, task: str, due_time: Optional[str] = None) -> int:
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reminders (task, due_time, is_completed, created_at) VALUES (?, ?, 0, ?)",
                (task, due_time, now)
            )
            conn.commit()
            return cursor.lastrowid

    def list_reminders(self, include_completed: bool = False) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if include_completed:
                cursor.execute("SELECT * FROM reminders ORDER BY created_at DESC")
            else:
                cursor.execute("SELECT * FROM reminders WHERE is_completed = 0 ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def complete_reminder(self, reminder_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reminders SET is_completed = 1 WHERE id = ?", (reminder_id,))
            conn.commit()
            return cursor.rowcount > 0

    # --- Alarms ---
    def add_alarm(self, time_str: str, label: str = "Alarm") -> int:
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO alarms (time_str, label, is_active, created_at) VALUES (?, ?, 1, ?)",
                (time_str, label, now)
            )
            conn.commit()
            return cursor.lastrowid

    def list_alarms(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alarms WHERE is_active = 1 ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    # --- User Facts & Preferences ---
    def set_fact(self, key: str, value: str, category: str = "general"):
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_facts (category, key, value, updated_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, category=excluded.category, updated_at=excluded.updated_at",
                (category, key, value, now)
            )
            conn.commit()

    def get_facts(self) -> Dict[str, str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM user_facts")
            return {row["key"]: row["value"] for row in cursor.fetchall()}

    # --- Conversation Context ---
    def log_message(self, role: str, content: str, agent_used: Optional[str] = None):
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (role, content, agent_used, timestamp) VALUES (?, ?, ?, ?)",
                (role, content, agent_used, now)
            )
            conn.commit()

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, content, agent_used, timestamp FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
            rows = [dict(row) for row in cursor.fetchall()]
            rows.reverse()
            return rows

memory_bank = MemoryBank()

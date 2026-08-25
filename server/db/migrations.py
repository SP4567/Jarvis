import time
import aiosqlite
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from server.db.async_db import AsyncDatabaseManager

BASE_TABLES = [
    # 1. User Facts & Long-term Preferences
    """
    CREATE TABLE IF NOT EXISTS user_facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        key TEXT NOT NULL UNIQUE,
        value TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        access_count INTEGER DEFAULT 0,
        created_at REAL NOT NULL,
        updated_at REAL NOT NULL
    );
    """,

    # 2. Conversation Turns & Multi-turn Dialog
    """
    CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT DEFAULT 'default',
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        agent_used TEXT,
        intent TEXT,
        entities TEXT,
        tokens INTEGER DEFAULT 0,
        timestamp REAL NOT NULL
    );
    """,

    # 3. Episodic Tool Executions & Metrics
    """
    CREATE TABLE IF NOT EXISTS episodic_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_id TEXT UNIQUE,
        session_id TEXT DEFAULT 'default',
        agent_name TEXT NOT NULL,
        tool_name TEXT NOT NULL,
        params TEXT,
        result TEXT,
        guardrail_tier TEXT,
        status TEXT,
        latency_ms REAL DEFAULT 0.0,
        timestamp REAL NOT NULL
    );
    """,

    # 4. Notes & Reminders
    """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT DEFAULT '',
        created_at REAL NOT NULL,
        updated_at REAL NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        due_time TEXT,
        is_completed INTEGER DEFAULT 0,
        created_at REAL NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS alarms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time_str TEXT NOT NULL,
        label TEXT DEFAULT 'Alarm',
        is_active INTEGER DEFAULT 1,
        created_at REAL NOT NULL
    );
    """,

    # 5. SOC Cases & Detection Rules
    """
    CREATE TABLE IF NOT EXISTS soc_cases (
        case_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        severity TEXT NOT NULL,
        risk_score INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        assigned_tier TEXT NOT NULL,
        case_data JSON NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS soc_detection_rules (
        rule_id TEXT PRIMARY KEY,
        case_id TEXT,
        title TEXT NOT NULL,
        rule_type TEXT NOT NULL,
        rule_content TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """,

    # 6. Immutable Hash-Chained Security Audit Ledger
    """
    CREATE TABLE IF NOT EXISTS security_audit_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_id TEXT UNIQUE NOT NULL,
        timestamp REAL NOT NULL,
        actor TEXT NOT NULL,
        action_name TEXT NOT NULL,
        target TEXT,
        details TEXT,
        tier TEXT NOT NULL,
        status TEXT NOT NULL,
        reason TEXT,
        previous_hash TEXT NOT NULL,
        current_hash TEXT NOT NULL
    );
    """,

    # 7. Threat Intelligence Feed Cache
    """
    CREATE TABLE IF NOT EXISTS cti_cache (
        ioc TEXT PRIMARY KEY,
        ioc_type TEXT NOT NULL,
        reputation TEXT NOT NULL,
        score INTEGER NOT NULL,
        actor TEXT,
        tags TEXT,
        raw_response TEXT,
        cached_at REAL NOT NULL,
        expires_at REAL NOT NULL
    );
    """
]

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_user_facts_key ON user_facts(key);",
    "CREATE INDEX IF NOT EXISTS idx_user_facts_cat ON user_facts(category);",
    "CREATE INDEX IF NOT EXISTS idx_conv_timestamp ON conversation_history(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_episodic_action_id ON episodic_actions(action_id);",
    "CREATE INDEX IF NOT EXISTS idx_episodic_agent ON episodic_actions(agent_name);",
    "CREATE INDEX IF NOT EXISTS idx_soc_cases_updated ON soc_cases(updated_at);",
    "CREATE INDEX IF NOT EXISTS idx_audit_action_id ON security_audit_ledger(action_id);",
    "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON security_audit_ledger(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_cti_cache_ioc ON cti_cache(ioc);",
    "CREATE INDEX IF NOT EXISTS idx_cti_cache_expires ON cti_cache(expires_at);"
]

async def _ensure_columns(conn: aiosqlite.Connection, table_name: str, required_cols: Dict[str, str]):
    """Ensures existing table has all required columns with their types"""
    cursor = await conn.execute(f"PRAGMA table_info({table_name});")
    existing_cols = {row[1]: row[2] for row in await cursor.fetchall()}
    
    for col_name, col_type in required_cols.items():
        if col_name not in existing_cols:
            try:
                await conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};")
            except Exception:
                pass

async def run_migrations(db_manager: "AsyncDatabaseManager"):
    """Executes schema initialization, column migrations, and index creation safely"""
    conn = await aiosqlite.connect(db_manager.db_path)
    try:
        # 1. Base table creation
        for stmt in BASE_TABLES:
            await conn.execute(stmt)
        await conn.commit()

        # 2. Incremental column upgrades on existing tables
        await _ensure_columns(conn, "conversation_history", {
            "session_id": "TEXT DEFAULT 'default'",
            "agent_used": "TEXT",
            "intent": "TEXT",
            "entities": "TEXT",
            "tokens": "INTEGER DEFAULT 0"
        })
        await _ensure_columns(conn, "episodic_actions", {
            "session_id": "TEXT DEFAULT 'default'",
            "latency_ms": "REAL DEFAULT 0.0"
        })
        await _ensure_columns(conn, "user_facts", {
            "confidence": "REAL DEFAULT 1.0",
            "access_count": "INTEGER DEFAULT 0"
        })
        await conn.commit()

        # 3. Create indexes
        for idx_stmt in INDEXES:
            try:
                await conn.execute(idx_stmt)
            except Exception:
                pass
        
        # Add index on session_id if column exists
        try:
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_session ON conversation_history(session_id);")
        except Exception:
            pass

        await conn.commit()
    finally:
        await conn.close()

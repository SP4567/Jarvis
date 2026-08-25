import asyncio
import aiosqlite
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager
from server.config import settings

class AsyncDatabaseManager:
    """
    Enterprise High-Performance Async SQLite Database Manager
    Supports Write-Ahead Logging (WAL), connection pooling patterns,
    transaction wrappers, and row-to-dictionary mapping.
    """
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or settings.DB_PATH)
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self):
        """Initializes database pragmas (WAL mode, foreign keys, busy timeout)"""
        async with self._lock:
            if self._initialized:
                return
            
            # Ensure parent directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            async with aiosqlite.connect(self.db_path) as db:
                if settings.ENABLE_WAL_MODE:
                    await db.execute("PRAGMA journal_mode=WAL;")
                    await db.execute("PRAGMA synchronous=NORMAL;")
                await db.execute("PRAGMA foreign_keys=ON;")
                await db.execute("PRAGMA busy_timeout=5000;")
                await db.commit()
            
            # Run schema migrations
            from server.db.migrations import run_migrations
            await run_migrations(self)
            self._initialized = True

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Provides an async connection with row_factory set to Row dictionary mapper"""
        if not self._initialized:
            await self.initialize()
            
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
        finally:
            await conn.close()

    async def execute(self, query: str, parameters: tuple = ()) -> int:
        """Executes INSERT/UPDATE/DELETE and returns lastrowid or rowcount"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(query, parameters)
            await conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    async def executemany(self, query: str, parameters_list: List[tuple]) -> int:
        """Executes batch operations"""
        async with self.get_connection() as conn:
            cursor = await conn.executemany(query, parameters_list)
            await conn.commit()
            return cursor.rowcount

    async def fetch_one(self, query: str, parameters: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetches a single row as a standard dictionary"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(query, parameters)
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def fetch_all(self, query: str, parameters: tuple = ()) -> List[Dict[str, Any]]:
        """Fetches multiple rows as a list of dictionaries"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(query, parameters)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @asynccontextmanager
    async def transaction(self):
        """Transaction context manager that auto-commits on success and rollbacks on exception"""
        async with self.get_connection() as conn:
            try:
                yield conn
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

async_db = AsyncDatabaseManager()

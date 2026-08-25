import pytest
import asyncio
from server.db.async_db import AsyncDatabaseManager

@pytest.mark.asyncio
async def test_async_database_crud(tmp_path):
    db_file = tmp_path / "test_async_memory.db"
    db = AsyncDatabaseManager(db_path=db_file)
    await db.initialize()

    # 1. Test insert user fact
    await db.execute("""
        INSERT INTO user_facts (category, key, value, confidence, access_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("test", "user_title", "Director", 1.0, 1, 1000.0, 1000.0))

    # 2. Test fetch one
    row = await db.fetch_one("SELECT * FROM user_facts WHERE key = ?", ("user_title",))
    assert row is not None
    assert row["value"] == "Director"

    # 3. Test transaction rollback on failure
    try:
        async with db.transaction() as conn:
            await conn.execute("INSERT INTO user_facts (category, key, value, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                               ("test", "temp_key", "temp_val", 1000.0, 1000.0))
            raise ValueError("Forced error to test rollback")
    except ValueError:
        pass

    rolled_back_row = await db.fetch_one("SELECT * FROM user_facts WHERE key = ?", ("temp_key",))
    assert rolled_back_row is None

    # 4. Test fetch all
    all_facts = await db.fetch_all("SELECT * FROM user_facts")
    assert len(all_facts) == 1

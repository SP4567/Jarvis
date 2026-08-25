import pytest
import asyncio
from server.core.guardrails import GuardrailEngine, SafetyTier, ApprovalStatus
from server.db.async_db import async_db

@pytest.mark.asyncio
async def test_guardrail_ast_validation():
    engine = GuardrailEngine(strictness="strict")

    # Safe AST
    is_safe, msg = engine.validate_python_ast("def add(a, b):\n    return a + b\nprint(add(2, 3))")
    assert is_safe is True

    # Forbidden ctypes import
    is_safe2, msg2 = engine.validate_python_ast("import ctypes\nctypes.windll.kernel32.ExitProcess(0)")
    assert is_safe2 is False
    assert "ctypes" in msg2.lower()

    # Forbidden dynamic eval
    is_safe3, msg3 = engine.validate_python_ast("eval('__import__(\"os\").system(\"calc\")')")
    assert is_safe3 is False
    assert "forbidden" in msg3.lower() or "eval" in msg3.lower()

@pytest.mark.asyncio
async def test_guardrail_path_and_process_validation():
    engine = GuardrailEngine(strictness="strict")

    # Path traversal protection
    is_valid, msg = engine.validate_file_path("..\\..\\Windows\\System32\\calc.exe")
    assert is_valid is False
    assert "traversal" in msg.lower() or "outside" in msg.lower()

    # Protected core Windows process protection
    is_valid_proc, proc_msg = engine.validate_process_target("lsass.exe", 100)
    assert is_valid_proc is False
    assert "protected" in proc_msg.lower()

@pytest.mark.asyncio
async def test_guardrail_sha256_audit_ledger():
    engine = GuardrailEngine(strictness="strict")
    await async_db.initialize()

    # Verify audit hash chaining
    await engine._record_audit_log(
        action_id="TEST-ACT-01",
        actor="TEST_USER",
        agent_name="system_agent",
        action_name="get_vitals",
        target="C:\\",
        details={"sample": "data"},
        tier=SafetyTier.TIER_1_SAFE,
        status=ApprovalStatus.APPROVED,
        reason="Test logging"
    )

    ledger = await async_db.fetch_one("SELECT * FROM security_audit_ledger WHERE action_id = ?", ("TEST-ACT-01",))
    assert ledger is not None
    assert len(ledger["current_hash"]) == 64
    assert len(ledger["previous_hash"]) > 0

import pytest
import asyncio
from server.core.guardrails import GuardrailEngine, SafetyTier, ApprovalStatus
from server.core.memory import MemoryBank
from server.core.orchestrator import Orchestrator
from server.agents.system_agent import SystemAgent
from server.agents.research_agent import ResearchAgent
from server.agents.productivity_agent import ProductivityAgent
from server.agents.media_agent import MediaAgent

def test_guardrails_classification():
    engine = GuardrailEngine(strictness="strict")
    
    # 1. Tier 1 Safe test
    tier, _ = engine.classify_action("research_agent", "get_weather", {"location": "London"})
    assert tier == SafetyTier.TIER_1_SAFE
    
    # 2. Tier 2 Sensitive test
    tier, _ = engine.classify_action("productivity_agent", "create_note", {"title": "Test", "content": "Hello"})
    assert tier == SafetyTier.TIER_2_SENSITIVE
    
    # 3. Tier 3 Dangerous test
    tier, _ = engine.classify_action("system_agent", "kill_process", {"process_name": "notepad.exe"})
    assert tier == SafetyTier.TIER_3_DANGEROUS
    
    # 4. Blocked test
    tier, _ = engine.classify_action("system_agent", "execute_shell_command", {"command": "rmdir /s /q C:\\Windows"})
    assert tier == SafetyTier.BLOCKED

def test_memory_bank(tmp_path):
    db_file = tmp_path / "test_memory.db"
    mem = MemoryBank(db_path=db_file)
    
    # Test Note
    note_id = mem.add_note("Meeting", "Prepare presentation", "work")
    notes = mem.list_notes()
    assert len(notes) == 1
    assert notes[0]["title"] == "Meeting"
    
    # Test Reminder
    rem_id = mem.add_reminder("Buy milk", "5 PM")
    rems = mem.list_reminders()
    assert len(rems) == 1
    assert rems[0]["task"] == "Buy milk"
    
    # Complete reminder
    assert mem.complete_reminder(rem_id) is True
    assert len(mem.list_reminders()) == 0

@pytest.mark.asyncio
async def test_orchestrator_local_fallback():
    orch = Orchestrator()
    
    # Test vitals query
    res = await orch.handle_user_command("JARVIS, what are my system vitals?")
    assert "cpu" in res["text"].lower() or "vitals" in res["text"].lower()
    assert res["agent_used"] == "system_agent"
    
    # Test reminder query
    res2 = await orch.handle_user_command("JARVIS, remind me to call Tony at 6 PM")
    assert "reminder" in res2["text"].lower() or "schedule" in res2["text"].lower()

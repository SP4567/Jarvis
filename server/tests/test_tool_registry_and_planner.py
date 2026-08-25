import pytest
import asyncio
from server.core.tool_registry import tool_registry
from server.core.router import intent_router
from server.core.intent_classifier import intent_engine

@pytest.mark.asyncio
async def test_tool_registry_registration_and_execution():
    # Test registered tool execution
    res = await tool_registry.execute_tool("get_system_vitals", {})
    assert res.success is True
    assert "cpu_percent" in res.result

    # Test tool schemas generation for Gemini
    schemas = tool_registry.get_gemini_tool_declarations()
    assert len(schemas) > 5
    tool_names = [s["name"] for s in schemas]
    assert "get_system_vitals" in tool_names
    assert "write_code_file" in tool_names

@pytest.mark.asyncio
async def test_intent_router_fast_path():
    # 1. System volume command
    intent1 = intent_engine.parse("increase the volume")
    assert intent_router.can_fast_path(intent1) is True

    # 2. Wikipedia lookup
    intent2 = intent_engine.parse("who was Nikola Tesla")
    assert intent_router.can_fast_path(intent2) is True

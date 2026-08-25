import pytest
import asyncio
from server.core.orchestrator import orchestrator

@pytest.mark.asyncio
async def test_soc_voice_tier1_dispatch():
    res = await orchestrator.handle_user_command("JARVIS, ask Tier 1 to triage alerts")
    assert res["agent_used"] == "tier1_triage_agent"
    assert "Tier 1 Triage Analyst reporting" in res["text"]

@pytest.mark.asyncio
async def test_soc_voice_tier2_dispatch():
    res = await orchestrator.handle_user_command("JARVIS, ask Tier 2 to investigate host PROD-DB-01")
    assert res["agent_used"] == "tier2_responder_agent"
    assert "Tier 2 Incident Responder reporting" in res["text"]

@pytest.mark.asyncio
async def test_soc_voice_tier3_dispatch():
    res = await orchestrator.handle_user_command("JARVIS, ask Tier 3 for threat hunting report")
    assert res["agent_used"] == "tier3_hunter_agent"
    assert "Tier 3 Threat Hunter" in res["text"]

@pytest.mark.asyncio
async def test_soc_voice_metrics():
    res = await orchestrator.handle_user_command("JARVIS, what is our mean time to detect and MTTR?")
    assert res["agent_used"] == "soc_orchestrator"
    assert "Mean Time to Detect" in res["text"]

@pytest.mark.asyncio
async def test_math_and_percentages():
    # Percentage
    res1 = await orchestrator.handle_user_command("JARVIS, what is 15% of 300?")
    assert "45" in res1["text"]

    # Tip
    res2 = await orchestrator.handle_user_command("what is 20 percent tip on 100 dollars")
    assert "20" in res2["text"]

    # Arithmetic
    res3 = await orchestrator.handle_user_command("calculate (50 * 2) + 25")
    assert "125" in res3["text"]

    # Square root
    res4 = await orchestrator.handle_user_command("what is the square root of 144")
    assert "12" in res4["text"]

@pytest.mark.asyncio
async def test_unit_conversions():
    # Distance
    res1 = await orchestrator.handle_user_command("convert 10 miles to km")
    assert "16.09" in res1["text"] or "kilometers" in res1["text"]

    # Temperature
    res2 = await orchestrator.handle_user_command("convert 100 celsius to fahrenheit")
    assert "212" in res2["text"]

    # Weight
    res3 = await orchestrator.handle_user_command("convert 50 kg to pounds")
    assert "110.23" in res3["text"] or "pounds" in res3["text"]

@pytest.mark.asyncio
async def test_global_clocks():
    res = await orchestrator.handle_user_command("what time is it in Tokyo?")
    assert "Tokyo" in res["text"]

@pytest.mark.asyncio
async def test_volume_controls():
    res = await orchestrator.handle_user_command("set volume to 75")
    assert "75 percent" in res["text"]

@pytest.mark.asyncio
async def test_conversational_persona():
    res1 = await orchestrator.handle_user_command("who created you?")
    assert "J.A.R.V.I.S." in res1["text"]

    res2 = await orchestrator.handle_user_command("give me a motivational quote")
    assert "Tony Stark" in res2["text"] or "Jobs" in res2["text"] or '"' in res2["text"]

    res3 = await orchestrator.handle_user_command("tell me a joke")
    assert "Sir" in res3["text"]

@pytest.mark.asyncio
async def test_code_writing_and_execution():
    # Write code
    res1 = await orchestrator.handle_user_command("JARVIS, write python code for fibonacci sequence to fib.py")
    assert res1["agent_used"] == "coding_agent"
    assert "fib.py" in res1["text"]

    # Execute code
    res2 = await orchestrator.handle_user_command("run python code: print(sum([1, 2, 3, 4, 5]))")
    assert res2["agent_used"] == "coding_agent"
    assert "15" in res2["text"]

    # Git status
    res3 = await orchestrator.handle_user_command("check git status")
    assert res3["agent_used"] == "coding_agent"
    assert "Git repository status" in res3["text"]

@pytest.mark.asyncio
async def test_wikipedia_and_global_web_research():
    # Wikipedia lookup
    res1 = await orchestrator.handle_user_command("who was Alexander Graham Bell?")
    assert res1["agent_used"] == "research_agent"
    assert "telephone" in res1["text"].lower() or "inventor" in res1["text"].lower() or "alexander" in res1["text"].lower()

    # General web query
    res2 = await orchestrator.handle_user_command("tell me about quantum computing")
    assert res2["agent_used"] == "research_agent"
    assert "quantum" in res2["text"].lower() or "computing" in res2["text"].lower()

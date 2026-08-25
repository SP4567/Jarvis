import pytest
import asyncio
from server.soc.cti_feed import cti_feed_manager
from server.soc.soc_orchestrator import soc_orchestrator
from server.soc.soc_guardrails import soc_guardrail_engine

@pytest.mark.asyncio
async def test_cti_feed_lookup_and_cache():
    # Test known malicious IOC lookup
    res = await cti_feed_manager.lookup_ioc("185.220.101.5", "IP")
    assert res.reputation == "MALICIOUS"
    assert res.score >= 90
    assert "Cobalt Strike" in str(res.threat_actor)

    # Test internal IP lookup (RFC1918)
    res_internal = await cti_feed_manager.lookup_ioc("192.168.1.10", "IP")
    assert res_internal.reputation == "CLEAN"
    assert res_internal.score == 0

@pytest.mark.asyncio
async def test_soc_orchestrator_live_event_pipeline():
    raw_event = {
        "source_type": "TEST_EDR",
        "hostname": "PROD-DB-01",
        "process_name": "powershell.exe",
        "command_line": "powershell -enc aW1wb3J0IG1pbWlrYXR6",
        "user_identity": "ADMINISTRATOR"
    }
    
    case = soc_orchestrator.process_incoming_security_event(raw_event)
    assert case is not None
    assert case.risk_score >= 60
    assert len(case.containment_actions) > 0

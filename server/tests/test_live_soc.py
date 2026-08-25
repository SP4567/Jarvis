import pytest
import os
from server.soc.live_collector import live_host_collector
from server.soc.soc_orchestrator import soc_orchestrator
from server.soc.soc_guardrails import soc_guardrail_engine
from server.soc.models import ActionRiskLevel, ApprovalStatus
from server.core.orchestrator import orchestrator

def test_live_process_collection():
    """Verifies actual running processes are retrieved from Windows OS"""
    procs = live_host_collector.get_live_processes(limit=50)
    assert isinstance(procs, list)
    assert len(procs) > 0
    first = procs[0]
    assert "pid" in first
    assert "name" in first
    assert "cpu_percent" in first

def test_live_network_connections():
    """Verifies actual active TCP/UDP sockets and listening ports are retrieved"""
    conns = live_host_collector.get_live_network_connections(limit=50)
    assert isinstance(conns, list)
    listening = live_host_collector.get_listening_ports()
    assert isinstance(listening, list)

def test_startup_persistence_inspection():
    """Verifies Windows Registry Run keys are scanned"""
    startup = live_host_collector.get_startup_persistence_items()
    assert isinstance(startup, list)

def test_360_degree_live_security_audit():
    """Verifies the 360-degree host security audit executes and returns structured telemetry"""
    audit = soc_orchestrator.run_live_security_audit()
    assert "audit_id" in audit
    assert "hostname" in audit
    assert "host_risk_score" in audit
    assert "total_active_processes" in audit
    assert audit["total_active_processes"] > 0
    assert "listening_ports_count" in audit

def test_production_containment_execution():
    """Verifies real containment policy actions are tracked and rollbacks function"""
    action = soc_guardrail_engine.propose_action(
        case_id="TEST-LIVE-CASE",
        action_name="block_firewall_ioc",
        target={"ip": "198.51.100.24"},
        reason="Malicious C2 IP detected in live traffic.",
        evidence=["Outbound socket to unauthorized external IP."],
        confidence=0.95,
        expected_impact="Remote IP blocked in Windows Firewall.",
        rollback_strategy="netsh advfirewall firewall delete rule name=\"JARVIS_BLOCK_IP_TEST\""
    )
    assert action.approval_status in [ApprovalStatus.AUTO_EXECUTED, ApprovalStatus.APPROVED]
    
    # Test rollback
    rollback_res = soc_guardrail_engine.rollback_action(action.action_id, operator="TEST_SUITE")
    assert rollback_res["success"] is True

@pytest.mark.asyncio
async def test_live_security_audit_voice_commands():
    """Verifies voice commands trigger live security audit and live process inspection"""
    res1 = await orchestrator.handle_user_command("JARVIS, run a live security audit on this host")
    assert res1["agent_used"] == "soc_orchestrator"
    assert "audit" in res1["text"].lower() or "scanned" in res1["text"].lower() or "processes" in res1["text"].lower()

    res2 = await orchestrator.handle_user_command("JARVIS, check running processes")
    assert res2["agent_used"] == "soc_orchestrator"
    assert "processes" in res2["text"].lower()

@pytest.mark.asyncio
async def test_soc_on_off_power_switch():
    """Verifies master SOC power switch turns monitoring on/off via voice & API methods"""
    # Deactivate
    res_off = await orchestrator.handle_user_command("JARVIS, deactivate SOC security")
    assert res_off["agent_used"] == "soc_orchestrator"
    assert "deactivated" in res_off["text"].lower() or "standby" in res_off["text"].lower()
    assert soc_orchestrator.is_monitoring_active is False

    # Check briefing when off
    summary = soc_orchestrator.get_security_posture_summary()
    assert "off" in summary.lower() or "standby" in summary.lower()

    # Reactivate
    res_on = await orchestrator.handle_user_command("JARVIS, activate SOC security")
    assert res_on["agent_used"] == "soc_orchestrator"
    assert "activated" in res_on["text"].lower() or "online" in res_on["text"].lower()
    assert soc_orchestrator.is_monitoring_active is True


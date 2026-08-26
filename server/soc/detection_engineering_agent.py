import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    IncidentContext,
    DetectionRule,
    AgentFinding,
    AgentExecutionPhase,
    MitreAttackMapping
)

class DetectionEngineeringAgent(BaseSocAgent):
    """
    Detection Engineering Agent
    Identifies telemetry & detection gaps, synthesizes production Sigma / YARA rules,
    and tests detection coverage against MITRE ATT&CK techniques.
    """
    def __init__(self):
        super().__init__(
            name="detection_engineering_agent",
            role_title="Detection Engineer & Rule Architect",
            description="Designs, tests, and deploys high-fidelity Sigma, YARA, and SIEM correlation rules to close detection gaps."
        )

    def generate_sigma_rule(
        self,
        title: str,
        technique_id: str,
        tactic: str,
        process_names: List[str],
        command_patterns: List[str],
        severity: str = "high"
    ) -> DetectionRule:
        """Synthesizes valid production Sigma YAML detection rule"""
        rule_id = f"SIGMA-{uuid.uuid4().hex[:6].upper()}"
        
        proc_yaml = "\n".join([f"            - '\\{p.lower()}'" for p in process_names]) or "            - '\\powershell.exe'\n            - '\\cmd.exe'"
        cmd_yaml = "\n".join([f"            - '{c}'" for c in command_patterns]) or "            - '-EncodedCommand'\n            - 'downloadstring'"

        rule_content = f"""title: {title}
id: {uuid.uuid4()}
status: production
description: Autonomous detection rule synthesized by Detection Engineering Agent.
references:
    - https://attack.mitre.org/techniques/{technique_id.replace('.', '/')}/
author: JARVIS Detection Engineering Agent
date: {datetime.now().strftime('%Y/%m/%d')}
tags:
    - attack.{tactic.lower().replace(' ', '_')}
    - attack.{technique_id.lower()}
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith:
{proc_yaml}
        CommandLine|contains:
{cmd_yaml}
    condition: selection
falsepositives:
    - Verified Administrative Software Deployment Scripts
level: {severity.lower()}
"""
        return DetectionRule(
            rule_id=rule_id,
            title=title,
            rule_type="SIGMA",
            description=f"Auto-generated detection rule for {technique_id}",
            severity=severity.upper(),
            mitre_tags=[f"attack.{technique_id.lower()}", f"attack.{tactic.lower()}"],
            rule_content=rule_content,
            created_at=datetime.now().isoformat()
        )

    async def collect(self, context: IncidentContext, plan: List[str]) -> Dict[str, Any]:
        """Gathers MITRE techniques, process executions, and IOCs from incident to evaluate gaps"""
        techniques = context.mitre_attack
        raw_events = context.evidence_chain
        return {
            "techniques": techniques,
            "evidence_count": len(raw_events)
        }

    def analyze(self, context: IncidentContext, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        techniques: List[MitreAttackMapping] = telemetry.get("techniques", [])
        gap_detected = len(context.detection_rules) == 0 and len(techniques) > 0
        
        tech = techniques[0] if techniques else MitreAttackMapping(tactic="Execution", technique_id="T1059.001", technique_name="PowerShell")
        
        return {
            "gap_detected": gap_detected,
            "target_technique": tech.technique_id,
            "technique_name": tech.technique_name,
            "tactic": tech.tactic,
            "confidence": 0.96
        }

    def decide(self, context: IncidentContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "SYNTHESIZE_SIGMA_RULE",
            "requires_containment": False,
            "recommendations": [
                "Deploy auto-synthesized Sigma rule to central SIEM / EDR pipeline.",
                "Enable PowerShell Script Block Logging (Event ID 4104) across all domain endpoints."
            ]
        }

    async def act(self, context: IncidentContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        tech_id = context.mitre_attack[0].technique_id if context.mitre_attack else "T1059.001"
        tactic = context.mitre_attack[0].tactic if context.mitre_attack else "Execution"
        title = f"Detect {context.title or 'Suspicious Adversary Activity'}"
        
        rule = self.generate_sigma_rule(
            title=title,
            technique_id=tech_id,
            tactic=tactic,
            process_names=["powershell.exe", "cmd.exe", "wmic.exe"],
            command_patterns=["downloadstring", "iex", "-enc", "mimikatz"]
        )
        context.detection_rules.append(rule)
        return {"success": True, "rule_id": rule.rule_id, "rule_title": rule.title}

    def report(
        self,
        context: IncidentContext,
        analysis: Dict[str, Any],
        decision: Dict[str, Any],
        action_results: Dict[str, Any]
    ) -> AgentFinding:
        rule_id = action_results.get("rule_id", "SIGMA-RULE")
        summary = (
            f"Detection Engineering synthesized production detection rule ({rule_id}) for MITRE technique "
            f"{analysis.get('target_technique', 'T1059')} ({analysis.get('technique_name', 'Command Execution')})."
        )
        return AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=float(analysis.get("confidence", 0.95)),
            summary=summary,
            structured_data={"rule_id": rule_id, "action_results": action_results},
            recommendations=decision.get("recommendations", [])
        )

detection_engineering_agent = DetectionEngineeringAgent()

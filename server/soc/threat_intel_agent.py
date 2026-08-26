import re
import uuid
from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    IncidentContext,
    ThreatIntelResult,
    AgentFinding,
    AgentExecutionPhase,
    MitreAttackMapping
)
from server.soc.cti_feed import cti_feed_manager

class ThreatIntelAgent(BaseSocAgent):
    """
    Threat Intelligence Agent (CTI Specialist)
    Analyzes IOCs, domains, hashes, and IP addresses.
    Correlates with global CTI feeds, CVE databases, and adversary campaign tracking.
    """
    def __init__(self):
        super().__init__(
            name="threat_intel_agent",
            role_title="Cyber Threat Intelligence Specialist",
            description="Analyzes indicators of compromise, CVEs, reputation scores, and threat actor campaigns."
        )

    def analyze_indicator(self, ioc: str, ioc_type: Optional[str] = None) -> ThreatIntelResult:
        """Determines reputation, confidence score, and threat actor tags for any IOC"""
        if not ioc_type:
            if re.match(r'^(?:\d{1,3}\.){3}\d{1,3}$', ioc):
                ioc_type = "IP"
            elif re.match(r'^[a-fA-F0-9]{64}$', ioc) or re.match(r'^[a-fA-F0-9]{32}$', ioc):
                ioc_type = "SHA256"
            elif ioc.startswith("http://") or ioc.startswith("https://"):
                ioc_type = "URL"
            elif ioc.upper().startswith("CVE-"):
                ioc_type = "CVE"
            else:
                ioc_type = "DOMAIN"

        return cti_feed_manager._lookup_offline_heuristic(ioc, ioc_type)

    async def collect(self, context: IncidentContext, plan: List[str]) -> Dict[str, Any]:
        """Collects all IOCs from incident context and queries CTI intelligence"""
        analyzed_iocs: List[ThreatIntelResult] = []
        
        # 1. Inspect existing indicators
        for ind in context.indicators:
            res = self.analyze_indicator(ind.ioc, ind.ioc_type)
            analyzed_iocs.append(res)

        # 2. Extract IOCs from evidence chain strings
        for ev in context.evidence_chain:
            ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', ev)
            for ip in ips:
                if not ip.startswith("127.") and not ip.startswith("10.") and not ip.startswith("192.168."):
                    res = self.analyze_indicator(ip, "IP")
                    if res not in analyzed_iocs:
                        analyzed_iocs.append(res)

            hashes = re.findall(r'\b[a-fA-F0-9]{64}\b', ev)
            for h in hashes:
                res = self.analyze_indicator(h, "SHA256")
                if res not in analyzed_iocs:
                    analyzed_iocs.append(res)

        return {"analyzed_iocs": analyzed_iocs}

    def analyze(self, context: IncidentContext, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        iocs: List[ThreatIntelResult] = telemetry.get("analyzed_iocs", [])
        malicious_count = sum(1 for i in iocs if i.reputation in ["MALICIOUS", "SUSPICIOUS"])
        max_score = max([i.score for i in iocs], default=0)
        
        threat_actors = list(set([i.threat_actor for i in iocs if i.threat_actor]))
        
        # Update incident context indicators
        context.indicators = iocs
        
        return {
            "total_iocs": len(iocs),
            "malicious_iocs": malicious_count,
            "max_reputation_score": max_score,
            "threat_actors": threat_actors,
            "risk_level": "CRITICAL" if max_score >= 80 else "HIGH" if max_score >= 50 else "MEDIUM" if max_score >= 20 else "LOW",
            "confidence": 0.95 if malicious_count > 0 else 0.80
        }

    def decide(self, context: IncidentContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        recommendations = []
        if analysis.get("malicious_iocs", 0) > 0:
            recommendations.append("Block malicious IP/domain indicators across enterprise border firewalls.")
            recommendations.append("Quarantine files matching malicious SHA-256 signatures via EDR.")
        if analysis.get("threat_actors"):
            recommendations.append(f"Initiate targeted campaign hunt for known TTPs of {', '.join(analysis['threat_actors'])}.")
            
        return {
            "action": "UPDATE_CTI_ENRICHMENT",
            "requires_containment": analysis.get("malicious_iocs", 0) > 0,
            "recommendations": recommendations
        }

    def report(
        self,
        context: IncidentContext,
        analysis: Dict[str, Any],
        decision: Dict[str, Any],
        action_results: Dict[str, Any]
    ) -> AgentFinding:
        actors = ", ".join(analysis.get("threat_actors", [])) or "Unattributed Threat Actor"
        summary = (
            f"CTI correlation completed. {analysis.get('malicious_iocs', 0)} of {analysis.get('total_iocs', 0)} indicators "
            f"flagged malicious (Peak Threat Score: {analysis.get('max_reputation_score', 0)}/100). Actor attribution: {actors}."
        )
        
        iocs_list = [f"{i.ioc_type}:{i.ioc}" for i in context.indicators if i.reputation in ["MALICIOUS", "SUSPICIOUS"]]
        
        return AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=float(analysis.get("confidence", 0.90)),
            summary=summary,
            structured_data=analysis,
            iocs_identified=iocs_list,
            recommendations=decision.get("recommendations", [])
        )

threat_intel_agent = ThreatIntelAgent()

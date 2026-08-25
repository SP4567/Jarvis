import asyncio
import time
import socket
from typing import Set, Dict, Any, Optional
from server.config import settings
from server.soc.live_collector import live_host_collector
from server.soc.cti_feed import cti_feed_manager

class BackgroundSecurityMonitor:
    """
    Continuous Real-Time Endpoint Event Ingestion & Threat Detection Worker
    Monitors process creation, network connection changes, and Windows Event Logs in the background,
    correlating live telemetry with CTI feeds and feeding anomalies into the SOC Multi-Agent Pipeline.
    """
    def __init__(self):
        self.hostname = socket.gethostname()
        self.is_running = False
        self._seen_pids: Set[int] = set()
        self._seen_connections: Set[str] = set()
        self._last_event_time: Optional[str] = None

    async def start(self):
        """Starts the continuous background ingestion loop"""
        if self.is_running:
            return
        self.is_running = True
        print("[SOC Monitor] Background Real-Time Security Ingestion Worker started.")

        while self.is_running:
            try:
                from server.soc.soc_orchestrator import soc_orchestrator
                if soc_orchestrator.is_monitoring_active:
                    await self._ingest_cycle(soc_orchestrator)
            except Exception as e:
                print(f"[SOC Monitor] Ingestion cycle error: {e}")

            await asyncio.sleep(4.0)

    def stop(self):
        self.is_running = False

    async def _ingest_cycle(self, soc_orchestrator):
        # 1. Process Telemetry Ingestion & Diff
        procs = await asyncio.to_thread(live_host_collector.get_live_processes, 100)
        current_pids = {p["pid"] for p in procs if p.get("pid")}

        if self._seen_pids:
            new_pids = current_pids - self._seen_pids
            for p in procs:
                if p.get("pid") in new_pids and p.get("is_suspicious"):
                    raw_event = {
                        "source_type": "REALTIME_EDR_PROCESS_SPAWN",
                        "hostname": self.hostname,
                        "process_name": p.get("name"),
                        "command_line": p.get("cmdline"),
                        "user_identity": p.get("username"),
                        "raw_payload": p
                    }
                    soc_orchestrator.process_incoming_security_event(raw_event)
        self._seen_pids = current_pids

        # 2. Network Socket & CTI Threat Correlation
        conns = await asyncio.to_thread(live_host_collector.get_live_network_connections, 50)
        for c in conns:
            remote_ip = c.get("remote_ip")
            if remote_ip and c.get("status") in ["ESTABLISHED", "SYN_SENT"]:
                conn_key = f"{c.get('pid')}:{remote_ip}"
                if conn_key not in self._seen_connections:
                    self._seen_connections.add(conn_key)
                    # Check CTI
                    ti_res = await cti_feed_manager.lookup_ioc(remote_ip, "IP")
                    if ti_res.reputation in ["MALICIOUS", "SUSPICIOUS"]:
                        raw_event = {
                            "source_type": "REALTIME_NDR_SOCKET_BEACON",
                            "hostname": self.hostname,
                            "ip_address": remote_ip,
                            "process_name": c.get("process_name"),
                            "raw_payload": {"connection": c, "threat_intel": ti_res.model_dump()}
                        }
                        soc_orchestrator.process_incoming_security_event(raw_event)

        # Cap seen connections set size
        if len(self._seen_connections) > 1000:
            self._seen_connections.clear()

background_security_monitor = BackgroundSecurityMonitor()

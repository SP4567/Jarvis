import re
import uuid
import asyncio
import time
import ast
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field
from enum import Enum

from server.config import settings
from server.db.async_db import async_db

class SafetyTier(str, Enum):
    TIER_1_SAFE = "tier_1_safe"            # Read-only, queries, informational lookups
    TIER_2_SENSITIVE = "tier_2_sensitive"  # Non-destructive changes (launch app, volume, create note, sandboxed code write)
    TIER_3_DANGEROUS = "tier_3_dangerous"  # Potentially destructive (file delete, kill proc, shell execution, isolation)
    BLOCKED = "blocked"                    # Malicious or fatal commands (always rejected)

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPIRED = "expired"
    AUTO_EXECUTED = "auto_executed"

class GuardrailRequest(BaseModel):
    action_id: str
    tier: SafetyTier
    agent_name: str
    action_name: str
    description: str
    details: Dict[str, Any]
    target_resource: Optional[str] = None
    risk_level: str = "HIGH"  # SAFE | LOW | MEDIUM | HIGH | CRITICAL
    expected_impact: Optional[str] = None
    rollback_plan: Optional[str] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = Field(default_factory=time.time)
    timeout_seconds: int = 90
    reason: Optional[str] = None
    approver: Optional[str] = None
    requires_dual_approval: bool = False
    first_approver: Optional[str] = None
    modified_params: Optional[Dict[str, Any]] = None

class GuardrailEngine:
    """
    Enterprise Defense-in-Depth Security Guardrail Engine
    Features:
    - 4-Tier Granular Action Gate & Dual Approval Policy
    - Adversarial Prompt Injection & Jailbreak Sanitization
    - Python AST Syntax & Low-Level Exploit Inspection
    - Path Traversal & Critical Process Protection Allowlist
    - Dynamic Admin Action Modification Support
    - Cryptographically Hashed Tamper-Evident SHA-256 Audit Ledger
    """
    def __init__(self, strictness: str = "strict"):
        self.strictness = strictness
        self.pending_approvals: Dict[str, GuardrailRequest] = {}
        self.futures: Dict[str, asyncio.Future] = {}
        self.last_audit_hash: str = "GENESIS_HASH_JARVIS_SEC_00000000000000000000000000000000"
        self._lock = asyncio.Lock()
        
        # Absolute Blacklist Patterns - Never Allowed
        self.forbidden_patterns = [
            r"format\s+[a-zA-Z]:",
            r"rmdir\s+/[sS]\s+/[qQ]\s+c:\\",
            r"del\s+/[fF]\s+/[sS]\s+/[qQ]\s+c:\\windows",
            r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # Fork bomb
            r"reg\s+delete\s+hklm",
            r"diskpart",
            r"bcdedit",
            r"shutdown\s+/[sS]\s+/[fF]\s+/[tT]\s+0",
            r"vssadmin\s+delete\s+shadows",
        ]
        
        # Dangerous Action Indicators
        self.dangerous_patterns = [
            r"del\s+",
            r"remove-item",
            r"rmdir",
            r"taskkill\s+/f",
            r"stop-process\s+-force",
            r"powershell\s+-enc",
            r"drop\s+table",
            r"truncate\s+table",
            r"git\s+reset\s+--hard",
            r"git\s+clean\s+-fdx"
        ]

        # Protected Critical Windows System Processes (Prevent termination)
        self.protected_processes = {
            "csrss.exe", "lsass.exe", "smss.exe", "services.exe", "svchost.exe",
            "wininit.exe", "winlogon.exe", "dwm.exe", "explorer.exe", "system"
        }

        # Prompt Injection & Jailbreak Heuristics
        self.prompt_injection_patterns = [
            r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
            r"disregard\s+(all\s+)?(system|safety)\s+(prompts|rules)",
            r"you\s+are\s+now\s+DAN\b",
            r"act\s+as\s+(an?\s+)?unrestricted\s+(ai|assistant)",
            r"jailbreak\s+mode\s+enabled",
            r"bypass\s+(all\s+)?content\s+filters",
            r"developer\s+mode\s+enabled",
            r"pretend\s+to\s+have\s+no\s+(rules|limits|safety)",
        ]

    def sanitize_prompt_input(self, user_text: str) -> Tuple[bool, str, Optional[str]]:
        """Scans incoming user prompts for adversarial prompt injections, DAN exploits, and jailbreak attempts."""
        for pattern in self.prompt_injection_patterns:
            if re.search(pattern, user_text, re.IGNORECASE):
                threat_id = str(uuid.uuid4())[:8]
                asyncio.create_task(self._record_audit_log(
                    action_id=threat_id,
                    actor="PROMPT_SANITIZER",
                    agent_name="GuardrailEngine",
                    action_name="prompt_injection_interlock",
                    target="User Prompt",
                    details={"prompt": user_text},
                    tier=SafetyTier.BLOCKED,
                    status=ApprovalStatus.REJECTED,
                    reason=f"Matched prompt injection pattern: {pattern}"
                ))
                return False, f"SECURITY INTERLOCK: Adversarial prompt injection pattern detected ({pattern}). Instruction rejected.", "PROMPT_INJECTION"

        return True, user_text, None

    def validate_python_ast(self, code_str: str) -> Tuple[bool, str]:
        """AST safety check on Python code prior to execution to block forbidden low-level exploits."""
        try:
            tree = ast.parse(code_str)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ["ctypes", "_winapi", "win32api", "win32con"]:
                            return False, f"Unauthorized low-level memory library import: {alias.name}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module in ["ctypes", "_winapi", "win32api", "win32con"]:
                        return False, f"Unauthorized low-level module import: {node.module}"
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ["eval", "exec", "__import__"]:
                        return False, f"Dynamic code execution '{node.func.id}()' is forbidden in sandboxed scripts."
            return True, "AST Validation Passed"
        except SyntaxError as e:
            return False, f"Syntax Error: {str(e)}"
        except Exception as e:
            return False, f"AST Parse Error: {str(e)}"

    def validate_file_path(self, file_path_str: str) -> Tuple[bool, str]:
        """Validates that target file paths remain strictly inside the workspace boundary."""
        try:
            target = Path(file_path_str)
            if not target.is_absolute():
                target = (settings.WORKSPACE_ROOT / target).resolve()
            else:
                target = target.resolve()

            workspace = settings.WORKSPACE_ROOT.resolve()
            if not str(target).startswith(str(workspace)):
                return False, f"Path traversal attempt: Target path '{target}' is outside workspace boundary '{workspace}'."
            return True, str(target)
        except Exception as e:
            return False, f"Invalid path format: {str(e)}"

    def validate_process_target(self, process_name: Optional[str], pid: Optional[int]) -> Tuple[bool, str]:
        """Ensures critical OS system processes are protected against accidental kill commands."""
        if process_name and process_name.lower() in self.protected_processes:
            return False, f"SECURITY INTERLOCK: Process '{process_name}' is a protected core Windows system process and cannot be terminated."
        return True, "Target valid"

    def classify_action(self, agent_name: str, action_name: str, params: Dict[str, Any]) -> Tuple[SafetyTier, str]:
        """
        Classifies an agent action into a Safety Tier.
        Returns: (tier: SafetyTier, explanation: str)
        """
        param_str = str(params).lower()

        # 1. Absolute Blacklist
        for pattern in self.forbidden_patterns:
            if re.search(pattern, param_str, re.IGNORECASE):
                return SafetyTier.BLOCKED, f"Command contains strictly forbidden pattern: {pattern}"

        # 2. Critical Process Termination Protection
        if action_name == "kill_process":
            proc_name = params.get("process_name")
            pid = params.get("pid")
            is_valid, msg = self.validate_process_target(proc_name, pid)
            if not is_valid:
                return SafetyTier.BLOCKED, msg

        # 3. File Operations Path Validation
        if action_name in ["write_code_file", "read_code_file", "modify_code_file", "delete_file"]:
            filename = params.get("filename") or params.get("path")
            if filename:
                is_valid, msg = self.validate_file_path(filename)
                if not is_valid:
                    return SafetyTier.BLOCKED, msg

        # 4. Tier 3 Dangerous Actions (Requires Admin Approval)
        if action_name in ["execute_shell_command", "run_terminal_command"]:
            cmd = params.get("command") or params.get("code") or ""
            for pattern in self.dangerous_patterns:
                if re.search(pattern, cmd, re.IGNORECASE):
                    return SafetyTier.TIER_3_DANGEROUS, f"Command contains high-risk operation: {cmd[:60]}"
            if self.strictness == "strict":
                return SafetyTier.TIER_3_DANGEROUS, f"Terminal command execution requested: {cmd[:60]}"
            return SafetyTier.TIER_2_SENSITIVE, "Terminal command execution"

        if action_name in ["delete_file", "remove_directory", "kill_process", "wipe_database", "isolate_endpoint"]:
            return SafetyTier.TIER_3_DANGEROUS, f"Destructive operation '{action_name}'"

        if action_name == "execute_python_code":
            code = params.get("code") or ""
            for pattern in self.dangerous_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    return SafetyTier.TIER_3_DANGEROUS, f"Code contains high-risk pattern: {code[:60]}"
            return SafetyTier.TIER_2_SENSITIVE, "Sandboxed Python execution"

        # 5. Tier 2 Sensitive Actions (Auto-executed with Audit)
        if action_name in [
            "launch_application", "set_system_volume", "set_screen_brightness",
            "create_note", "delete_note", "update_note", "add_reminder", "delete_reminder",
            "create_calendar_event", "play_music", "play_youtube", "block_firewall_ioc",
            "write_code_file", "modify_code_file", "git_commit"
        ]:
            return SafetyTier.TIER_2_SENSITIVE, f"System modification / safe write: {action_name}"

        # 6. Tier 1 Safe Actions (Read-Only)
        return SafetyTier.TIER_1_SAFE, f"Read-only query or analysis: {action_name}"

    async def verify_and_authorize(
        self,
        agent_name: str,
        action_name: str,
        params: Dict[str, Any],
        description: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Evaluates action through guardrail tiers and executes human-in-the-loop interlock if dangerous.
        Returns: (is_allowed: bool, reason: str, action_id: Optional[str])
        """
        tier, reason = self.classify_action(agent_name, action_name, params)
        requires_dual = (action_name in ["isolate_endpoint", "wipe_database"] and settings.DUAL_APPROVAL_REQUIRED_TIER3)
        action_id = f"ACT-{uuid.uuid4().hex[:12].upper()}"

        # 1. BLOCKED
        if tier == SafetyTier.BLOCKED:
            await self._record_audit_log(action_id, "SYSTEM", agent_name, action_name, str(params), params, tier, ApprovalStatus.REJECTED, reason)
            return False, f"SECURITY INTERLOCK: Action strictly blocked by safety guardrails. Reason: {reason}", action_id

        # 2. TIER 1 - SAFE
        if tier == SafetyTier.TIER_1_SAFE:
            await self._record_audit_log(action_id, "SYSTEM", agent_name, action_name, str(params), params, tier, ApprovalStatus.APPROVED, reason)
            return True, "Authorized (Safe Operation)", action_id

        # 3. TIER 2 - SENSITIVE (Auto-approved if configured)
        if tier == SafetyTier.TIER_2_SENSITIVE:
            await self._record_audit_log(action_id, "POLICY_ENGINE", agent_name, action_name, str(params), params, tier, ApprovalStatus.AUTO_EXECUTED, reason)
            return True, "Authorized (Sensitive Operation Logged)", action_id

        # 4. TIER 3 - DANGEROUS (Requires Human Confirmation)
        target_res = params.get("filename") or params.get("process_name") or params.get("hostname") or params.get("command") or str(params)[:50]
        req = GuardrailRequest(
            action_id=action_id,
            tier=tier,
            agent_name=agent_name,
            action_name=action_name,
            description=description or reason,
            details=params,
            target_resource=str(target_res),
            risk_level="CRITICAL" if requires_dual else "HIGH",
            expected_impact=f"Execute {action_name} on target {target_res}",
            created_at=time.time(),
            timeout_seconds=settings.APPROVAL_TIMEOUT_SECONDS,
            reason=reason,
            requires_dual_approval=requires_dual
        )
        self.pending_approvals[action_id] = req
        
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self.futures[action_id] = future
        
        await self._record_audit_log(action_id, "OPERATOR_PENDING", agent_name, action_name, str(params), params, tier, ApprovalStatus.PENDING, reason)
        
        try:
            approved: bool = await asyncio.wait_for(future, timeout=req.timeout_seconds)
            if approved:
                req.status = ApprovalStatus.APPROVED
                await self._record_audit_log(action_id, req.approver or "OPERATOR", agent_name, action_name, str(params), params, tier, ApprovalStatus.APPROVED, "Authorized by user")
                return True, "Action authorized by administrator.", action_id
            else:
                req.status = ApprovalStatus.REJECTED
                await self._record_audit_log(action_id, req.approver or "OPERATOR", agent_name, action_name, str(params), params, tier, ApprovalStatus.REJECTED, "Denied by user")
                return False, "Action explicitly denied by administrator.", action_id
        except asyncio.TimeoutError:
            req.status = ApprovalStatus.EXPIRED
            await self._record_audit_log(action_id, "SYSTEM_TIMEOUT", agent_name, action_name, str(params), params, tier, ApprovalStatus.EXPIRED, "Confirmation Timeout")
            self.pending_approvals.pop(action_id, None)
            self.futures.pop(action_id, None)
            return False, "Security confirmation timed out. Action aborted.", action_id

    def resolve_action(
        self,
        action_id: str,
        approved: bool,
        approver: str = "OPERATOR",
        modified_params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Called by WebSocket or REST endpoint when user clicks Approve/Deny/Modify"""
        req = self.pending_approvals.get(action_id)
        if not req:
            return False

        if modified_params:
            req.modified_params = modified_params
            req.details = modified_params
            req.status = ApprovalStatus.MODIFIED

        if req.requires_dual_approval and approved:
            if not req.first_approver:
                req.first_approver = approver
                req.reason = f"Primary approval by {approver}. Dual confirmation required."
                return True
            elif req.first_approver == approver:
                return True

        req.approver = approver
        future = self.futures.get(action_id)
        if future and not future.done():
            future.set_result(approved)

        self.pending_approvals.pop(action_id, None)
        self.futures.pop(action_id, None)
        return True

    def resolve_latest_pending(self, approved: bool, approver: str = "VOICE_AUTHORIZATION") -> Optional[GuardrailRequest]:
        """Resolves the most recent pending guardrail action via voice or shortcut"""
        if not self.pending_approvals:
            return None
        latest_id = list(self.pending_approvals.keys())[-1]
        req = self.pending_approvals[latest_id]
        self.resolve_action(latest_id, approved, approver=approver)
        return req

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Returns list of currently pending guardrail confirmations"""
        return [req.model_dump() for req in self.pending_approvals.values()]

    async def _record_audit_log(
        self,
        action_id: str,
        actor: str,
        agent_name: str,
        action_name: str,
        target: str,
        details: Dict[str, Any],
        tier: SafetyTier,
        status: ApprovalStatus,
        reason: str
    ):
        """Calculates cryptographic SHA-256 hash chaining and stores immutable ledger entry in SQLite."""
        async with self._lock:
            now = time.time()
            payload_str = f"{self.last_audit_hash}|{action_id}|{now}|{actor}|{action_name}|{tier.value}|{status.value}|{reason}"
            current_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
            prev_hash = self.last_audit_hash
            self.last_audit_hash = current_hash

            try:
                await async_db.execute("""
                    INSERT INTO security_audit_ledger (action_id, timestamp, actor, action_name, target, details, tier, status, reason, previous_hash, current_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    action_id,
                    now,
                    actor,
                    action_name,
                    str(target)[:200],
                    json.dumps(details) if isinstance(details, dict) else str(details),
                    tier.value,
                    status.value,
                    reason,
                    prev_hash,
                    current_hash
                ))
            except Exception as e:
                print(f"[GuardrailEngine] Error writing audit log: {e}")

guardrail_engine = GuardrailEngine(strictness=settings.GUARDRAIL_STRICTNESS)


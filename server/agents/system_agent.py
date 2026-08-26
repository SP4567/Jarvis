import os
import subprocess
import psutil
import time
import shutil
import math
import ast
import operator
import platform
import socket
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from server.agents.base_agent import BaseAgent
from server.config import settings
from server.core.tool_registry import tool_registry
from server.core.models import TaskPlan, PlanStep, VerificationResult

class SystemAgent(BaseAgent):
    """
    JARVIS System & OS Controller Agent 3.0
    Comprehensive Windows OS Orchestrator:
    Vitals, Process Trees, Network Interfaces, Storage Analytics, Clipboard, Shell Automation, World Clock & Advanced Math
    """
    def __init__(self):
        super().__init__(
            name="system_agent",
            display_name="System & OS Controller",
            description="Manages Windows OS vitals, application launching, volume control, process tree inspection, network interfaces, disk analytics, clipboard, math evaluation, and shell execution."
        )
        self._register_all_tools()

    def register_tool(self, name: str, func, schema: Dict[str, Any]):
        super().register_tool(name, func, schema)
        tool_registry.register_tool(
            name=name,
            func=func,
            description=schema.get("description", ""),
            parameters=schema,
            agent_name=self.name
        )

    def _register_all_tools(self):
        # 1. System Vitals
        self.register_tool(
            "get_system_vitals",
            self.get_system_vitals,
            {
                "type": "object",
                "description": "Get real-time CPU, RAM, Disk, and Battery diagnostics for the host machine.",
                "properties": {}
            }
        )
        
        # 2. Launch App
        self.register_tool(
            "launch_application",
            self.launch_application,
            {
                "type": "object",
                "description": "Launch a Windows application by name (e.g. 'chrome', 'notepad', 'calculator', 'vscode', 'spotify', 'explorer', 'cmd', 'powershell').",
                "properties": {
                    "app_name": {"type": "string", "description": "Name or executable of the application to open."}
                },
                "required": ["app_name"]
            }
        )
        
        # 3. Volume Control
        self.register_tool(
            "set_system_volume",
            self.set_system_volume,
            {
                "type": "object",
                "description": "Adjust Windows system volume level (0 to 100) or toggle mute.",
                "properties": {
                    "level": {"type": "integer", "description": "Volume percentage from 0 to 100."},
                    "mute": {"type": "boolean", "description": "Whether to mute audio."}
                }
            }
        )
        
        # 4. List Processes
        self.register_tool(
            "list_running_processes",
            self.list_running_processes,
            {
                "type": "object",
                "description": "List top active processes sorted by memory or CPU usage.",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of processes to return (default 10)."},
                    "sort_by": {"type": "string", "enum": ["memory", "cpu", "name"], "description": "Sorting metric."}
                }
            }
        )

        # 5. Inspect Process Tree
        self.register_tool(
            "inspect_process_tree",
            self.inspect_process_tree,
            {
                "type": "object",
                "description": "Inspect detailed process hierarchy, threads, memory, and status for a PID or process name.",
                "properties": {
                    "process_name": {"type": "string", "description": "Name of the process to inspect."},
                    "pid": {"type": "integer", "description": "PID of the process."}
                }
            }
        )

        # 6. Kill Process (Tier 3 Guardrailed)
        self.register_tool(
            "kill_process",
            self.kill_process,
            {
                "type": "object",
                "description": "Terminate a process by name or PID with graceful shutdown and force fallback. Requires security confirmation.",
                "properties": {
                    "process_name": {"type": "string", "description": "Name of the process (e.g. 'notepad.exe')."},
                    "pid": {"type": "integer", "description": "Process ID to terminate."},
                    "force": {"type": "boolean", "description": "Force terminate immediately."}
                }
            }
        )

        # 7. Disk Storage Info
        self.register_tool(
            "get_disk_storage_info",
            self.get_disk_storage_info,
            {
                "type": "object",
                "description": "Get detailed disk partition usage, storage distribution, and available free space across all drives.",
                "properties": {}
            }
        )

        # 8. Network Interfaces
        self.register_tool(
            "get_network_interfaces",
            self.get_network_interfaces,
            {
                "type": "object",
                "description": "Get network interface configurations, active IP addresses, MAC addresses, and network status.",
                "properties": {}
            }
        )

        # 9. Manage Clipboard
        self.register_tool(
            "manage_clipboard",
            self.manage_clipboard,
            {
                "type": "object",
                "description": "Read from or write text to the Windows system clipboard.",
                "properties": {
                    "action": {"type": "string", "enum": ["read", "write", "clear"], "description": "Clipboard action."},
                    "text": {"type": "string", "description": "Text to write to clipboard if action is write."}
                },
                "required": ["action"]
            }
        )

        # 10. Math Calculation
        self.register_tool(
            "calculate_math",
            self.calculate_math,
            {
                "type": "object",
                "description": "Evaluate an arithmetic or mathematical expression securely (supports trigonometry, log, sqrt, powers).",
                "properties": {
                    "expression": {"type": "string", "description": "Mathematical expression to evaluate (e.g. 'sqrt(144) + 8', '25 * 4', 'sin(0.5)')."}
                },
                "required": ["expression"]
            }
        )

        # 11. Convert Units
        self.register_tool(
            "convert_units",
            self.convert_units,
            {
                "type": "object",
                "description": "Convert values between physical and computational units (temperature, distance, weight, digital storage).",
                "properties": {
                    "value": {"type": "number", "description": "Numeric value to convert."},
                    "from_unit": {"type": "string", "description": "Original unit (e.g. 'km', 'miles', 'celsius', 'fahrenheit', 'kg', 'lbs', 'gb', 'mb')."},
                    "to_unit": {"type": "string", "description": "Target unit."}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        )

        # 12. Global Time / World Clock
        self.register_tool(
            "get_global_time",
            self.get_global_time,
            {
                "type": "object",
                "description": "Get the current time and date for any major world city or timezone.",
                "properties": {
                    "location": {"type": "string", "description": "City or timezone name (e.g. 'London', 'Tokyo', 'New York', 'Sydney', 'Paris', 'UTC')."}
                },
                "required": ["location"]
            }
        )

        # 13. System Info Summary
        self.register_tool(
            "get_system_info_summary",
            self.get_system_info_summary,
            {
                "type": "object",
                "description": "Get high-level summary of OS version, architecture, CPU model, hostname, and platform specifications.",
                "properties": {}
            }
        )

        # 14. Execute Shell Command (Tier 3 Guardrailed)
        self.register_tool(
            "execute_shell_command",
            self.execute_shell_command,
            {
                "type": "object",
                "description": "Execute a Windows PowerShell / CMD command with security interlock.",
                "properties": {
                    "command": {"type": "string", "description": "PowerShell command to execute."}
                },
                "required": ["command"]
            }
        )

    # --- Tool Implementations ---

    def calculate_math(self, expression: str) -> Dict[str, Any]:
        """Safely evaluates an arithmetic expression using AST parsing"""
        clean_expr = expression.lower().replace("calculate", "").replace("what is", "").replace("evaluate", "").strip()
        
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        functions = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "abs": abs,
            "round": round,
            "pow": math.pow,
            "exp": math.exp,
            "floor": math.floor,
            "ceil": math.ceil
        }

        def eval_node(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                op_type = type(node.op)
                if op_type in operators:
                    return operators[op_type](left, right)
                raise ValueError(f"Unsupported operator: {op_type}")
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                op_type = type(node.op)
                if op_type in operators:
                    return operators[op_type](operand)
                raise ValueError(f"Unsupported unary operator: {op_type}")
            elif isinstance(node, ast.Call):
                func_name = node.func.id if isinstance(node.func, ast.Name) else None
                if func_name in functions:
                    args = [eval_node(arg) for arg in node.args]
                    return functions[func_name](*args)
                raise ValueError(f"Unsupported function: {func_name}")
            else:
                raise ValueError(f"Unsupported AST expression: {node}")

        try:
            tree = ast.parse(clean_expr, mode='eval')
            val = eval_node(tree.body)
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            return {
                "success": True,
                "expression": clean_expr,
                "result": f"The answer to {clean_expr} is {val}, Sir.",
                "value": val
            }
        except Exception as e:
            return {"success": False, "error": f"Math calculation failed: {str(e)}", "result": f"Calculation error for expression: {clean_expr}"}

    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Converts between units"""
        fu = from_unit.lower().strip()
        tu = to_unit.lower().strip()
        converted = value
        unit_label = tu

        # Temperature
        if fu in ["celsius", "c"] and tu in ["fahrenheit", "f"]:
            converted = (value * 9/5) + 32
            unit_label = "Fahrenheit"
        elif fu in ["fahrenheit", "f"] and tu in ["celsius", "c"]:
            converted = (value - 32) * 5/9
            unit_label = "Celsius"
        elif fu in ["celsius", "c"] and tu in ["kelvin", "k"]:
            converted = value + 273.15
            unit_label = "Kelvin"
        # Distance
        elif fu in ["mile", "miles"] and tu in ["km", "kilometer", "kilometers"]:
            converted = value * 1.60934
            unit_label = "kilometers"
        elif fu in ["km", "kilometer", "kilometers"] and tu in ["mile", "miles"]:
            converted = value * 0.621371
            unit_label = "miles"
        elif fu in ["meter", "meters", "m"] and tu in ["feet", "ft"]:
            converted = value * 3.28084
            unit_label = "feet"
        elif fu in ["feet", "ft"] and tu in ["meter", "meters", "m"]:
            converted = value * 0.3048
            unit_label = "meters"
        # Weight
        elif fu in ["kg", "kilogram", "kilograms"] and tu in ["pound", "pounds", "lbs"]:
            converted = value * 2.20462
            unit_label = "pounds"
        elif fu in ["pound", "pounds", "lbs"] and tu in ["kg", "kilogram", "kilograms"]:
            converted = value * 0.453592
            unit_label = "kilograms"
        # Digital Storage
        elif fu in ["gb", "gigabytes"] and tu in ["mb", "megabytes"]:
            converted = value * 1024
            unit_label = "MB"
        elif fu in ["mb", "megabytes"] and tu in ["gb", "gigabytes"]:
            converted = value / 1024
            unit_label = "GB"
        elif fu in ["tb", "terabytes"] and tu in ["gb", "gigabytes"]:
            converted = value * 1024
            unit_label = "GB"

        res_str = f"{value:g} {from_unit} is equal to {converted:.2f} {unit_label}, Sir."
        return {
            "success": True,
            "original_value": value,
            "converted_value": round(converted, 4),
            "from_unit": from_unit,
            "to_unit": unit_label,
            "result": res_str
        }

    def get_global_time(self, location: str) -> Dict[str, Any]:
        """Calculates global time across world cities"""
        now = datetime.now()
        loc = location.lower().strip()
        
        # Offsets relative to local IST (+5:30) or UTC
        offsets = {
            "london": -4.5,
            "uk": -4.5,
            "new york": -9.5,
            "nyc": -9.5,
            "san francisco": -12.5,
            "tokyo": 3.5,
            "japan": 3.5,
            "sydney": 5.5,
            "australia": 5.5,
            "paris": -3.5,
            "berlin": -3.5,
            "dubai": -1.5,
            "singapore": 2.5,
            "utc": -5.5
        }
        
        target_offset = 0.0
        found_key = "Local"
        for k, off in offsets.items():
            if k in loc:
                target_offset = off
                found_key = k.title()
                break
                
        target_dt = now + timedelta(hours=target_offset)
        time_str = target_dt.strftime("%I:%M %p")
        date_str = target_dt.strftime("%A, %B %d, %Y")
        
        return {
            "success": True,
            "location": location,
            "resolved_city": found_key,
            "time": time_str,
            "date": date_str,
            "message": f"The current time in {found_key} is {time_str} ({date_str}), Sir."
        }

    def get_system_vitals(self) -> Dict[str, Any]:
        """Collects host diagnostics"""
        cpu_pct = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")
        
        battery_info = None
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_info = {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "seconds_left": battery.secsleft if battery.secsleft != -1 else "Calculating/Plugged in"
                }
        except Exception:
            battery_info = None

        return {
            "cpu_percent": cpu_pct,
            "cpu_count": psutil.cpu_count(logical=True),
            "ram_percent": mem.percent,
            "ram_used_gb": round(mem.used / (1024**3), 2),
            "ram_total_gb": round(mem.total / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "battery": battery_info,
            "boot_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.boot_time()))
        }

    def get_system_info_summary(self) -> Dict[str, Any]:
        """Returns detailed host OS & platform specs"""
        return {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }

    def get_disk_storage_info(self) -> Dict[str, Any]:
        """Returns partition information across all mounted drives"""
        partitions = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent_used": usage.percent
                })
            except (PermissionError, OSError):
                continue
        return {"partitions": partitions}

    def get_network_interfaces(self) -> Dict[str, Any]:
        """Returns network interface information"""
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        interfaces = []
        for iface_name, addr_list in addrs.items():
            stat = stats.get(iface_name)
            ip_info = []
            for a in addr_list:
                if a.family == socket.AF_INET:
                    ip_info.append({"ip": a.address, "netmask": a.netmask})
            if ip_info:
                interfaces.append({
                    "interface": iface_name,
                    "is_up": stat.isup if stat else False,
                    "speed_mbps": stat.speed if stat else 0,
                    "ipv4": ip_info
                })
        return {"interfaces": interfaces}

    def manage_clipboard(self, action: str, text: Optional[str] = None) -> Dict[str, Any]:
        """Interacts with Windows clipboard using PowerShell"""
        act = action.lower()
        if act == "read":
            try:
                res = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "Get-Clipboard"], capture_output=True, text=True, timeout=3)
                clip_text = res.stdout.strip()
                return {"success": True, "action": "read", "content": clip_text}
            except Exception as e:
                return {"success": False, "error": str(e)}
        elif act == "write":
            if not text:
                return {"success": False, "error": "No text provided to write."}
            try:
                ps_cmd = f"Set-Clipboard -Value @'\n{text}\n'@"
                subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, timeout=3)
                return {"success": True, "action": "write", "message": "Text copied to system clipboard."}
            except Exception as e:
                return {"success": False, "error": str(e)}
        elif act == "clear":
            try:
                subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "Set-Clipboard -Value $null"], capture_output=True, timeout=3)
                return {"success": True, "action": "clear", "message": "Clipboard cleared."}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": f"Unknown action: {action}"}

    def launch_application(self, app_name: str) -> Dict[str, Any]:
        """Launches a desktop application on Windows"""
        app_clean = app_name.lower().strip()
        app_map = {
            "chrome": ["cmd.exe", "/c", "start", "chrome"],
            "google chrome": ["cmd.exe", "/c", "start", "chrome"],
            "edge": ["cmd.exe", "/c", "start", "msedge"],
            "microsoft edge": ["cmd.exe", "/c", "start", "msedge"],
            "vscode": ["cmd.exe", "/c", "code"],
            "vs code": ["cmd.exe", "/c", "code"],
            "code": ["cmd.exe", "/c", "code"],
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "calc": ["calc.exe"],
            "spotify": ["cmd.exe", "/c", "start", "spotify"],
            "explorer": ["explorer.exe"],
            "file explorer": ["explorer.exe"],
            "files": ["explorer.exe"],
            "terminal": ["wt.exe"],
            "windows terminal": ["wt.exe"],
            "cmd": ["cmd.exe", "/c", "start", "cmd.exe"],
            "powershell": ["cmd.exe", "/c", "start", "powershell.exe"],
            "task manager": ["taskmgr.exe"],
            "settings": ["cmd.exe", "/c", "start", "ms-settings:"]
        }

        cmd_args = app_map.get(app_clean, ["cmd.exe", "/c", "start", app_clean])
        try:
            subprocess.Popen(cmd_args, shell=False)
            return {"success": True, "message": f"Successfully initiated launch for '{app_name}'."}
        except Exception as e:
            return {"success": False, "error": f"Failed to launch '{app_name}': {str(e)}"}

    def set_system_volume(self, level: Optional[int] = None, mute: Optional[bool] = None) -> str:
        """Adjusts volume using PowerShell Audio controls"""
        try:
            if level is not None:
                level = max(0, min(100, level))
                ps_script = f"""
                $obj = New-Object -ComObject WScript.Shell
                for ($i=0; $i -lt 50; $i++) {{ $obj.SendKeys([char]174) }}
                for ($i=0; $i -lt {int(level / 2)}; $i++) {{ $obj.SendKeys([char]175) }}
                """
                subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script], capture_output=True, timeout=5)
                return f"System audio volume set to approximately {level}%."
            elif mute is not None:
                ps_script = "$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys([char]173)"
                subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script], capture_output=True, timeout=5)
                return f"System mute toggled."
            return "No volume change parameter specified."
        except Exception as e:
            return f"Volume adjustment error: {str(e)}"

    def list_running_processes(self, limit: int = 10, sort_by: str = "memory") -> List[Dict[str, Any]]:
        """Returns highest memory or CPU processes"""
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                procs.append({
                    "pid": p.info['pid'],
                    "name": p.info['name'],
                    "cpu_percent": p.info.get('cpu_percent', 0.0) or 0.0,
                    "memory_percent": round(p.info.get('memory_percent', 0.0) or 0.0, 1),
                    "status": p.info.get('status', 'running')
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        sort_key = 'cpu_percent' if sort_by == 'cpu' else 'memory_percent'
        procs.sort(key=lambda x: x.get(sort_key, 0.0), reverse=True)
        return procs[:limit]

    def inspect_process_tree(self, process_name: Optional[str] = None, pid: Optional[int] = None) -> Dict[str, Any]:
        """Inspects detailed process metadata and children"""
        try:
            target_proc = None
            if pid:
                target_proc = psutil.Process(pid)
            elif process_name:
                for p in psutil.process_iter(['pid', 'name']):
                    if p.info['name'].lower() == process_name.lower():
                        target_proc = p
                        break
            if not target_proc:
                return {"success": False, "error": f"Process '{process_name or pid}' not found."}

            with target_proc.oneshot():
                return {
                    "success": True,
                    "pid": target_proc.pid,
                    "name": target_proc.name(),
                    "status": target_proc.status(),
                    "cpu_percent": target_proc.cpu_percent(),
                    "memory_mb": round(target_proc.memory_info().rss / (1024*1024), 2),
                    "num_threads": target_proc.num_threads(),
                    "num_handles": target_proc.num_handles() if hasattr(target_proc, 'num_handles') else None,
                    "create_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(target_proc.create_time())),
                    "children": [c.pid for c in target_proc.children(recursive=True)]
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def kill_process(self, process_name: Optional[str] = None, pid: Optional[int] = None, force: bool = False) -> str:
        """Kills targeted process safely with force fallback"""
        killed_count = 0
        if pid:
            try:
                p = psutil.Process(pid)
                p_name = p.name()
                if force:
                    p.kill()
                else:
                    p.terminate()
                return f"Process {p_name} (PID: {pid}) terminated successfully."
            except Exception as e:
                return f"Failed to terminate PID {pid}: {str(e)}"
        
        if process_name:
            for p in psutil.process_iter(['pid', 'name']):
                try:
                    if p.info['name'].lower() == process_name.lower():
                        if force:
                            p.kill()
                        else:
                            p.terminate()
                        killed_count += 1
                except Exception:
                    continue
            return f"Terminated {killed_count} instances of '{process_name}'."
        return "Please specify process_name or pid to terminate."

    def execute_shell_command(self, command: str) -> Dict[str, Any]:
        """Runs a shell command safely"""
        try:
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(settings.WORKSPACE_ROOT)
            )
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:1000]
            }
        except subprocess.TimeoutExpired:
            return {"exit_code": -1, "stdout": "", "stderr": "Command execution timed out after 15 seconds."}
        except Exception as e:
            return {"exit_code": -1, "stdout": "", "stderr": str(e)}

    # --- Autonomous Planning & Verification Hooks ---

    async def verify_tool_execution(self, tool_name: str, params: Dict[str, Any], result: Dict[str, Any]) -> VerificationResult:
        """Domain-specific verification for OS actions"""
        if not result.get("success", True) and result.get("exit_code", 0) != 0:
            return VerificationResult(
                verified=False,
                verdict=f"System operation '{tool_name}' failed.",
                details=result
            )

        if tool_name == "kill_process":
            pid = params.get("pid")
            if pid:
                still_alive = psutil.pid_exists(pid)
                return VerificationResult(
                    verified=not still_alive,
                    verdict="Process confirmed terminated." if not still_alive else "Process still alive.",
                    details={"pid": pid, "terminated": not still_alive}
                )

        return VerificationResult(
            verified=True,
            verdict=f"System action '{tool_name}' completed successfully.",
            details={"tool": tool_name}
        )

    async def formulate_plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> TaskPlan:
        """Formulates OS task plan"""
        q = query.lower()
        steps = []
        if "diagnostics" in q or "vitals" in q or "status" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Query system vitals and diagnostic telemetry",
                agent_name=self.name,
                tool_name="get_system_vitals",
                params={}
            ))
        elif "process" in q and "inspect" in q:
            steps.append(PlanStep(
                step_number=1,
                description="List running processes",
                agent_name=self.name,
                tool_name="list_running_processes",
                params={"limit": 10}
            ))
        elif "storage" in q or "disk" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Inspect disk storage info",
                agent_name=self.name,
                tool_name="get_disk_storage_info",
                params={}
            ))
        elif "network" in q or "ip" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Inspect network interfaces",
                agent_name=self.name,
                tool_name="get_network_interfaces",
                params={}
            ))

        return TaskPlan(
            plan_id=f"PLAN-SYS-{int(time.time())}",
            goal=query,
            initiating_agent=self.name,
            steps=steps
        )

system_agent = SystemAgent()

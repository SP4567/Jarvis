import os
import subprocess
import psutil
import time
import shutil
import math
import ast
import operator
from typing import Dict, Any, Optional, List
from server.agents.base_agent import BaseAgent
from server.config import settings
from server.core.tool_registry import tool_registry

class SystemAgent(BaseAgent):
    """
    JARVIS System & OS Controller Agent for Windows Automation and Telemetry
    """
    def __init__(self):
        super().__init__(
            name="system_agent",
            display_name="System & OS Controller",
            description="Manages Windows OS vitals, application launching, volume control, process management, math evaluation, and terminal execution."
        )
        self._register_all_tools()

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
                "description": "List top active processes sorted by memory/CPU usage.",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of processes to return (default 10)."}
                }
            }
        )
        
        # 5. Math Calculation
        self.register_tool(
            "calculate_math",
            self.calculate_math,
            {
                "type": "object",
                "description": "Evaluate an arithmetic or mathematical expression securely.",
                "properties": {
                    "expression": {"type": "string", "description": "Mathematical expression to evaluate (e.g. 'sqrt(144) + 8', '25 * 4')."}
                },
                "required": ["expression"]
            }
        )

        # 6. Kill Process (Tier 3 Guardrailed)
        self.register_tool(
            "kill_process",
            self.kill_process,
            {
                "type": "object",
                "description": "Terminate a process by name or PID. Requires security confirmation.",
                "properties": {
                    "process_name": {"type": "string", "description": "Name of the process (e.g. 'notepad.exe')."},
                    "pid": {"type": "integer", "description": "Process ID to terminate."}
                }
            }
        )
        
        # 7. Execute Shell Command (Tier 3 Guardrailed)
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

    def register_tool(self, name: str, func, schema: Dict[str, Any]):
        super().register_tool(name, func, schema)
        tool_registry.register_tool(
            name=name,
            func=func,
            description=schema.get("description", ""),
            parameters=schema,
            agent_name=self.name
        )

    def calculate_math(self, expression: str) -> Dict[str, Any]:
        """Safely evaluates an arithmetic expression using AST parsing"""
        clean_expr = expression.lower().replace("calculate", "").replace("what is", "").replace("evaluate", "").strip()
        
        # Allowed operators & functions
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
            "pow": math.pow
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

    def launch_application(self, app_name: str) -> Dict[str, Any]:
        """Launches a desktop application on Windows using parameterized arguments (no shell=True)"""
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
        """Adjusts volume using PowerShell Audio controls without shell=True"""
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

    def list_running_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns highest memory processes"""
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append({
                    "pid": p.info['pid'],
                    "name": p.info['name'],
                    "cpu_percent": p.info.get('cpu_percent', 0.0) or 0.0,
                    "memory_percent": round(p.info.get('memory_percent', 0.0) or 0.0, 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x['memory_percent'], reverse=True)
        return procs[:limit]

    def kill_process(self, process_name: Optional[str] = None, pid: Optional[int] = None) -> str:
        """Kills targeted process safely"""
        killed_count = 0
        if pid:
            try:
                p = psutil.Process(pid)
                p_name = p.name()
                p.terminate()
                return f"Process {p_name} (PID: {pid}) terminated successfully."
            except Exception as e:
                return f"Failed to terminate PID {pid}: {str(e)}"
        
        if process_name:
            for p in psutil.process_iter(['pid', 'name']):
                try:
                    if p.info['name'].lower() == process_name.lower():
                        p.terminate()
                        killed_count += 1
                except Exception:
                    continue
            return f"Terminated {killed_count} instances of '{process_name}'."
        return "Please specify process_name or pid to terminate."

    def execute_shell_command(self, command: str) -> Dict[str, Any]:
        """Runs a shell command safely without shell=True"""
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

system_agent = SystemAgent()

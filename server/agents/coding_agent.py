import sys
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional
from server.agents.base_agent import BaseAgent
from server.config import settings
from server.core.tool_registry import tool_registry

class CodingAgent(BaseAgent):
    """
    JARVIS Developer, Code Writing, Execution & Workspace Specialist
    """
    def __init__(self):
        super().__init__(
            name="coding_agent",
            display_name="Developer & Terminal Assistant",
            description="Writes code files, generates algorithms, executes Python scratchpad scripts, and checks Git repositories."
        )
        self._register_all_tools()

    def _register_all_tools(self):
        # 1. Execute Python Code (Tier 3 Guardrailed)
        self.register_tool(
            "execute_python_code",
            self.execute_python_code,
            {
                "type": "object",
                "description": "Execute a Python script or calculation safely in a sandboxed subprocess.",
                "properties": {
                    "code": {"type": "string", "description": "Python source code to execute."}
                },
                "required": ["code"]
            }
        )
        
        # 2. Write Code to File
        self.register_tool(
            "write_code_file",
            self.write_code_file,
            {
                "type": "object",
                "description": "Create or write code to a file in the workspace.",
                "properties": {
                    "filename": {"type": "string", "description": "Name or relative path of the file (e.g. 'script.py', 'server.js')."},
                    "code": {"type": "string", "description": "The complete source code to write."}
                },
                "required": ["filename", "code"]
            }
        )

        # 3. Read Code File
        self.register_tool(
            "read_code_file",
            self.read_code_file,
            {
                "type": "object",
                "description": "Read the contents of a code file in the workspace.",
                "properties": {
                    "filename": {"type": "string", "description": "Name or relative path of the file to read."}
                },
                "required": ["filename"]
            }
        )
        
        # 4. Git Status
        self.register_tool(
            "get_git_status",
            self.get_git_status,
            {
                "type": "object",
                "description": "Inspect git status, current branch, and unstaged changes in the project workspace.",
                "properties": {}
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

    def write_code_file(self, filename: str, code: str) -> Dict[str, Any]:
        """Writes code to a workspace file safely"""
        try:
            from server.core.guardrails import guardrail_engine
            is_valid, target_path_str = guardrail_engine.validate_file_path(filename)
            if not is_valid:
                return {"success": False, "error": target_path_str}

            target_path = Path(target_path_str)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(code)
            return {
                "success": True,
                "path": str(target_path),
                "filename": target_path.name,
                "bytes_written": len(code.encode("utf-8")),
                "message": f"Successfully created code file '{target_path.name}'."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_code_file(self, filename: str) -> Dict[str, Any]:
        """Reads code from a workspace file"""
        try:
            from server.core.guardrails import guardrail_engine
            is_valid, target_path_str = guardrail_engine.validate_file_path(filename)
            if not is_valid:
                return {"success": False, "error": target_path_str}

            target_path = Path(target_path_str)
            if not target_path.exists():
                return {"success": False, "error": f"File '{target_path.name}' does not exist."}
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "success": True,
                "filename": target_path.name,
                "content": content[:4000],
                "lines": len(content.splitlines())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_python_code(self, code: str) -> Dict[str, Any]:
        """Runs Python code in a separate process with AST security validation"""
        from server.core.guardrails import guardrail_engine
        is_safe, ast_msg = guardrail_engine.validate_python_ast(code)
        if not is_safe:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Security Interlock: Code failed AST validation: {ast_msg}"
            }

        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
                tf.write(code)
                temp_filename = tf.name

            try:
                result = subprocess.run(
                    [sys.executable, temp_filename],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=str(settings.WORKSPACE_ROOT)
                )
                return {
                    "exit_code": result.returncode,
                    "stdout": result.stdout[:2000],
                    "stderr": result.stderr[:1000]
                }
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        except subprocess.TimeoutExpired:
            return {"exit_code": -1, "stdout": "", "stderr": "Script execution timed out after 10 seconds."}
        except Exception as e:
            return {"exit_code": -1, "stdout": "", "stderr": str(e)}

    def get_git_status(self) -> Dict[str, Any]:
        """Checks git repository state"""
        try:
            res = subprocess.run(
                ["git", "status", "--short", "--branch"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(settings.WORKSPACE_ROOT)
            )
            return {
                "exit_code": res.returncode,
                "output": res.stdout or res.stderr or "No git changes detected."
            }
        except Exception as e:
            return {"error": f"Git command failed: {str(e)}"}

coding_agent = CodingAgent()

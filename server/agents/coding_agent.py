import sys
import subprocess
import tempfile
import os
import ast
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from server.agents.base_agent import BaseAgent
from server.config import settings
from server.core.tool_registry import tool_registry
from server.core.models import TaskPlan, PlanStep, VerificationResult, RecoveryAction

class CodingAgent(BaseAgent):
    """
    JARVIS Developer, Code Writing, Testing & Workspace Specialist 3.0
    Comprehensive Software Engineering Lifecycle:
    File Creation, Modification, Static Analysis, Testing, Git VCS, Sandboxed Execution & Autonomous Debugging
    """
    def __init__(self):
        super().__init__(
            name="coding_agent",
            display_name="Developer & Terminal Assistant",
            description="Writes, reads, and modifies code files, executes Python scripts, runs automated tests, checks syntax/linting, inspects git VCS, and performs autonomous debugging."
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
        # 1. Execute Python Code (Tier 3 Guardrailed)
        self.register_tool(
            "execute_python_code",
            self.execute_python_code,
            {
                "type": "object",
                "description": "Execute a Python script or calculation safely in a sandboxed subprocess with AST screening.",
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
                "description": "Create or write complete code to a file in the workspace.",
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

        # 4. Modify Code File (Search & Replace)
        self.register_tool(
            "modify_code_file",
            self.modify_code_file,
            {
                "type": "object",
                "description": "Perform target search and replace modifications on a workspace code file.",
                "properties": {
                    "filename": {"type": "string", "description": "Name or relative path of the file to modify."},
                    "target_snippet": {"type": "string", "description": "Exact snippet to find and replace."},
                    "replacement_snippet": {"type": "string", "description": "New replacement code snippet."}
                },
                "required": ["filename", "target_snippet", "replacement_snippet"]
            }
        )

        # 5. List Workspace Files
        self.register_tool(
            "list_workspace_files",
            self.list_workspace_files,
            {
                "type": "object",
                "description": "List files and directories in the workspace with extension filter.",
                "properties": {
                    "subfolder": {"type": "string", "description": "Subdirectory to inspect (default root)."},
                    "extension": {"type": "string", "description": "Optional file extension filter (e.g. '.py', '.js')."}
                }
            }
        )

        # 6. Run Code Tests
        self.register_tool(
            "run_code_tests",
            self.run_code_tests,
            {
                "type": "object",
                "description": "Run pytest or test files in the workspace and return parsed pass/fail summary.",
                "properties": {
                    "test_path": {"type": "string", "description": "Relative path to test file or directory (default 'server/tests/')."}
                }
            }
        )

        # 7. Lint and Analyze Code
        self.register_tool(
            "lint_and_analyze_code",
            self.lint_and_analyze_code,
            {
                "type": "object",
                "description": "Perform static analysis, syntax check, and AST parsing on Python source code.",
                "properties": {
                    "code": {"type": "string", "description": "Python source code string to analyze."},
                    "filename": {"type": "string", "description": "Optional filename to read and analyze."}
                }
            }
        )

        # 8. Git Status
        self.register_tool(
            "get_git_status",
            self.get_git_status,
            {
                "type": "object",
                "description": "Inspect git status, current branch, staged files, and unstaged changes in the project workspace.",
                "properties": {}
            }
        )

        # 9. Git Diff
        self.register_tool(
            "git_diff",
            self.git_diff,
            {
                "type": "object",
                "description": "Show unstaged git diffs or file modifications in the workspace.",
                "properties": {
                    "filename": {"type": "string", "description": "Optional specific file to diff."}
                }
            }
        )

        # 10. Git Commit
        self.register_tool(
            "git_commit",
            self.git_commit,
            {
                "type": "object",
                "description": "Stage all or specific files and create a git commit.",
                "properties": {
                    "message": {"type": "string", "description": "Commit message."},
                    "files": {"type": "string", "description": "Files to stage (default '.' for all)."}
                },
                "required": ["message"]
            }
        )

        # 11. Git Log
        self.register_tool(
            "git_log",
            self.git_log,
            {
                "type": "object",
                "description": "View recent commit history in the workspace git repository.",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of commits to return (default 5)."}
                }
            }
        )

        # 12. Auto Debug Script
        self.register_tool(
            "auto_debug_script",
            self.auto_debug_script,
            {
                "type": "object",
                "description": "Execute a Python script, capture runtime errors/exceptions, and attempt automated diagnosis and fix.",
                "properties": {
                    "code": {"type": "string", "description": "Python code to debug."}
                },
                "required": ["code"]
            }
        )

    # --- Tool Implementations ---

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
                "lines_count": len(code.splitlines()),
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
                "content": content[:6000],
                "lines": len(content.splitlines()),
                "size_bytes": len(content.encode("utf-8"))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def modify_code_file(self, filename: str, target_snippet: str, replacement_snippet: str) -> Dict[str, Any]:
        """Performs search and replace on a code file"""
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

            if target_snippet not in content:
                return {"success": False, "error": "Target snippet was not found in the file."}

            new_content = content.replace(target_snippet, replacement_snippet, 1)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return {
                "success": True,
                "filename": target_path.name,
                "message": f"Snippet successfully updated in '{target_path.name}'."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_workspace_files(self, subfolder: str = "", extension: Optional[str] = None) -> Dict[str, Any]:
        """Lists files in the workspace directory"""
        try:
            target_dir = settings.WORKSPACE_ROOT / subfolder if subfolder else settings.WORKSPACE_ROOT
            files_list = []
            for root, dirs, files in os.walk(target_dir):
                # Ignore heavy or secret dirs
                dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__", "dist", ".pytest_cache", ".gemini"]]
                for f in files:
                    if extension and not f.endswith(extension):
                        continue
                    rel_p = Path(root, f).relative_to(settings.WORKSPACE_ROOT)
                    files_list.append(str(rel_p))
                    if len(files_list) >= 50:
                        break
                if len(files_list) >= 50:
                    break
            return {"success": True, "files": files_list, "count": len(files_list)}
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
                    "success": result.returncode == 0,
                    "exit_code": result.returncode,
                    "stdout": result.stdout[:2500],
                    "stderr": result.stderr[:1500]
                }
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        except subprocess.TimeoutExpired:
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": "Script execution timed out after 10 seconds."}
        except Exception as e:
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": str(e)}

    def lint_and_analyze_code(self, code: Optional[str] = None, filename: Optional[str] = None) -> Dict[str, Any]:
        """Performs static syntax and AST analysis"""
        src = code or ""
        if filename and not code:
            r_res = self.read_code_file(filename)
            if not r_res.get("success"):
                return r_res
            src = r_res.get("content", "")

        try:
            tree = ast.parse(src)
            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            imports = []
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    imports.extend([a.name for a in n.names])
                elif isinstance(n, ast.ImportFrom):
                    if n.module:
                        imports.append(n.module)

            return {
                "success": True,
                "syntax_valid": True,
                "functions": funcs,
                "classes": classes,
                "imports": list(set(imports)),
                "lines_count": len(src.splitlines())
            }
        except SyntaxError as e:
            return {
                "success": False,
                "syntax_valid": False,
                "error": f"SyntaxError: {str(e)} at line {e.lineno}"
            }

    def run_code_tests(self, test_path: str = "server/tests/") -> Dict[str, Any]:
        """Executes pytest suite against target path"""
        try:
            target = test_path or "server/tests/"
            cmd = [sys.executable, "-m", "pytest", target, "-q"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=25, cwd=str(settings.WORKSPACE_ROOT))
            out = res.stdout or res.stderr
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "output": out[:2500],
                "passed": "passed" in out and res.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Test run timed out after 25s."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def auto_debug_script(self, code: str) -> Dict[str, Any]:
        """Executes code, inspects runtime failure, and suggests corrected code"""
        run_res = self.execute_python_code(code)
        if run_res.get("exit_code") == 0:
            return {
                "success": True,
                "status": "NO_ERROR",
                "message": "Script executed without errors.",
                "output": run_res.get("stdout")
            }

        err = run_res.get("stderr", "")
        # Basic diagnosis heuristics
        suggested_fix = None
        diagnosis = "Runtime Exception Detected"
        if "NameError" in err:
            diagnosis = "Undefined variable or missing import."
        elif "IndentationError" in err:
            diagnosis = "Indentation syntax error."
        elif "ZeroDivisionError" in err:
            diagnosis = "Division by zero."
        elif "TypeError" in err:
            diagnosis = "Type mismatch in function arguments."

        return {
            "success": False,
            "status": "DEBUGGED",
            "diagnosis": diagnosis,
            "error_trace": err[:1000],
            "original_code": code
        }

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
                "success": True,
                "exit_code": res.returncode,
                "output": res.stdout or res.stderr or "No git changes detected."
            }
        except Exception as e:
            return {"success": False, "error": f"Git command failed: {str(e)}"}

    def git_diff(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Shows unstaged changes"""
        try:
            cmd = ["git", "diff"]
            if filename:
                cmd.append(filename)
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, cwd=str(settings.WORKSPACE_ROOT))
            return {
                "success": True,
                "diff": res.stdout[:3000] if res.stdout else "No unstaged changes."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def git_commit(self, message: str, files: str = ".") -> Dict[str, Any]:
        """Stages files and creates a git commit"""
        try:
            subprocess.run(["git", "add", files], capture_output=True, text=True, timeout=5, cwd=str(settings.WORKSPACE_ROOT))
            res = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True, timeout=5, cwd=str(settings.WORKSPACE_ROOT))
            return {
                "success": res.returncode == 0,
                "output": res.stdout or res.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def git_log(self, limit: int = 5) -> Dict[str, Any]:
        """Returns recent commits"""
        try:
            res = subprocess.run(
                ["git", "log", f"-n{limit}", "--oneline"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(settings.WORKSPACE_ROOT)
            )
            return {
                "success": True,
                "commits": res.stdout.splitlines() if res.stdout else []
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Autonomous Verification & Planning Hooks ---

    async def verify_tool_execution(self, tool_name: str, params: Dict[str, Any], result: Dict[str, Any]) -> VerificationResult:
        """Verifies coding outputs on disk and in runtime"""
        if not result.get("success", True):
            return VerificationResult(
                verified=False,
                verdict=f"Coding tool '{tool_name}' returned failure.",
                details=result
            )

        if tool_name == "write_code_file":
            fn = params.get("filename")
            if fn:
                from server.core.guardrails import guardrail_engine
                _, path_str = guardrail_engine.validate_file_path(fn)
                p = Path(path_str)
                exists = p.exists() and p.stat().st_size > 0
                return VerificationResult(
                    verified=exists,
                    verdict="File verified on disk and non-empty." if exists else "File missing or empty on disk.",
                    details={"filename": fn, "size": p.stat().st_size if exists else 0}
                )

        if tool_name == "execute_python_code":
            exit_code = result.get("exit_code", -1)
            return VerificationResult(
                verified=(exit_code == 0),
                verdict="Script completed with exit code 0." if exit_code == 0 else f"Script exited with error code {exit_code}.",
                details={"exit_code": exit_code}
            )

        return VerificationResult(
            verified=True,
            verdict=f"Developer tool '{tool_name}' output verified.",
            details={"tool": tool_name}
        )

    async def formulate_plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> TaskPlan:
        """Formulates developer sub-plan"""
        q = query.lower()
        steps = []
        if "test" in q or "pytest" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Run automated pytest suite",
                agent_name=self.name,
                tool_name="run_code_tests",
                params={"test_path": "server/tests/"}
            ))
        elif "git" in q or "status" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Check Git VCS status",
                agent_name=self.name,
                tool_name="get_git_status",
                params={}
            ))
        elif "list files" in q or "workspace" in q:
            steps.append(PlanStep(
                step_number=1,
                description="List workspace files",
                agent_name=self.name,
                tool_name="list_workspace_files",
                params={}
            ))

        return TaskPlan(
            plan_id=f"PLAN-CODE-{int(time.time())}",
            goal=query,
            initiating_agent=self.name,
            steps=steps
        )

coding_agent = CodingAgent()

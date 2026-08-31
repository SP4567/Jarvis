import ast
import time
import uuid
import inspect
from typing import Dict, Any, List, Optional, Callable
from server.core.models import SynthesizedTool, SafetyTier
from server.core.tool_registry import tool_registry

class ToolSynthesizer:
    """
    JARVIS-V2 Autonomous Dynamic Tool Synthesizer.
    Enables agents to write, validate, sandbox-test, and register novel runtime capabilities
    on-the-fly when standard tools are insufficient.
    """

    def __init__(self):
        self.synthesized_tools: Dict[str, SynthesizedTool] = {}
        self.forbidden_calls = {
            "eval", "exec", "compile", "__import__", "globals", "locals",
            "os.system", "shutil.rmtree", "subprocess.call"
        }

    def validate_ast_security(self, code_str: str) -> tuple[bool, str]:
        """
        Performs static AST validation to ensure the synthesized code is safe
        and contains no malicious bypasses.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError as se:
            return False, f"Syntax Error: {str(se)}"

        for node in ast.walk(tree):
            # Check forbidden function calls
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        func_name = f"{node.func.value.id}.{node.func.attr}"

                if func_name in self.forbidden_calls:
                    return False, f"Security Violation: Forbidden call '{func_name}' detected."

            # Disallow direct private/magic attributes tampering
            if isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr.endswith("__"):
                if node.attr not in ("__name__", "__doc__"):
                    return False, f"Security Violation: Magic attribute '{node.attr}' access blocked."

        return True, "AST Security Validation Passed."

    async def execute_in_sandbox(
        self,
        code_str: str,
        entry_func: str,
        test_cases: List[Dict[str, Any]]
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Compiles and tests the synthesized function against provided test cases in a sandbox.
        """
        safe_globals = {
            "__builtins__": {
                "range": range,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "min": min,
                "max": max,
                "sum": sum,
                "round": round,
                "abs": abs,
                "print": print,
                "Exception": Exception,
                "ValueError": ValueError,
                "TypeError": TypeError,
                "KeyError": KeyError,
                "IndexError": IndexError
            }
        }
        local_scope: Dict[str, Any] = {}

        try:
            exec(code_str, safe_globals, local_scope)
        except Exception as e:
            return False, {"error": f"Compilation failed: {str(e)}"}

        if entry_func not in local_scope:
            return False, {"error": f"Entry function '{entry_func}' not found in synthesized code."}

        func = local_scope[entry_func]
        results = []

        for idx, tc in enumerate(test_cases):
            inputs = tc.get("inputs", {})
            expected = tc.get("expected")
            try:
                if inspect.iscoroutinefunction(func):
                    res = await func(**inputs)
                else:
                    res = func(**inputs)

                passed = True
                if expected is not None:
                    passed = (res == expected)

                results.append({
                    "test_case": idx + 1,
                    "inputs": inputs,
                    "output": res,
                    "expected": expected,
                    "passed": passed
                })
            except Exception as ex:
                results.append({
                    "test_case": idx + 1,
                    "inputs": inputs,
                    "error": str(ex),
                    "passed": False
                })

        all_passed = all(r.get("passed", False) for r in results) if results else True
        return all_passed, {"test_cases": results, "all_passed": all_passed}

    async def synthesize_and_register(
        self,
        name: str,
        description: str,
        parameters_schema: Dict[str, Any],
        python_code: str,
        entry_func: str,
        test_cases: List[Dict[str, Any]],
        created_by: str = "coding_agent",
        safety_tier: SafetyTier = SafetyTier.TIER_1_SAFE
    ) -> tuple[bool, Optional[SynthesizedTool], str]:
        """
        End-to-end synthesis pipeline: AST check -> Sandbox test -> Dynamic tool registration.
        """
        tool_id = f"synth_{uuid.uuid4().hex[:8]}"

        # 1. AST Static Security Check
        ast_ok, ast_msg = self.validate_ast_security(python_code)
        if not ast_ok:
            return False, None, f"AST Security Check Failed: {ast_msg}"

        # 2. Sandbox Verification
        sb_ok, sb_res = await self.execute_in_sandbox(python_code, entry_func, test_cases)
        if not sb_ok:
            return False, None, f"Sandbox Test Execution Failed: {sb_res.get('error', 'Test case mismatch')}"

        # 3. Create execution wrapper for ToolRegistry
        safe_globals = {
            "__builtins__": {
                "range": range, "len": len, "str": str, "int": int, "float": float,
                "bool": bool, "list": list, "dict": dict, "set": set, "tuple": tuple,
                "min": min, "max": max, "sum": sum, "round": round, "abs": abs,
                "print": print, "Exception": Exception, "ValueError": ValueError
            }
        }
        local_scope: Dict[str, Any] = {}
        exec(python_code, safe_globals, local_scope)
        executable_func = local_scope[entry_func]

        async def dynamic_tool_wrapper(**kwargs):
            if inspect.iscoroutinefunction(executable_func):
                return await executable_func(**kwargs)
            return executable_func(**kwargs)

        # 4. Register dynamically into JARVIS tool registry
        tool_registry.register_tool(
            name=name,
            func=dynamic_tool_wrapper,
            description=description,
            parameters=parameters_schema,
            agent_name=created_by
        )

        synth_tool = SynthesizedTool(
            tool_id=tool_id,
            name=name,
            description=description,
            parameters_schema=parameters_schema,
            python_code=python_code,
            verified_ast=True,
            sandbox_tested=True,
            test_results=sb_res,
            created_by=created_by
        )
        self.synthesized_tools[name] = synth_tool

        return True, synth_tool, f"Synthesized tool '{name}' successfully verified and registered into runtime fleet."

tool_synthesizer = ToolSynthesizer()

import pytest
import asyncio
from server.core.dag_planner import dag_planner
from server.core.tool_synthesizer import tool_synthesizer
from server.core.vision_grounding import vision_grounding_engine
from server.core.knowledge_graph import knowledge_graph
from server.core.desktop_controller import desktop_controller
from server.soc.kernel_etw_monitor import kernel_etw_monitor
from server.core.orchestrator import orchestrator
from server.core.models import ExecutionLifecycleState, SafetyTier

@pytest.mark.asyncio
async def test_dag_planner_cycle_detection_and_concurrency():
    """Verifies DAG cycle detection and concurrent multi-branch execution."""
    # 1. Test cycle detection
    cyclic_nodes = [
        {"node_id": "a", "description": "Step A", "dependencies": ["b"]},
        {"node_id": "b", "description": "Step B", "dependencies": ["a"]}
    ]
    with pytest.raises(ValueError, match="Invalid DAG"):
        dag_planner.create_dag_plan(goal="Cyclic Goal", nodes_definition=cyclic_nodes)

    # 2. Test valid parallel DAG execution
    valid_nodes = [
        {"node_id": "root", "description": "Fetch Vitals", "agent_name": "system_agent", "tool_name": "get_system_vitals", "dependencies": []},
        {"node_id": "math_branch", "description": "Compute Math", "agent_name": "system_agent", "tool_name": "calculate_math", "params": {"expression": "25 * 4"}, "dependencies": ["root"]},
        {"node_id": "time_branch", "description": "Get Time", "agent_name": "system_agent", "tool_name": "get_global_time", "params": {"location": "Tokyo"}, "dependencies": ["root"]}
    ]
    plan = dag_planner.create_dag_plan(goal="Multi-branch Test", nodes_definition=valid_nodes)
    res = await dag_planner.execute_dag(plan)

    assert res.success is True
    assert len(plan.completed_nodes) == 3
    assert plan.status == ExecutionLifecycleState.VERIFIED

@pytest.mark.asyncio
async def test_tool_synthesizer_ast_security_and_sandbox():
    """Verifies AST security checks, sandbox compilation, and dynamic registration."""
    # 1. Test AST security rejection of forbidden calls
    malicious_code = """
def evil_tool(cmd: str):
    import os
    os.system(cmd)
    return "executed"
"""
    ast_ok, msg = tool_synthesizer.validate_ast_security(malicious_code)
    assert ast_ok is False
    assert "Forbidden call" in msg

    # 2. Test safe tool synthesis & registration
    safe_code = """
def calculate_discount(price: float, discount_pct: float) -> float:
    final_price = price - (price * (discount_pct / 100.0))
    return round(final_price, 2)
"""
    success, synth_tool, msg = await tool_synthesizer.synthesize_and_register(
        name="calculate_discount",
        description="Calculates discounted price from percentage",
        parameters_schema={"type": "object", "properties": {"price": {"type": "number"}, "discount_pct": {"type": "number"}}},
        python_code=safe_code,
        entry_func="calculate_discount",
        test_cases=[
            {"inputs": {"price": 100.0, "discount_pct": 20.0}, "expected": 80.0},
            {"inputs": {"price": 50.0, "discount_pct": 10.0}, "expected": 45.0}
        ]
    )

    assert success is True
    assert synth_tool is not None
    assert synth_tool.name == "calculate_discount"
    assert synth_tool.verified_ast is True
    assert synth_tool.sandbox_tested is True

def test_vision_grounding_ocr_and_coordinates():
    """Verifies screen vision analysis, token coordinate grounding, and error detection."""
    sample_screen_text = "Traceback (most recent call last):\n  File 'app.py', line 12\nZeroDivisionError: division by zero"
    analysis = vision_grounding_engine.analyze_screen_telemetry(
        window_title="Debug Console - VS Code",
        ocr_text_override=sample_screen_text
    )

    assert analysis.active_window_title == "Debug Console - VS Code"
    assert len(analysis.detected_errors) > 0
    assert "ZeroDivisionError" in analysis.detected_errors[0] or "Traceback" in analysis.detected_errors[0]
    assert len(analysis.detected_elements) > 0

    bbox = vision_grounding_engine.get_grounding_coordinates("ZeroDivisionError")
    assert bbox is not None
    assert bbox.width > 0

def test_knowledge_graph_4_tier_hybrid_search():
    """Verifies entity-relation graph modeling and token overlap hybrid search."""
    knowledge_graph.add_entity(
        name="Production Database",
        entity_type="server",
        properties={"host": "10.0.0.5", "port": 5432, "engine": "PostgreSQL"}
    )
    knowledge_graph.add_relation("JARVIS Core", "Production Database", "MONITORS")

    results = knowledge_graph.search_knowledge_hybrid("PostgreSQL server")
    assert len(results) > 0
    assert any(r["entity"]["name"] == "Production Database" for r in results)

    related = knowledge_graph.get_related_entities("Production Database")
    assert len(related) > 0

def test_desktop_controller_and_action_journal():
    """Verifies fast file search, window enumeration, action recording, and rollback."""
    # 1. File search
    files = desktop_controller.search_local_files("main.py", limit=5)
    assert len(files) > 0
    assert any("main.py" in f["name"] for f in files)

    # 2. Window list
    windows = desktop_controller.get_open_windows()
    assert isinstance(windows, list)

    # 3. Action journal & rollback
    entry = desktop_controller.record_action(
        agent_name="system_agent",
        action_type="UPDATE_CONFIG",
        description="Updated telemetry refresh interval to 1s",
        reversible=True
    )
    assert entry.status == "EXECUTED"

    success, msg = desktop_controller.rollback_last_action()
    assert success is True
    assert "Successfully rolled back" in msg

def test_kernel_etw_monitor_and_memory_injection():
    """Verifies live kernel event tracing and process memory scan heuristics."""
    events = kernel_etw_monitor.inspect_live_kernel_telemetry()
    assert len(events) > 0

    mem_scan = kernel_etw_monitor.detect_memory_injection(1000)
    assert "memory_injection_detected" in mem_scan

@pytest.mark.asyncio
async def test_orchestrator_v2_unified_dispatch():
    """Verifies unified Orchestrator V2 endpoints (DAG execution, vision, knowledge search)."""
    # 1. Knowledge search
    k_res = orchestrator.search_knowledge_graph("Suyash")
    assert len(k_res) > 0

    # 2. Desktop vision
    v_res = orchestrator.inspect_desktop_vision()
    assert v_res.screen_width > 0

    # 3. DAG execution through orchestrator
    dag_res = await orchestrator.execute_dag_workflow(
        goal="Unified DAG Pipeline Test",
        nodes=[
            {"node_id": "n1", "description": "Fetch Vitals", "agent_name": "system_agent", "tool_name": "get_system_vitals", "dependencies": []}
        ]
    )
    assert dag_res.success is True

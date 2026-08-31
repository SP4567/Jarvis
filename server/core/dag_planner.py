import time
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Set, Callable
from server.core.models import (
    DAGTaskPlan,
    DAGNode,
    ExecutionLifecycleState,
    AgentThought,
    VerificationResult,
    CommandResponse
)
from server.core.tool_registry import tool_registry
from server.core.agent_registry import agent_registry

class DAGPlanner:
    """
    JARVIS-V2 Dynamic Directed Acyclic Graph (DAG) Task Planner.
    Supports concurrent branch execution, dynamic topological sorting,
    intermediate context propagation, dependency resolution, and self-healing.
    """

    def __init__(self):
        self.active_plans: Dict[str, DAGTaskPlan] = {}

    def create_dag_plan(
        self,
        goal: str,
        nodes_definition: List[Dict[str, Any]],
        initiating_agent: str = "orchestrator",
        concurrency_limit: int = 4
    ) -> DAGTaskPlan:
        """
        Creates a DAG task plan from node definitions.
        Validates acyclicity and structural integrity.
        """
        plan_id = f"dag_{uuid.uuid4().hex[:8]}"
        nodes: Dict[str, DAGNode] = {}

        for nd in nodes_definition:
            node_id = nd.get("node_id") or f"node_{len(nodes) + 1}"
            nodes[node_id] = DAGNode(
                node_id=node_id,
                description=nd.get("description", ""),
                agent_name=nd.get("agent_name", "system_agent"),
                tool_name=nd.get("tool_name"),
                params=nd.get("params", {}),
                dependencies=nd.get("dependencies", []),
                expected_outcome=nd.get("expected_outcome")
            )

        # Validate DAG (ensure no cycles)
        if not self._is_valid_dag(nodes):
            raise ValueError(f"Invalid DAG: Cycle detected in node dependencies.")

        plan = DAGTaskPlan(
            plan_id=plan_id,
            goal=goal,
            initiating_agent=initiating_agent,
            nodes=nodes,
            concurrency_limit=concurrency_limit,
            status=ExecutionLifecycleState.PLANNED
        )
        self.active_plans[plan_id] = plan
        return plan

    def _is_valid_dag(self, nodes: Dict[str, DAGNode]) -> bool:
        """Checks for cycles using Kahn's algorithm (Topological Sort)"""
        in_degree: Dict[str, int] = {nid: 0 for nid in nodes}
        adj_list: Dict[str, List[str]] = {nid: [] for nid in nodes}

        for nid, node in nodes.items():
            for dep in node.dependencies:
                if dep in nodes:
                    adj_list[dep].append(nid)
                    in_degree[nid] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for neighbor in adj_list[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return visited_count == len(nodes)

    def get_ready_nodes(self, plan: DAGTaskPlan) -> List[DAGNode]:
        """Returns list of nodes whose dependencies are all completed and are still in PLANNED state."""
        ready = []
        completed_set = set(plan.completed_nodes)

        for node_id, node in plan.nodes.items():
            if node.status == ExecutionLifecycleState.PLANNED:
                # Check if all dependencies are satisfied
                if all(dep in completed_set for dep in node.dependencies):
                    ready.append(node)

        return ready

    async def execute_dag(
        self,
        plan: DAGTaskPlan,
        session_id: str = "default",
        thought_callback: Optional[Callable[[AgentThought], None]] = None
    ) -> CommandResponse:
        """
        Executes the DAG plan concurrently by resolving dependencies iteratively.
        Propagates intermediate outputs across nodes.
        """
        start_time = time.time()
        plan.status = ExecutionLifecycleState.ATTEMPTING
        context_accumulator: Dict[str, Any] = {}
        all_executed_actions = []
        all_verifications = []

        semaphore = asyncio.Semaphore(plan.concurrency_limit)

        async def execute_single_node(node: DAGNode):
            async with semaphore:
                node.start_time = time.time()
                node.status = ExecutionLifecycleState.ATTEMPTING

                if thought_callback:
                    thought_callback(AgentThought(
                        step=len(plan.completed_nodes) + 1,
                        agent_name=node.agent_name,
                        thought=f"Executing DAG Node '{node.node_id}': {node.description}",
                        tool_name=node.tool_name,
                        state=ExecutionLifecycleState.ATTEMPTING
                    ))

                # Resolve parameter references (e.g. $nodes.node_1.result or $context.key)
                resolved_params = dict(node.params)
                for k, v in resolved_params.items():
                    if isinstance(v, str) and v.startswith("$nodes."):
                        parts = v.split(".")
                        src_node_id = parts[1]
                        if src_node_id in plan.nodes and plan.nodes[src_node_id].result is not None:
                            src_res = plan.nodes[src_node_id].result
                            if isinstance(src_res, dict) and len(parts) > 2:
                                subkey = parts[2]
                                resolved_params[k] = str(src_res.get(subkey, src_res))
                            else:
                                resolved_params[k] = str(src_res)
                    elif isinstance(v, str) and v.startswith("$context."):
                        ctx_key = v.replace("$context.", "")
                        if ctx_key in context_accumulator:
                            resolved_params[k] = str(context_accumulator[ctx_key])

                # Execute tool if present
                agent = agent_registry.get_agent(node.agent_name)
                if node.tool_name:
                    tool_res = await tool_registry.execute_tool(
                        tool_name=node.tool_name,
                        params=resolved_params,
                        session_id=session_id
                    )

                    # Verify execution if agent is registered
                    if agent:
                        ver = await agent.verify_tool_execution(
                            tool_name=node.tool_name,
                            params=resolved_params,
                            result=tool_res.result if isinstance(tool_res.result, dict) else {"result": tool_res.result}
                        )
                        node.verification = ver.dict()
                        all_verifications.append(ver)
                    else:
                        node.verification = {"verified": tool_res.success, "verdict": "Self-checked"}

                    if tool_res.success:
                        node.status = ExecutionLifecycleState.VERIFIED
                        node.result = tool_res.result
                        context_accumulator[node.node_id] = tool_res.result
                        plan.completed_nodes.append(node.node_id)
                    else:
                        node.status = ExecutionLifecycleState.FAILED
                        node.error = tool_res.error or "Tool execution failed"
                        plan.failed_nodes.append(node.node_id)

                    all_executed_actions.append({
                        "node_id": node.node_id,
                        "agent": node.agent_name,
                        "tool": node.tool_name,
                        "result": tool_res.result,
                        "verified": node.status == ExecutionLifecycleState.VERIFIED
                    })
                else:
                    # No tool, pure reasoning step
                    node.status = ExecutionLifecycleState.VERIFIED
                    node.result = {"status": "Reasoning step completed"}
                    plan.completed_nodes.append(node.node_id)

                node.end_time = time.time()

        # Dynamic execution loop
        while True:
            ready_nodes = self.get_ready_nodes(plan)
            if not ready_nodes:
                # Check if all completed or blocked
                all_done = all(
                    n.status in (ExecutionLifecycleState.VERIFIED, ExecutionLifecycleState.FAILED, ExecutionLifecycleState.BLOCKED)
                    for n in plan.nodes.values()
                )
                if all_done or len(ready_nodes) == 0:
                    break

            # Run all currently ready nodes in parallel
            await asyncio.gather(*(execute_single_node(node) for node in ready_nodes))

        # Check for unexecuted nodes due to dependency failures
        for node_id, node in plan.nodes.items():
            if node.status == ExecutionLifecycleState.PLANNED:
                node.status = ExecutionLifecycleState.BLOCKED
                node.error = "Upstream dependency failed"
                plan.failed_nodes.append(node_id)

        plan.status = (
            ExecutionLifecycleState.VERIFIED
            if len(plan.failed_nodes) == 0
            else ExecutionLifecycleState.FAILED
        )

        latency = (time.time() - start_time) * 1000.0

        summary_lines = [f"Goal: {plan.goal}", f"Status: {plan.status.value.upper()}"]
        for nid, n in plan.nodes.items():
            summary_lines.append(f" • [{nid}] {n.description} -> {n.status.value.upper()}")

        return CommandResponse(
            success=plan.status == ExecutionLifecycleState.VERIFIED,
            text="\n".join(summary_lines),
            agent_used=plan.initiating_agent,
            actions=all_executed_actions,
            dag_plan=plan,
            verification_results=all_verifications,
            latency_ms=round(latency, 2)
        )

dag_planner = DAGPlanner()

import pytest
import asyncio
import os
from server.agents.system_agent import system_agent
from server.agents.coding_agent import coding_agent
from server.agents.research_agent import research_agent
from server.agents.productivity_agent import productivity_agent
from server.agents.media_agent import media_agent
from server.agents.vision_agent import vision_agent
from server.core.orchestrator import orchestrator
from server.core.models import TaskPlan, PlanStep, AgentStatus
from server.core.guardrails import guardrail_engine

@pytest.mark.asyncio
async def test_system_agent_math_and_units():
    res_math = system_agent.calculate_math('sqrt(144) + 8')
    assert res_math['success'] is True
    assert res_math['value'] == 20

    res_unit = system_agent.convert_units(10, 'km', 'miles')
    assert res_unit['success'] is True
    assert round(res_unit['converted_value'], 1) == 6.2

    res_time = system_agent.get_global_time('Tokyo')
    assert res_time['success'] is True
    assert 'Tokyo' in res_time['resolved_city']

    specs = system_agent.get_system_info_summary()
    assert 'os' in specs
    storage = system_agent.get_disk_storage_info()
    assert 'partitions' in storage

@pytest.mark.asyncio
async def test_coding_agent_lifecycle_and_verification():
    test_filename = 'temp_test_module.py'
    code_content = 'def hello():\n    return 42\n'
    
    w_res = coding_agent.write_code_file(test_filename, code_content)
    assert w_res['success'] is True

    ver_res = await coding_agent.verify_tool_execution('write_code_file', {'filename': test_filename}, w_res)
    assert ver_res.verified is True

    r_res = coding_agent.read_code_file(test_filename)
    assert r_res['success'] is True
    assert 'hello' in r_res['content']

    m_res = coding_agent.modify_code_file(test_filename, '42', '100')
    assert m_res['success'] is True
    r_res2 = coding_agent.read_code_file(test_filename)
    assert '100' in r_res2['content']

    lint_res = coding_agent.lint_and_analyze_code(filename=test_filename)
    assert lint_res['success'] is True
    assert 'hello' in lint_res['functions']

    exec_res = coding_agent.execute_python_code('print(2 + 2)')
    assert exec_res['success'] is True
    assert '4' in exec_res['stdout']

    if os.path.exists(test_filename):
        os.remove(test_filename)

@pytest.mark.asyncio
async def test_research_agent_robots_compliance():
    allowed, reason = await research_agent.check_robots_allowed('https://example.com/test')
    assert isinstance(allowed, bool)

    wiki_res = await research_agent.lookup_wikipedia('Python (programming language)')
    assert wiki_res['success'] is True
    assert 'Python' in wiki_res['title']

    comp_res = await research_agent.comprehensive_research('Alan Turing')
    assert comp_res['success'] is True
    assert len(comp_res['spoken_answer']) > 0

@pytest.mark.asyncio
async def test_productivity_agent_extended_capabilities():
    n_res = productivity_agent.create_note('Test Note Alpha', 'Quantum computing research notes.', 'quantum,ai')
    assert n_res['success'] is True
    note_id = n_res['note_id']

    r_res = productivity_agent.add_reminder('Review codebase architecture', due_time='Tomorrow', priority='high')
    assert r_res['success'] is True
    assert r_res['priority'] == 'high'

    c_res = productivity_agent.create_calendar_event('Team Sync', '2026-08-27 15:00', location='HUD Conference')
    assert c_res['success'] is True
    assert len(productivity_agent.list_calendar_events()) > 0

    chk_res = productivity_agent.manage_todo_checklist('Project Orion', 'create')
    assert chk_res['success'] is True
    add_res = productivity_agent.manage_todo_checklist('Project Orion', 'add_item', item_text='Refactor Agents')
    assert len(add_res['items']) == 1
    done_res = productivity_agent.manage_todo_checklist('Project Orion', 'check_item', item_index=0)
    assert done_res['items'][0]['done'] is True

    briefing = productivity_agent.get_daily_briefing()
    assert briefing['success'] is True
    assert 'briefing_summary' in briefing

@pytest.mark.asyncio
async def test_media_and_vision_agents():
    yt_res = await media_agent.play_youtube('synthwave chill')
    assert yt_res['success'] is True
    assert len(yt_res['video_id']) == 11

    playlist_res = media_agent.create_hud_playlist(['Track 1', 'Track 2'])
    assert playlist_res['queued_count'] == 2

    sfx_res = media_agent.play_sound_effect('startup')
    assert sfx_res['success'] is True

    ss_res = vision_agent.take_screenshot('test_snap.png')
    assert ss_res['success'] is True
    if os.path.exists(ss_res['saved_to']):
        os.remove(ss_res['saved_to'])

@pytest.mark.asyncio
async def test_autonomous_solve_task_lifecycle():
    plan_query = 'What is 500 * 25?'
    resp = await system_agent.solve_task(plan_query)
    assert resp.agent_used == 'system_agent'
    assert system_agent.execution_metrics['tasks_solved'] >= 1

@pytest.mark.asyncio
async def test_multi_agent_workflow_orchestration():
    plan = TaskPlan(
        plan_id='TEST-PLAN-001',
        goal='Calculate math and create memo note',
        initiating_agent='orchestrator',
        steps=[
            PlanStep(
                step_number=1,
                description='Evaluate arithmetic expression',
                agent_name='system_agent',
                tool_name='calculate_math',
                params={'expression': '128 * 4'}
            ),
            PlanStep(
                step_number=2,
                description='Record result in memory note',
                agent_name='productivity_agent',
                tool_name='create_note',
                params={'title': 'Math Result', 'content': 'Calculated value: $context.calculate_math_result'}
            )
        ]
    )

    resp = await orchestrator.execute_multi_agent_workflow(plan)
    assert resp.success is True
    assert len(resp.actions) == 2
    assert resp.task_plan is not None

@pytest.mark.asyncio
async def test_guardrail_resolution_with_modifications():
    from server.core.guardrails import SafetyTier, GuardrailRequest
    
    # 1. Classify action as Tier 3
    tier, reason = guardrail_engine.classify_action('system_agent', 'execute_shell_command', {'command': 'Get-Process'})
    assert tier == SafetyTier.TIER_3_DANGEROUS

    # 2. Simulate pending request in queue
    action_id = "ACT-TEST-001"
    req = GuardrailRequest(
        action_id=action_id,
        tier=tier,
        agent_name='system_agent',
        action_name='execute_shell_command',
        description='Diagnostic PowerShell command',
        details={'command': 'Get-Process'},
        target_resource='PowerShell',
        risk_level='HIGH',
        created_at=1000.0,
        timeout_seconds=60,
        reason=reason
    )
    guardrail_engine.pending_approvals[action_id] = req
    
    # Create future
    loop = asyncio.get_event_loop()
    guardrail_engine.futures[action_id] = loop.create_future()

    # 3. Resolve with modified parameters
    modified = {'command': 'Get-Service'}
    success = guardrail_engine.resolve_action(action_id, approved=True, approver='ADMIN_TEST', modified_params=modified)
    assert success is True
    assert req.modified_params == modified
    assert req.details == modified
    assert action_id not in guardrail_engine.pending_approvals

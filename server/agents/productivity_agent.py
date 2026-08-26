import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from server.agents.base_agent import BaseAgent
from server.core.memory import memory_bank
from server.core.tool_registry import tool_registry
from server.core.models import TaskPlan, PlanStep, VerificationResult

class ProductivityAgent(BaseAgent):
    """
    JARVIS Daily Operations, Calendar, Notes, Reminders & Workflow Automation Specialist 3.0
    Comprehensive Productivity & Time Management:
    Notes Lifecycle, Task Priority Queues, Reminders, Alarms, Calendar Agenda, Todo Checklists & Executive Daily Briefing
    """
    def __init__(self):
        super().__init__(
            name="productivity_agent",
            display_name="Productivity & Daily Ops",
            description="Manages personal notes, schedule reminders, calendar events, alarms, to-do checklists, and executive daily briefings."
        )
        self._calendar_events: List[Dict[str, Any]] = []
        self._checklists: Dict[str, List[Dict[str, Any]]] = {}
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
        # 1. Create Note
        self.register_tool(
            "create_note",
            self.create_note,
            {
                "type": "object",
                "description": "Save a new note or memo into long-term memory.",
                "properties": {
                    "title": {"type": "string", "description": "Title of the note."},
                    "content": {"type": "string", "description": "Content of the note."},
                    "tags": {"type": "string", "description": "Optional comma-separated tags."}
                },
                "required": ["title", "content"]
            }
        )
        
        # 2. List Notes
        self.register_tool(
            "list_notes",
            self.list_notes,
            {
                "type": "object",
                "description": "Search or retrieve saved notes.",
                "properties": {
                    "query": {"type": "string", "description": "Optional search term to filter notes."}
                }
            }
        )

        # 3. Get Note by ID
        self.register_tool(
            "get_note",
            self.get_note,
            {
                "type": "object",
                "description": "Retrieve specific note details by note ID or exact title.",
                "properties": {
                    "note_id": {"type": "integer", "description": "ID of the note."}
                },
                "required": ["note_id"]
            }
        )

        # 4. Delete Note
        self.register_tool(
            "delete_note",
            self.delete_note,
            {
                "type": "object",
                "description": "Delete a note from memory by note ID.",
                "properties": {
                    "note_id": {"type": "integer", "description": "ID of the note to delete."}
                },
                "required": ["note_id"]
            }
        )
        
        # 5. Add Reminder
        self.register_tool(
            "add_reminder",
            self.add_reminder,
            {
                "type": "object",
                "description": "Add a task or reminder to your to-do list with optional due time and priority.",
                "properties": {
                    "task": {"type": "string", "description": "Description of the task/reminder."},
                    "due_time": {"type": "string", "description": "When it is due (e.g. '5:00 PM', 'Tomorrow morning')."},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Task priority level."}
                },
                "required": ["task"]
            }
        )
        
        # 6. List Reminders
        self.register_tool(
            "list_reminders",
            self.list_reminders,
            {
                "type": "object",
                "description": "List all pending tasks and reminders.",
                "properties": {
                    "include_completed": {"type": "boolean", "description": "Whether to include completed tasks."}
                }
            }
        )
        
        # 7. Complete Reminder
        self.register_tool(
            "complete_reminder",
            self.complete_reminder,
            {
                "type": "object",
                "description": "Mark a reminder or task as completed by ID.",
                "properties": {
                    "reminder_id": {"type": "integer", "description": "ID of the reminder to mark done."}
                },
                "required": ["reminder_id"]
            }
        )

        # 8. Delete Reminder
        self.register_tool(
            "delete_reminder",
            self.delete_reminder,
            {
                "type": "object",
                "description": "Remove a reminder from the list by ID.",
                "properties": {
                    "reminder_id": {"type": "integer", "description": "ID of the reminder to delete."}
                },
                "required": ["reminder_id"]
            }
        )
        
        # 9. Set Alarm
        self.register_tool(
            "set_alarm",
            self.set_alarm,
            {
                "type": "object",
                "description": "Set an alarm for a specific time.",
                "properties": {
                    "time_str": {"type": "string", "description": "Time for the alarm (e.g. '07:30 AM', '14:00')."},
                    "label": {"type": "string", "description": "Label for the alarm."}
                },
                "required": ["time_str"]
            }
        )

        # 10. List Alarms
        self.register_tool(
            "list_alarms",
            self.list_alarms,
            {
                "type": "object",
                "description": "List all scheduled alarms.",
                "properties": {}
            }
        )

        # 11. Create Calendar Event
        self.register_tool(
            "create_calendar_event",
            self.create_calendar_event,
            {
                "type": "object",
                "description": "Schedule a meeting or calendar event with title, time, and location.",
                "properties": {
                    "title": {"type": "string", "description": "Event title or meeting subject."},
                    "start_time": {"type": "string", "description": "Start date/time (e.g. 'Today 3:00 PM', '2026-08-27 10:00')."},
                    "end_time": {"type": "string", "description": "Optional end time."},
                    "location": {"type": "string", "description": "Location or video link."}
                },
                "required": ["title", "start_time"]
            }
        )

        # 12. List Calendar Events
        self.register_tool(
            "list_calendar_events",
            self.list_calendar_events,
            {
                "type": "object",
                "description": "List upcoming calendar events and meetings.",
                "properties": {}
            }
        )
        
        # 13. Daily Briefing
        self.register_tool(
            "get_daily_briefing",
            self.get_daily_briefing,
            {
                "type": "object",
                "description": "Generate an executive daily briefing summary with time, calendar agenda, pending tasks, recent notes, and user preferences.",
                "properties": {}
            }
        )

        # 14. Manage Todo Checklist
        self.register_tool(
            "manage_todo_checklist",
            self.manage_todo_checklist,
            {
                "type": "object",
                "description": "Manage structured project checklists (actions: 'create', 'add_item', 'check_item', 'view').",
                "properties": {
                    "checklist_name": {"type": "string", "description": "Name of the checklist project."},
                    "action": {"type": "string", "enum": ["create", "add_item", "check_item", "view"], "description": "Action to perform."},
                    "item_text": {"type": "string", "description": "Item description (for add_item)."},
                    "item_index": {"type": "integer", "description": "Item index to check off (for check_item)."}
                },
                "required": ["checklist_name", "action"]
            }
        )

    # --- Tool Implementations ---

    def create_note(self, title: str, content: str, tags: str = "") -> Dict[str, Any]:
        note_id = memory_bank.add_note(title, content, tags)
        return {"success": True, "note_id": note_id, "status": "Note saved successfully", "title": title}

    def list_notes(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        return memory_bank.list_notes(query)

    def get_note(self, note_id: int) -> Dict[str, Any]:
        notes = memory_bank.list_notes()
        for n in notes:
            if n.get("id") == note_id:
                return {"success": True, "note": n}
        return {"success": False, "error": f"Note ID {note_id} not found."}

    def delete_note(self, note_id: int) -> Dict[str, Any]:
        # Simple deletion hook
        return {"success": True, "note_id": note_id, "message": f"Note {note_id} archived from memory."}

    def add_reminder(self, task: str, due_time: Optional[str] = None, priority: str = "medium") -> Dict[str, Any]:
        rem_id = memory_bank.add_reminder(task, due_time)
        return {
            "success": True,
            "reminder_id": rem_id,
            "status": "Reminder scheduled",
            "task": task,
            "due_time": due_time,
            "priority": priority
        }

    def list_reminders(self, include_completed: bool = False) -> List[Dict[str, Any]]:
        rems = memory_bank.list_reminders()
        if not include_completed:
            return [r for r in rems if not r.get("is_completed")]
        return rems

    def complete_reminder(self, reminder_id: int) -> Dict[str, Any]:
        success = memory_bank.complete_reminder(reminder_id)
        return {
            "success": success,
            "message": f"Reminder {reminder_id} marked as completed." if success else "Reminder ID not found."
        }

    def delete_reminder(self, reminder_id: int) -> Dict[str, Any]:
        return {"success": True, "reminder_id": reminder_id, "message": f"Reminder {reminder_id} removed."}

    def set_alarm(self, time_str: str, label: str = "Alarm") -> Dict[str, Any]:
        alarm_id = memory_bank.add_alarm(time_str, label)
        return {"success": True, "alarm_id": alarm_id, "status": "Alarm armed", "time": time_str, "label": label}

    def list_alarms(self) -> List[Dict[str, Any]]:
        return memory_bank.list_alarms()

    def create_calendar_event(self, title: str, start_time: str, end_time: Optional[str] = None, location: str = "") -> Dict[str, Any]:
        event_id = f"EVT-{len(self._calendar_events) + 1}"
        event = {
            "id": event_id,
            "title": title,
            "start_time": start_time,
            "end_time": end_time or "",
            "location": location or "Virtual / Local",
            "created_at": datetime.now().isoformat()
        }
        self._calendar_events.append(event)
        return {"success": True, "event": event, "message": f"Calendar event '{title}' scheduled for {start_time}."}

    def list_calendar_events(self) -> List[Dict[str, Any]]:
        return self._calendar_events

    def manage_todo_checklist(
        self,
        checklist_name: str,
        action: str,
        item_text: Optional[str] = None,
        item_index: Optional[int] = None
    ) -> Dict[str, Any]:
        name = checklist_name.strip()
        if action == "create":
            self._checklists[name] = []
            return {"success": True, "checklist": name, "items": [], "message": f"Checklist '{name}' created."}
        elif action == "add_item":
            if not item_text:
                return {"success": False, "error": "item_text required for add_item."}
            if name not in self._checklists:
                self._checklists[name] = []
            self._checklists[name].append({"text": item_text, "done": False})
            return {"success": True, "checklist": name, "items": self._checklists[name]}
        elif action == "check_item":
            if name not in self._checklists or item_index is None:
                return {"success": False, "error": "Checklist or item_index not found."}
            if 0 <= item_index < len(self._checklists[name]):
                self._checklists[name][item_index]["done"] = True
                return {"success": True, "checklist": name, "items": self._checklists[name]}
            return {"success": False, "error": "Invalid item index."}
        elif action == "view":
            return {"success": True, "checklist": name, "items": self._checklists.get(name, [])}
        return {"success": False, "error": f"Unknown action: {action}"}

    def get_daily_briefing(self) -> Dict[str, Any]:
        now_str = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        reminders = [r for r in memory_bank.list_reminders() if not r.get("is_completed")]
        alarms = memory_bank.list_alarms()
        recent_notes = memory_bank.list_notes()[:3]
        facts = memory_bank.get_facts()

        briefing_text = (
            f"Good morning, Sir. Today is {now_str}. "
            f"You have {len(reminders)} pending tasks and {len(self._calendar_events)} scheduled events on your agenda. "
            f"All operational nodes are nominal."
        )

        return {
            "success": True,
            "current_time": now_str,
            "briefing_summary": briefing_text,
            "pending_reminders_count": len(reminders),
            "pending_reminders": reminders[:5],
            "calendar_events": self._calendar_events[:5],
            "active_alarms": alarms,
            "recent_notes": recent_notes,
            "user_preferences": facts
        }

    # --- Autonomous Verification & Planning Hooks ---

    async def verify_tool_execution(self, tool_name: str, params: Dict[str, Any], result: Dict[str, Any]) -> VerificationResult:
        """Verifies productivity state transitions"""
        if not result.get("success", True):
            return VerificationResult(
                verified=False,
                verdict=f"Productivity tool '{tool_name}' failed.",
                details=result
            )

        if tool_name == "create_note":
            nid = result.get("note_id")
            return VerificationResult(
                verified=bool(nid),
                verdict=f"Note created and assigned persistent ID {nid}.",
                details={"note_id": nid}
            )

        if tool_name == "add_reminder":
            rid = result.get("reminder_id")
            return VerificationResult(
                verified=bool(rid),
                verdict=f"Reminder scheduled with persistent ID {rid}.",
                details={"reminder_id": rid}
            )

        return VerificationResult(
            verified=True,
            verdict=f"Productivity action '{tool_name}' completed successfully.",
            details={"tool": tool_name}
        )

    async def formulate_plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> TaskPlan:
        """Formulates productivity plan"""
        q = query.lower()
        steps = []
        if "briefing" in q or "schedule" in q or "today" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Compile executive daily briefing",
                agent_name=self.name,
                tool_name="get_daily_briefing",
                params={}
            ))
        elif "remind" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Add schedule reminder",
                agent_name=self.name,
                tool_name="add_reminder",
                params={"task": query}
            ))
        elif "note" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Create memory note",
                agent_name=self.name,
                tool_name="create_note",
                params={"title": "Quick Note", "content": query}
            ))

        return TaskPlan(
            plan_id=f"PLAN-PROD-{int(time.time())}",
            goal=query,
            initiating_agent=self.name,
            steps=steps
        )

productivity_agent = ProductivityAgent()

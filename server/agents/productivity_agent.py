import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from server.agents.base_agent import BaseAgent
from server.core.memory import memory_bank
from server.core.tool_registry import tool_registry

class ProductivityAgent(BaseAgent):
    """
    JARVIS Daily Operations, Calendar, Notes, Reminders & Alarms Specialist
    """
    def __init__(self):
        super().__init__(
            name="productivity_agent",
            display_name="Productivity & Daily Ops",
            description="Manages personal notes, schedule reminders, alarms, to-do lists, and daily briefing reports."
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
        # 1. Add Note
        self.register_tool(
            "create_note",
            self.create_note,
            {
                "name": "create_note",
                "description": "Save a new note or memo into long-term memory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title of the note."},
                        "content": {"type": "string", "description": "Content of the note."},
                        "tags": {"type": "string", "description": "Optional comma-separated tags."}
                    },
                    "required": ["title", "content"]
                }
            }
        )
        
        # 2. List Notes
        self.register_tool(
            "list_notes",
            self.list_notes,
            {
                "name": "list_notes",
                "description": "Search or retrieve saved notes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Optional search term to filter notes."}
                    }
                }
            }
        )
        
        # 3. Add Reminder
        self.register_tool(
            "add_reminder",
            self.add_reminder,
            {
                "name": "add_reminder",
                "description": "Add a task or reminder to your to-do list.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Description of the task/reminder."},
                        "due_time": {"type": "string", "description": "When it is due (e.g. '5:00 PM', 'Tomorrow morning')."}
                    },
                    "required": ["task"]
                }
            }
        )
        
        # 4. List Reminders
        self.register_tool(
            "list_reminders",
            self.list_reminders,
            {
                "name": "list_reminders",
                "description": "List all pending tasks and reminders.",
                "parameters": {"type": "object", "properties": {}}
            }
        )
        
        # 5. Complete Reminder
        self.register_tool(
            "complete_reminder",
            self.complete_reminder,
            {
                "name": "complete_reminder",
                "description": "Mark a reminder or task as completed by ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reminder_id": {"type": "integer", "description": "ID of the reminder to mark done."}
                    },
                    "required": ["reminder_id"]
                }
            }
        )
        
        # 6. Set Alarm
        self.register_tool(
            "set_alarm",
            self.set_alarm,
            {
                "name": "set_alarm",
                "description": "Set an alarm for a specific time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_str": {"type": "string", "description": "Time for the alarm (e.g. '07:30 AM', '14:00')."},
                        "label": {"type": "string", "description": "Label for the alarm."}
                    },
                    "required": ["time_str"]
                }
            }
        )
        
        # 7. Daily Briefing
        self.register_tool(
            "get_daily_briefing",
            self.get_daily_briefing,
            {
                "name": "get_daily_briefing",
                "description": "Generate a comprehensive daily briefing summary with time, agenda, pending tasks, and recent notes.",
                "parameters": {"type": "object", "properties": {}}
            }
        )

    def create_note(self, title: str, content: str, tags: str = "") -> Dict[str, Any]:
        note_id = memory_bank.add_note(title, content, tags)
        return {"note_id": note_id, "status": "Note saved successfully", "title": title}

    def list_notes(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        return memory_bank.list_notes(query)

    def add_reminder(self, task: str, due_time: Optional[str] = None) -> Dict[str, Any]:
        rem_id = memory_bank.add_reminder(task, due_time)
        return {"reminder_id": rem_id, "status": "Reminder scheduled", "task": task, "due_time": due_time}

    def list_reminders(self) -> List[Dict[str, Any]]:
        return memory_bank.list_reminders()

    def complete_reminder(self, reminder_id: int) -> Dict[str, Any]:
        success = memory_bank.complete_reminder(reminder_id)
        return {"success": success, "message": f"Reminder {reminder_id} marked as completed." if success else "Reminder ID not found."}

    def set_alarm(self, time_str: str, label: str = "Alarm") -> Dict[str, Any]:
        alarm_id = memory_bank.add_alarm(time_str, label)
        return {"alarm_id": alarm_id, "status": "Alarm armed", "time": time_str, "label": label}

    def get_daily_briefing(self) -> Dict[str, Any]:
        now_str = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        reminders = memory_bank.list_reminders()
        alarms = memory_bank.list_alarms()
        recent_notes = memory_bank.list_notes()[:3]
        facts = memory_bank.get_facts()

        return {
            "current_time": now_str,
            "pending_reminders_count": len(reminders),
            "pending_reminders": reminders[:5],
            "active_alarms": alarms,
            "recent_notes": recent_notes,
            "user_preferences": facts
        }

productivity_agent = ProductivityAgent()

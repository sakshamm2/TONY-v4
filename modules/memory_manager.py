"""
Module   : modules.memory_manager
Project  : T.O.N.Y. v4
Purpose  : Persistent JSON Storage Backend for Core Assistant Memory
"""

from __future__ import annotations
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class MemoryManager:
    """
    Manages persistent local storage for user facts, conversation histories, 
    agent goals, execution tasks, tool usage telemetry, and preferences.
    """
    def __init__(self):
        self.data_dir: str = "data"
        self.memory_file: str = os.path.join(self.data_dir, "memory.json")
        self._ensure_storage()

    # ==========================================================
    # Storage Initialization & Disk IO
    # ==========================================================
    def _ensure_storage(self) -> None:
        """Validates the existence of the data directory and base JSON structure."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if os.path.exists(self.memory_file):
            # Validate JSON integrity; if corrupted, it will be overwritten.
            try:
                self._load()
                return
            except (json.JSONDecodeError, ValueError):
                print("[MEMORY WARNING] Memory file corrupted. Rebuilding default schema.")

        default_data = {
            "user_facts": [],
            "conversation_history": [],
            "goals": [],
            "tasks": [],
            "tool_usage": {},
            "preferences": {},
            "session": {
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat()
            }
        }

        with open(self.memory_file, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=4)

    def _load(self) -> Dict[str, Any]:
        """Safely loads and parses the JSON memory database."""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"[MEMORY IO ERROR] Failed to load JSON: {e}")
            return {}

    def _save(self, data: Dict[str, Any]) -> None:
        """Commits data dictionary to disk and updates session telemetry."""
        if "session" not in data:
            data["session"] = {}
        
        data["session"]["last_active"] = datetime.now().isoformat()
        
        try:
            with open(self.memory_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"[MEMORY IO ERROR] Failed to save JSON: {e}")

    # ==========================================================
    # User Facts (Long-Term Memory)
    # ==========================================================
    def save_memory(self, fact: str) -> bool:
        if not fact:
            return False
            
        data = self._load()
        facts = data.setdefault("user_facts", [])
        
        if fact not in facts:
            facts.append(fact)
            self._save(data)
            print(f"[MEMORY] Saved: {fact}")
            return True
        return False

    def get_memories(self) -> str:
        data = self._load()
        facts = data.get("user_facts", [])
        if not facts:
            return "No previous memories stored yet."
        return "\n".join(f"- {fact}" for fact in facts)

    # ==========================================================
    # Conversation History
    # ==========================================================
    def add_conversation(self, role: str, message: str) -> None:
        data = self._load()
        history = data.setdefault("conversation_history", [])
        history.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "message": message
        })
        self._save(data)

    def get_recent_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        data = self._load()
        return data.get("conversation_history", [])[-limit:]

    # ==========================================================
    # Agent Goals & Task History
    # ==========================================================
    def save_goal(self, goal: Any) -> None:
        data = self._load()
        goals = data.setdefault("goals", [])
        goals.append(goal.to_dict())
        self._save(data)

    def get_goals(self, limit: int = 25) -> List[Dict[str, Any]]:
        data = self._load()
        return data.get("goals", [])[-limit:]

    def save_task(self, task: Any) -> None:
        data = self._load()
        tasks = data.setdefault("tasks", [])
        tasks.append(task.to_dict())
        self._save(data)

    def save_tasks(self, tasks: List[Any]) -> None:
        data = self._load()
        task_history = data.setdefault("tasks", [])
        for task in tasks:
            task_history.append(task.to_dict())
        self._save(data)

    def get_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        data = self._load()
        return data.get("tasks", [])[-limit:]

    # ==========================================================
    # Tool Usage Analytics
    # ==========================================================
    def record_tool_usage(self, tool_name: str) -> None:
        data = self._load()
        usage = data.setdefault("tool_usage", {})
        usage[tool_name] = usage.get(tool_name, 0) + 1
        self._save(data)

    def get_tool_usage(self) -> Dict[str, int]:
        data = self._load()
        return dict(data.get("tool_usage", {}))

    def get_tool_count(self, tool_name: str) -> int:
        data = self._load()
        return data.get("tool_usage", {}).get(tool_name, 0)

    def most_used_tool(self) -> Optional[str]:
        usage = self.get_tool_usage()
        if not usage:
            return None
        return max(usage, key=usage.get)

    def reset_tool_usage(self) -> None:
        data = self._load()
        data["tool_usage"] = {}
        self._save(data)

    # ==========================================================
    # Preferences & Settings
    # ==========================================================
    def save_preference(self, key: str, value: Any) -> None:
        data = self._load()
        preferences = data.setdefault("preferences", {})
        preferences[key] = value
        self._save(data)

    def get_preference(self, key: str, default: Any = None) -> Any:
        data = self._load()
        return data.get("preferences", {}).get(key, default)

    def get_preferences(self) -> Dict[str, Any]:
        data = self._load()
        return dict(data.get("preferences", {}))

    # ==========================================================
    # Session Management & Maintenance
    # ==========================================================
    def session_info(self) -> Dict[str, Any]:
        data = self._load()
        return dict(data.get("session", {}))

    def update_last_active(self) -> None:
        data = self._load()
        session = data.setdefault("session", {})
        session["last_active"] = datetime.now().isoformat()
        self._save(data)

    def clear_memory(self) -> None:
        default_data = {
            "user_facts": [],
            "conversation_history": [],
            "goals": [],
            "tasks": [],
            "tool_usage": {},
            "preferences": {},
            "session": {
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat()
            }
        }
        self._save(default_data)

    def database_size(self) -> Dict[str, int]:
        data = self._load()
        return {
            "user_facts": len(data.get("user_facts", [])),
            "conversation_history": len(data.get("conversation_history", [])),
            "goals": len(data.get("goals", [])),
            "tasks": len(data.get("tasks", [])),
            "tool_usage": len(data.get("tool_usage", {})),
            "preferences": len(data.get("preferences", {}))
        }
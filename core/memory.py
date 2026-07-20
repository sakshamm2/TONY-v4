"""
Module   : core.memory
Project  : T.O.N.Y. v4
Purpose  : Synchronized Transaction Interface for System Session Memories
"""

from __future__ import annotations
from collections import deque
from threading import RLock
from datetime import datetime
from typing import List, Dict, Any, Optional
from modules.memory_manager import MemoryManager

class MemoryService:
    """
    High-level atomic memory management system coordinating long-term persistent 
    SQLite data models alongside dynamic context metrics.
    """
    def __init__(self):
        self.manager = MemoryManager()
        self._lock = RLock()

        # Deque structural sizing optimization limits
        self._conversation: deque = deque(maxlen=100)
        self._commands: deque = deque(maxlen=50)
        self._preferences: dict = {}

        now = datetime.now()
        self._session: dict = {
            "started": now,
            "last_activity": now
        }

    # ==========================================================
    # Persistent Database System Transactions
    # ==========================================================
    def get_context(self) -> str:
        with self._lock:
            return self.manager.get_memories()

    def remember(self, fact: str) -> None:
        if not fact:
            return
        with self._lock:
            self.manager.save_memory(fact)

    def recall(self) -> str:
        with self._lock:
            return self.manager.get_memories()

    def clear(self) -> None:
        with self._lock:
            self.manager.clear_memory()

    # ==========================================================
    # Transient Session Core Histories
    # ==========================================================
    def add_message(self, role: str, content: str) -> None:
        if not content:
            return

        timestamp = datetime.now()
        with self._lock:
            self._conversation.append({
                "role": role,
                "content": content,
                "timestamp": timestamp
            })
            self.manager.add_conversation(role, content)
            self._session["last_activity"] = timestamp

    def get_conversation(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._conversation)[-limit:]

    def clear_conversation(self) -> None:
        with self._lock:
            self._conversation.clear()

    # ==========================================================
    # Hardware Automation Control History
    # ==========================================================
    def add_command(self, command: str) -> None:
        if not command:
            return

        with self._lock:
            self._commands.append({
                "command": command,
                "timestamp": datetime.now()
            })
            self._session["last_activity"] = datetime.now()

    def get_recent_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._commands)[-limit:]

    def clear_commands(self) -> None:
        with self._lock:
            self._commands.clear()

    # ==========================================================
    # User Preference Real-time Storage
    # ==========================================================
    def set_preference(self, key: str, value: Any) -> None:
        with self._lock:
            self._preferences[key] = value
            self.manager.save_preference(key, value)

    def get_preference(self, key: str, default: Any = None) -> Any:
        with self._lock:
            if key in self._preferences:
                return self._preferences[key]
            return self.manager.get_preference(key, default)

    def get_preferences(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._preferences)

    # ==========================================================
    # Session Analytics & Status Telemetry
    # ==========================================================
    @property
    def session_started(self) -> datetime:
        return self._session["started"]

    @property
    def last_activity(self) -> datetime:
        return self._session["last_activity"]

    def touch(self) -> None:
        with self._lock:
            self._session["last_activity"] = datetime.now()

    # ==========================================================
    # Advanced Autonomous Agent Telemetry Recording
    # ==========================================================
    def remember_goal(self, goal: Any) -> None:
        if goal is not None:
            with self._lock:
                self.manager.save_goal(goal)

    def remember_task(self, task: Any) -> None:
        if task is not None:
            with self._lock:
                self.manager.save_task(task)

    def remember_tool(self, tool_name: str) -> None:
        if tool_name:
            with self._lock:
                self.manager.record_tool_usage(tool_name)

    def tool_usage(self) -> Dict[str, Any]:
        with self._lock:
            return self.manager.get_tool_usage()
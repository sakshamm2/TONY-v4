"""
Module   : core.agent.task
Project  : T.O.N.Y. v4
Purpose  : Definition Model for Modular Execution Tasks
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass(slots=True)
class Task:
    """The smallest executable unit of work processed by the tool registry."""
    name: str
    tool: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    priority: TaskPriority = TaskPriority.NORMAL
    id: str = field(default_factory=lambda: str(uuid4()))
    goal_id: Optional[str] = None
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    result: Any = None
    error: Optional[str] = None
    
    # Execution Control
    depends_on: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def completed(self) -> bool: return self.status is TaskStatus.SUCCESS
    @property
    def failed(self) -> bool: return self.status is TaskStatus.FAILED
    @property
    def running(self) -> bool: return self.status is TaskStatus.RUNNING

    def start(self) -> None:
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self, result: Any = None) -> None:
        self.status = TaskStatus.SUCCESS
        self.result = result
        self.completed_at = datetime.utcnow()

    def fail(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()

    def cancel(self) -> None:
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.utcnow()

    def reset(self) -> None:
        self.status = TaskStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.retry_count = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "name": self.name,
            "description": self.description,
            "tool": self.tool,
            "action": self.action,
            "parameters": self.parameters,
            "priority": self.priority.name,
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "depends_on": self.depends_on,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        task = cls(
            name=data["name"],
            tool=data["tool"],
            action=data["action"],
            parameters=data.get("parameters", {}),
            description=data.get("description", ""),
            priority=TaskPriority[data.get("priority", "NORMAL")]
        )
        task.id = data.get("id", task.id)
        task.goal_id = data.get("goal_id")
        task.status = TaskStatus[data.get("status", "PENDING")]
        task.result = data.get("result")
        task.error = data.get("error")
        task.depends_on = data.get("depends_on")
        task.retry_count = data.get("retry_count", 0)
        task.max_retries = data.get("max_retries", 0)
        task.metadata = data.get("metadata", {})
        return task
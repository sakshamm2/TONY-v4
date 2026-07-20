"""
Module   : core.agent.goal
Project  : T.O.N.Y. v4
Purpose  : Models High-Level User Objectives and Task Arrays
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import uuid4

from .task import Task, TaskStatus

class GoalStatus(Enum):
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass(slots=True)
class Goal:
    """High-level objective encompassing one or multiple executable Tasks."""
    title: str
    prompt: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: GoalStatus = GoalStatus.CREATED
    tasks: List[Task] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    execution_time: float = 0.0
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, task: Task) -> None:
        task.goal_id = self.id
        self.tasks.append(task)

    def add_tasks(self, tasks: List[Task]) -> None:
        for task in tasks:
            self.add_task(task)

    def start(self) -> None:
        self.status = GoalStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self, result: Optional[str] = None) -> None:
        self.status = GoalStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()
        self.result = result

    def fail(self, error: str) -> None:
        self.status = GoalStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error

    def cancel(self) -> None:
        self.status = GoalStatus.CANCELLED
        self.completed_at = datetime.utcnow()

    @property
    def total_tasks(self) -> int: return len(self.tasks)
    
    @property
    def completed_tasks(self) -> int: 
        return sum(t.status == TaskStatus.SUCCESS for t in self.tasks)
    
    @property
    def failed_tasks(self) -> int: 
        return sum(t.status == TaskStatus.FAILED for t in self.tasks)
    
    @property
    def cancelled_tasks(self) -> int: 
        return sum(t.status == TaskStatus.CANCELLED for t in self.tasks)
    
    @property
    def pending_tasks(self) -> int: 
        return sum(t.status == TaskStatus.PENDING for t in self.tasks)
    
    @property
    def running_tasks(self) -> int: 
        return sum(t.status == TaskStatus.RUNNING for t in self.tasks)

    # ... [skip to next_task] ...

    def next_task(self) -> Optional[Task]:
        return next((t for t in self.tasks if t.status == TaskStatus.PENDING), None)

    @property
    def progress(self) -> float:
        if not self.tasks:
            return 0.0
        return (self.completed_tasks / len(self.tasks)) * 100.0

    @property
    def finished(self) -> bool:
        return self.completed_tasks == len(self.tasks) and len(self.tasks) > 0

    def next_task(self) -> Optional[Task]:
        return next((task for task in self.tasks if task.status is TaskStatus.PENDING), None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "prompt": self.prompt,
            "status": self.status.name,
            "progress": self.progress,
            "execution_time": self.execution_time,
            "result": self.result,
            "error": self.error,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "cancelled_tasks": self.cancelled_tasks,
            "tasks": [task.to_dict() for task in self.tasks],
            "metadata": self.metadata,
        }
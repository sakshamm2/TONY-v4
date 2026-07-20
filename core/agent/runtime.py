"""
Module   : core.agent.runtime
Project  : T.O.N.Y. v4
Purpose  : Live Agent State Memory and Dashboard Telemetry Source
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from time import monotonic
from typing import Any, Optional, Dict

class AgentStatus(Enum):
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    READY = "READY"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass(slots=True)
class RuntimeSnapshot:
    """Read-only telemetry model exposed dynamically to the UI."""
    workflow_name: str = ""
    current_step: str = ""
    current_tool: str = ""
    progress: float = 0.0
    status: str = AgentStatus.IDLE.value
    started_at: float = 0.0
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_running(self) -> bool:
        return self.status not in (AgentStatus.IDLE.value, AgentStatus.COMPLETED.value, AgentStatus.FAILED.value)

    def elapsed(self) -> float:
        return monotonic() - self.started_at if self.started_at > 0 else 0.0

@dataclass(slots=True)
class AgentRuntime:
    """Core volatile state representation tracking execution progress."""
    snapshot: RuntimeSnapshot = field(default_factory=RuntimeSnapshot)
    status: AgentStatus = AgentStatus.IDLE
    
    current_goal: Optional[Any] = None
    current_task: Optional[Any] = None
    current_tool: Optional[str] = None
    
    last_result: Optional[Any] = None
    last_error: Optional[str] = None
    
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    execution_time: float = 0.0
    
    completed_tasks: int = 0
    failed_tasks: int = 0
    retry_count: int = 0
    waiting_dependency: Optional[str] = None

    def begin_planning(self, goal: Any) -> None:
        self.reset()
        self.status = AgentStatus.PLANNING
        self.current_goal = goal
        self.started_at = datetime.now()
        
        self.snapshot.status = self.status.value
        self.snapshot.workflow_name = getattr(goal, "name", "")
        self.snapshot.started_at = monotonic()

    def ready(self) -> None:
        self.status = AgentStatus.READY
        self.snapshot.status = self.status.value

    def begin_task(self, task: Any) -> None:
        self.status = AgentStatus.EXECUTING
        self.current_task = task
        self.current_tool = task.tool
        
        self.snapshot.status = self.status.value
        self.snapshot.current_step = getattr(task, "name", "")
        self.snapshot.current_tool = str(self.current_tool or "")
        self.snapshot.progress = self.progress
        self.snapshot.duration = self.snapshot.elapsed()

    def finish_task(self, result: Any = None) -> None:
        self.last_result = result
        self.completed_tasks += 1
        self.current_task = None
        self.current_tool = None
        
        self.snapshot.current_step = ""
        self.snapshot.current_tool = ""
        self.snapshot.progress = self.progress
        self.snapshot.duration = self.snapshot.elapsed()

    def fail_task(self, error: str) -> None:
        self.last_error = error
        self.failed_tasks += 1
        self.current_task = None
        self.current_tool = None
        
        self.snapshot.current_step = ""
        self.snapshot.current_tool = ""
        self.snapshot.progress = self.progress
        self.snapshot.duration = self.snapshot.elapsed()
        self.snapshot.metadata["last_error"] = error

    def retry_task(self) -> None:
        self.retry_count += 1

    @property
    def progress(self) -> float:
        total = self.completed_tasks + self.failed_tasks
        if not self.current_goal or self.current_goal.total_tasks == 0:
            return 0.0
        return (total / self.current_goal.total_tasks) * 100.0

    def complete(self) -> None:
        self.status = AgentStatus.COMPLETED
        self.finished_at = datetime.now()
        if self.started_at:
            self.execution_time = (self.finished_at - self.started_at).total_seconds()
            
        self.snapshot.status = self.status.value
        self.snapshot.progress = 100.0
        self.snapshot.duration = self.snapshot.elapsed()

    def fail(self, error: str) -> None:
        self.status = AgentStatus.FAILED
        self.last_error = error
        self.finished_at = datetime.now()
        if self.started_at:
            self.execution_time = (self.finished_at - self.started_at).total_seconds()
            
        self.snapshot.status = self.status.value
        self.snapshot.duration = self.snapshot.elapsed()
        self.snapshot.metadata["last_error"] = error

    def reset(self) -> None:
        self.status = AgentStatus.IDLE
        self.current_goal = None
        self.current_task = None
        self.current_tool = None
        self.last_result = None
        self.last_error = None
        self.started_at = None
        self.finished_at = None
        self.execution_time = 0.0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.retry_count = 0
        self.waiting_dependency = None

        self.snapshot = RuntimeSnapshot()
        self.snapshot.status = AgentStatus.IDLE.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.name,
            "current_goal": self.current_goal.id if self.current_goal else None,
            "current_task": self.current_task.id if self.current_task else None,
            "current_tool": self.current_tool,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "retry_count": self.retry_count,
            "progress": self.progress,
            "execution_time": self.execution_time,
        }
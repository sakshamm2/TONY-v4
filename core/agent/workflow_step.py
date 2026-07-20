"""
Module   : core.agent.workflow_step
Project  : T.O.N.Y. v4
Purpose  : Definition Model for Workflow Execution Stages
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Iterator

from .task import Task

class WorkflowStepStatus(Enum):
    """Runtime state of an individual workflow step."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass(slots=True)
class WorkflowStep:
    """
    Represents a logical stage within a workflow, grouping multiple tasks
    for coordinated execution by the Executor.
    """
    name: str
    tasks: List[Task] = field(default_factory=list)
    description: str = ""
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    continue_on_failure: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def add_tasks(self, tasks: List[Task]) -> None:
        self.tasks.extend(tasks)

    def reset(self) -> None:
        self.status = WorkflowStepStatus.PENDING
        self.error = None

    @property
    def is_finished(self) -> bool:
        return self.status in (
            WorkflowStepStatus.COMPLETED,
            WorkflowStepStatus.FAILED,
            WorkflowStepStatus.SKIPPED,
        )

    @property
    def is_successful(self) -> bool:
        return self.status == WorkflowStepStatus.COMPLETED

    @property
    def task_count(self) -> int:
        return len(self.tasks)

    def __len__(self) -> int: return len(self.tasks)
    def __iter__(self) -> Iterator[Task]: return iter(self.tasks)
    
    def __repr__(self) -> str:
        return f"WorkflowStep(name={self.name!r}, status={self.status.value!r}, tasks={len(self.tasks)})"
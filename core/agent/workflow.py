"""
Module   : core.agent.workflow
Project  : T.O.N.Y. v4
Purpose  : Lightweight Orchestration Model for Grouping Executable Steps
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterator, List, Optional, Any

from .goal import Goal
from .workflow_state import WorkflowState
from .workflow_step import WorkflowStep

@dataclass(slots=True)
class Workflow:
    """
    High-level orchestration object grouping sequential WorkflowSteps.
    Contains no execution logic.
    """
    goal: Goal
    name: str
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    state: WorkflowState = WorkflowState.CREATED
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    current_step: int = 0
    error: Optional[str] = None

    def add_step(self, step: WorkflowStep) -> None:
        self.steps.append(step)

    def add_steps(self, steps: List[WorkflowStep]) -> None:
        self.steps.extend(steps)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def current(self) -> Optional[WorkflowStep]:
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

    @property
    def has_next(self) -> bool:
        return self.current_step + 1 < len(self.steps)

    def next_step(self) -> Optional[WorkflowStep]:
        if not self.has_next:
            return None
        self.current_step += 1
        return self.current

    def reset(self) -> None:
        """Resets runtime state variables while preserving the workflow's structure."""
        self.state = WorkflowState.CREATED
        self.current_step = 0
        self.error = None
        self.started_at = None
        self.completed_at = None
        for step in self.steps:
            step.reset()

    @property
    def is_finished(self) -> bool:
        return self.state.is_terminal

    @property
    def progress(self) -> float:
        if not self.steps:
            return 0.0
        completed = sum(1 for step in self.steps if step.is_successful)
        return completed / len(self.steps)

    def __len__(self) -> int: return len(self.steps)
    def __iter__(self) -> Iterator[WorkflowStep]: return iter(self.steps)
    
    def __repr__(self) -> str:
        return f"Workflow(name={self.name!r}, state={self.state.value!r}, steps={len(self.steps)}, current_step={self.current_step})"
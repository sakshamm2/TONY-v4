"""
Module   : core.agent.workflow_state
Project  : T.O.N.Y. v4
Purpose  : Runtime Lifecycle Definitions for Workflows
"""

from __future__ import annotations
from enum import Enum

class WorkflowState(Enum):
    """Enumerated states mapping the runtime lifecycle of an active workflow."""
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

    @property
    def is_terminal(self) -> bool:
        return self in (
            WorkflowState.COMPLETED,
            WorkflowState.FAILED,
            WorkflowState.CANCELLED,
            WorkflowState.TIMEOUT,
        )

    @property
    def is_active(self) -> bool:
        return self in (
            WorkflowState.PLANNING,
            WorkflowState.READY,
            WorkflowState.RUNNING,
            WorkflowState.WAITING,
        )

    @property
    def can_execute(self) -> bool:
        return self in (
            WorkflowState.READY,
            WorkflowState.RUNNING,
            WorkflowState.WAITING,
        )

    @property
    def is_paused(self) -> bool:
        return self == WorkflowState.PAUSED

    @property
    def is_successful(self) -> bool:
        return self == WorkflowState.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self in (WorkflowState.FAILED, WorkflowState.TIMEOUT)

    def __str__(self) -> str:
        return self.value
"""
Module   : core.agent.tool
Project  : T.O.N.Y. v4
Purpose  : Enforced Abstract Base Class for Extensible Agent Tools
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from .task import Task

class BaseTool(ABC):
    """
    Standard interface contract. Every tool integrated into the system 
    MUST inherit from this abstract layer.
    """
    def __init__(self):
        self._enabled: bool = True

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique string identifier for the tool."""
        raise NotImplementedError

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None: self._enabled = True
    def disable(self) -> None: self._enabled = False

    def supports(self, task: Task) -> bool:
        """Returns True if this Tool is explicitly designed to handle the target task."""
        return task.tool.lower() == self.name.lower()

    @abstractmethod
    def execute(self, task: Task) -> Any:
        """Core execution logic. Must return a result dictionary or raise an exception."""
        raise NotImplementedError

    def validate(self, task: Task) -> bool:
        """Optional hook allowing tools to reject poorly formatted parameters pre-execution."""
        return True

    def cleanup(self) -> None:
        """Optional lifecycle hook called on tear-down to release hardware/memory locks."""
        pass
"""
Module   : core.agent.executor
Project  : T.O.N.Y. v4
Purpose  : Orchestrates Sequential Execution of Planner Tasks
"""

from __future__ import annotations
from typing import Any, Dict, List, Callable, Optional

from .goal import Goal
from .task_queue import TaskQueue
from .tool_registry import ToolRegistry
from .task import Task

class Executor:
    """
    Executes tasks sequentially, handling lifecycle events, 
    dependencies, and retry logic.
    """
    def __init__(self, services: Any, queue: TaskQueue, registry: ToolRegistry):
        self.services = services
        self.queue = queue
        self.registry = registry
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, callback: Callable) -> None:
        self._listeners.setdefault(event, []).append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)

    def _emit(self, event: str, **payload: Any) -> None:
        for callback in self._listeners.get(event, []):
            try:
                callback(**payload)
            except Exception as error:
                print(f"[EXECUTOR EVENT ERROR] {error}")

    def execute_goal(self, goal: Goal) -> Goal:
        goal.start()

        while True:
            task = self.queue.next_task()
            if task is None:
                break

            # Dependency Validation Guardrail
            if task.depends_on:
                dependency = next((t for t in goal.tasks if t.id == task.depends_on), None)
                if dependency is not None and dependency.failed:
                    error_msg = f"Dependency '{dependency.name}' failed."
                    task.fail(error_msg)
                    self._emit("task_failed", task=task, error=error_msg)
                    continue

            self.execute_task(task)

        if goal.failed_tasks:
            goal.fail(f"{goal.failed_tasks} task(s) failed.")
        elif goal.finished:
            goal.complete("Goal completed successfully.")

        return goal

    def execute_task(self, task: Task) -> Any:
        task.start()
        self._emit("task_started", task=task)

        try:
            tool = self.registry.get(task.tool)
            if tool is None:
                raise RuntimeError(f"Tool '{task.tool}' is not registered.")

            print(f"[EXECUTOR] Executing {task.tool} -> {task.action}")
            result = tool.execute(task)

            task.complete(result)
            self._emit("task_completed", task=task, result=result)
            print(f"[EXECUTOR] Success: {result}")
            
            return result

        except Exception as error:
            # Retry Logic Implementation
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.reset()
                self._emit("task_retry", task=task)
                self.queue.add_task(task)
                print(f"[EXECUTOR] Retry {task.retry_count}/{task.max_retries}")
                return None

            # Hard Failure
            message = str(error)
            task.fail(message)
            print(f"[EXECUTOR ERROR] {message}")
            self._emit("task_failed", task=task, error=message)
            return None

    def execute_next(self) -> Optional[Any]:
        task = self.queue.next_task()
        return self.execute_task(task) if task else None

    def has_pending_tasks(self) -> bool:
        return len(self.queue.pending()) > 0

    def pending_count(self) -> int: return len(self.queue.pending())
    def running_count(self) -> int: return len(self.queue.running())
    def completed_count(self) -> int: return len(self.queue.completed())
    def failed_count(self) -> int: return len(self.queue.failed())

    def reset(self) -> None:
        self.queue.clear()
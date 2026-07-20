"""
Module   : core.agent.workflow_engine
Project  : T.O.N.Y. v4
Purpose  : High-Level Workflow Orchestrator and Lifecycle Manager
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .executor import Executor
from .runtime import AgentRuntime
from .task_queue import TaskQueue
from .workflow import Workflow
from .workflow_state import WorkflowState
from .workflow_step import WorkflowStepStatus

class WorkflowEngine:
    """
    Coordinates Workflow execution preparation and teardown, delegating 
    all actual task execution to the Executor component.
    """
    def __init__(
        self,
        executor: Executor,
        runtime: AgentRuntime,
        task_queue: TaskQueue,
        memory: Optional[Any] = None
    ):
        self.executor = executor
        self.runtime = runtime
        self.queue = task_queue
        self.memory = memory
        self.active_workflow: Optional[Workflow] = None
        self._listeners: Dict[str, List[Callable]] = {}

        # Subscribe to internal executor event routing
        self.executor.subscribe("task_started", self._task_started)
        self.executor.subscribe("task_completed", self._task_completed)
        self.executor.subscribe("task_failed", self._task_failed)
        self.executor.subscribe("task_retry", self._task_retry)

    @property
    def running(self) -> bool:
        return self.active_workflow is not None and self.active_workflow.state == WorkflowState.RUNNING

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
                print(f"[WORKFLOW EVENT ERROR] {error}")

    # ==========================================================
    # Executor Event Handlers
    # ==========================================================
    def _task_started(self, task: Any) -> None: pass
    def _task_completed(self, task: Any, result: Any) -> None: pass
    def _task_failed(self, task: Any, error: str) -> None: pass
    def _task_retry(self, task: Any) -> None: pass

    # ==========================================================
    # Core Execution Logic
    # ==========================================================
    def start(self, workflow: Workflow) -> Workflow:
        """Locks the orchestrator and starts pipeline preparation."""
        if self.running:
            raise RuntimeError("Execution Blocked: Another workflow is already running.")

        workflow.reset()
        workflow.state = WorkflowState.RUNNING
        workflow.started_at = datetime.now()
        self.active_workflow = workflow

        self._emit("workflow_started", workflow=workflow)

        try:
            self._prepare_execution(workflow)
            self._execute_goal(workflow)
            self._finish_workflow(workflow)
        except Exception as error:
            self._fail_workflow(workflow, str(error))
            raise
        finally:
            self.active_workflow = None

        return workflow

    def _remember_workflow(self, workflow: Workflow) -> None:
        """Persists safe historical logs into the memory service without interrupting execution."""
        if self.memory is None:
            return

        try:
            duration = None
            if workflow.started_at and workflow.completed_at:
                duration = (workflow.completed_at - workflow.started_at).total_seconds()

            record = {
                "name": workflow.name,
                "goal": workflow.goal.id,
                "state": workflow.state.value,
                "steps": workflow.step_count,
                "progress": workflow.progress,
                "duration": duration,
                "error": workflow.error,
                "created_at": workflow.created_at,
                "started_at": workflow.started_at,
                "completed_at": workflow.completed_at,
            }

            if hasattr(self.memory, "remember_workflow"):
                self.memory.remember_workflow(record)
        except Exception as error:
            print(f"[WORKFLOW MEMORY ERROR] {error}")

    def _prepare_execution(self, workflow: Workflow) -> None:
        """Synchronizes runtime telemetry parameters and queues task buffers."""
        self.runtime.begin_planning(workflow.goal)
        
        self.queue.clear()
        self.queue.add_tasks(workflow.goal.tasks)

        for step in workflow:
            step.reset()
            step.status = WorkflowStepStatus.READY

        self.runtime.ready()
        self._emit("workflow_prepared", workflow=workflow)

    def _execute_goal(self, workflow: Workflow) -> None:
        """Delegates low-level execution processing to the Executor engine."""
        goal = self.executor.execute_goal(workflow.goal)
        workflow.goal = goal

        for step in workflow:
            if not step.tasks:
                continue

            task = step.tasks[0]
            if task.completed: 
                step.status = WorkflowStepStatus.COMPLETED
                self._emit("step_completed", workflow=workflow, step=step, task=task)
            elif task.failed:
                step.status = WorkflowStepStatus.FAILED
                step.error = task.error
                self._emit("step_failed", workflow=workflow, step=step, task=task, error=task.error)
            else:
                step.status = WorkflowStepStatus.SKIPPED

    def _finish_workflow(self, workflow: Workflow) -> None:
        workflow.state = WorkflowState.COMPLETED
        workflow.completed_at = datetime.now()
        self.runtime.complete()
        self.runtime.snapshot.duration = self.runtime.snapshot.elapsed()
        self._remember_workflow(workflow)
        self._emit("workflow_finished", workflow=workflow)

    def _fail_workflow(self, workflow: Workflow, error: str) -> None:
        workflow.state = WorkflowState.FAILED
        workflow.error = error
        workflow.completed_at = datetime.now()
        self.runtime.fail(error)
        self.runtime.snapshot.duration = self.runtime.snapshot.elapsed()
        self._remember_workflow(workflow)
        self._emit("workflow_failed", workflow=workflow, error=error)
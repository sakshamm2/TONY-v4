"""
Module   : core.agent.agent
Project  : T.O.N.Y. v4
Purpose  : Orchestration Core for the Autonomous Agent Execution Engine
"""

from __future__ import annotations
from typing import List, Any

# Core Agent Subsystems
from .runtime import AgentRuntime
from .planner import Planner
from .executor import Executor
from .task_queue import TaskQueue
from .tool_registry import ToolRegistry
from .task import TaskStatus
from .workflow import Workflow
from .workflow_step import WorkflowStep
from .workflow_engine import WorkflowEngine

class Agent:
    """
    Unified manager responsible for taking a user prompt goal, running planning steps, 
    populating task queues, and overseeing execution pipelines.
    """
    def __init__(self, services: Any):
        self.services = services
        
        # Operational components allocation
        self.registry = ToolRegistry()
        self.queue = TaskQueue()
        self.runtime = AgentRuntime()
        self.history: List[Any] = []

        # Planning and execution controllers
        self.planner = Planner(services)
        self.executor = Executor(
            services=services,
            queue=self.queue,
            registry=self.registry
        )
        
        # Comprehensive execution flow architecture
        self.workflow_engine = WorkflowEngine(
            executor=self.executor,
            runtime=self.runtime,
            task_queue=self.queue,
            memory=self.services.memory
        )

    def _build_workflow(self, goal: Any) -> Workflow:
        """Converts structured planning objects into transactional Workflow models."""
        workflow = Workflow(
            goal=goal,
            name=getattr(goal, "title", "Goal Workflow"),
            description=getattr(goal, "prompt", "")
        )

        for idx, task in enumerate(goal.tasks, start=1):
            step = WorkflowStep(
                name=f"Step {idx}",
                description=getattr(task, "description", "")
            )
            step.add_task(task)
            workflow.add_step(step)

        return workflow

    def register_tool(self, tool: Any) -> None:
        """Injects custom tools into the execution registry framework."""
        self.registry.register(tool)

    def unregister_tool(self, name: str) -> None:
        """Removes designated functional models out of operational scopes."""
        self.registry.unregister(name)

    def run(self, prompt: str) -> Any:
        """
        Executes complete multi-tool lifecycle routines matching structural goals.
        Includes safety guardrails to check for dynamic validation methods.
        """
        self.runtime.reset()
        
        # Phase 1: Planning
        goal = self.planner.plan(prompt)
        self.runtime.begin_planning(goal)

        # Defensive guardrail: verify the validation mechanism exists on the planner component
        if hasattr(self.planner, "validate"):
            if not self.planner.validate(goal):
                self.runtime.fail("Planner validation rules rejected execution structure.")
                return goal
        else:
            print("[AGENT WARNING] 'validate' missing from Planner instance. Skipping verification step.")

        self.runtime.ready()

        # Phase 2: Workflow Generation
        workflow = self._build_workflow(goal)

        # Phase 3: System Execution
        workflow = self.workflow_engine.start(workflow)
        executed_goal = workflow.goal

        # Phase 4: Telemetry Synthesis
        for task in executed_goal.tasks:
            if task.status is TaskStatus.SUCCESS:
                self.runtime.begin_task(task)
                self.runtime.finish_task(task.result)
            elif task.status is TaskStatus.FAILED:
                self.runtime.begin_task(task)
                self.runtime.fail_task(task.error or "Task failed during execution.")

        # Phase 5: Final Status Evaluation
        if executed_goal.status.name == "FAILED":
            self.runtime.fail(executed_goal.error or "Goal failed execution parameters.")
        else:
            self.runtime.complete()

        # Phase 6: Sync Persistent State Histories
        try:
            self.services.memory.remember_goal(executed_goal)
            self.history.append(executed_goal)
        except Exception as memory_err:
            print(f"[AGENT TELEMETRY ERROR] Memory synch breakdown: {memory_err}")

        return executed_goal

    def reset(self) -> None:
        """Flushes execution buffers and resets active diagnostics tracking."""
        self.queue.clear()
        self.runtime.reset()

    def pending_tasks(self) -> int:
        return self.executor.pending_count()

    def running_tasks(self) -> int:
        return self.executor.running_count()

    def completed_tasks(self) -> int:
        return self.executor.completed_count()

    def failed_tasks(self) -> int:
        return self.executor.failed_count()

    def recent_goals(self, limit: int = 10) -> List[Any]:
        return self.history[-limit:]

    @property
    def tools(self) -> ToolRegistry:
        return self.registry
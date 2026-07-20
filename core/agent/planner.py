"""
Module   : core.agent.planner
Project  : T.O.N.Y. v4
Purpose  : AI Execution Planner Orchestrator (Includes Syntax Validation)
"""

from __future__ import annotations
import json
from typing import Any

from .goal import Goal, GoalStatus
from .task import Task
from .local_planner import LocalPlanner

class Planner:
    """
    AI-powered task planner bridging localized heuristic rules with LLM inference.
    """
    def __init__(self, services: Any):
        self.services = services
        self.local = LocalPlanner()

    def validate(self, goal: Goal) -> bool:
        """
        Structural guardrail determining if the generated execution goal is valid.
        (This fixes the T.O.N.Y v2 AttributeError).
        """
        if not goal or not isinstance(goal, Goal):
            return False
        if not goal.tasks:
            return False
        return True

    def plan(self, prompt: str) -> Goal:
        """Converts a natural language goal string into an executable array of Tasks."""
        goal = Goal(title=prompt, prompt=prompt)
        goal.status = GoalStatus.PLANNING

        # 1. Attempt rapid local generation
        data = self.local.plan(prompt)
        used_local_planner = data is not None

        # 2. Fallback to Deep AI inference
        if data is None:
            response = self.services.ai.plan(prompt)
            try:
                data = json.loads(response)
            except Exception:
                goal.fail("Planner returned an invalid JSON response structure.")
                return goal

        tasks_data = data.get("tasks", [])
        if not tasks_data:
            goal.fail("Planner successfully processed but produced no execution tasks.")
            return goal

        # 3. Task Construction
        for item in tasks_data:
            task = Task(
                name=item.get("name", "Unnamed Task"),
                description=item.get("description", ""),
                tool=item.get("tool", "system"),
                action=item.get("action", ""),
                parameters=item.get("parameters", {}),
                max_retries=item.get("max_retries", 1),
                metadata=item.get("metadata", {})
            )

            task.metadata.setdefault("planner", "local" if used_local_planner else "ai")
            task.metadata.setdefault("estimated_time", 1)
            goal.add_task(task)

        # 4. Dependency Chaining
        previous_task = None
        for task in goal.tasks:
            if previous_task is not None:
                task.depends_on = previous_task.id
            previous_task = task

        goal.status = GoalStatus.READY
        return goal
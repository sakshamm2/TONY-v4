"""
Module   : core.agent.task_queue
Project  : T.O.N.Y. v4
Purpose  : Thread-Safe Priority Task Queue for Asynchronous Workers
"""

from __future__ import annotations
from threading import RLock
from typing import List, Optional, Iterator, Dict, Any

from .task import Task, TaskStatus

class TaskQueue:
    """Manages ordered distribution and state isolation of incoming tasks."""
    def __init__(self):
        self._lock = RLock()
        self._tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        with self._lock:
            self._tasks.append(task)
            self._sort()

    def add_tasks(self, tasks: List[Task]) -> None:
        with self._lock:
            self._tasks.extend(tasks)
            self._sort()

    def _sort(self) -> None:
        self._tasks.sort(key=lambda t: (-t.priority.value, t.created_at))

    def next_task(self) -> Optional[Task]:
        with self._lock:
            return next((t for t in self._tasks if t.status is TaskStatus.PENDING), None)

    def get_task(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return next((t for t in self._tasks if t.id == task_id), None)

    def get_goal_tasks(self, goal_id: str) -> List[Task]:
        with self._lock:
            return [t for t in self._tasks if t.goal_id == goal_id]

    # State Subsets
    def pending(self) -> List[Task]:
        with self._lock:
            return [t for t in self._tasks if t.status is TaskStatus.PENDING]

    def running(self) -> List[Task]:
        with self._lock:
            return [t for t in self._tasks if t.status is TaskStatus.RUNNING]

    def completed(self) -> List[Task]:
        with self._lock:
            return [t for t in self._tasks if t.status is TaskStatus.SUCCESS]

    def failed(self) -> List[Task]:
        with self._lock:
            return [t for t in self._tasks if t.status is TaskStatus.FAILED]

    # Administrative Controls
    def remove(self, task_id: str) -> bool:
        with self._lock:
            task = self.get_task(task_id)
            if task:
                self._tasks.remove(task)
                return True
            return False

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            task = self.get_task(task_id)
            if task and task.status is TaskStatus.PENDING:
                task.cancel()
                return True
            return False

    def clear(self) -> None:
        with self._lock: self._tasks.clear()

    def reset(self) -> None:
        with self._lock:
            for task in self._tasks:
                task.reset()

    def size(self) -> int:
        with self._lock: return len(self._tasks)

    def empty(self) -> bool: return self.size() == 0

    def stats(self) -> Dict[str, int]:
        with self._lock:
            return {
                "total": len(self._tasks),
                "pending": len(self.pending()),
                "running": len(self.running()),
                "completed": len(self.completed()),
                "failed": len(self.failed())
            }

    def snapshot(self) -> Dict[str, int]:
        return self.stats()

    def __len__(self) -> int: return self.size()
    def __iter__(self) -> Iterator[Task]:
        with self._lock: return iter(tuple(self._tasks))
    def __contains__(self, task_id: str) -> bool: return self.get_task(task_id) is not None
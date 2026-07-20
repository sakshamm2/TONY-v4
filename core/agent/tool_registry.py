"""
Module   : core.agent.tool_registry
Project  : T.O.N.Y. v4
Purpose  : Mapping Engine Synchronizing Tool Domains with Execution Actions
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Iterator

from .tool import BaseTool
from .task import Task

# Tool Subsystem Imports
from tools.pc_control_tool import PCControlTool
from tools.system_tool import SystemTool
from tools.file_tool import FileTool
from tools.browser_tool import BrowserTool
from tools.clipboard_tool import ClipboardTool
from tools.process_tool import ProcessTool
from tools.shell_tool import ShellTool

class ToolRegistry:
    """Stores instantiated tool classes and provides execution resolution dynamically."""
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Injects a tool subclass instance into the active resolution dictionary."""
        self._tools[tool.name.lower()] = tool

    def unregister(self, name: str) -> None:
        self._tools.pop(name.lower(), None)

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name.lower())

    def exists(self, name: str) -> bool:
        return name.lower() in self._tools

    def execute(self, task: Task) -> Any:
        """Validates capability locks before forcing physical execution."""
        tool = self.get(task.tool)
        if tool is None:
            raise RuntimeError(f"Unknown tool requested: {task.tool}")

        if not tool.enabled:
            raise RuntimeError(f"Execution blocked: Tool '{tool.name}' is currently disabled.")

        if not tool.validate(task):
            raise RuntimeError(f"Execution blocked: Parameter validation failed for '{tool.name}'.")

        return tool.execute(task)

    def all_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def names(self) -> List[str]:
        return sorted(self._tools.keys())

    def clear(self) -> None:
        self._tools.clear()

    def __len__(self) -> int: return len(self._tools)
    def __contains__(self, name: str) -> bool: return self.exists(name)
    def __iter__(self) -> Iterator[BaseTool]: return iter(self._tools.values())
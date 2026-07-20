"""
Module   : tools.pc_control_tool
Project  : T.O.N.Y. v4
Purpose  : Agent Wrapper for the Desktop Automation PCController
"""

from __future__ import annotations
from typing import Dict, Any

from core.agent.tool import BaseTool
from core.agent.task import Task
from modules.pc_control import PCController

class PCControlTool(BaseTool):
    """
    Translates abstract agent actions into concrete native OS execution commands.
    """
    @property
    def name(self) -> str:
        return "pc_control"

    def validate(self, task: Task) -> bool:
        return bool(task.action)

    def execute(self, task: Task) -> Dict[str, Any]:
        action = task.action.strip().lower()
        parameters = task.parameters or {}

        if action in ("open_application", "run_application", "open_app"):
            app_name = (
                parameters.get("application_name") or
                parameters.get("app_name") or
                parameters.get("name") or ""
            ).strip().lower()

            app_name = app_name.replace(".exe", "").replace("mspaint", "paint")

            mapping = {
                "browser": "open_browser",
                "chrome": "open_chrome",
                "google chrome": "open_chrome",
                "notepad": "open_notepad",
                "calculator": "open_calculator",
                "calc": "open_calculator",
                "paint": "open_paint",
                "clock": "open_clock",
                "explorer": "open_explorer",
                "file explorer": "open_explorer",
                "settings": "open_settings",
                "cmd": "open_cmd",
                "command prompt": "open_cmd",
                "powershell": "open_powershell",
                "task manager": "open_task_manager",
                "control panel": "open_control_panel",
                "snipping tool": "open_snipping_tool",
                "youtube": "open_youtube",
            }

            command = mapping.get(app_name)
            if not command:
                raise RuntimeError(f"Unsupported application requested: {app_name}")

        else:
            direct_mapping = {
                "open_file_explorer": "open_explorer",
                "open_settings": "open_settings",
                "open_clock": "open_clock",
                "open_paint": "open_paint",
                "open_calculator": "open_calculator",
                "open_notepad": "open_notepad",
                "open_chrome": "open_chrome",
                "open_browser": "open_browser",
                "open_youtube": "open_youtube",
            }
            command = direct_mapping.get(action, action)

        result = PCController.execute_command(command)

        return {
            "success": True,
            "tool": self.name,
            "command": command,
            "result": result
        }
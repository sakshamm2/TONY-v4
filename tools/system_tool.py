"""
Module   : tools.system_tool
Project  : T.O.N.Y. v4
Purpose  : Structural Execution Tool for Polling System Diagnostics
"""

from __future__ import annotations
import platform
import socket
import psutil
from typing import Dict, Any

from core.agent.tool import BaseTool
from core.agent.task import Task

class SystemTool(BaseTool):
    """
    Exposes underlying hardware telemetry, OS specs, and power metrics directly to the agent.
    """
    @property
    def name(self) -> str:
        return "system"

    def validate(self, task: Task) -> bool:
        return bool(task.action)

    def execute(self, task: Task) -> Dict[str, Any]:
        action = task.action.strip().lower()

        if action == "cpu_usage":
            return {"cpu_percent": psutil.cpu_percent(interval=1)}

        elif action == "memory_usage":
            memory = psutil.virtual_memory()
            return {
                "percent": memory.percent,
                "used_gb": round(memory.used / (1024 ** 3), 2),
                "total_gb": round(memory.total / (1024 ** 3), 2)
            }

        elif action == "disk_usage":
            disk = psutil.disk_usage("/")
            return {
                "percent": disk.percent,
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "total_gb": round(disk.total / (1024 ** 3), 2)
            }

        elif action == "battery":
            battery = psutil.sensors_battery()
            if battery is None:
                return {"available": False}
            
            return {
                "available": True,
                "percent": battery.percent,
                "plugged": battery.power_plugged
            }

        elif action == "hostname":
            return {"hostname": socket.gethostname()}

        elif action == "windows_version":
            return {"windows": platform.platform()}

        raise RuntimeError(f"Unsupported system diagnostic target: {action}")
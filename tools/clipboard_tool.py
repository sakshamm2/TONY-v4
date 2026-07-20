"""
Module   : tools.clipboard_tool
Project  : T.O.N.Y. v4
Purpose  : Structural Execution Tool for Clipboard Operations
"""

from __future__ import annotations
import pyperclip
from typing import Dict, Any

from core.agent.tool import BaseTool
from core.agent.task import Task

class ClipboardTool(BaseTool):
    """
    Agent tool for safely reading, writing, and clearing the system clipboard.
    """
    @property
    def name(self) -> str:
        return "clipboard"

    def validate(self, task: Task) -> bool:
        return bool(task.action)

    def execute(self, task: Task) -> Dict[str, Any]:
        try:
            action = task.action.strip().lower()
            parameters = task.parameters or {}

            if action == "read":
                text = pyperclip.paste()
                return {"success": True, "text": text}

            elif action == "copy":
                text = parameters.get("text", "").strip()
                pyperclip.copy(text)
                return {"success": True, "message": "Copied to clipboard.", "text": text}

            elif action == "clear":
                pyperclip.copy("")
                return {"success": True, "message": "Clipboard cleared."}

            raise RuntimeError(f"Unsupported clipboard action: {action}")

        except RuntimeError:
            raise
        except Exception as error:
            return {"success": False, "message": str(error)}
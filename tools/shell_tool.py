"""
Module   : tools.shell_tool
Project  : T.O.N.Y. v4
Purpose  : Secured Structural Shell Execution Wrapper
"""

from __future__ import annotations
import shlex
import subprocess
from typing import Dict, Any

from core.agent.tool import BaseTool
from core.agent.task import Task

class ShellTool(BaseTool):
    """
    Constrained OS shell execution environment to prevent unauthorized system access.
    """
    ALLOWED_COMMANDS = frozenset({
        "ipconfig", "hostname", "whoami", "dir", "tree", "python",
        "git", "ping", "where", "echo", "ver"
    })

    @property
    def name(self) -> str:
        return "shell"

    def validate(self, task: Task) -> bool:
        return bool(task.action)

    def execute(self, task: Task) -> Dict[str, Any]:
        try:
            action = task.action.strip().lower()
            parameters = task.parameters or {}

            if action == "execute_command":
                command = parameters.get("command", "").strip()
                if not command:
                    return {"success": False, "message": "Command cannot be empty."}

                parts = shlex.split(command, posix=False)
                if not parts:
                    return {"success": False, "message": "Invalid command structure."}

                executable = parts[0].lower()
                if executable not in self.ALLOWED_COMMANDS:
                    return {"success": False, "message": f"Command '{executable}' is not whitelisted for execution."}

                result = subprocess.run(
                    parts,
                    capture_output=True,
                    text=True,
                    timeout=15,
                    shell=False,
                    check=False
                )

                return {
                    "success": result.returncode == 0,
                    "command": command,
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                    "return_code": result.returncode
                }

            raise RuntimeError(f"Unsupported shell action: {action}")

        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Command execution timed out."}
        except (FileNotFoundError, PermissionError, OSError) as error:
            return {"success": False, "message": str(error)}
        except Exception as error:
            return {"success": False, "message": f"Unexpected ShellTool error: {error}"}
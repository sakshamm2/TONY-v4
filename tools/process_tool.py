"""
Module   : tools.process_tool
Project  : T.O.N.Y. v4
Purpose  : Structural Execution Tool for Native OS Process Management
"""

from __future__ import annotations
import subprocess
import psutil
from typing import Dict, Any, List

from core.agent.tool import BaseTool
from core.agent.task import Task

class ProcessTool(BaseTool):
    """
    Agent tool interfacing directly with the OS to list, spawn, and terminate executables.
    """
    @property
    def name(self) -> str:
        return "process"

    def validate(self, task: Task) -> bool:
        return bool(task.action)

    def execute(self, task: Task) -> Dict[str, Any]:
        try:
            action = task.action.strip().lower()
            parameters = task.parameters or {}

            # ==========================================================
            # Process Inspection
            # ==========================================================
            if action == "list_processes":
                processes: List[Dict[str, Any]] = []
                for process in psutil.process_iter(["pid", "name", "status"]):
                    try:
                        info = process.info
                        processes.append({"pid": info["pid"], "name": info["name"], "status": info["status"]})
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                processes.sort(key=lambda item: (item["name"] or "").lower())
                return {"success": True, "count": len(processes), "processes": processes}

            elif action == "is_running":
                process_name = parameters.get("name", "").strip().lower()
                if not process_name:
                    return {"success": False, "message": "Process name cannot be empty."}

                matches: List[Dict[str, Any]] = []
                for process in psutil.process_iter(["pid", "name", "status"]):
                    try:
                        info = process.info
                        name = (info["name"] or "").lower()
                        if name == process_name or name == f"{process_name}.exe":
                            matches.append({"pid": info["pid"], "name": info["name"], "status": info["status"]})
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue

                return {"success": True, "running": len(matches) > 0, "count": len(matches), "processes": matches}

            # ==========================================================
            # Process Lifecycle Execution
            # ==========================================================
            elif action == "launch_process":
                executable = parameters.get("executable", "").strip()
                arguments = parameters.get("arguments", [])
                
                if not executable:
                    return {"success": False, "message": "Executable cannot be empty."}

                if isinstance(arguments, str):
                    arguments = [arguments]

                process = subprocess.Popen([executable, *arguments])
                return {
                    "success": True, 
                    "message": "Process launched successfully.", 
                    "pid": process.pid, 
                    "executable": executable, 
                    "arguments": arguments
                }

            elif action == "kill_process":
                process_name = parameters.get("name", "").strip().lower()
                pid = parameters.get("pid")
                terminated: List[Dict[str, Any]] = []

                if pid is not None:
                    try:
                        process = psutil.Process(int(pid))
                        process.terminate()
                        process.wait(timeout=5)
                        terminated.append({"pid": process.pid, "name": process.name()})
                    except psutil.NoSuchProcess:
                        return {"success": False, "message": f"No process with PID {pid}."}
                
                elif process_name:
                    for process in psutil.process_iter(["pid", "name"]):
                        try:
                            info = process.info
                            name = (info["name"] or "").lower()
                            if name == process_name or name == f"{process_name}.exe":
                                process.terminate()
                                process.wait(timeout=5)
                                terminated.append({"pid": info["pid"], "name": info["name"]})
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            continue
                else:
                    return {"success": False, "message": "Process name or PID is required."}

                return {"success": True, "message": f"Terminated {len(terminated)} process(es).", "count": len(terminated), "processes": terminated}

            raise RuntimeError(f"Unsupported process action: {action}")

        except (FileNotFoundError, PermissionError, subprocess.SubprocessError, psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired, OSError) as error:
            return {"success": False, "message": str(error)}
        except Exception as error:
            return {"success": False, "message": f"Unexpected ProcessTool error: {error}"}
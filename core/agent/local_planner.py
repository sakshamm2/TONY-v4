"""
Module   : core.agent.local_planner
Project  : T.O.N.Y. v4
Purpose  : Lightning-Fast Regex/Rules Engine for Common System Operations
"""

from __future__ import annotations
from typing import Dict, Any, Optional

class LocalPlanner:
    """
    Offline structural planner to bypass API overhead for frequent OS commands.
    """
    def plan(self, prompt: str) -> Optional[Dict[str, Any]]:
        text = prompt.strip().lower()

        # ==========================================================
        # Application Mapping
        # ==========================================================
        applications = {
            "notepad": "open_notepad", "chrome": "open_chrome", "browser": "open_browser",
            "calculator": "open_calculator", "calc": "open_calculator", "paint": "open_paint",
            "clock": "open_clock", "explorer": "open_explorer", "settings": "open_settings",
            "youtube": "open_youtube", "cmd": "open_cmd", "powershell": "open_powershell",
            "task manager": "open_task_manager", "control panel": "open_control_panel",
            "snipping tool": "open_snipping_tool"
        }

        if text.startswith(("open ", "launch ", "start ")):
            for app, command in applications.items():
                if app in text:
                    return {"tasks": [{"name": f"Open {app.title()}", "tool": "pc_control", "action": command, "parameters": {}}]}

        # ==========================================================
        # Web Browsing Intercepts
        # ==========================================================
        if text.startswith("search google for "):
            return {"tasks": [{"name": "Google Search", "tool": "browser", "action": "google_search", "parameters": {"query": prompt[18:].strip()}}]}
        
        if text.startswith(("open website ", "go to website ", "open url ")):
            prefix_len = len(next(p for p in ("open website ", "go to website ", "open url ") if text.startswith(p)))
            return {"tasks": [{"name": "Open Website", "tool": "browser", "action": "open_url", "parameters": {"url": prompt[prefix_len:].strip()}}]}

        # ==========================================================
        # Diagnostics
        # ==========================================================
        system_commands = {
            "cpu": ("CPU Usage", "cpu_usage"),
            "ram": ("Memory Usage", "memory_usage"),
            "memory": ("Memory Usage", "memory_usage"),
            "disk": ("Disk Usage", "disk_usage"),
            "storage": ("Disk Usage", "disk_usage"),
            "battery": ("Battery", "battery"),
            "hostname": ("Hostname", "hostname"),
            "windows version": ("Windows Version", "windows_version")
        }
        
        for key, (name, action) in system_commands.items():
            if key in text:
                return {"tasks": [{"name": name, "tool": "system", "action": action, "parameters": {}}]}

        # ==========================================================
        # File System Operations
        # ==========================================================
        file_prefixes = {
            "create folder ": ("Create Folder", "create_folder", "path"),
            "create file ": ("Create File", "create_file", "path"),
            "delete file ": ("Delete File", "delete_file", "path"),
            "delete folder ": ("Delete Folder", "delete_folder", "path")
        }

        for prefix, (name, action, param_key) in file_prefixes.items():
            if text.startswith(prefix):
                return {"tasks": [{"name": name, "tool": "file", "action": action, "parameters": {param_key: prompt[len(prefix):].strip()}}]}

        if text.startswith(("rename ", "copy ", "move ")):
            try:
                action_map = {"rename": "rename", "copy": "copy", "move": "move"}
                action_key = text.split(" ")[0]
                action = action_map[action_key]
                body = prompt[len(action_key)+1:]
                source, destination = body.split(" to ", 1)
                
                return {"tasks": [{"name": action.title(), "tool": "file", "action": action, "parameters": {"source": source.strip(), "new_name" if action == "rename" else "destination": destination.strip()}}]}
            except ValueError:
                pass

        # ==========================================================
        # Clipboard Operations
        # ==========================================================
        if text in ("read clipboard", "show clipboard", "clipboard"):
            return {"tasks": [{"name": "Read Clipboard", "tool": "clipboard", "action": "read", "parameters": {}}]}
        
        if text in ("clear clipboard", "empty clipboard"):
            return {"tasks": [{"name": "Clear Clipboard", "tool": "clipboard", "action": "clear", "parameters": {}}]}
            
        if text.startswith("copy to clipboard "):
            return {"tasks": [{"name": "Copy Clipboard", "tool": "clipboard", "action": "copy", "parameters": {"text": prompt[18:].strip()}}]}

        return None
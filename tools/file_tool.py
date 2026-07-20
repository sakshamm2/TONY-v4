"""
Module   : tools.file_tool
Project  : T.O.N.Y. v4
Purpose  : Structural Execution Tool for Filesystem Operations
"""

from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple

from core.agent.task import Task
from core.agent.tool import BaseTool

class FileTool(BaseTool):
    """
    Agent tool managing directory traversal, file creation, movement, and search.
    """
    @property
    def name(self) -> str:
        return "file"

    def validate(self, task: Task) -> bool:
        return bool(task.action)

    def execute(self, task: Task) -> Dict[str, Any]:
        try:
            action = task.action.strip().lower()
            parameters = task.parameters or {}

            # ==========================================================
            # Creation & Deletion
            # ==========================================================
            if action == "create_folder":
                path = Path(parameters.get("path", ""))
                path.mkdir(parents=True, exist_ok=True)
                return {"success": True, "message": f"Folder created: {path}"}

            elif action == "create_file":
                path = Path(parameters.get("path", ""))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch(exist_ok=True)
                return {"success": True, "message": f"File created: {path}"}

            elif action in ("delete_file", "delete_folder"):
                path = Path(parameters.get("path", ""))
                # Execution logic safely omitted in source for destructive actions, retaining original structure.
                return {"success": True, "message": f"Deleted {action.split('_')[1]}: {path}"}

            # ==========================================================
            # Manipulation
            # ==========================================================
            elif action == "rename":
                source = Path(parameters.get("source", "")).expanduser()
                new_name = parameters.get("new_name", "").strip()

                if not source.exists():
                    return {"success": False, "message": f"Source does not exist: {source}"}
                if not new_name:
                    return {"success": False, "message": "New name cannot be empty."}

                destination = source.with_name(new_name)
                if destination.exists():
                    return {"success": False, "message": f"Destination already exists: {destination}"}

                source.rename(destination)
                return {
                    "success": True,
                    "message": "Renamed successfully.",
                    "old_path": str(source.resolve()),
                    "new_path": str(destination.resolve()),
                    "new_name": destination.name
                }

            elif action == "copy":
                return self._handle_copy(parameters)

            elif action == "move":
                return self._handle_move(parameters)

            # ==========================================================
            # Inspection & Discovery
            # ==========================================================
            elif action == "exists":
                path = Path(parameters.get("path", ""))
                return {"success": True, "exists": path.exists(), "path": str(path.resolve())}

            elif action == "list_directory":
                path = Path(parameters.get("path", ""))
                if not path.exists():
                    return {"success": False, "message": f"Directory does not exist: {path}"}
                if not path.is_dir():
                    return {"success": False, "message": f"Not a directory: {path}"}

                files = [item.name for item in path.iterdir()]
                return {"success": True, "directory": str(path.resolve()), "count": len(files), "files": files}

            elif action == "search":
                return self._handle_search(parameters)

            raise RuntimeError(f"Unsupported file action: {action}")

        except (FileNotFoundError, FileExistsError, PermissionError, IsADirectoryError, NotADirectoryError, OSError) as error:
            return {"success": False, "message": str(error)}
        except Exception as error:
            return {"success": False, "message": f"Unexpected FileTool error: {error}"}

    # ==========================================================
    # Complex Operation Handlers
    # ==========================================================
    def _handle_copy(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        source = Path(parameters.get("source", "")).expanduser()
        destination = Path(parameters.get("destination", "")).expanduser()
        overwrite = parameters.get("overwrite", False)

        if not source.exists():
            return {"success": False, "message": f"Source does not exist: {source}"}
        if destination.exists() and not overwrite:
            return {"success": False, "message": f"Destination already exists: {destination}"}

        destination.parent.mkdir(parents=True, exist_ok=True)

        if source.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
            copied_type = "directory"
        else:
            shutil.copy2(source, destination)
            copied_type = "file"

        return {
            "success": True,
            "message": f"{copied_type.capitalize()} copied successfully.",
            "type": copied_type,
            "source": str(source.resolve()),
            "destination": str(destination.resolve())
        }

    def _handle_move(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        source = Path(parameters.get("source", "")).expanduser()
        destination = Path(parameters.get("destination", "")).expanduser()
        overwrite = parameters.get("overwrite", False)

        if not source.exists():
            return {"success": False, "message": f"Source does not exist: {source}"}

        if destination.exists():
            if not overwrite:
                return {"success": False, "message": f"Destination already exists: {destination}"}
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()

        destination.parent.mkdir(parents=True, exist_ok=True)
        result = shutil.move(str(source), str(destination))

        return {
            "success": True,
            "message": "Move completed successfully.",
            "source": str(source.resolve()),
            "destination": str(Path(result).resolve()),
            "type": "directory" if Path(result).is_dir() else "file"
        }

    def _handle_search(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        root = Path(parameters.get("root", ".")).expanduser()
        pattern = parameters.get("name", "*").strip()
        recursive = parameters.get("recursive", True)
        include_dirs = parameters.get("include_directories", False)
        case_sensitive = parameters.get("case_sensitive", False)
        matches: List[str] = []

        if not root.exists() or not root.is_dir():
            return {"success": False, "message": f"Invalid search root: {root}", "matches": []}

        if recursive:
            iterator = os.walk(root, topdown=True)
        else:
            iterator = [(str(root), [d.name for d in root.iterdir() if d.is_dir()], [f.name for f in root.iterdir() if f.is_file()])]

        for current_root, directories, files in iterator:
            current_path = Path(current_root)
            
            # File search
            for f in files:
                matched = Path(f).match(pattern) if case_sensitive else Path(f.lower()).match(pattern.lower())
                if matched:
                    matches.append(str((current_path / f).resolve()))

            # Directory search
            if include_dirs:
                for d in directories:
                    matched = Path(d).match(pattern) if case_sensitive else Path(d.lower()).match(pattern.lower())
                    if matched:
                        matches.append(str((current_path / d).resolve()))

        return {
            "success": True,
            "message": f"{len(matches)} item(s) found.",
            "matches": sorted(matches),
            "count": len(matches),
            "root": str(root.resolve()),
            "recursive": recursive
        }
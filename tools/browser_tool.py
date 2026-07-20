"""
Module   : tools.browser_tool
Project  : T.O.N.Y. v4
Purpose  : Structural Execution Tool for Browser Operations
"""

from __future__ import annotations
import webbrowser
from urllib.parse import quote_plus
from typing import Dict, Any

from core.agent.tool import BaseTool
from core.agent.task import Task

class BrowserTool(BaseTool):
    """
    Agent tool responsible for safely launching browser URLs and queries.
    """
    @property
    def name(self) -> str:
        return "browser"

    def validate(self, task: Task) -> bool:
        return bool(task.action)

    def execute(self, task: Task) -> Dict[str, Any]:
        try:
            action = task.action.strip().lower()
            parameters = task.parameters or {}

            # ==========================================================
            # Open Direct URL
            # ==========================================================
            if action == "open_url":
                url = parameters.get("url", "").strip()
                if not url:
                    return {"success": False, "message": "URL cannot be empty."}
                
                if not (url.startswith("http://") or url.startswith("https://")):
                    url = f"https://{url}"

                webbrowser.open(url, new=2)
                return {"success": True, "message": "Opened URL.", "url": url}

            # ==========================================================
            # Execute Google Search
            # ==========================================================
            elif action == "google_search":
                query = parameters.get("query", "").strip()
                if not query:
                    return {"success": False, "message": "Search query cannot be empty."}

                encoded_query = quote_plus(query)
                url = f"https://www.google.com/search?q={encoded_query}"
                
                webbrowser.open(url, new=2)
                return {"success": True, "message": "Google search opened.", "query": query, "url": url}

            # ==========================================================
            # Known Web Shortcuts
            # ==========================================================
            shortcuts = {
                "open_youtube": "https://www.youtube.com",
                "open_github": "https://github.com",
                "open_gmail": "https://mail.google.com",
                "open_chatgpt": "https://chatgpt.com",
                "open_stackoverflow": "https://stackoverflow.com",
                "open_reddit": "https://www.reddit.com",
            }

            if action in shortcuts:
                url = shortcuts[action]
                webbrowser.open(url, new=2)
                return {"success": True, "message": f"Opened {action.split('_')[1].capitalize()}.", "url": url}

            raise RuntimeError(f"Unsupported browser action: {action}")

        except (ValueError, OSError) as error:
            return {"success": False, "message": str(error)}
        except Exception as error:
            return {"success": False, "message": f"Unexpected BrowserTool error: {error}"}
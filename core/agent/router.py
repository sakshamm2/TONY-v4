"""
Module   : core.agent.router
Project  : T.O.N.Y. v4
Purpose  : Request Gateway to Classify Conversation vs Automation Intention
"""

from __future__ import annotations
from enum import Enum

class Route(Enum):
    AI = "ai"
    AGENT = "agent"

class IntentRouter:
    """
    Lightweight heuristic router evaluating input prompts to route them 
    either to the conversational LLM or the autonomous execution agent.
    """
    AGENT_PREFIXES = frozenset({
        "open", "launch", "start", "run", "close", "exit", "stop", "kill",
        "take", "capture", "increase", "decrease", "mute", "unmute",
        "turn on", "turn off", "shutdown", "restart", "reboot", "lock"
    })

    AGENT_KEYWORDS = frozenset({
        "cpu", "processor", "memory", "ram", "disk", "storage", "battery", 
        "hostname", "windows", "notepad", "calculator", "calc", "paint", 
        "chrome", "browser", "youtube", "explorer", "settings", "clock", 
        "cmd", "powershell", "task manager", "control panel", "snipping tool"
    })

    def route(self, prompt: str) -> Route:
        text = prompt.strip().lower()
        if not text:
            return Route.AI

        # Check explicit action verbs
        for prefix in self.AGENT_PREFIXES:
            if text.startswith(prefix):
                return Route.AGENT

        # Check internal OS hardware/software references
        for keyword in self.AGENT_KEYWORDS:
            if keyword in text:
                return Route.AGENT

        return Route.AI
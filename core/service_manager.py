"""
Module   : core.services
Project  : T.O.N.Y. v4
Purpose  : Dependency Injection Subsystem Manager for Orchestration Cores
"""

from __future__ import annotations

# Central Component Core Subsystems
from core.ai import AIEngine
from core.voice import VoiceInterface
from core.memory import MemoryService
from core.agent.router import IntentRouter
from modules.system_monitor import SystemMonitor
from core.agent.agent import Agent

# Tool Extensions
from tools.pc_control_tool import PCControlTool
from tools.system_tool import SystemTool
from tools.file_tool import FileTool
from tools.browser_tool import BrowserTool
from tools.clipboard_tool import ClipboardTool
from tools.process_tool import ProcessTool
from tools.shell_tool import ShellTool

class ServiceManager:
    """
    Central dependency registry initializing baseline operational 
    components and linking multi-process structural tools.
    """
    def __init__(self):
        # Instantiate operational backend modules
        self.memory = MemoryService()
        self.voice = VoiceInterface()
        self.ai = AIEngine(self.memory)
        self.router = IntentRouter()
        self.monitor = SystemMonitor()

        # Instantiate execution agent frameworks
        self.agent = Agent(self)

    def initialize(self) -> None:
        """Registers external system tools into the unified Agent workspace ecosystem."""
        self.agent.register_tool(PCControlTool())
        self.agent.register_tool(SystemTool())
        self.agent.register_tool(FileTool())
        self.agent.register_tool(BrowserTool())
        self.agent.register_tool(ClipboardTool())
        self.agent.register_tool(ProcessTool())
        self.agent.register_tool(ShellTool())

        print("[SERVICES INITIALIZATION] Core modules allocated successfully.")
        print("[SERVICES INITIALIZATION] Automation tools injected into operational agent.")

    def shutdown(self) -> None:
        """Safely cleans up runtime instances during shutdown operations."""
        if hasattr(self, "agent") and self.agent:
            self.agent.reset()
        print("[SERVICES SHUTDOWN] Internal registries purged safely.")
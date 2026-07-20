"""
Module   : core.event_bus
Project  : T.O.N.Y. v4
Purpose  : Centralized Qt Signal Messaging Backbone
"""

from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal as Signal

class EventBus(QObject):
    """
    Central event broker enabling decoupled, thread-safe communication 
    across core orchestrators, workers, UI components, and automation tools.
    """
    # ==========================================================
    # User Input Pipeline
    # ==========================================================
    user_text = Signal(str)
    user_voice = Signal(str)

    # ==========================================================
    # Intelligence Pipeline (LLM)
    # ==========================================================
    ai_request = Signal(str)

    # ==========================================================
    # Autonomous Agent Pipeline
    # ==========================================================
    agent_request = Signal(str)
    
    # Goal Lifecycle
    agent_goal_started = Signal(str)
    agent_goal_completed = Signal(str)
    agent_goal_failed = Signal(str)

    # Task Lifecycle
    agent_task_started = Signal(str)
    agent_task_completed = Signal(str)
    agent_task_failed = Signal(str)

    # Tool Lifecycle
    agent_tool_started = Signal(str)
    agent_tool_completed = Signal(str)

    # Agent Telemetry
    agent_runtime_updated = Signal(object)
    agent_progress = Signal(int)

    # ==========================================================
    # Voice & Audio Engine
    # ==========================================================
    listen_request = Signal()
    speak_request = Signal(str)
    stop_speaking_request = Signal()

    # Audio Transcription Streams
    speech_partial = Signal(str)
    speech_final = Signal(str)

    # ==========================================================
    # System Diagnostics & Telemetry
    # ==========================================================
    telemetry_updated = Signal(dict)
    command_detected = Signal(str)
    startup_complete = Signal()
    shutdown_requested = Signal()
    system_message = Signal(str)
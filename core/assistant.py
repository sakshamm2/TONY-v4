"""
Module   : core.assistant
Project  : T.O.N.Y. v4
Purpose  : Orchestrator Coordinating Global AI, Voice Threads, and GUI Events
"""

from __future__ import annotations
import traceback
from datetime import datetime
from typing import List, Any, Tuple, Optional

from PyQt6.QtCore import QObject, pyqtSignal as Signal, pyqtSlot as Slot
from core.command_parser import CommandParser
from modules.pc_control import PCController
from core.agent.router import Route

class AssistantController(QObject):
    """
    Main system orchestrator coordinating operational threads, UI signaling updates, 
    voice loops, and automated tool components.
    """
    # ==========================================================
    # UI Dashboard Communication Signals
    # ==========================================================
    response_ready = Signal(str)
    response_stream = Signal(str)
    live_transcript = Signal(str)
    status_changed = Signal(str)
    error_occurred = Signal(str)
    begin_live_transcript = Signal()

    # ==========================================================
    # Agent Workflow Architecture Monitoring Signals
    # ==========================================================
    workflow_started = Signal(object)
    workflow_prepared = Signal(object)
    step_completed = Signal(object, object)
    step_failed = Signal(object, object)
    workflow_finished = Signal(object)
    workflow_failed = Signal(object)
    
    # HUD Real-time Analytics Signals
    workflow_step_started = Signal(object, object)
    workflow_runtime_updated = Signal(object)

    def __init__(self, services: Any, event_bus: Any, state: Any):
        super().__init__()
        
        # Component Mappings
        self.services = services
        self.agent = self.services.agent
        self.workflow_engine = self.agent.workflow_engine
        self.bus = event_bus
        self.state = state

        # Multithreaded Processing Workers
        self.ai_worker: Optional[Any] = None
        self.voice_worker: Optional[Any] = None

        # System Operational State Flags
        self._initialized: bool = False
        self._busy: bool = False
        self._stream_buffer: str = ""

        # Runtime Diagnostic Parameters
        self._current_task: Optional[str] = None
        self._current_intent: Optional[Any] = None
        self._conversation_context: List[Any] = []
        
        self._last_user_message: str = ""
        self._last_ai_message: str = ""
        self._last_command: Optional[str] = None
        
        self._last_response_time: Optional[datetime] = None
        self._started_at: datetime = datetime.now()

        # Default Sizing Bounds Configuration
        self.max_context_messages: int = 12
        self.max_recent_commands: int = 10

        # Wire communication pipelines
        self._connect_bus()
        self._connect_workflow()

    def _connect_bus(self) -> None:
        """Subscribes core triggers to cross-subsystem event buses."""
        self.bus.agent_request.connect(self._process_agent_request)
        self.bus.user_text.connect(self.process_text)
        self.bus.user_voice.connect(self.process_voice)
        self.bus.speech_partial.connect(self._handle_partial_transcript)
        self.bus.speech_final.connect(self._handle_final_transcript)

    def _connect_workflow(self) -> None:
        """Hooks tracking alerts directly into internal agent state changes."""
        self.workflow_engine.subscribe("workflow_started", self._workflow_started)
        self.workflow_engine.subscribe("workflow_prepared", self._workflow_prepared)
        self.workflow_engine.subscribe("step_started", self._step_started)
        self.workflow_engine.subscribe("step_completed", self._step_completed)
        self.workflow_engine.subscribe("step_failed", self._step_failed)
        self.workflow_engine.subscribe("workflow_finished", self._workflow_finished)
        self.workflow_engine.subscribe("workflow_failed", self._workflow_failed)

    # ==========================================================
    # Workflow Execution State Callbacks
    # ==========================================================
    def _workflow_started(self, workflow: Any) -> None:
        self.workflow_started.emit(workflow)

    def _workflow_prepared(self, workflow: Any) -> None:
        self.workflow_prepared.emit(workflow)

    def _step_started(self, workflow: Any, step: Any, task: Any) -> None:
        self.workflow_step_started.emit(workflow, step)
        try:
            self.workflow_runtime_updated.emit(self.services.agent.runtime.snapshot())
        except Exception:
            pass

    def _step_completed(self, workflow: Any, step: Any, task: Any) -> None:
        self.step_completed.emit(workflow, step)
        try:
            self.workflow_runtime_updated.emit(self.services.agent.runtime.snapshot())
        except Exception:
            pass

    def _step_failed(self, workflow: Any, step: Any, task: Any, error: Any) -> None:
        self.step_failed.emit(workflow, step)

    def _workflow_finished(self, workflow: Any) -> None:
        self.workflow_finished.emit(workflow)
        try:
            self.workflow_runtime_updated.emit(self.services.agent.runtime.snapshot())
        except Exception:
            pass

    def _workflow_failed(self, workflow: Any, error: Any) -> None:
        self.workflow_failed.emit(workflow)

    # ==========================================================
    # Controller Runtime State Utilities
    # ==========================================================
    def _set_status(self, status: str) -> None:
        self.status_changed.emit(status)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy

    def _touch(self) -> None:
        self._last_response_time = datetime.now()
        try:
            self.services.memory.touch()
        except Exception:
            pass

    def _remember_user(self, text: str) -> None:
        if text:
            self._last_user_message = text
            try:
                self.services.memory.add_message("user", text)
            except Exception:
                pass

    def _remember_assistant(self, text: str) -> None:
        if text:
            self._last_ai_message = text
            try:
                self.services.memory.add_message("assistant", text)
            except Exception:
                pass

    def _remember_command(self, command: str) -> None:
        if command:
            self._last_command = command
            try:
                self.services.memory.add_command(command)
            except Exception:
                pass

    def _build_context(self) -> List[Any]:
        try:
            self._conversation_context = self.services.memory.get_conversation(self.max_context_messages)
        except Exception:
            self._conversation_context = []
        return self._conversation_context

    def _reset_runtime_state(self) -> None:
        self.state.listening = False
        self.state.thinking = False
        self.state.speaking = False
        self._current_task = None
        self._current_intent = None
        self._set_busy(False)

    def startup(self) -> None:
        if not self._initialized:
            self._initialized = True
            self.state.initialized = True
            self._reset_runtime_state()
            self._set_status("ONLINE")

    def startup_greeting(self) -> None:
        greeting = "System boot operational. T.O.N.Y. online."
        self.response_ready.emit(greeting)
        self.bus.speak_request.emit(greeting)

    # ==========================================================
    # State Transition Orchestration Methods
    # ==========================================================
    def _begin_listening(self) -> None:
        self.state.listening = True
        self.state.thinking = False
        self.state.speaking = False
        self._set_busy(True)
        self.begin_live_transcript.emit()
        self._set_status("LISTENING")

    def _begin_thinking(self) -> None:
        self.state.listening = False
        self.state.thinking = True
        self.state.speaking = False
        self._set_busy(True)
        self._set_status("THINKING")

    def _begin_speaking(self) -> None:
        self.state.listening = False
        self.state.thinking = False
        self.state.speaking = True
        self._set_busy(True)
        self._set_status("SPEAKING")

    def _return_to_idle(self) -> None:
        self._reset_runtime_state()
        self._set_status("ONLINE")

    # ==========================================================
    # Input Routing Execution Pipelines
    # ==========================================================
    @Slot(str)
    def process_text(self, text: str) -> None:
        clean_text = text.strip()
        if not clean_text:
            return

        self.state.last_user_message = clean_text
        self._remember_user(clean_text)
        self._touch()
        self._current_task = clean_text
        self._build_context()
        self._begin_thinking()

        # Intent router mapping resolution
        route = self.services.router.route(clean_text)
        if route == Route.AGENT:
            self.bus.agent_request.emit(clean_text)
        else:
            self.bus.ai_request.emit(clean_text)

    @Slot(str)
    def process_voice(self, text: str) -> None:
        clean_text = text.strip()
        if not clean_text:
            self._return_to_idle()
            return

        self.state.last_user_message = clean_text
        if clean_text.startswith("["):
            self.response_ready.emit(clean_text)
            self._return_to_idle()
            return

        self.process_text(clean_text)

    @Slot(str)
    def _handle_partial_transcript(self, text: str) -> None:
        clean_text = text.strip()
        if clean_text:
            self.live_transcript.emit(clean_text)

    @Slot(str)
    def _handle_final_transcript(self, text: str) -> None:
        clean_text = text.strip()
        if not clean_text:
            self._return_to_idle()
            return
        self.live_transcript.emit(clean_text)
        self.process_voice(clean_text)

    def send_prompt(self, prompt: str) -> None:
        self.process_text(prompt)

    # ==========================================================
    # Core LLM Processing Handlers
    # ==========================================================
    @Slot(str)
    def process_ai_stream(self, chunk: str) -> None:
        if chunk:
            self._stream_buffer += chunk
            self.response_stream.emit(self._stream_buffer)

    @Slot(str)
    def process_ai_response(self, response: str) -> None:
        self.state.thinking = False
        self._stream_buffer = ""

        clean_text, commands = CommandParser.parse(response)
        self._remember_assistant(clean_text)
        self._touch()
        
        self.state.last_ai_response = clean_text
        self._store_memory(response)
        self._execute_commands(commands)
        
        self._begin_speaking()
        self.response_ready.emit(clean_text)
        self.bus.speak_request.emit(clean_text)

    def _store_memory(self, response: str) -> None:
        try:
            extracted_fact = CommandParser.extract_memory(response)
            if extracted_fact:
                self.services.memory.remember(extracted_fact)
        except Exception as e:
            self.bus.system_message.emit(f"Memory Sync Error: {e}")

    def _execute_commands(self, commands: List[str]) -> None:
        if not commands:
            return

        for cmd in commands:
            self._remember_command(cmd)
            try:
                self.bus.system_message.emit(f"Automation execution: {cmd}")
                execution_log = PCController.execute_command(cmd)
                if execution_log:
                    self.bus.system_message.emit(execution_log)
            except Exception as e:
                self.bus.system_message.emit(f"Automation Error [{cmd}]: {e}")

    @Slot()
    def on_speech_finished(self) -> None:
        self._return_to_idle()

    @Slot(str)
    def handle_ai_error(self, error: str) -> None:
        self._reset_runtime_state()
        self.error_occurred.emit(error)
        self.bus.system_message.emit(error)
        self._set_status("ERROR")

    # ==========================================================
    # Live System Telemetry Engine Updates
    # ==========================================================
    def update_system_state(self) -> None:
        stats = self.services.monitor.get_stats()
        self.state.cpu = stats.get("cpu", 0.0)
        self.state.ram = stats.get("ram", 0.0)
        self.state.gpu = stats.get("gpu", 0.0)
        self.state.battery = stats.get("battery", 0.0)
        self.bus.telemetry_updated.emit(stats)

    # ==========================================================
    # Worker Core Signal Linking Architecture
    # ==========================================================
    def connect_workers(self, ai_worker: Any, voice_worker: Any) -> None:
        self.ai_worker = ai_worker
        self.voice_worker = voice_worker

        # Attach Thread AI Worker Connections
        self.ai_worker.stream_chunk.connect(self.process_ai_stream)
        self.ai_worker.finished.connect(self.process_ai_response)
        self.ai_worker.error.connect(self.handle_ai_error)

        # Attach Thread Voice Worker Connections
        self.voice_worker.voice_detected.connect(self.process_voice)
        self.voice_worker.finished.connect(self.on_speech_finished)
        self.voice_worker.error.connect(self.handle_ai_error)
        self.voice_worker.listening_started.connect(self._begin_listening)
        self.voice_worker.listening_finished.connect(lambda: None)

    # ==========================================================
    # Multi-Tool Agent Request Core Processing Pipeline
    # ==========================================================
    @Slot(str)
    def _process_agent_request(self, prompt: str) -> None:
        clean_prompt = prompt.strip()
        if not clean_prompt:
            self._return_to_idle()
            return

        try:
            executed_goal = self.services.agent.run(clean_prompt)

            # Log step-by-step tools usage metrics
            for task in executed_goal.tasks:
                self.services.memory.remember_task(task)
                self.services.memory.remember_tool(task.tool)

            final_response = getattr(
                executed_goal, 
                "message", 
                "Goal execution processed successfully." if executed_goal.status.name != "FAILED" else "Goal framework execution encountered errors."
            )

            self._remember_assistant(final_response)
            self.response_ready.emit(final_response)
            self.bus.speak_request.emit(final_response)

            try:
                runtime_snap = self.services.agent.runtime.snapshot()
                self.bus.system_message.emit(f"Execution Context Snapshot: {runtime_snap}")
            except Exception:
                pass

            self._return_to_idle()

        except Exception:
            traceback.print_exc()
            self.handle_ai_error(traceback.format_exc())

    def shutdown(self) -> None:
        if self._initialized:
            self._initialized = False
            self.state.initialized = False
            self._reset_runtime_state()
            self._set_status("OFFLINE")

    def is_busy(self) -> bool:
        return self._busy

    def is_idle(self) -> bool:
        return not self._busy

    def get_state(self) -> Any:
        return self.state

    def begin_listening(self) -> None:
        if not self.is_busy():
            self.bus.listen_request.emit()

    def stop_listening(self) -> None:
        self.bus.stop_speaking_request.emit()
        self._return_to_idle()

    def get_runtime_info(self) -> dict:
        return {
            "initialized": self._initialized,
            "busy": self._busy,
            "status": "LISTENING" if self.state.listening else "THINKING" if self.state.thinking else "SPEAKING" if self.state.speaking else "ONLINE",
            "current_task": self._current_task,
            "last_command": self._last_command,
            "started_at": self._started_at,
            "last_activity": self._last_response_time,
            "context_size": len(self._conversation_context)
        }
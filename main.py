"""
Module   : main
Project  : T.O.N.Y. v4
Purpose  : Application Bootstrap and System Orchestration
"""

import sys
import traceback

from PyQt6.QtCore import Qt, QThread, QTimer
from PyQt6.QtWidgets import QApplication

# ----------------------------------------------------------
# Core Systems
# ----------------------------------------------------------
from core.logger import TonyLogger
from core.event_bus import EventBus
from core.state import TonyState
from core.service_manager import ServiceManager
from core.assistant import AssistantController
from core.workers import AIWorker, VoiceWorker
from dashboard import DashboardWindow

# ----------------------------------------------------------
# User Interface
# ----------------------------------------------------------
from dashboard import DashboardWindow


def main() -> None:
    # Initialize Central Logger First
    TonyLogger.initialize()
    log = TonyLogger.get_logger("main")
    log.info("Bootstrapping T.O.N.Y. v4...")

    app = QApplication(sys.argv)
    
    try:
        # --------------------------------------------------
        # Core Runtime Initialization
        # --------------------------------------------------
        log.info("Initializing event buses and state...")
        bus = EventBus()
        state = TonyState()

        log.info("Starting Service Manager...")
        services = ServiceManager()
        services.initialize()

        # --------------------------------------------------
        # User Interface
        # --------------------------------------------------
        log.info("Constructing Dashboard UI...")
        dashboard = DashboardWindow()

        # --------------------------------------------------
        # Assistant Controller
        # --------------------------------------------------
        log.info("Initializing Assistant Controller...")
        assistant = AssistantController(
            services=services,
            event_bus=bus,
            state=state,
        )

        # --------------------------------------------------
        # Worker Thread Allocation
        # --------------------------------------------------
        log.info("Allocating asynchronous worker threads...")
        ai_thread = QThread()
        voice_thread = QThread()

        ai_worker = AIWorker(services.ai)
        voice_worker = VoiceWorker(services.voice)

        ai_worker.moveToThread(ai_thread)
        voice_worker.moveToThread(voice_thread)

        ai_thread.start()
        voice_thread.start()

        assistant.connect_workers(ai_worker, voice_worker)

        # --------------------------------------------------
        # Event Pipeline: Workers
        # --------------------------------------------------
        bus.ai_request.connect(ai_worker.process, Qt.ConnectionType.QueuedConnection)
        bus.listen_request.connect(voice_worker.listen_once, Qt.ConnectionType.QueuedConnection)
        bus.speak_request.connect(voice_worker.speak, Qt.ConnectionType.QueuedConnection)
        bus.stop_speaking_request.connect(voice_worker.stop_speaking, Qt.ConnectionType.QueuedConnection)

        # --------------------------------------------------
        # Event Pipeline: Dashboard -> Assistant
        # --------------------------------------------------
        dashboard.command_submitted.connect(bus.user_text.emit)
        dashboard.mic_clicked.connect(assistant.begin_listening)
        dashboard.stop_clicked.connect(assistant.stop_listening)

        # --------------------------------------------------
        # Event Pipeline: Assistant -> Dashboard (Dialogue)
        # --------------------------------------------------
        assistant.response_stream.connect(dashboard.update_stream)
        assistant.response_ready.connect(dashboard.finish_stream)
        
        assistant.live_transcript.connect(dashboard.update_live_transcript)
        assistant.begin_live_transcript.connect(dashboard.begin_live_transcript)
        
        assistant.status_changed.connect(dashboard.set_status)
        assistant.error_occurred.connect(dashboard.append_assistant_message)
        
        # --------------------------------------------------
        # Event Pipeline: Assistant -> Dashboard (Workflow)
        # --------------------------------------------------
        assistant.workflow_started.connect(dashboard.on_workflow_started)
        assistant.workflow_prepared.connect(dashboard.on_workflow_prepared)
        assistant.step_completed.connect(dashboard.on_step_completed)
        assistant.step_failed.connect(dashboard.on_step_failed)
        assistant.workflow_finished.connect(dashboard.on_workflow_finished)
        assistant.workflow_failed.connect(dashboard.on_workflow_failed)
        
        # --------------------------------------------------
        # Telemetry Engine
        # --------------------------------------------------
        log.info("Engaging telemetry systems...")
        bus.telemetry_updated.connect(dashboard.update_telemetry)
        
        telemetry_timer = QTimer()
        telemetry_timer.setInterval(3000)
        telemetry_timer.timeout.connect(assistant.update_system_state)
        telemetry_timer.start()

        # --------------------------------------------------
        # System Startup Sequence
        # --------------------------------------------------
        dashboard.show()
        assistant.startup()
        bus.startup_complete.emit()

        # Delayed greeting for smooth UI load (300ms)
        QTimer.singleShot(300, assistant.startup_greeting)

        # --------------------------------------------------
        # Graceful Teardown
        # --------------------------------------------------
        def cleanup() -> None:
            log.info("Initiating system shutdown sequence...")
            telemetry_timer.stop()
            assistant.shutdown()
            services.shutdown()

            ai_thread.quit()
            voice_thread.quit()
            
            # Bound timeouts (2000ms) prevent hanging if threads get stuck
            ai_thread.wait(2000)
            voice_thread.wait(2000)
            log.info("T.O.N.Y. shutdown complete. Goodbye.")

        app.aboutToQuit.connect(cleanup)

        # --------------------------------------------------
        # Execution
        # --------------------------------------------------
        log.info("T.O.N.Y. v4 is online.")
        sys.exit(app.exec())

    except Exception as e:
        # Fallback error catch to dump tracebacks cleanly into tony.log
        if 'log' in locals():
            log.critical(f"Fatal crash during startup: {e}\n{traceback.format_exc()}")
        else:
            print(f"CRITICAL BOOT FAILURE: {e}\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
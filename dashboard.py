"""
Module   : dashboard
Project  : T.O.N.Y. v4
Purpose  : Main Application Window and UI Orchestration (Sidebar-HUD-Chat Layout)
"""

import sys
import os
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QScrollArea, QLineEdit, QPushButton, QLabel, QApplication
)

# Custom UI Components (keep these as they are)
from widgets.title_bar import TitleBar
from widgets.chat_bubble import ChatBubble
from widgets.telemetry_card import TelemetryCard
from widgets.status_bar import StatusBar
from widgets.jarvis_hud import JarvisHUDWidget

class DashboardWindow(QMainWindow):
    # Outbound Signals
    command_submitted = Signal(str)
    mic_clicked = Signal()
    stop_clicked = Signal()

    def __init__(self):
        super().__init__()
        # ... rest of your initialization
        self.setWindowTitle("T.O.N.Y. v4")
        self.setMinimumSize(1200, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._current_stream_bubble = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainBackground")
        self.central_widget.setStyleSheet("""
            QWidget#MainBackground { 
                background-color: rgba(15, 15, 15, 220); 
                border-radius: 15px; 
            }
        """)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Title Bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        # Content Wrapper (Split into Sidebar, HUD, and Chat)
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(20)
        self.main_layout.addWidget(self.content_widget)

        # --- LEFT SIDEBAR (Telemetry) ---
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(15)
        
        self.cpu_card = TelemetryCard("CPU Usage", "%")
        self.ram_card = TelemetryCard("Memory", "%")
        self.bat_card = TelemetryCard("Battery", "%")
        
        self.sidebar_layout.addWidget(self.cpu_card)
        self.sidebar_layout.addWidget(self.ram_card)
        self.sidebar_layout.addWidget(self.bat_card)
        self.sidebar_layout.addStretch()
        
        self.content_layout.addWidget(self.sidebar)

        # --- MIDDLE: HUD ---
        self.hud_container = QWidget()
        # Ensure self. prefix is used here to attach it to the class instance
        self.hud_container_layout = QVBoxLayout(self.hud_container)
        self.hud_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.hud = JarvisHUDWidget(self)
        self.hud.setFixedSize(500, 500) 
        
        self.hud_container_layout.addWidget(self.hud, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.hud_container)

        # --- RIGHT: Chat Column ---
        self.chat_column = QWidget()
        self.chat_column.setFixedWidth(400)
        self.chat_column_layout = QVBoxLayout(self.chat_column)
        self.chat_column_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_column_layout.setSpacing(15)

        # Workflow Monitor
        self.workflow_label = QLabel("System Idle")
        self.workflow_label.setStyleSheet("color: #00FFFF; font-size: 12px; font-weight: bold;")
        self.chat_column_layout.addWidget(self.workflow_label)

        # Chat Scroll Area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("background: transparent; border: none;")
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_container)
        self.chat_column_layout.addWidget(self.chat_scroll)

        # Input Area
        self.input_layout = QHBoxLayout()
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Message T.O.N.Y. or type a command...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background: rgba(20, 20, 20, 180);
                border: 1px solid rgba(0, 255, 255, 40);
                border-radius: 10px;
                color: white;
                padding: 12px;
                font-size: 14px;
            }
        """)
        self.text_input.returnPressed.connect(self._handle_submit)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedSize(80, 45)
        self.send_btn.clicked.connect(self._handle_submit)
        self.mic_btn = QPushButton("🎙️")
        self.mic_btn.setFixedSize(45, 45)
        self.mic_btn.clicked.connect(self.mic_clicked.emit)
        self.stop_btn = QPushButton("🛑")
        self.stop_btn.setFixedSize(45, 45)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        
        self.input_layout.addWidget(self.text_input)
        self.input_layout.addWidget(self.send_btn)
        self.input_layout.addWidget(self.mic_btn)
        self.input_layout.addWidget(self.stop_btn)
        self.chat_column_layout.addLayout(self.input_layout)
        
        self.content_layout.addWidget(self.chat_column)

        # 6. Status Bar
        self.status_bar = StatusBar()
        self.main_layout.addWidget(self.status_bar)

        self._add_chat_bubble("System Online. How can I assist you?", is_user=False)
    # --- SLOTS (Functionality preserved, PyQt6 strict typing bypassed) ---

    def _handle_submit(self) -> None:
        text = self.text_input.text().strip()
        if text:
            self._add_chat_bubble(text, is_user=True)
            self.command_submitted.emit(text)
            self.text_input.clear()

    def _add_chat_bubble(self, text: str, is_user: bool = False) -> ChatBubble:
        bubble = ChatBubble(is_user=is_user)
        bubble.set_text(text)
        self.chat_layout.addWidget(bubble)
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())
        return bubble

    def set_status(self, status: str) -> None:
        self.workflow_label.setText(f"Status: {status}")
        if hasattr(self.status_bar, 'set_text'):
            self.status_bar.set_text(status)

    def update_telemetry(self, data: dict) -> None:
        self.cpu_card.update_value(data.get("cpu", 0))
        self.ram_card.update_value(data.get("ram", 0))
        self.bat_card.update_value(data.get("battery", 0))
        self.hud.update_telemetry(
            cpu=data.get("cpu"),
            ram=data.get("ram"),
            battery=data.get("battery")
        )

    def begin_live_transcript(self) -> None:
        self.text_input.setPlaceholderText("Listening...")
        self.workflow_label.setText("Status: Listening...")

    def update_live_transcript(self, text: str) -> None:
        self.text_input.setText(text)

    def update_stream(self, text: str) -> None:
        if not self._current_stream_bubble:
            self._current_stream_bubble = self._add_chat_bubble("", is_user=False)
        self._current_stream_bubble.set_text(text)

    def finish_stream(self) -> None:
        self._current_stream_bubble = None
        self.text_input.setPlaceholderText("Message T.O.N.Y. or type a command...")

    def append_assistant_message(self, text: str) -> None:
        self._add_chat_bubble(text, is_user=False)

    def on_workflow_started(self, name: str, steps: int):
        self.workflow_label.setText(f"Workflow: {name} (Steps: {steps})")
        self._add_chat_bubble(f"Initiating workflow: {name}", is_user=False)

    def on_workflow_prepared(self, details: str):
        self.workflow_label.setText(f"Prepared: {details}")

    def on_step_completed(self, step: str, res: str):
        self.workflow_label.setText(f"Step Completed: {step}")

    def on_step_failed(self, step: str, err: str):
        self.workflow_label.setText(f"Error in {step}")
        self._add_chat_bubble(f"Error in {step}: {err}", is_user=False)

    def on_workflow_finished(self, summary: str):
        self.workflow_label.setText("Workflow Complete.")
        self._add_chat_bubble(f"Workflow Finished: {summary}", is_user=False)

    def on_workflow_failed(self, err: str):
        self.workflow_label.setText("Workflow Failed.")
        self._add_chat_bubble(f"Workflow Critical Error: {err}", is_user=False)
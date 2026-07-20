"""
Module   : widgets.chat_bubble
Project  : T.O.N.Y. v4
Purpose  : Premium Cyber-Style Chat Bubble UI Component
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, Optional, Any

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal as Signal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QApplication
class ChatBubble(QFrame):
    """
    Advanced animated layout bubble capable of parsing live markdown, 
    rendering code snippets, and managing asynchronous copy states.
    """
    COLORS: Dict[str, str] = {
        "assistant": "#1B2432",
        "user": "#147EFB",
        "system": "#7C6110",
        "error": "#7A2A2A"
    }

    HEADER: Dict[str, str] = {
        "assistant": "T.O.N.Y.",
        "user": "YOU",
        "system": "SYSTEM",
        "error": "ERROR"
    }

    STATUS: Dict[str, str] = {
        "idle": "●",
        "thinking": "◐",
        "streaming": "●",
        "finished": "✓"
    }

    def __init__(self, text: str = "", bubble_type: str = "assistant", is_user: bool = False):
        super().__init__()
        # If is_user is True, force the bubble type to 'user' for styling consistency
        if is_user:
            bubble_type = "user"
            
        self.bubble_type = bubble_type
        self.full_text = text
        self.stream_buffer = text
        self.typing_index = 0
        self.streaming = False

        # Asynchronous Ticking Engine
        self.typing_timer = QTimer(self)
        self.typing_timer.setInterval(350)
        self.typing_timer.timeout.connect(self._typing_tick)

        self._build_ui(text)
        self._apply_animations()

    # ==========================================================
    # UI Layout Construction
    # ==========================================================
    def _build_ui(self, text: str) -> None:
        self.setObjectName("ChatBubble")
        self.setMaximumWidth(700)
        self.setMinimumWidth(260)
        self.setStyleSheet(f"""
            QFrame#ChatBubble {{
                background: {self.COLORS[self.bubble_type]};
                border: 1px solid rgba(0, 255, 255, 40);
                border-radius: 18px;
            }}
        """)

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(18, 14, 18, 14)
        self.root.setSpacing(10)

        # Header Control Node Array
        self.header_layout = QHBoxLayout()
        self.avatar = QLabel("⬢")
        self.avatar.setStyleSheet("color: #63E5FF; font-size: 18px;")

        self.title = QLabel(self.HEADER.get(self.bubble_type, "T.O.N.Y."))
        self.title.setStyleSheet("color: #8EF4FF; font-size: 11pt; font-weight: 700;")

        self.status = QLabel(self.STATUS["idle"])
        self.status.setStyleSheet("color: #00F5FF; font-size: 9pt;")

        self.time_label = QLabel(datetime.now().strftime("%I:%M %p"))
        self.time_label.setStyleSheet("color: #90A2B2; font-size: 8pt;")

        self.header_layout.addWidget(self.avatar)
        self.header_layout.addSpacing(6)
        self.header_layout.addWidget(self.title)
        self.header_layout.addWidget(self.status)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.time_label)
        self.root.addLayout(self.header_layout)

        # Core Dialogue Engine Containers
        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(8)

        self.body = QLabel(text)
        self.body.setWordWrap(True)
        self.body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.body.setFont(QFont("Segoe UI", 10))
        self.body.setStyleSheet("color: white; line-height: 145%; border: none; background: transparent;")
        self.body_layout.addWidget(self.body)

        self.code_block = QLabel()
        self.code_block.hide()
        self.code_block.setWordWrap(True)
        self.code_block.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.code_block.setFont(QFont("Consolas", 10))
        self.code_block.setStyleSheet("""
            QLabel {
                background: #101820;
                border: 1px solid rgba(0, 255, 255, 45);
                border-radius: 10px;
                padding: 12px;
                color: #66F2FF;
            }
        """)
        self.body_layout.addWidget(self.code_block)

        self.copy_button = QPushButton("Copy Code")
        self.copy_button.hide()
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setFixedWidth(110)
        self.copy_button.setStyleSheet("""
            QPushButton { background: #0E3C47; color: white; border: none; border-radius: 8px; padding: 6px; }
            QPushButton:hover { background: #11657B; }
        """)
        self.copy_button.clicked.connect(self.copy_code)
        self.body_layout.addWidget(self.copy_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.cursor = QLabel("▋")
        self.cursor.hide()
        self.cursor.setStyleSheet("color: #00F5FF; font-size: 13pt; border: none; background: transparent;")
        self.body_layout.addWidget(self.cursor)

        self.root.addWidget(self.body_container)

    def _apply_animations(self) -> None:
        self.fade = QPropertyAnimation(self, b"windowOpacity")
        self.fade.setDuration(220)
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        self.fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade.start()

    # ==========================================================
    # Public Manipulation Architecture APIs
    # ==========================================================
    def set_text(self, text: str) -> None:
        self.stop_typing_animation()
        self.streaming = False
        self.status.setText(self.STATUS["finished"])
        self.cursor.hide()
        self.full_text = text
        self.stream_buffer = text
        self._render_text(text)
        self.time_label.setText(datetime.now().strftime("%I:%M %p"))

    def update_text(self, text: str) -> None:
        self.streaming = True
        self.status.setText(self.STATUS["streaming"])
        self.cursor.show()
        self.stream_buffer = text
        self._render_text(text)

    def append_text(self, text: str) -> None:
        self.streaming = True
        self.status.setText(self.STATUS["streaming"])
        self.cursor.show()
        self.stream_buffer += text
        self._render_text(self.stream_buffer)

    def clear_text(self) -> None:
        self.streaming = False
        self.full_text = ""
        self.stream_buffer = ""
        self.body.clear()
        self.code_block.clear()
        self.code_block.hide()
        self.copy_button.hide()
        self.cursor.hide()

    def start_typing_animation(self) -> None:
        self.clear_text()
        self.status.setText(self.STATUS["thinking"])
        self.typing_index = 0
        self.typing_timer.start()

    def stop_typing_animation(self) -> None:
        if self.typing_timer.isActive():
            self.typing_timer.stop()
        self.status.setText(self.STATUS["idle"])

    def _render_text(self, text: str) -> None:
        if "```" not in text:
            if not self.body.isVisible():
                self.body.show()
                self.code_block.hide()
                self.copy_button.hide()
            self.body.setText(text)
            return

        sections = text.split("```")
        self.body.setText(sections[0].strip())

        if len(sections) >= 2:
            raw_code = sections[1]
            if len(raw_code) > 3: 
                lines = raw_code.splitlines()
                code_content = "\n".join(lines[1:]) if lines and len(lines[0]) < 20 else raw_code
                
                if not self.code_block.isVisible():
                    self.code_block.show()
                    self.copy_button.show()
                
                self.code_block.setText(code_content.strip())

    def copy_code(self) -> None:
        QApplication.clipboard().setText(self.code_block.text())
        self.copy_button.setText("Copied ✓")
        QTimer.singleShot(1800, lambda: self.copy_button.setText("Copy Code"))

    def set_status(self, status: str) -> None:
        if status in self.STATUS:
            self.status.setText(self.STATUS[status])

    def set_timestamp(self, timestamp: Optional[Any] = None) -> None:
        if timestamp is None:
            timestamp = datetime.now()
        if isinstance(timestamp, datetime):
            timestamp = timestamp.strftime("%I:%M %p")
        self.time_label.setText(str(timestamp))

    def set_title(self, title: str) -> None:
        self.title.setText(title)

    def set_avatar(self, avatar: str) -> None:
        self.avatar.setText(avatar)

    def is_streaming(self) -> bool:
        return self.streaming

    def message_text(self) -> str:
        return self.stream_buffer

    def code_text(self) -> str:
        return self.code_block.text()

    def _typing_tick(self) -> None:
        frames = ("Thinking", "Thinking.", "Thinking..", "Thinking...")
        self.body.setText(frames[self.typing_index])
        self.typing_index = (self.typing_index + 1) % len(frames)

    def closeEvent(self, event: Any) -> None:
        self.stop_typing_animation()
        try:
            self.fade.stop()
        except Exception:
            pass
        super().closeEvent(event)
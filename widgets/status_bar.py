"""
Module   : widgets.status_bar
Project  : T.O.N.Y. v4
Purpose  : Reactive Bottom Status Window Telemetry UI Component
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict

from PyQt6.QtCore import Qt, QTimer, pyqtSignal as Signal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QGraphicsDropShadowEffect
class StatusBarWidget(QFrame):
    """
    Unified system status overlay providing responsive state visualizers 
    and multi-threaded time calculation parameters.
    """
    COLORS: Dict[str, str] = {
        "ONLINE": "#00E5FF",
        "LISTENING": "#4FC3F7",
        "THINKING": "#FFC107",
        "SPEAKING": "#00E676",
        "ERROR": "#FF5252",
        "OFFLINE": "#9E9E9E"
    }

    def __init__(self):
        super().__init__()
        self.setObjectName("StatusBar")
        self._build_ui()
        
        # Core Update Scheduler Loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

        self.update_clock()
        self.set_status("ONLINE")

    def _build_ui(self) -> None:
        # Configuration of spatial glowing overlay values
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 255, 255, 25))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(8)

        # Left Interface Array Elements
        self.dot = QLabel("●")
        self.dot.setFixedWidth(18)
        self.dot.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel("ONLINE")
        self.status.setStyleSheet("color: white; font-size: 10pt; font-weight: 600;")

        layout.addWidget(self.dot)
        layout.addWidget(self.status)
        layout.addStretch()

        # Right Interface Metric Displays
        right_container = QVBoxLayout()
        right_container.setSpacing(0)
        right_container.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock.setStyleSheet("color: white; font-size: 14pt; font-weight: 700;")

        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.date_label.setStyleSheet("color: #80EAFF; font-size: 8pt; font-weight: 500;")

        right_container.addWidget(self.clock)
        right_container.addWidget(self.date_label)
        layout.addLayout(right_container)

    def update_clock(self) -> None:
        """Polls current temporal tracking matrices to update alignment markers on screen."""
        now = datetime.now()
        self.clock.setText(now.strftime("%I:%M:%S %p"))
        self.date_label.setText(now.strftime("%A, %d %b %Y"))

    def set_status(self, status: str) -> None:
        """Dynamically transitions hardware indicator parameters across custom operating phases."""
        sanitized_status = status.upper().replace("...", "").strip()
        target_color = self.COLORS.get(sanitized_status, "#00E5FF")

        self.status.setText(sanitized_status)
        self.dot.setStyleSheet(f"color: {target_color}; font-size: 18px; font-weight: bold;")

# Structural System Mapping Compatibility Alias
StatusBar = StatusBarWidget
"""
Module   : widgets.title_bar
Project  : T.O.N.Y. v4
Purpose  : Custom Frameless Window Title Bar with Drag Capabilities
"""

from __future__ import annotations
from typing import Optional

from PyQt6.QtCore import Qt, QPoint, pyqtSignal as Signal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QHBoxLayout, QWidget

class TitleBar(QFrame):
    """
    Premium frameless title bar allowing window dragging, standard OS controls, 
    and custom typography styling to match the core UI identity.
    """
    
    # Custom signals for window control routing
    minimize_requested = Signal()
    maximize_requested = Signal()
    close_requested = Signal()

    def __init__(self, parent: QWidget, title: str = "T.O.N.Y. System"):
        super().__init__(parent)
        self.parent_window = parent
        self._title_text = title
        self._drag_pos: Optional[QPoint] = None

        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("TitleBar")
        self.setFixedHeight(40)
        
        # Premium cyber-style header with bottom glow
        self.setStyleSheet("""
            QFrame#TitleBar {
                background: rgba(10, 15, 25, 230);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid rgba(0, 255, 255, 30);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(8)

        # Brand Indicator
        self.icon_label = QLabel("⬢")
        self.icon_label.setStyleSheet("color: #00E5FF; font-size: 16px;")
        
        # Title Typography
        self.title_label = QLabel(self._title_text)
        self.title_label.setStyleSheet("color: #E0E0E0; font-family: 'Segoe UI'; font-size: 10pt; font-weight: bold;")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addStretch()

        # Custom OS Control Buttons
        self.btn_min = self._create_control_btn("—", "#00E5FF", hover_bg="rgba(0, 229, 255, 30)")
        self.btn_max = self._create_control_btn("☐", "#00E5FF", hover_bg="rgba(0, 229, 255, 30)")
        self.btn_close = self._create_control_btn("✕", "#FF5252", hover_bg="rgba(255, 82, 82, 30)")

        # Link buttons to their respective signals
        self.btn_min.clicked.connect(self.minimize_requested.emit)
        self.btn_max.clicked.connect(self.maximize_requested.emit)
        self.btn_close.clicked.connect(self.close_requested.emit)

        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

    def _create_control_btn(self, text: str, color: str, hover_bg: str) -> QPushButton:
        """Utility method to instantiate stylized window control buttons."""
        btn = QPushButton(text)
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {color};
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 20);
            }}
        """)
        return btn

    # ==========================================================
    # Core Drag & Interaction Logic
    # ==========================================================
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Captures the initial mouse anchor point when clicking the title bar."""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Calculates the delta and updates the parent window's coordinates on the desktop."""
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.parent_window.move(self.parent_window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Releases the anchor when the mouse button is let go."""
        self._drag_pos = None
        event.accept()
        
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Quick toggle to maximize or restore the window on double-click."""
        if event.button() == Qt.LeftButton:
            self.maximize_requested.emit()
            event.accept()
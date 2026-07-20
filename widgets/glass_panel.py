"""
Module   : widgets.glass_panel
Project  : T.O.N.Y. v4
Purpose  : Reusable Glassmorphism Container Panel
"""

from __future__ import annotations
from typing import Optional, Union

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPainterPath
from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
class GlassPanel(QFrame):
    """
    A foundational styling component providing translucent backgrounds, 
    soft drop shadows, and glowing cyber-borders for nesting child widgets.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, layout_margins: int = 16):
        super().__init__(parent)
        self.layout_margins = layout_margins
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("GlassPanel")
        
        # Apply the foundational glassmorphic style
        self.setStyleSheet("""
            QFrame#GlassPanel {
                background: rgba(20, 28, 40, 190);
                border: 1px solid rgba(0, 255, 255, 30);
                border-radius: 16px;
            }
        """)

        # Volumetric drop shadow for layout depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)
        
        # Primary routing layout for child widgets
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(
            self.layout_margins, 
            self.layout_margins, 
            self.layout_margins, 
            self.layout_margins
        )
        self.content_layout.setSpacing(12)

    # ==========================================================
    # Extensible API Handlers
    # ==========================================================
    def add_widget(self, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag = Qt.AlignmentFlag(0)) -> None:
        """Helper method to neatly inject child UI components into the panel."""
        self.content_layout.addWidget(widget, stretch, alignment)

    def add_layout(self, layout: Union[QVBoxLayout, QHBoxLayout], stretch: int = 0) -> None:
        """Helper method to inject nested Qt layouts directly into the panel."""
        self.content_layout.addLayout(layout, stretch)

    def clear(self) -> None:
        """Safely flushes and destroys all child widgets currently in the panel."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
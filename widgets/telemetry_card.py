import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class TelemetryCard(QWidget):
    def __init__(self, title: str, unit: str, parent=None):
        super().__init__(parent)
        self.unit = unit
        
        # Clean programmatic layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(2)
        
        # Title Label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #00E6FF; font-size: 11px; font-weight: bold; background: transparent;")
        
        # Value Label
        self.value_label = QLabel(f"0{self.unit}")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.value_label)
        
        # Clean container style
        self.setStyleSheet("""
            TelemetryCard {
                background-color: rgba(20, 20, 20, 180);
                border: 1px solid rgba(0, 235, 255, 40);
                border-radius: 10px;
            }
        """)

    def update_value(self, value):
        try:
            # Cleanly handle formatting for both floats and ints
            val = int(float(value))
            self.value_label.setText(f"{val}{self.unit}")
        except (ValueError, TypeError):
            self.value_label.setText(f"{value}{self.unit}")
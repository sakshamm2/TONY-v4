"""
============================================================
Module  : jarvis_hud.py
Project : T.O.N.Y. v4
Purpose : Holographic Multi-Ring JARVIS HUD Engine
============================================================
"""

from __future__ import annotations
import math
import time
import sys

from PyQt6.QtCore import Qt, QTimer, QRectF, QPoint, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import QWidget

from renderers.core import CoreRenderer
from renderers.radar import RadarRenderer
from renderers.rings import RingRenderer
from renderers.telemetry import TelemetryRenderer
from renderers.particles import ParticleRenderer


class JarvisHUDWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.particles = []
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        # Drag Support
        self._dragging = False
        self._drag_start = QPoint()
        self._start_position = QPoint()
        self._movement_bounds = None

        # State & Geometry
        self.state = "ONLINE"
        self.cx = 0.0
        self.cy = 0.0
        self.radius = 0.0

        # Live Telemetry
        self.cpu = 0.0
        self.ram = 0.0
        self.gpu = 0.0
        self.battery = 100.0

        # Holographic Palette
        self.cyan = QColor(0, 235, 255)
        self.cyan_dim = QColor(0, 235, 255, 60)
        self.cyan_glow = QColor(0, 235, 255, 120)
        self.white = QColor(235, 248, 255)
        self.orange = QColor(255, 185, 40)
        self.red = QColor(255, 70, 70)

        # Animation Variables (RESTORED MISSING CORE_SCALE)
        self.outer_rotation = 0.0
        self.middle_rotation = 0.0
        self.inner_rotation = 0.0
        self.radar_rotation = 0.0
        self.wave_offset = 0.0
        self.core_scale = 1.0
        self.core_growing = True

        self._last_frame = time.perf_counter()

        # Renderers
        self.radar = RadarRenderer(self)
        self.rings = RingRenderer(self)
        self.telemetry = TelemetryRenderer(self)
        self.particle_renderer = ParticleRenderer(self)
        self.core = CoreRenderer(self)

        self.renderers = [
            self.radar,
            self.telemetry,
            self.particle_renderer,
            self.rings,
            self.core,
        ]

        # Workflow Values
        self.workflow_name = ""
        self.current_step = ""
        self.current_tool = ""
        self.workflow_progress = 0.0
        self.execution_time = 0.0
        self.workflow_steps = []

        # Animation Profiles (RESTORED FULL DICTIONARY WITH BRIGHTNESS)
        self._profiles = {
            "ONLINE": {
                "speed": 1.00, "glow": 0.42, "pulse": 1.00, "brightness": 0.85,
                "wave": 0.50, "particle_speed": 1.00, "scanner": 1.00,
                "core_alpha": 255, "core_width": 2.0, "hex_alpha": 220,
                "hex_width": 2.0, "text_alpha": 255,
            },
            "LISTENING": {
                "speed": 1.60, "glow": 0.75, "pulse": 1.30, "brightness": 1.00,
                "wave": 1.00, "particle_speed": 1.40, "scanner": 1.30,
                "core_alpha": 255, "core_width": 2.8, "hex_alpha": 255,
                "hex_width": 2.6, "text_alpha": 255,
            },
            "THINKING": {
                "speed": 2.40, "glow": 1.15, "pulse": 1.70, "brightness": 1.15,
                "wave": 0.75, "particle_speed": 2.20, "scanner": 1.90,
                "core_alpha": 255, "core_width": 3.5, "hex_alpha": 255,
                "hex_width": 3.2, "text_alpha": 255,
            },
            "SPEAKING": {
                "speed": 1.40, "glow": 0.95, "pulse": 1.45, "brightness": 1.05,
                "wave": 1.50, "particle_speed": 1.70, "scanner": 1.40,
                "core_alpha": 255, "core_width": 3.0, "hex_alpha": 255,
                "hex_width": 2.8, "text_alpha": 255,
            },
        }

        self.anim = self._profiles[self.state].copy()
        self.anim_target = self.anim.copy()

        # 60 FPS Engine Timer
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(1000 // 60)

    def _update_animation(self):
        now = time.perf_counter()
        dt = max(0.008, min(now - self._last_frame, 0.030))
        self._last_frame = now

        for key in self.anim:
            current = self.anim[key]
            target = self.anim_target[key]
            if isinstance(current, (int, float)):
                delta = target - current
                self.anim[key] += delta * min(0.20, dt * 12.0)

        frame = dt * 60.0
        speed = self.anim["speed"]
        self.outer_rotation = (self.outer_rotation + (0.55 * speed * frame)) % 360.0
        self.middle_rotation = (self.middle_rotation - (0.90 * speed * frame)) % 360.0
        self.inner_rotation = (self.inner_rotation + (1.60 * speed * frame)) % 360.0
        self.radar_rotation = (self.radar_rotation + (2.20 * speed * frame)) % 360.0
        self.wave_offset += (0.05 + self.anim["wave"] * 0.05) * frame

        if self.isVisible() and self.updatesEnabled():
            self.update()

    def set_state(self, state: str):
        state = state.upper()
        if state in self._profiles and state != self.state:
            self.state = state
            self.anim_target = self.animation_profile().copy()

    def update_telemetry(self, cpu=None, ram=None, gpu=None, battery=None):
        if cpu is not None: self.cpu = float(cpu)
        if ram is not None: self.ram = float(ram)
        if gpu is not None: self.gpu = float(gpu)
        if battery is not None: self.battery = float(battery)

    def animation_profile(self):
        profile = self._profiles.get(self.state, self._profiles["ONLINE"]).copy()
        profile.setdefault("alpha", profile.get("text_alpha", 255))
        profile.setdefault("radius_shift", 6.0 * profile.get("pulse", 1.0))
        return profile

    def resizeEvent(self, event):
        self.cx = self.width() / 2.0
        self.cy = self.height() / 2.0
        self.radius = max(20.0, min(self.width(), self.height()) / 2.0 - 85.0)

        if hasattr(self, 'particle_renderer'):
            self.particle_renderer.radius = self.radius
            self.particle_renderer._initialize_particles()

        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start = event.globalPosition().toPoint()
            self._start_position = self.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            delta = event.globalPosition().toPoint() - self._drag_start
            new_pos = self._start_position + delta
            if self._movement_bounds:
                x = max(self._movement_bounds.left(), min(new_pos.x(), self._movement_bounds.right() - self.width()))
                y = max(self._movement_bounds.top(), min(new_pos.y(), self._movement_bounds.bottom() - self.height()))
                new_pos = QPoint(x, y)
            self.move(new_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # =========================================================
    # MASTER HUD PAINT ENGINE
    # =========================================================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.cx <= 0 or self.cy <= 0:
            self.cx = self.width() / 2.0
            self.cy = self.height() / 2.0
            self.radius = max(20.0, min(self.width(), self.height()) / 2.0 - 85.0)

        # 1. Shift the canvas origin directly to the center so all renderers align perfectly
        painter.translate(self.cx, self.cy)

        # 2. Execute Premium Sub-renderers
        for renderer in self.renderers:
            try:
                if hasattr(renderer, 'draw'):
                    renderer.draw(painter)
            except Exception as e:
                print(f"[HUD Renderer Crash] {renderer.__class__.__name__}: {e}")

        # 3. Draw Center Text "T.O.N.Y."
        painter.setPen(self.white)
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        text_box = QRectF(-40, -15, 80, 30)
        painter.drawText(text_box, Qt.AlignmentFlag.AlignCenter, "T.O.N.Y.")

    # --- Compatibility Methods ---
    def set_workflow(self, name: str): self.workflow_name = name; self.update()
    def set_current_step(self, step: str): self.current_step = step; self.update()
    def set_current_tool(self, tool: str): self.current_tool = tool; self.update()
    def set_progress(self, progress: float): self.workflow_progress = progress; self.update()
    def set_movement_bounds(self, rect): self._movement_bounds = rect
    def start(self): 
        if not self.timer.isActive(): self.timer.start(1000 // 60)
    def stop(self): 
        if self.timer.isActive(): self.timer.stop()


JarvisHUD = JarvisHUDWidget
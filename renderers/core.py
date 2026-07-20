from __future__ import annotations
import math
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen

class CoreRenderer:
    def __init__(self, hud):
        self.hud = hud
        self.profile = {}
        
    @staticmethod
    def clamp(value):
        return max(0, min(255, int(value)))
        
    def color(self, r, g, b, a):
        return QColor(r, g, b, self.clamp(a))
        
    def arc(self, painter, rect, color, width, start, sweep):
        pen = QPen(color)
        pen.setWidthF(width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.drawArc(rect, int(start * 16), int(sweep * 16))
        
    def _cache_geometry(self):
        self.profile = self.hud.animation_profile()
        self.outer_rotation = self.hud.outer_rotation
        self.middle_rotation = self.hud.middle_rotation
        self.inner_rotation = self.hud.inner_rotation
        self.wave = self.hud.wave_offset
        self.scale = self.hud.core_scale
        self.brightness = self.profile["brightness"]
        self.glow = self.profile["glow"]
        self.speed = self.profile["speed"]
        self.pulse = 0.5 + 0.5 * math.sin(self.wave * 2.6)
        self.outer_glow = 60 + self.pulse * 7 * self.glow
        self.inner_glow = 36 + self.pulse * 4
        self.reactor_radius = 56
        self.segment_radius = 48
        self.inner_ring = 22
        self.hex_radius = 66
        self.hex_inner = 42
        self.node_orbit = 54
        self.cyan = self.color(0, 235, 255, 220)
        self.white = self.color(245, 252, 255, 255)
        self.core = self.color(170, 250, 255, 230)
        
    def draw(self, painter):
        self._cache_geometry()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.draw_volume_glow(painter)
        self.draw_pulse_core(painter)
        self.draw_hex_reticle(painter)
        self.draw_core(painter)
        
    def title_font(self):
        return QFont("Segoe UI", 17, QFont.Weight.Bold)
        
    def reactor_pulse(self):
        return 0.5 + 0.5 * math.sin(self.wave * 2.8)
        
    def draw_volume_glow(self, painter):
        painter.save()
        pulse = self.reactor_pulse()
        
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        for layer in range(16):
            alpha = max(0, int(24 + self.glow * 38 - layer * 2))
            radius = 60 + layer * 7 + pulse * 7 * self.glow
            pen = QPen(self.color(0, 235, 255, alpha))
            pen.setWidthF(1.0)
            painter.setPen(pen)
            painter.drawEllipse(QPointF(), radius, radius)

        for layer in range(9):
            alpha = max(0, int(85 - layer * 5 + pulse * 14))
            radius = 36 + layer * 3 + pulse * 4
            pen = QPen(self.color(120, 248, 255, alpha))
            pen.setWidthF(1.0)
            painter.setPen(pen)
            painter.drawEllipse(QPointF(), radius, radius)
            
        bloom = 24 + pulse * 5 + self.glow * 4
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(210, 255, 255, 45 * self.brightness))
        painter.drawEllipse(QPointF(), bloom, bloom)
        
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for layer in range(5):
            alpha = max(0, int(42 - layer * 6 + pulse * 12))
            radius = 18 + layer * 4 + pulse * 2
            pen = QPen(self.color(90, 255, 255, alpha))
            pen.setWidthF(1.0)
            painter.setPen(pen)
            painter.drawEllipse(QPointF(), radius, radius)
            
        pen = QPen(self.color(255, 255, 255, 35 + 35 * pulse))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        aura = 44 + pulse * 3
        painter.drawEllipse(QPointF(), aura, aura)
        
        self.arc(
            painter,
            QRectF(-48, -48, 96, 96),
            self.color(255, 255, 255, 180),
            1.8,
            self.outer_rotation,
            24,
        )
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255, 255, 255, 170))
        orbit = 34
        spin = math.radians(self.middle_rotation)
        for i in range(8):
            a = spin + math.radians(i * 45)
            painter.drawEllipse(
                QPointF(math.cos(a) * orbit, math.sin(a) * orbit),
                1.2,
                1.2,
            )
            
        painter.setBrush(self.color(255, 255, 255, 220))
        painter.drawEllipse(QPointF(), 4.5, 4.5)
        painter.restore()

    def draw_pulse_core(self, painter):
        painter.save()
        pulse = self.reactor_pulse()
        painter.scale(self.scale, self.scale)
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        
        rings = ((56, 2.2), (44, 1.8), (32, 1.4))
        for radius, width in rings:
            pen = QPen(self.color(0, 235, 255, 185 * self.brightness))
            pen.setWidthF(width * self.brightness)
            painter.setPen(pen)
            painter.drawEllipse(QPointF(), radius + pulse * 2, radius + pulse * 2)
            
        rect = QRectF(-self.segment_radius, -self.segment_radius, self.segment_radius * 2, self.segment_radius * 2)
        painter.save()
        painter.rotate(self.outer_rotation)
        for angle in (0, 90, 180, 270):
            self.arc(painter, rect, self.core, 3.0, angle, 42)
        painter.restore()
        
        painter.save()
        painter.rotate(-self.inner_rotation)
        pen = QPen(self.color(235, 248, 255, 210))
        pen.setWidthF(1.8)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), self.inner_ring, self.inner_ring)
        
        # FIX: Wrapped raw numbers in QPointF for consistency
        painter.drawLine(QPointF(-18, 0), QPointF(-8, 0))
        painter.drawLine(QPointF(8, 0), QPointF(18, 0))
        painter.drawLine(QPointF(0, -18), QPointF(0, -8))
        painter.drawLine(QPointF(0, 8), QPointF(0, 18))
        painter.restore()
        
        painter.setPen(Qt.PenStyle.NoPen)
        orbit = 40
        spin = math.radians(self.middle_rotation)
        painter.setBrush(self.color(170, 250, 255, 180))
        for i in range(6):
            a = spin + math.radians(i * 60)
            painter.drawEllipse(QPointF(math.cos(a) * orbit, math.sin(a) * orbit), 2.0, 2.0)
            
        painter.setBrush(self.color(255, 255, 255, 220))
        orbit = 28
        spin = math.radians(self.middle_rotation)
        for i in range(4):
            a = spin + math.radians(i * 90)
            painter.drawEllipse(QPointF(math.cos(a) * orbit, math.sin(a) * orbit), 1.8, 1.8)
            
        pulse_rect = QRectF(-34, -34, 68, 68)
        painter.save()
        painter.rotate(-self.outer_rotation * 1.5)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for angle in (25, 145, 265):
            self.arc(painter, pulse_rect, self.color(255, 255, 255, 170), 1.5, angle, 26)
        painter.restore()
        
        pen = QPen(self.color(0, 235, 255, 150))
        pen.setWidthF(1.2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), 14 + pulse, 14 + pulse)
        
        crystal = 7 + pulse * 1.2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(225, 255, 255, 245))
        painter.drawEllipse(QPointF(), crystal, crystal)
        painter.restore()

    def draw_hex_reticle(self, painter):
        painter.save()
        painter.rotate(self.outer_rotation * (0.35 + self.speed * 0.08))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        outer = []
        for i in range(6):
            a = math.radians(i * 60 - 30)
            outer.append(QPointF(math.cos(a) * self.hex_radius, math.sin(a) * self.hex_radius))
            
        pen = QPen(self.white)
        pen.setWidthF(2.2 * self.brightness)
        painter.setPen(pen)
        for i in range(6):
            painter.drawLine(outer[i], outer[(i + 1) % 6])
            
        inner = []
        for i in range(6):
            a = math.radians(i * 60 - 30)
            inner.append(QPointF(math.cos(a) * self.hex_inner, math.sin(a) * self.hex_inner))
            
        pen = QPen(self.color(0, 235, 255, 180))
        pen.setWidthF(1.4)
        painter.setPen(pen)
        for i in range(6):
            painter.drawLine(inner[i], inner[(i + 1) % 6])
            
        pen = QPen(self.color(0, 235, 255, 120))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        for o, i in zip(outer, inner):
            painter.drawLine(i, o)
            
        pen = QPen(self.color(0, 255, 255, 220))
        pen.setWidthF(2.0)
        painter.setPen(pen)
        for p in outer:
            d = math.atan2(p.y(), p.x())
            painter.drawLine(p, QPointF(p.x() + math.cos(d) * 10, p.y() + math.sin(d) * 10))
            
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255, 255, 255, 230))
        spin = math.radians(self.inner_rotation)
        for i in range(6):
            a = spin + math.radians(i * 60)
            painter.drawEllipse(QPointF(math.cos(a) * self.node_orbit, math.sin(a) * self.node_orbit), 2.3, 2.3)
            
        pen = QPen(self.color(160, 245, 255, 170))
        pen.setWidthF(1.2)
        painter.setPen(pen)
        for angle in range(0, 360, 30):
            a = math.radians(angle)
            painter.drawLine(
                QPointF(math.cos(a) * 82, math.sin(a) * 82),
                QPointF(math.cos(a) * 90, math.sin(a) * 90)
            )
            
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self.arc(painter, QRectF(-72, -72, 144, 144), self.color(255, 255, 255, 120), 1.5, -self.outer_rotation, 16)
        
        pen = QPen(self.color(0, 235, 255, 70 + 40 * self.pulse))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        orbit = 60 + self.pulse * 2
        painter.drawEllipse(QPointF(), orbit, orbit)
        painter.restore()

    def draw_core(self, painter):
        painter.save()
        pulse = self.reactor_pulse()
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255, 255, 255, 220))
        crystal = 6 + pulse * 1.2
        painter.drawEllipse(QPointF(), crystal, crystal)
        
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        for layer in range(5):
            alpha = 70 - layer * 12
            radius = 8 + layer * 2.5 + pulse * 1.5
            pen = QPen(self.color(0, 235, 255, alpha))
            pen.setWidthF(1.0)
            painter.setPen(pen)
            painter.drawEllipse(QPointF(), radius, radius)
            
        pen = QPen(self.color(170, 250, 255, 170))
        pen.setWidthF(1.3)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(), 18 + pulse, 18 + pulse)
        
        self.arc(painter, QRectF(-22, -22, 44, 44), self.color(255, 255, 255, 180), 1.6, self.inner_rotation, 24)
        
        pen = QPen(self.color(0, 235, 255, 90))
        pen.setWidthF(0.9)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), 28, 28)
        
        pen = QPen(self.color(0, 235, 255, 90))
        pen.setWidthF(1.2)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(), 18, 18)
        painter.drawEllipse(QPointF(), 24, 24)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255, 255, 255, 150 + 70 * pulse))
        painter.drawEllipse(QPointF(), 2.4 + pulse * 0.4, 2.4 + pulse * 0.4)
        painter.restore()
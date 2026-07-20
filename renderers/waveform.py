from __future__ import annotations

import math

from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal as Signal
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget

class WaveformRenderer:
    ##################################################
    # Initialization
    ##################################################
    def __init__(self, hud):
        self.hud = hud
        self.profile = {}

    ##################################################
    # Helpers
    ##################################################
    @staticmethod
    def clamp(value):
        return max(0,min(255,int(value)))

    def color(self,r,g,b,a):
        return QColor(r,g,b,self.clamp(a))

    def arc(self,painter,rect,color,width,start,sweep):
        pen=QPen(color)
        pen.setWidthF(width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) # FIX: Enforce hollow arcs
        painter.drawArc(rect,int(start*16),int(sweep*16))

    ##################################################
    # Runtime Cache
    ##################################################
    def _cache_geometry(self):
        r=max(20.0,self.hud.radius)
        self.profile=self.hud.animation_profile()
        self.radius=r-36
        self.inner_radius=self.radius-26
        self.band_radius=r-42
        self.time=self.hud.wave_offset
        self.outer_rotation=self.hud.outer_rotation
        self.middle_rotation=self.hud.middle_rotation
        self.inner_rotation=self.hud.inner_rotation
        self.brightness=self.profile["brightness"]
        self.glow=self.profile["glow"]
        self.base_amplitude=5+self.glow*8

    ##################################################
    # Draw Entry
    ##################################################
    def draw(self,painter):
        self._cache_geometry()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing,True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,True)
        self.draw_waveform(painter)
        self.draw_energy_band(painter)

    ##################################################
    # Wave Generator
    ##################################################
    def generate_wave(self,radius,f1,f2,f3,a1,a2,a3):
        wave=QPolygonF()
        for degree in range(361):
            angle=math.radians(degree)
            harmonic=math.sin(angle*f1+self.time*2.2)*a1
            ripple=math.cos(angle*f2-self.time*1.6)*a2
            micro=math.sin(angle*f3+self.time*3.4)*a3
            dynamic=radius+harmonic+ripple+micro
            wave.append(QPointF(math.cos(angle)*dynamic, math.sin(angle)*dynamic))
        return wave
        
    ##################################################
    # Premium Circular Waveform
    ##################################################
    def draw_waveform(self,painter):
        painter.save()
        painter.rotate(-self.inner_rotation)
        amplitude=self.base_amplitude
        outer_wave=self.generate_wave(self.radius, 5, 10, 16, amplitude, amplitude*0.22, amplitude*0.06)

        ##################################################
        # Outer Glow
        ##################################################
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for width,alpha in ((5.0,14), (3.5,24), (2.0,38)):
            pen=QPen(self.color(0, 235, 255, alpha*self.brightness))
            pen.setWidthF(width)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawPolyline(outer_wave)

        ##################################################
        # Primary Wave
        ##################################################
        pen=QPen(self.color(205, 248, 255, 210))
        pen.setWidthF(1.5)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPolyline(outer_wave)

        ##################################################
        # Secondary Inner Wave
        ##################################################
        inner_wave=self.generate_wave(self.inner_radius, 6, 12, 18, amplitude*0.35, amplitude*0.10, amplitude*0.04)
        pen=QPen(self.color(235, 248, 255, 145))
        pen.setWidthF(1.0)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPolyline(inner_wave)

        ##################################################
        # Scanner Wave
        ##################################################
        scanner=self.generate_wave(self.radius-12, 8, 18, 28, amplitude*0.18, amplitude*0.06, amplitude*0.02)
        pen=QPen(self.color(0, 235, 255, 65*self.glow))
        pen.setWidthF(0.9)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPolyline(scanner)

        ##################################################
        # Reactive Pulse Ring
        ##################################################
        pulse=0.5+0.5*math.sin(self.time*2.6)
        pen=QPen(self.color(255, 255, 255, 50+45*pulse))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) # FIX: Safety clear
        r=self.radius+8+(pulse*2)
        painter.drawEllipse(QPointF(), r, r)

        ##################################################
        # Highlight Sweep
        ##################################################
        self.arc(
            painter,
            QRectF(-self.radius-4, -self.radius-4, (self.radius+4)*2, (self.radius+4)*2),
            self.color(255, 255, 255, 255),
            2.0,
            self.inner_rotation,
            12,
        )
        painter.restore()
        
    ##################################################
    # Premium Energy Band
    ##################################################
    def draw_energy_band(self,painter):
        painter.save()
        pulse=0.5+0.5*math.sin(self.time*2.8)
        band_rect=QRectF(-self.band_radius, -self.band_radius, self.band_radius*2, self.band_radius*2)

        ##################################################
        # Primary Energy Arc
        ##################################################
        self.arc(painter, band_rect, self.color(0, 235, 255, 165*self.brightness), 3.0, -self.outer_rotation, 64)

        ##################################################
        # Secondary Energy Arc
        ##################################################
        self.arc(painter, band_rect, self.color(235, 248, 255, 115), 1.5, self.middle_rotation, 28)

        ##################################################
        # Flowing Energy Stream
        ##################################################
        self.arc(painter, band_rect, self.color(0, 235, 255, 80*self.glow), 1.0, self.outer_rotation*2, 18)
        self.arc(painter, band_rect, self.color(255, 255, 255, 70), 0.9, -self.middle_rotation*2, 14)

        ##################################################
        # Pulse Nodes
        ##################################################
        painter.setPen(Qt.PenStyle.NoPen)
        spin=math.radians(self.outer_rotation)
        for offset in (0,120,240):
            angle=spin+math.radians(offset)
            painter.setBrush(self.color(255, 255, 255, 170+55*pulse))
            painter.drawEllipse(
                QPointF(math.cos(angle)*self.band_radius, math.sin(angle)*self.band_radius),
                2.0+0.6*pulse, 2.0+0.6*pulse,
            )

        ##################################################
        # Orbit Scanner Nodes
        ##################################################
        orbit=self.band_radius-10
        spin=math.radians(-self.middle_rotation*1.6)
        painter.setBrush(self.color(0, 235, 255, 150*self.glow))
        for i in range(6):
            angle=spin+math.radians(i*60)
            painter.drawEllipse(
                QPointF(math.cos(angle)*orbit, math.sin(angle)*orbit),
                1.2, 1.2,
            )

        ##################################################
        # Energy Markers
        ##################################################
        pen=QPen(self.color(0, 235, 255, 110*self.glow))
        pen.setWidthF(1.2)
        painter.setPen(pen)
        inner=self.band_radius-6
        outer=self.band_radius+6
        for angle in range(0,360,20):
            a=math.radians(angle)
            painter.drawLine(
                QPointF(math.cos(a)*inner, math.sin(a)*inner),
                QPointF(math.cos(a)*outer, math.sin(a)*outer),
            )

        ##################################################
        # Reactor Pulse Ring
        ##################################################
        pen=QPen(self.color(255, 255, 255, 30+35*pulse))
        pen.setWidthF(0.9)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) # FIX: Clear brush leak from scanner nodes
        radius=self.band_radius-18+(pulse*2)
        painter.drawEllipse(QPointF(), radius, radius)

        ##################################################
        # Micro Scanner Sweep
        ##################################################
        self.arc(
            painter,
            QRectF(-radius, -radius, radius*2, radius*2),
            self.color(255, 255, 255, 210),
            1.5,
            self.outer_rotation*3,
            10,
        )
        painter.restore()
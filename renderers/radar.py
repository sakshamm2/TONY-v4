from __future__ import annotations
import math
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen

class RadarRenderer:
    def __init__(self,hud):
        self.hud = hud
        self.profile = {}
        
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
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect,int(start*16),int(sweep*16))
        
    def _cache_runtime(self):
        self.profile=self.hud.animation_profile()
        self.radius=self.hud.radius
        self.wave=self.hud.wave_offset
        self.radar_rotation=self.hud.radar_rotation
        self.outer_rotation=self.hud.outer_rotation
        self.middle_rotation=self.hud.middle_rotation
        self.inner_rotation=self.hud.inner_rotation
        self.brightness=self.profile["brightness"]
        self.glow=self.profile["glow"]
        self.speed=self.profile["speed"]
        self.radar_radius=self.radius*0.72
        self.orbit_x=self.radius*0.53
        self.orbit_y=self.radius*0.30
        self.target_radius=self.radius*0.23
        self.node_radius=self.radius*0.38
        self.cyan=self.color(0,235,255,220)
        self.white=self.color(235,248,255,255)
        
    def draw(self,painter):
        self._cache_runtime()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing,True)
        self.draw_radar(painter)
        self.draw_orbits(painter)
        
    def draw_radar(self,painter):
        painter.save()
        painter.rotate(self.radar_rotation)
        r=self.radar_radius
        rect=QRectF(-r, -r, r*2, r*2)
        
        pen=QPen(self.color(0, 235, 255, 38*self.brightness))
        pen.setWidthF(1.1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), r, r)
        
        self.arc(painter, rect, self.color(0, 255, 255, 170*self.glow), 2.6, 0, 18)
        
        pen=QPen(self.color(235, 248, 255, 90))
        pen.setWidthF(1.2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), r-16, r-16)
        
        pen=QPen(self.color(0, 235, 255, 35))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for scale in (0.22, 0.40, 0.58, 0.76):
            painter.drawEllipse(QPointF(), r*scale, r*scale)
            
        # FIX: Wrapped raw numbers in QPointF
        painter.drawLine(QPointF(-r, 0), QPointF(r, 0))
        painter.drawLine(QPointF(0, -r), QPointF(0, r))
        
        for angle in range(30,360,30):
            a=math.radians(angle)
            painter.drawLine(QPointF(), QPointF(math.cos(a)*r, math.sin(a)*r))
            
        sweep=math.radians(self.radar_rotation)
        pen=QPen(self.color(180, 250, 255, 150))
        pen.setWidthF(1.6)
        painter.setPen(pen)
        painter.drawLine(QPointF(), QPointF(math.cos(sweep)*r, math.sin(sweep)*r))
        
        self.arc(painter, rect, self.color(255, 255, 255, 80), 4.5, -4, 10)
        
        pen=QPen(self.color(0, 235, 255, 110*self.glow))
        pen.setWidthF(2.0)
        painter.setPen(pen)
        bracket=r+8
        size=8
        # FIX: Wrapped raw numbers in QPointF
        painter.drawLine(QPointF(-size, bracket), QPointF(size, bracket))
        painter.drawLine(QPointF(-size, -bracket), QPointF(size, -bracket))
        painter.drawLine(QPointF(bracket, -size), QPointF(bracket, size))
        painter.drawLine(QPointF(-bracket, -size), QPointF(-bracket, size))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(200, 245, 255, 240))
        orbit=r+2
        spin=math.radians(-self.middle_rotation*2.5)
        for offset in (0,45,90,135,180,225,270,315):
            a=spin+math.radians(offset)
            painter.drawEllipse(QPointF(math.cos(a)*orbit, math.sin(a)*orbit), 1.8, 1.8)
            
        painter.setBrush(self.color(255, 255, 255, 120))
        orbit=r*0.82
        spin=math.radians(self.outer_rotation*0.6)
        for i in range(24):
            a=spin+math.radians(i*15)
            painter.drawEllipse(QPointF(math.cos(a)*orbit, math.sin(a)*orbit), 0.9, 0.9)
            
        self.arc(painter, rect, self.white, 2.2, self.radar_rotation, 12)
        self.arc(painter, rect, self.white, 2.2, self.radar_rotation+160, 8)
        painter.restore()
        
    def draw_orbits(self,painter):
        painter.save()
        
        pen=QPen(self.color(0, 235, 255, 55*self.brightness))
        pen.setWidthF(0.9)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawEllipse(QPointF(), self.orbit_x, self.orbit_y)
        
        painter.save()
        painter.rotate(90)
        painter.drawEllipse(QPointF(), self.orbit_x, self.orbit_y)
        painter.restore()
        
        painter.save()
        painter.rotate(45)
        painter.drawEllipse(QPointF(), self.orbit_x*0.88, self.orbit_y*0.88)
        painter.restore()
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255, 255, 255, 170))
        spin=math.radians(self.outer_rotation)
        for offset in (0,120,240):
            a=spin+math.radians(offset)
            painter.drawEllipse(QPointF(math.cos(a)*self.orbit_x*0.94, math.sin(a)*self.orbit_y*0.94), 2.0, 2.0)
            
        pen=QPen(self.color(235, 248, 255, 70))
        pen.setWidthF(1.0)
        pen.setDashPattern([2,7])
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), self.orbit_x*0.62, self.orbit_y*0.62)
        
        painter.save()
        painter.rotate(-self.inner_rotation)
        rect=QRectF(-self.target_radius, -self.target_radius, self.target_radius*2, self.target_radius*2)
        self.arc(painter, rect, self.color(0, 235, 255, 145*self.glow), 1.4, 0, 30)
        self.arc(painter, rect, self.color(0, 235, 255, 145*self.glow), 1.4, 120, 18)
        self.arc(painter, rect, self.color(0, 235, 255, 145*self.glow), 1.4, 240, 22)
        painter.restore()
        
        pen=QPen(self.color(255, 255, 255, 120))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        cross=self.radius*0.12
        # FIX: Wrapped raw numbers in QPointF
        painter.drawLine(QPointF(-cross, 0), QPointF(cross, 0))
        painter.drawLine(QPointF(0, -cross), QPointF(0, cross))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(0, 235, 255, 120*self.glow))
        spin=math.radians(self.middle_rotation*1.8)
        for i in range(8):
            a=spin+math.radians(i*45)
            painter.drawEllipse(QPointF(math.cos(a)*self.node_radius, math.sin(a)*self.node_radius), 1.6, 1.6)
            
        painter.setBrush(self.color(255, 255, 255, 110))
        secondary=self.radius*0.54
        spin=math.radians(-self.outer_rotation)
        for i in range(16):
            a=spin+math.radians(i*22.5)
            painter.drawEllipse(QPointF(math.cos(a)*secondary, math.sin(a)*secondary), 1.2, 1.2)
            
        pen=QPen(self.color(0, 235, 255, 60))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), self.radius*0.46, self.radius*0.46)
        
        orbit=self.radius*0.46
        self.arc(painter, QRectF(-orbit, -orbit, orbit*2, orbit*2), self.white, 1.2, -self.outer_rotation, 18)
        
        pulse=0.5+0.5*math.sin(self.wave*2.6)
        pen=QPen(self.color(0, 235, 255, 65*self.brightness))
        pen.setWidthF(1.4)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), self.radius*0.32+pulse*3, self.radius*0.32+pulse*3)
        painter.restore()
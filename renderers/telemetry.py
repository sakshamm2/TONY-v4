from __future__ import annotations
import math
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush

class TelemetryRenderer:
    def __init__(self,hud):
        self.hud=hud
        self.profile={}
        
    @staticmethod
    def clamp(value):
        return max(0,min(255,int(value)))
        
    def color(self,r,g,b,a):
        return QColor(r,g,b,self.clamp(a))
        
    def font(self,size,bold=False):
        return QFont("Consolas", size, QFont.Weight.Bold if bold else QFont.Weight.Normal)
        
    def arc(self,painter,rect,color,width,start,sweep):
        pen=QPen(color)
        pen.setWidthF(width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, int(start*16), int(sweep*16))
        
    def progress_bar(self,painter,x,y,width,value):
        painter.setPen(QPen(self.white,1.0))
        painter.drawLine(QPointF(x,y), QPointF(x+width,y))
        painter.setPen(QPen(self.cyan,2.6))
        painter.drawLine(QPointF(x,y), QPointF(x+(width*max(0,min(100,value))/100.0), y))
        
    def _cache_geometry(self):
        r=max(20.0,self.hud.radius)
        self.profile=self.hud.animation_profile()
        self.radius=r
        self.crosshair_radius=r+42
        self.data_ring_radius=r+56
        self.progress_radius=r+28
        self.decoration_radius=r+82
        self.outer_rotation=self.hud.outer_rotation
        self.middle_rotation=self.hud.middle_rotation
        self.inner_rotation=self.hud.inner_rotation
        self.wave=self.hud.wave_offset
        self.brightness=self.profile["brightness"]
        self.glow=self.profile["glow"]
        self.cyan=self.color(0, 235, 255, 210)
        self.white=self.color(235, 248, 255, 190)
        self.green=self.color(90, 255, 160, 220)
        self.amber=self.color(255, 185, 45, 220)
        
    def draw(self,painter):
        self._cache_geometry()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.draw_crosshair(painter)
        self.draw_data_ring(painter)
        self.draw_workflow_progress(painter)
        self.draw_decorations(painter)
        self.draw_status_labels(painter)
        self.draw_workflow_status(painter)
        painter.restore()
        
    def draw_crosshair(self,painter):
        painter.save()
        r=self.crosshair_radius
        pen=QPen(self.color(0, 235, 255, 60*self.brightness))
        pen.setWidthF(0.9)
        painter.setPen(pen)
        
        # FIX: Wrapped raw numbers in QPointF
        painter.drawLine(QPointF(-r, 0), QPointF(r, 0))
        painter.drawLine(QPointF(0, -r), QPointF(0, r))
        
        pen.setWidthF(1.6)
        painter.setPen(pen)
        marker=14
        painter.drawLine(QPointF(-marker, 0), QPointF(marker, 0))
        painter.drawLine(QPointF(0, -marker), QPointF(0, marker))
        
        pen=QPen(self.color(0, 235, 255, 150*self.brightness))
        pen.setWidthF(1.5)
        painter.setPen(pen)
        outer=r+6
        inner=r-12
        painter.drawLine(QPointF(-outer, 0), QPointF(-inner, 0))
        painter.drawLine(QPointF(inner, 0), QPointF(outer, 0))
        painter.drawLine(QPointF(0, -outer), QPointF(0, -inner))
        painter.drawLine(QPointF(0, inner), QPointF(0, outer))
        
        pen=QPen(self.color(0, 235, 255, 45*self.glow))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        diag=r*0.72
        for angle in (45,135,225,315):
            a=math.radians(angle)
            x=math.cos(a)*diag
            y=math.sin(a)*diag
            painter.drawLine(QPointF(x*0.92,y*0.92), QPointF(x,y))
            
        pulse=0.5+0.5*math.sin(self.wave*2.8)
        pen=QPen(self.color(255, 255, 255, 28+26*pulse))
        pen.setWidthF(0.9)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), 18+pulse*2, 18+pulse*2)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.white)
        painter.drawEllipse(QPointF(), 2.4, 2.4)
        painter.restore()
        
    def draw_data_ring(self,painter):
        painter.save()
        painter.rotate(self.outer_rotation*0.28)
        r=self.data_ring_radius
        rect=QRectF(-r, -r, r*2, r*2)
        sectors=((2,16), (34,12), (66,18), (102,10), (134,18), (176,20), (220,14), (252,18), (292,14), (326,16))
        for start,sweep in sectors:
            self.arc(painter, rect, self.color(0, 235, 255, 165*self.brightness), 2.1, start, sweep)
            
        pen=QPen(self.color(235, 245, 255, 90*self.brightness))
        pen.setWidthF(1.0)
        pen.setDashPattern([2,7])
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), r-9, r-9)
        
        pen=QPen(self.color(0, 235, 255, 40))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(), r+8, r+8)
        
        self.arc(painter, rect, self.color(255, 255, 255, 235), 2.0, -self.outer_rotation, 14)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255, 255, 255, 170))
        orbit=r-5
        spin=math.radians(self.outer_rotation)
        for angle in range(0,360,45):
            a=spin+math.radians(angle)
            painter.drawEllipse(QPointF(math.cos(a)*orbit, math.sin(a)*orbit), 2.1, 2.1)
            
        orbit=r-18
        painter.setBrush(self.color(0, 235, 255, 120))
        for angle in range(18):
            a=spin+math.radians(angle*20)
            painter.drawEllipse(QPointF(math.cos(a)*orbit, math.sin(a)*orbit), 1.2, 1.2)
        painter.restore()
        
    def draw_workflow_progress(self,painter):
        painter.save()
        painter.rotate(-self.middle_rotation*0.45)
        r=self.progress_radius
        rect=QRectF(-r, -r, r*2, r*2)
        pen=QPen(self.color(255, 255, 255, 26))
        pen.setWidthF(5.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)
        
        progress=max(0.0, min(1.0, self.hud.workflow_progress))
        glow=150+80*math.sin(self.wave*3.0)
        self.arc(painter, rect, self.color(0, 235, 255, glow), 5.4, 90, -360*progress)
        self.arc(painter, rect, self.color(255, 255, 255, 70), 1.2, 90, -360*progress)
        
        angle=math.radians(90-360*progress)
        orbit=r
        x=math.cos(angle)*orbit
        y=-math.sin(angle)*orbit
        pulse=0.5+0.5*math.sin(self.wave*4.0)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255, 255, 255, 170+70*pulse))
        painter.drawEllipse(QPointF(x,y), 3.4+pulse, 3.4+pulse)
        
        painter.setFont(self.font(8, True))
        painter.setPen(self.white)
        painter.drawText(QRectF(-34, -12, 68, 24), Qt.AlignmentFlag.AlignCenter, f"{progress*100:.0f}%")
        painter.restore()
        
    def draw_decorations(self,painter):
        painter.save()
        painter.rotate(self.inner_rotation*0.22)
        r=self.decoration_radius
        pen=QPen(self.color(0, 235, 255, 42*self.glow))
        pen.setWidthF(0.9)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for angle in range(0,360,30):
            painter.save()
            painter.rotate(angle)
            # FIX: Used QPointF instead of raw int casting
            painter.drawLine(QPointF(r, 0), QPointF(r+12, 0))
            painter.restore()
            
        pen=QPen(self.color(255, 255, 255, 55))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(), r+18, r+18)
        painter.restore()
        
    def draw_status_labels(self,painter):
        painter.save()
        cyan=self.color(0, 235, 255, 205*self.brightness)
        white=self.color(235, 248, 255, 185)
        painter.setFont(self.font(8, True))
        
        painter.setPen(cyan)
        painter.drawText(QPointF(-20, -self.radius-72), "TARGET")
        painter.drawText(QPointF(-18, self.radius+74), "ACTIVE")
        painter.drawText(QPointF(self.radius+26, 4), "SCAN")
        
        painter.setPen(self.amber)
        painter.drawText(QPointF(-self.radius-191, -self.radius-58), "60 FPS")
        
        painter.setFont(self.font(7))
        start_x = -self.radius - 175
        start_y = -44
        
        telemetry=(
            ("CPU",self.hud.cpu),
            ("RAM",self.hud.ram),
            ("GPU",self.hud.gpu),
            ("BAT",self.hud.battery),
        )
        for index,(name,value) in enumerate(telemetry):
            y=start_y+(index*20)
            painter.setPen(cyan)
            painter.drawText(QPointF(start_x, y), name)
            painter.setPen(white)
            painter.drawText(QPointF(start_x+86, y), f"{value:.0f}%")
            self.progress_bar(painter, start_x+22, y+5, 52, value)
            
        painter.setPen(cyan)
        painter.drawText(QPointF(-self.radius-175, self.radius+26), "SECURE LINK")
        painter.setPen(white)
        painter.drawText(QPointF(-self.radius-175, self.radius+42), "SYSTEM STABLE")
        
        pen=QPen(self.color(0, 235, 255, 70))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        anchor=self.radius+18
        
        painter.drawLine(QPointF(-anchor, -24), QPointF(start_x+60, -24))
        painter.drawLine(QPointF(start_x+60, -24), QPointF(start_x+60, -46))
        
        pulse=0.5+0.5*math.sin(self.wave*2.6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255, 255, 255, 120+80*pulse))
        for i in range(len(telemetry)):
            painter.drawEllipse(QPointF(start_x-12, start_y+(i*20)-3), 1.8+0.5*pulse, 1.8+0.5*pulse)
        painter.restore()

    def draw_workflow_status(self,painter):
        painter.save()
        painter.setFont(self.font(7))
        
        x = self.radius + 115 
        y = -60
        
        rows=(
            ("WORKFLOW", self.hud.workflow_name or "--", self.cyan, self.white),
            ("STEP", self.hud.current_step or "--", self.cyan, self.white),
            ("TOOL", self.hud.current_tool or "--", self.cyan, self.white),
            ("TIME", f"{self.hud.execution_time:.2f}s", self.cyan, self.white),
            ("STATUS", self.hud.state, self.cyan, self.green),
        )
        offset=0
        for title,value,left,right in rows:
            painter.setPen(left)
            painter.drawText(QPointF(x, y+offset), title)
            painter.setPen(right)
            painter.drawText(QPointF(x, y+18+offset), value)
            offset+=42
            
        progress=max(0.0, min(1.0, self.hud.workflow_progress))
        painter.setPen(self.cyan)
        painter.drawText(QPointF(x, y+210), f"PROGRESS {progress*100:.0f}%")
        self.progress_bar(painter, x, y+224, 110, progress*100)
        
        pen=QPen(self.color(0, 235, 255, 60))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        anchor=self.radius+20
        
        painter.drawLine(QPointF(anchor, -12), QPointF(x-12, -12))
        painter.drawLine(QPointF(x-12, -12), QPointF(x-12, 170))
        
        pulse=0.5+0.5*math.sin(self.wave*3.0)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(90, 255, 160, 140+90*pulse))
        painter.drawEllipse(QPointF(x+118, y+228), 2.6+0.6*pulse, 2.6+0.6*pulse)
        
        painter.setFont(self.font(6))
        painter.setPen(self.color(180, 220, 255, 150))
        painter.drawText(QPointF(x, y+255), f"QUEUE : {getattr(self.hud,'queued_tasks',0)}")
        painter.drawText(QPointF(x, y+270), f"AGENT : {self.hud.state.upper()}")
        painter.restore()
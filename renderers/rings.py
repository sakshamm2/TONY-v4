from __future__ import annotations
import math
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen

class RingRenderer:

    def __init__(self, hud):
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

    def _cache_geometry(self):
        r=max(20.0,self.hud.radius)
        self.profile=self.hud.animation_profile()
        self.outer=r+8
        self.middle=r-42
        self.inner=r-76
        self.segment=r-94
        self.tick=r+22
        self.pulse=r*0.36
        self.shock=r*0.48
        self.arc_radius=r*0.58
        self.spark=r*0.63
        self.rot_outer=self.hud.outer_rotation
        self.rot_middle=self.hud.middle_rotation
        self.rot_inner=self.hud.inner_rotation
        self.wave=self.hud.wave_offset

    def draw(self,painter):
        self._cache_geometry()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing,True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,True)
        self.draw_crosshair(painter)
        self.draw_outer_ring(painter)
        self.draw_middle_ring(painter)
        self.draw_inner_ring(painter)
        self.draw_segment_ring(painter)
        self.draw_ticks(painter)
        self.draw_pulse_rings(painter)
        painter.restore()
    
    def draw_crosshair(self,painter):
        painter.save()
        pen=QPen(self.hud.cyan_dim)
        pen.setWidthF(1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        r=self.outer-2
        # FIX: Wrapped raw numbers in QPointF
        painter.drawLine(QPointF(0, -r), QPointF(0, r))
        painter.drawLine(QPointF(-r, 0), QPointF(r, 0))
        painter.drawEllipse(QPointF(),r+2,r+2)
        painter.restore()
        
    def draw_outer_ring(self,painter):
        painter.save()
        p=self.profile
        b=p["brightness"]
        g=p["glow"]
        painter.rotate(self.rot_outer)
        r=self.outer
        rect=QRectF(-r,-r,r*2,r*2)

        pen=QPen(self.color(0,235,255,28))
        pen.setWidthF(1.2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(),r,r)

        pen=QPen(self.color(0,235,255,170*b))
        pen.setWidthF(2.4*b)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        sectors=[
            (0,18),(26,10),(52,18),(84,26),
            (126,14),(154,20),(188,14),(214,22),
            (252,18),(286,24),(326,14)
        ]
        for start,sweep in sectors:
            painter.drawArc(rect,start*16,sweep*16)

        pen=QPen(self.color(235,248,255,140))
        pen.setWidthF(1.5)
        pen.setDashPattern([3,10])
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(),r-16,r-16)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255,255,255,170))
        orbit=r-5
        spin=math.radians(self.rot_outer)
        for a in range(0,360,60):
            ang=spin+math.radians(a)
            x=math.cos(ang)*orbit
            y=math.sin(ang)*orbit
            painter.drawEllipse(QPointF(x,y),1.4,1.4)

        pen=QPen(self.color(0,235,255,145*g))
        pen.setWidthF(1.3)
        painter.setPen(pen)
        gap=r+10
        size=14
        # FIX: Wrapped raw numbers in QPointF
        painter.drawLine(QPointF(-size, -gap), QPointF(size, -gap))
        painter.drawLine(QPointF(-gap, -size), QPointF(-gap, size))
        painter.drawLine(QPointF(-size, gap), QPointF(size, gap))
        painter.drawLine(QPointF(gap, -size), QPointF(gap, size))

        pen=QPen(self.color(0,235,255,35))
        pen.setWidthF(0.7)
        painter.setPen(pen)
        inner=r-18
        outer=r+6
        for a in range(0,360,15):
            rad=math.radians(a)
            painter.drawLine(
                QPointF(math.cos(rad)*inner,math.sin(rad)*inner),
                QPointF(math.cos(rad)*outer,math.sin(rad)*outer)
            )
        painter.restore()
        
    def draw_middle_ring(self,painter):
        painter.save()
        p=self.profile
        b=p["brightness"]
        painter.rotate(self.rot_middle)
        r=self.middle
        rect=QRectF(-r,-r,r*2,r*2)

        pen=QPen(self.color(235,248,255,175*b))
        pen.setWidthF(1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        arcs=[
            (0,24),(36,42),(94,12),
            (126,54),(208,28),(252,40),
            (318,20)
        ]
        for start,sweep in arcs:
            self.arc(painter,rect,self.color(235,248,255,175*b),1.6,start,sweep)

        pen=QPen(self.color(0,235,255,120))
        pen.setWidthF(1.0)
        pen.setDashPattern([2,5])
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(),r-8,r-8)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(0,235,255,170))
        orbit=r-4
        spin=math.radians(-self.rot_middle)
        for a in (0,120,240):
            ang=spin+math.radians(a)
            x=math.cos(ang)*orbit
            y=math.sin(ang)*orbit
            painter.drawEllipse(QPointF(x,y),3,3)

        self.arc(painter,rect,self.color(255,255,255,240),2.0,-self.rot_inner,12)

        pen=QPen(self.color(0,235,255,60))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        inner=r-14
        outer=r+2
        for a in range(0,360,20):
            rad=math.radians(a)
            painter.drawLine(
                QPointF(math.cos(rad)*inner,math.sin(rad)*inner),
                QPointF(math.cos(rad)*outer,math.sin(rad)*outer)
            )

        pen=QPen(self.color(255,255,255,45))
        pen.setWidthF(0.8)
        pen.setDashPattern([1,6])
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.drawEllipse(QPointF(),orbit+6,orbit+6)
        painter.restore()
        
    def draw_inner_ring(self,painter):
        painter.save()
        p=self.profile
        g=p["glow"]
        painter.rotate(-self.rot_inner)
        r=self.inner
        rect=QRectF(-r,-r,r*2,r*2)

        pen=QPen(self.color(0,235,255,95))
        pen.setWidthF(1.2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(),r,r)

        pen=QPen(self.color(0,235,255,95))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        for a in range(0,360,8):
            rad=math.radians(a)
            painter.drawLine(
                QPointF(math.cos(rad)*(r-8),math.sin(rad)*(r-8)),
                QPointF(math.cos(rad)*r,math.sin(rad)*r)
            )

        pen=QPen(self.color(255,255,255,145))
        pen.setWidthF(1.2)
        painter.setPen(pen)
        for a in range(0,360,30):
            rad=math.radians(a)
            painter.drawLine(
                QPointF(math.cos(rad)*(r-10),math.sin(rad)*(r-10)),
                QPointF(math.cos(rad)*(r+4),math.sin(rad)*(r+4))
            )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(0,235,255,110*g))
        orbit=r-20
        spin=math.radians(self.rot_inner*1.8)
        for i in range(16):
            ang=spin+math.radians(i*22.5)
            x=math.cos(ang)*orbit
            y=math.sin(ang)*orbit
            painter.save()
            painter.translate(x,y)
            painter.rotate(math.degrees(ang))
            painter.drawRoundedRect(QRectF(-1.5,-5,3,10),1,1)
            painter.restore()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255,255,255,170))
        orbit=r-28
        spin=math.radians(-self.rot_inner*2.4)
        for a in (0,90,145,270):
            ang=spin+math.radians(a)
            painter.drawEllipse(
                QPointF(math.cos(ang)*orbit, math.sin(ang)*orbit), 1.6, 1.6
            )

        self.arc(painter,rect,self.color(255,255,255,240),3.0,-self.rot_inner,12)

        pen=QPen(self.color(255,255,255,35))
        pen.setWidthF(0.8)
        pen.setDashPattern([2,7])
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.drawEllipse(QPointF(),r-34,r-34)
        painter.restore()
        
    def draw_segment_ring(self,painter):
        painter.save()
        p=self.profile
        b=p["brightness"]
        g=p["glow"]
        painter.rotate(self.rot_outer*0.55)
        r=self.segment
        rect=QRectF(-r,-r,r*2,r*2)

        pen=QPen(self.color(0,235,255,170*b))
        pen.setWidthF(2.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        sectors=[
            (0,10),(12,12),(48,8),(70,24),
            (110,12),(138,12),(178,8),(200,22),
            (242,10),(266,30),(318,12),(340,8)
        ]
        for start,sweep in sectors:
            self.arc(painter, rect, self.color(0,235,255,170*b), 2.2, start, sweep)

        inner=r-8
        scan_rect=QRectF(-inner,-inner,inner*2,inner*2)
        pen=QPen(self.color(235,248,255,120))
        pen.setWidthF(1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for angle in range(0,360,15):
            painter.drawArc(scan_rect,angle*16,5*16)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(0,235,255,170*g))
        orbit=r-16
        spin=math.radians(self.rot_middle*1.4)
        for i in range(18):
            ang=spin+math.radians(i*20)
            x=math.cos(ang)*orbit
            y=math.sin(ang)*orbit
            painter.save()
            painter.translate(x,y)
            painter.rotate(math.degrees(ang))
            painter.drawRoundedRect(QRectF(-1.5,-5,3,10),1.2,1.2)
            painter.restore()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255,255,255,160))
        orbit=r-30
        spin=math.radians(-self.rot_outer)
        for a in range(0,360,45):
            ang=spin+math.radians(a)
            painter.drawEllipse(
                QPointF(math.cos(ang)*orbit, math.sin(ang)*orbit), 1.4, 1.4
            )

        self.arc(painter,rect,self.color(255,255,255,235),2.0,-self.rot_outer,16)

        pen=QPen(self.color(0,235,255,40))
        pen.setWidthF(0.8)
        pen.setDashPattern([2,6])
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.drawEllipse(QPointF(),r-22,r-22)
        painter.restore()
        
    def draw_ticks(self,painter):
        painter.save()
        p=self.profile
        b=p["brightness"]
        painter.rotate(self.rot_outer*0.25)
        r=self.tick

        pen=QPen(self.color(0,235,255,45))
        pen.setWidthF(0.7)
        painter.setPen(pen)
        for angle in range(0,360,6):
            rad=math.radians(angle)
            painter.drawLine(
                QPointF(math.cos(rad)*(r-4),math.sin(rad)*(r-4)),
                QPointF(math.cos(rad)*r,math.sin(rad)*r)
            )

        pen=QPen(self.color(0,235,255,95))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        for angle in range(0,360,15):
            rad=math.radians(angle)
            painter.drawLine(
                QPointF(math.cos(rad)*(r-8),math.sin(rad)*(r-8)),
                QPointF(math.cos(rad)*(r+2),math.sin(rad)*(r+2))
            )

        pen=QPen(self.color(255,255,255,170*b))
        pen.setWidthF(1.8)
        painter.setPen(pen)
        for angle in range(0,360,30):
            rad=math.radians(angle)
            painter.drawLine(
                QPointF(math.cos(rad)*(r-14),math.sin(rad)*(r-14)),
                QPointF(math.cos(rad)*(r+6),math.sin(rad)*(r+6))
            )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(0,235,255,210))
        marker_radius=r+10
        for angle in (0,90,180,270):
            rad=math.radians(angle)
            x=math.cos(rad)*marker_radius
            y=math.sin(rad)*marker_radius
            painter.drawEllipse(QPointF(x,y), 2.6, 2.6)

        pen=QPen(self.color(255,255,255,120))
        pen.setWidthF(1.3)
        painter.setPen(pen)
        size=8
        offset=r+18
        # FIX: Wrapped raw numbers in QPointF
        painter.drawLine(QPointF(-size, -offset), QPointF(size, -offset))
        painter.drawLine(QPointF(-size, offset), QPointF(size, offset))
        painter.drawLine(QPointF(-offset, -size), QPointF(-offset, size))
        painter.drawLine(QPointF(offset, -size), QPointF(offset, size))

        pen=QPen(self.color(0,235,255,28))
        pen.setWidthF(0.9)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.drawEllipse(QPointF(),r+14,r+14)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(255,255,255,150))
        orbit=r+14
        spin=math.radians(self.rot_outer*1.6)
        for angle in range(0,360,60):
            ang=spin+math.radians(angle)
            painter.drawEllipse(
                QPointF(math.cos(ang)*orbit, math.sin(ang)*orbit), 1.5, 1.5
            )
        painter.restore()
        
    def draw_pulse_rings(self,painter):
        painter.save()
        p=self.profile
        b=p["brightness"]
        g=p["glow"]
        pulse=0.5+0.5*math.sin(self.wave)

        r=self.pulse*(0.95+0.05*pulse)
        self.arc(painter, QRectF(-r,-r,r*2,r*2), self.color(0,235,255,120*g), 2.2, self.rot_outer, 130)
        self.arc(painter, QRectF(-r,-r,r*2,r*2), self.color(255,255,255,170), 1.4, self.rot_outer+180, 70)

        shock=self.shock*(0.97+0.03*math.sin(self.wave*0.8))
        pen=QPen(self.color(0,235,255,45+45*pulse))
        pen.setWidthF(1.0)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), shock, shock)

        rr=self.arc_radius
        self.arc(painter, QRectF(-rr,-rr,rr*2,rr*2), self.color(255,255,255,210), 2.0, -self.rot_middle, 38)
        self.arc(painter, QRectF(-rr,-rr,rr*2,rr*2), self.color(0,235,255,170*b), 2.6, -self.rot_middle+120, 26)
        self.arc(painter, QRectF(-rr,-rr,rr*2,rr*2), self.color(0,235,255,150), 1.6, -self.rot_middle+235, 18)

        painter.setPen(Qt.PenStyle.NoPen)
        orbit=self.arc_radius
        spin=math.radians(self.rot_middle*2)
        for angle in (0,90,180,270):
            ang=spin+math.radians(angle)
            alpha=150+70*math.sin(self.wave+math.radians(angle))
            painter.setBrush(self.color(255, 255, 255, alpha))
            painter.drawEllipse(
                QPointF(math.cos(ang)*orbit, math.sin(ang)*orbit), 2.5, 2.5,
            )

        orbit=self.spark
        spin=math.radians(-self.rot_outer*2.5)
        painter.setBrush(self.color(0, 235, 255, 170*g))
        for i in range(24):
            ang=spin+math.radians(i*15)
            radius=0.6+(i%4)*0.35
            painter.drawEllipse(
                QPointF(math.cos(ang)*orbit, math.sin(ang)*orbit), radius, radius,
            )

        pen=QPen(self.color(255,255,255,55))
        pen.setWidthF(0.9)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        halo=self.pulse*0.72
        painter.drawEllipse(QPointF(), halo, halo)

        pen=QPen(self.color(0,235,255,90+50*pulse))
        pen.setWidthF(1.3)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        core=self.pulse*0.42*(0.98+0.04*pulse)
        painter.drawEllipse(QPointF(), core, core)
        painter.restore()
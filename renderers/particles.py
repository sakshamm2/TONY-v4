from __future__ import annotations

import math
import random

from PyQt6.QtCore import Qt,QPointF,QRectF
from PyQt6.QtGui import QColor,QPainter,QPen
print("ParticleRenderer Loaded From:", __file__)

class ParticleRenderer:
    ##################################################
    # Initialization
    #################################################
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
        
    ##################################################
    # Runtime Cache
    ##################################################
    def _cache_runtime(self):
        self.profile=self.hud.animation_profile()
        self.time=self.hud.wave_offset
        self.radius=self.hud.radius
        self.outer_rotation=self.hud.outer_rotation
        self.middle_rotation=self.hud.middle_rotation
        self.speed=self.profile.get("speed",1.0)
        self.alpha=self.profile.get("alpha",220)
        self.shift=self.profile.get("radius_shift",6.0)
        self.cyan=self.color(0,235,255,220)
        self.white=self.color(255,255,255,230)
        
    ##################################################
    # Draw Entry
    ##################################################
    def draw(self,painter):
        self._cache_runtime()
        self._initialize_particles()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        self.draw_particles(painter)
        self.draw_corner_nodes(painter)
        
    ##################################################
    # Particle Generation
    ##################################################
    def _initialize_particles(self):
        # --- ADD ONLY THIS DATA INJECTION BLOCK ---
        if not hasattr(self, 'radius'):
            # Safe default base radius for your 350x350 HUD layout
            self.radius = 130 
        # ------------------------------------------

        # ... LEAVE ALL YOUR EXISTING CODE BELOW UNTOUCHED ...
        # The code will continue down to line 69 naturally:
        # "radius": random.uniform(50, self.radius+40),
    ##################################################
    # Premium Particle Field
    ##################################################
    def draw_particles(self,painter):
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        for particle in self.hud.particles:
            ##################################################
            # Motion
            ##################################################
            particle["angle"]+=(particle["speed"]*self.speed*particle["orbit"])
            drift=math.sin(self.time*particle["drift"]+particle["phase"])*4
            breathe=math.sin(self.time*particle["pulse"]+particle["phase"])*self.shift
            radius=(particle["radius"]+drift+breathe)
            
            ##################################################
            # Position
            ##################################################
            x=math.cos(particle["angle"])*radius
            y=math.sin(particle["angle"])*radius
            
            ##################################################
            # Twinkle
            ##################################################
            twinkle=(math.sin(self.time*particle["twinkle"]+particle["phase"])+1)*0.5
            alpha=min(self.alpha, int(particle["alpha"]*(0.35+twinkle)))
            
            ##################################################
            # Size
            ##################################################
            size=particle["size"]
            if particle["layer"]=="fog":
                size*=0.80
            elif particle["layer"]=="tracker":
                size*=1.0+twinkle*0.35
                
            ##################################################
            # Color
            ##################################################
            color=QColor(particle["color"])
            color.setAlpha(self.clamp(alpha))
            painter.setBrush(color)
            
            ##################################################
            # Draw Particle
            ##################################################
            painter.drawEllipse(QPointF(x,y), size, size)
            
            ##################################################
            # Tracker Trail
            ##################################################
            if particle["layer"]=="tracker":
                trail=particle["trail"]
                tail=QPointF(
                    x-math.cos(particle["angle"])*trail,
                    y-math.sin(particle["angle"])*trail,
                )
                pen=QPen(QColor(color.red(), color.green(), color.blue(), self.clamp(alpha//3)))
                pen.setWidthF(1.0)
                painter.setPen(pen)
                painter.drawLine(QPointF(x,y), tail)
                painter.setPen(Qt.PenStyle.NoPen)
                
            ##################################################
            # Reactor Spark
            ##################################################
            if particle["layer"]=="core" and twinkle>0.92:
                painter.setBrush(self.white)
                painter.drawEllipse(QPointF(x,y), size*0.45, size*0.45)
        painter.restore()
        
    ##################################################
    # Premium Corner Nodes
    ##################################################
    def draw_corner_nodes(self,painter):
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        
        #################################################
        # Corner Nodes
        ##################################################
        painter.setBrush(self.white)
        orbit=self.radius+26
        spin=math.radians(self.outer_rotation*0.8)
        for angle in (45,135,225,315):
            a=spin+math.radians(angle)
            painter.drawEllipse(QPointF(math.cos(a)*orbit, math.sin(a)*orbit), 2.8, 2.8)
            
        ##################################################
        # Cross Axis Guides
        ##################################################
        pen=QPen(self.color(0, 235, 255, 40))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        guide=self.radius+12
        painter.drawLine(QPointF(-guide,0), QPointF( guide,0))
        painter.drawLine(QPointF(0,-guide), QPointF(0, guide))
        
        ##################################################
        # Alignment Markers
        ##################################################
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(0, 235, 255, 140))
        for angle in range(0,360,45):
            a=math.radians(angle)
            painter.drawEllipse(QPointF(math.cos(a)*(self.radius+4), math.sin(a)*(self.radius+4)), 1.6, 1.6)
            
        ##################################################
        # Orbit Pulse Nodes
        ##################################################
        orbit=self.radius+18
        painter.setBrush(self.white)
        spin=math.radians(self.middle_rotation)
        for angle in (0,90,180,270):
            a=spin+math.radians(angle)
            painter.drawEllipse(QPointF(math.cos(a)*orbit, math.sin(a)*orbit), 2.1, 2.1)
            
        ##################################################
        # Scanner Orbit Ring
        ##################################################
        pen=QPen(self.color(0, 235, 255, 65))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) # Ensures no fill leak
        painter.drawEllipse(QPointF(), self.radius+18, self.radius+18)
        
        ##################################################
        # Orbit Scanner Sweep
        ##################################################
        pen=QPen(self.color(255, 255, 255, 110))
        pen.setWidthF(1.3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush) # Ensures no fill leak
        rect=QRectF(-(self.radius+18), -(self.radius+18), (self.radius+18)*2, (self.radius+18)*2)
        painter.drawArc(rect, int(-self.outer_rotation*16), int(18*16))
        
        ##################################################
        # Rotating Micro Nodes
        ##################################################
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color(170, 250, 255, 150))
        orbit=self.radius+32
        spin=math.radians(self.outer_rotation*0.5)
        for i in range(12):
            a=spin+math.radians(i*30)
            painter.drawEllipse(QPointF(math.cos(a)*orbit, math.sin(a)*orbit), 1.1, 1.1)
            
        ##################################################
        # Cardinal Indicators
        ##################################################
        pen=QPen(self.color(255, 255, 255, 90))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        inner=self.radius+38
        outer=self.radius+46
        for angle in (0,90,180,270):
            a=math.radians(angle)
            painter.drawLine(
                QPointF(math.cos(a)*inner, math.sin(a)*inner),
                QPointF(math.cos(a)*outer, math.sin(a)*outer)
            )
        painter.restore()
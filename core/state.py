"""
Module   : core.state
Project  : T.O.N.Y. v4
Purpose  : Global Assistant Runtime State Model
"""

from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class TonyState:
    """
    Unified, reactive state model representing the real-time operational 
    status and telemetry metrics of the T.O.N.Y. assistant core.
    """
    initialized: bool = False
    listening: bool = False
    thinking: bool = False
    speaking: bool = False
    
    last_user_message: str = ""
    last_ai_response: str = ""
    
    cpu: float = 0.0
    ram: float = 0.0
    battery: float = 0.0
    internet: bool = True
    
    metadata: dict = field(default_factory=dict)